"""Fast parameterised engine for rule fitting (same state machine as the Pine indicator, with variant switches)."""
import math, os, sys
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from engine import prepare as _prep, rma, rtick
from engine2 import prepare
TIES=[]

BASE = dict(brkLen=6, entryLen=6, retest=5, dispAtr=0.8, bodyPct=60.0, closePct=30.0, brkMin=0.0, bodyAtr=0.0,
            stopAtr=1.8, cooldown=2, cancelCool=0, maxFills=5, atrLen=14, tp4=2.0, vwap='close',
            minBars=0, rearm='replace', stopMode='atr', stopMinAtr=1.0, stopBuf=0.0, swingLen=6, fillTouchStrict=False,
            maxVwapAtr=0.0, armOnExitBar=False, entryMode='maxmid', roundLevels=True, maxLossDay=0, rearmBetter=False, sessEntry=False, coolWin=None, coolLoss=None, maxDayR=0.0, consecLoss=0)

_cache = {}
def _unused_prepare(sym):
    if sym in _cache: return _cache[sym]
    P = _prep(sym); R = P['rows']; n = len(R)
    P['O'] = [r['o'] for r in R]; P['H'] = [r['h'] for r in R]; P['L'] = [r['l'] for r in R]; P['C'] = [r['c'] for r in R]
    P['V'] = [r['vwap'] for r in R]; P['T'] = [r['t'] for r in R]
    sinc = [0] * n; k = 0
    for i in range(n):
        k = 0 if P['daystart'][i] else k + 1
        sinc[i] = k
    P['sinceStart'] = sinc; P['sym'] = sym
    import datetime as _dt
    P['dowutc'] = [(_dt.datetime.strptime(t, '%Y-%m-%d %H:%M') - _dt.timedelta(hours=5, minutes=30)).weekday() for t in P['T']]
    _cache[sym] = P
    return P

def hh(H, i, n): return max(H[i - n:i])
def ll(L, i, n): return min(L[i - n:i])

def run(P, cfg=None):
    c = dict(BASE); c.update(cfg or {})
    O, H, L, C, V = P['O'], P['H'], P['L'], P['C'], P['V']
    mt = P['mt']; n = len(O)
    key = ('atr', c['atrLen'])
    if key not in P: P[key] = rma(P['tr'], c['atrLen'])
    atr = P[key]
    st = 0; armBar = fillBar = lastExit = lastCancel = None; lim = stp = t4 = None; rk_ = None
    dayFills = 0; dayLoss = 0; dayR = 0.0; streak = 0; lastRes = 0.0; trades = []; cur = None
    rl = (lambda x: rtick(x, mt)) if c['roundLevels'] else (lambda x: x)
    mx = max(c['brkLen'], c['entryLen'], c['swingLen']) + 1
    for i in range(n):
        if P['daystart'][i]: dayFills = 0; dayLoss = 0; dayR = 0.0; streak = 0
        if abs(st) == 2 and i > fillBar:
            isL = st == 2
            sh = L[i] <= stp if isL else H[i] >= stp
            th = H[i] >= t4 if isL else L[i] <= t4
            if sh or th:
                cur['exit'] = i; cur['res'] = -1.0 if sh else c['tp4']; lastExit = i; st = 0; lastRes = cur['res']; dayR += cur['res']
                if sh: dayLoss += 1; streak += 1
                else: streak = 0
        if abs(st) == 1 and i > armBar:
            isL = st == 1
            ef = c.get('epsF', 0.0) * mt
            if abs((L[i] if isL else H[i]) - lim) <= 1e-6 * mt: TIES.append(('fill', P['sym'], P['T'][i], L[i] if isL else H[i], lim))
            touched = (L[i] <= lim + ef if isL else H[i] >= lim - ef)
            if touched and dayFills < c['maxFills']:
                st = 2 if isL else -2; fillBar = i; dayFills += 1
                cur = dict(dir=1 if isL else -1, arm=armBar, fill=i, entry=lim, stop=stp, t4=t4, exit=None, res=None)
                trades.append(cur)
                if (L[i] <= stp if isL else H[i] >= stp):
                    cur['exit'] = i; cur['res'] = -1.0; lastExit = i; st = 0; dayLoss += 1; streak += 1; lastRes = -1.0; dayR -= 1.0
            elif i - armBar >= c['retest']:
                st = 0; lastCancel = i
        if i < mx or atr[i] is None or atr[i] <= 0: continue
        if abs(st) == 2: continue
        if lastExit is not None:
            gap = i - lastExit
            cd = c['cooldown']
            if lastRes > 0 and c['coolWin'] is not None: cd = c['coolWin']
            if lastRes < 0 and c['coolLoss'] is not None: cd = c['coolLoss']
            if gap < cd or (gap == 0 and not c['armOnExitBar']): continue
        if c['cancelCool'] and lastCancel is not None and i - lastCancel < c['cancelCool']: continue
        if dayFills >= c['maxFills']: continue
        if c['maxLossDay'] and dayLoss >= c['maxLossDay']: continue
        if c['maxDayR'] and dayR <= -c['maxDayR']: continue
        if c['consecLoss'] and streak >= c['consecLoss']: continue
        if P['sinceStart'][i] < c['minBars']: continue
        if abs(st) == 1 and c['rearm'] == 'ignore': continue
        A = atr[i]; o, h, l, cl = O[i], H[i], L[i], C[i]; rng = h - l
        if rng <= 0: continue
        body = abs(cl - o)
        er = c.get('epsR', 0.0)
        bp = body / rng * 100
        if rng >= c['dispAtr'] * A and abs(bp - c['bodyPct']) < 1e-6: TIES.append(('body', P['sym'], P['T'][i], bp))
        if rng < c['dispAtr'] * A or bp < c['bodyPct'] - er or body < c['bodyAtr'] * A: continue
        up = cl > o; dn = cl < o
        vw = V[i]
        bull = bear = False
        if up and abs((h - cl) / rng * 100 - c['closePct']) < 1e-6: TIES.append(('closeU', P['sym'], P['T'][i], (h - cl) / rng * 100))
        if dn and abs((cl - l) / rng * 100 - c['closePct']) < 1e-6: TIES.append(('closeD', P['sym'], P['T'][i], (cl - l) / rng * 100))
        if up and (h - cl) / rng * 100 <= c['closePct'] + er:
            ph = hh(H, i, c['brkLen']) if c.get('brkSrc', 'wick') == 'wick' else (max(C[i - c['brkLen']:i]) if c['brkSrc'] == 'close' else max(max(O[x], C[x]) for x in range(i - c['brkLen'], i)))
            bull = cl > ph + c['brkMin'] * A
        if dn and (cl - l) / rng * 100 <= c['closePct'] + er:
            pl = ll(L, i, c['brkLen']) if c.get('brkSrc', 'wick') == 'wick' else (min(C[i - c['brkLen']:i]) if c['brkSrc'] == 'close' else min(min(O[x], C[x]) for x in range(i - c['brkLen'], i)))
            bear = cl < pl - c['brkMin'] * A
        if c['vwap'] == 'close':
            bull = bull and vw is not None and cl > vw; bear = bear and vw is not None and cl < vw
        elif c['vwap'] == 'open':
            bull = bull and vw is not None and o > vw and cl > vw; bear = bear and vw is not None and o < vw and cl < vw
        if c.get('zMin'):
            if 'vsd' not in P:
                from volrec import recover; recover(P['sym'])
            sd = P['vsd'][i]; z = (cl - vw) / sd if sd else 0.0
            bull = bull and z >= c['zMin']; bear = bear and -z >= c['zMin']
        if c.get('noSunUTC') and P['dowutc'][i] == 6: bull = bear = False
        if c.get('momMin'):
            mn = c.get('momN', 10); mv = cl - C[i - mn]
            bull = bull and mv >= c['momMin'] * A; bear = bear and -mv >= c['momMin'] * A
        if c.get('vsLag'):
            lg = c['vsLag']
            if P['sinceStart'][i] >= lg:
                sl = V[i] - V[i - lg]
                bull = bull and sl > c.get('vsMin', 0.0) * A; bear = bear and -sl > c.get('vsMin', 0.0) * A
        if c['maxVwapAtr'] and vw is not None:
            if abs(cl - vw) > c['maxVwapAtr'] * A: bull = bear = False
        if not (bull or bear): continue
        d = 1 if bull else -1
        if abs(st) == 1 and c['rearm'] == 'samedir' and st == d: continue
        ctx = dict(trades=trades, dayFills=dayFills, dayLoss=dayLoss, dayR=dayR, streak=streak, lastExit=lastExit, lastRes=lastRes, st=st, armBar=armBar, lim=lim)
        if c.get('armFn') and not c['armFn'](P, i, d, ctx): continue
        mid = (o + cl) / 2
        if bull:
            lvl = hh(H, i, c['entryLen']); entry = max(mid, lvl) if c['entryMode'] == 'maxmid' else mid
        else:
            lvl = ll(L, i, c['entryLen']); entry = min(mid, lvl) if c['entryMode'] == 'maxmid' else mid
        if c['stopMode'] == 'atr':
            stop = entry - d * c['stopAtr'] * A
        elif c['stopMode'] == 'disp':   # beyond the displacement candle extreme + buffer, clamped to [stopMinAtr, stopAtr] x ATR
            s0 = (l - c['stopBuf'] * A) if bull else (h + c['stopBuf'] * A)
            dist = min(max(d * (entry - s0), c['stopMinAtr'] * A), c['stopAtr'] * A)
            stop = entry - d * dist
        elif c['stopMode'] == 'swing':
            s0 = (min(L[i - c['swingLen'] + 1:i + 1]) - c['stopBuf'] * A) if bull else (max(H[i - c['swingLen'] + 1:i + 1]) + c['stopBuf'] * A)
            dist = min(max(d * (entry - s0), c['stopMinAtr'] * A), c['stopAtr'] * A)
            stop = entry - d * dist
        if c.get('stopFn'): stop = c['stopFn'](P, i, d, entry, stop, A, ctx)
        if c.get('tightSet') and (P['sym'], P['T'][i]) in c['tightSet']:
            stop = entry - d * max(0.9 * A, d * (entry - ((l) if bull else (h))))
        rk = d * (entry - stop)
        if rk >= mt and rtick(stop, mt) != rtick(entry, mt):
            if abs(st) == 1 and c['rearmBetter'] and st == d and d * (entry - lim) < 0:
                pass  # keep the existing, better-priced limit
            else:
                st = d; armBar = i; lim = rl(entry); stp = rl(stop); rk_ = rk
                t4 = rl(lim + d * c['tp4'] * rk)
    return trades
