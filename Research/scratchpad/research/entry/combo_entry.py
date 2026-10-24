"""Research copy of hunt4/combo.py (key=entry): entry / stop / management options, all default OFF (defaults == combo.py).
New options:
  entryMode: 'base' | 'candle' (H - f*(H-L) of the signal candle) | 'leg' (H - f*(H - lowest low of legLen bars incl. signal)) |
             'vwap' (VWAP of the signal bar) | 'vwapLive' (limit follows VWAP of the previous bar) | 'atr' (close - f*ATR)
  entryFib f, legLen, deepOnly (never shallower than the base entry), retestBars (existing)
  stopMode: 'atr' (base: entry -/+ stopAtr*ATR, tight rule kept) | 'basePx' (keep the base stop price) | 'candle' (signal candle extreme -/+ stopBuf*ATR)
            | 'leg' (leg extreme -/+ stopBuf*ATR); stopMinAtr / stopMaxAtr clamp the risk in ATR
  confirm: after the limit is touched, wait up to confBars bars (touch bar included if confSame) for a close back in the trade direction
           (confType 'bull' C>O, 'reclaim' C>limit, 'both', 'brk' C>H[-1]); enter at that close; confStop 'pull' (pullback extreme -/+ stopBuf*ATR),
           'orig' (armed stop), 'atr' (close -/+ stopAtr*ATR, never inside the pullback bar); cancelled if the armed stop trades first.
  csR/csBars/csFill: exit at the close when the close is csR R against the entry (within csBars bars, fill bar too if csFill).
  extK/extRef: use the deeper entry only if the base entry is more than extK ATR beyond the leg extreme ('leg') or VWAP ('vwap').
  management: beR (move stop to entry+beOff*R after +beR R), partR/partFrac (bank partFrac at +partR R, partBE -> stop to BE after),
              tsBars/tsR (exit at close after tsBars bars if the trade never reached +tsR R).
Decisions are taken only from data up to the signal bar (arm) or the bar on which the order is placed."""
import os, sys, datetime
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from engine import prepare as eprep, rma, rtick
IN = dict(structLen=10, entryLen=6, retestBars=5, dispAtr=0.8, dispBodyPct=55.0, dispClosePct=25.0, momLen=10, momAtr=0.85,
          rearmKeep=True, stopAtr=1.8, cooldownBars=2, maxFills=5, dayStopR=3.0, atrLen=14, vwapFilter=True, slopeBars=3,
          minOpenBars=1, skipSunday=True, tp4R=2.0, tightOn=True, tightAtr=0.9, netMin=3, eps=True, legReset=True, sameBarDayStop=False,
          slopeCross=False, tightOut=False, erMin=0.0, erLen=0, legFrom='fill',
          entryMode='base', entryFib=0.5, legLen=10, deepOnly=False, stopMode='atr', stopBuf=0.0, stopMinAtr=0.0, stopMaxAtr=0.0,
          confirm=False, confBars=3, confSame=True, confType='bull', confStop='pull', confMaxChase=0.0,
          beR=0.0, beOff=0.0, partR=0.0, partFrac=0.5, partBE=False, tsBars=0, tsR=0.5,
          csR=0.0, csBars=0, csFill=False, extK=0.0, extRef='leg')
EPS = 1e-7
_P = {}
def run(sym, inp=None):
    p = dict(IN); p.update(inp or {}); e = EPS if p['eps'] else 0.0
    if sym not in _P: _P[sym] = eprep(sym)
    P = _P[sym]; R = P['rows']; n = len(R); mt = P['mt']
    atr = rma(P['tr'], p['atrLen'])
    O = [r['o'] for r in R]; H = [r['h'] for r in R]; L = [r['l'] for r in R]; C = [r['c'] for r in R]; V = [r['vwap'] for r in R]
    dow = [(datetime.datetime.strptime(r['t'], '%Y-%m-%d %H:%M') - datetime.timedelta(hours=5, minutes=30)).weekday() for r in R]
    st = 0; armBar = fillBar = lastExit = None; lim = stp = t4 = None; tightArm = False; dist = None; armA = None
    dayFills = 0; dayR = 0.0; dayRiskR = 0.0; vwBars = 0; trades = []; cur = None
    touchBar = None; pullX = None
    # live-trade management state
    risk0 = ent = None; realized = 0.0; rem = 1.0; partDone = beDone = False; mfe = 0.0
    bullN = bearN = 0; prevNet = None
    sesH = sesL = sesO = pdH = pdL = None
    def close_trade(i, res):
        nonlocal st, lastExit, dayR, dayRiskR
        dayR += res; dayRiskR += res; lastExit = i; st = 0; cur.update(exit=i, res=res)
    def open_trade(i, d, entry, stop, tight):
        nonlocal st, fillBar, dayFills, cur, risk0, ent, realized, rem, partDone, beDone, mfe, stp, t4, lim
        st = 2 * d; fillBar = i; dayFills += 1; lim = entry; stp = stop; risk0 = d * (entry - stop); ent = entry
        t4 = entry + d * p['tp4R'] * risk0; realized = 0.0; rem = 1.0; partDone = beDone = False; mfe = 0.0
        cur = dict(dir=d, arm=armBar, fill=i, entry=entry, stop=stop, exit=None, res=None, tight=tight); trades.append(cur)
    for i in range(n):
        newAnchor = P['daystart'][i]; newDay = newAnchor
        vwBars = 0 if newAnchor else vwBars + 1
        if newDay:
            dayFills = 0; dayR = 0.0; dayRiskR = 0.0
            if i > 0: prevNet = bullN - bearN
            bullN = bearN = 0
            pdH, pdL = sesH, sesL; sesH, sesL, sesO = H[i], L[i], O[i]
        else:
            sesH = H[i] if sesH is None else max(sesH, H[i]); sesL = L[i] if sesL is None else min(sesL, L[i])
        # 1. live trade
        if abs(st) == 2 and i > fillBar:
            isL = st == 2; d = 1 if isL else -1
            stopHit = L[i] <= stp if isL else H[i] >= stp
            tp4Hit = H[i] >= t4 if isL else L[i] <= t4
            fav = d * ((H[i] if isL else L[i]) - ent) / risk0
            if stopHit:
                sr = -1.0 if stp == cur['stop'] else d * (stp - ent) / risk0
                close_trade(i, realized + rem * sr)
            elif tp4Hit:
                if p['partR'] > 0 and not partDone: realized += p['partFrac'] * p['partR']; rem -= p['partFrac']
                close_trade(i, realized + rem * p['tp4R'])
            else:
                mfe = max(mfe, fav)
                if p['partR'] > 0 and not partDone and fav >= p['partR']:
                    realized += p['partFrac'] * p['partR']; rem -= p['partFrac']; partDone = True
                    if p['partBE']: stp = ent + d * p['beOff'] * risk0; beDone = True
                if p['beR'] > 0 and not beDone and fav >= p['beR']:
                    stp = ent + d * p['beOff'] * risk0; beDone = True
                if p['tsBars'] > 0 and i - fillBar >= p['tsBars'] and mfe < p['tsR']:
                    close_trade(i, realized + rem * d * (C[i] - ent) / risk0)
                elif p['csR'] > 0 and (p['csBars'] <= 0 or i - fillBar <= p['csBars']) and d * (C[i] - ent) / risk0 <= -p['csR']:
                    close_trade(i, realized + rem * d * (C[i] - ent) / risk0)
        # 2b. touched, waiting for a confirmation close
        if abs(st) == 3 and i > touchBar:
            isL = st == 3; d = 1 if isL else -1
            pullX = min(pullX, L[i]) if isL else max(pullX, H[i])
            if (L[i] <= stp if isL else H[i] >= stp): st = 0
            elif i - touchBar > p['confBars']: st = 0
        # 2. armed limit
        if abs(st) == 1 and i > armBar:
            isL = st == 1; d = 1 if isL else -1
            if p['entryMode'] == 'vwapLive':
                lim = V[i - 1]; stp = lim - d * dist
            touched = L[i] <= lim + 1e-3 * mt if isL else H[i] >= lim - 1e-3 * mt
            if touched and dayFills < p['maxFills']:
                if p['confirm']:
                    if (L[i] <= stp if isL else H[i] >= stp): st = 0          # armed stop traded before any confirmation
                    else: st = 3 * d; touchBar = i; pullX = L[i] if isL else H[i]
                else:
                    open_trade(i, d, lim, stp, tightArm)
                    if (L[i] <= stp if isL else H[i] >= stp): close_trade(i, -1.0)
                    elif p['csR'] > 0 and p['csFill'] and d * (C[i] - lim) / risk0 <= -p['csR']: close_trade(i, d * (C[i] - lim) / risk0)
            elif i - armBar >= p['retestBars']:
                st = 0
        # confirmation check (the touch bar itself counts when confSame)
        if abs(st) == 3 and (i > touchBar or p['confSame']) and dayFills < p['maxFills']:
            isL = st == 3; d = 1 if isL else -1; A0 = atr[i]
            ct = p['confType']
            okBull = C[i] > O[i] if isL else C[i] < O[i]
            okRec = C[i] > lim if isL else C[i] < lim
            okBrk = C[i] > H[i - 1] if isL else C[i] < L[i - 1]
            ok = okBull if ct == 'bull' else okRec if ct == 'reclaim' else (okBull and okRec) if ct == 'both' else okBrk
            if ok and p['confMaxChase'] > 0 and d * (C[i] - lim) > p['confMaxChase'] * A0: ok = False
            if ok:
                entry = C[i]
                if p['confStop'] == 'orig': stop = stp
                elif p['confStop'] == 'atr': stop = entry - d * p['stopAtr'] * A0
                else: stop = pullX - d * p['stopBuf'] * A0
                if p['stopMinAtr'] > 0: stop = min(stop, entry - p['stopMinAtr'] * A0) if isL else max(stop, entry + p['stopMinAtr'] * A0)
                if p['stopMaxAtr'] > 0: stop = max(stop, entry - p['stopMaxAtr'] * A0) if isL else min(stop, entry + p['stopMaxAtr'] * A0)
                tickOff = mt  # stop must lie beyond this bar's extreme (order placed at the close)
                stop = min(stop, L[i] - tickOff) if isL else max(stop, H[i] + tickOff)
                if d * (entry - stop) >= mt: open_trade(i, d, entry, stop, tightArm)
                else: st = 0
        if i < max(p['structLen'], p['entryLen'], p['momLen'], p['slopeBars'], p['legLen']) + 1 or atr[i] is None: continue
        A = atr[i]
        priorHigh = max(H[i - p['structLen']:i]); priorLow = min(L[i - p['structLen']:i])
        entHigh = max(H[i - min(p['entryLen'], p['structLen']):i]); entLow = min(L[i - min(p['entryLen'], p['structLen']):i])
        rng = H[i] - L[i]; body = abs(C[i] - O[i]); bodyMid = (O[i] + C[i]) / 2
        momMove = C[i] - C[i - p['momLen']]
        vwSlope = V[i] - V[i - p['slopeBars']] if p['slopeBars'] > 0 and vwBars >= p['slopeBars'] else None
        slopeUp = vwSlope is None or vwSlope > 0; slopeDn = vwSlope is None or vwSlope < 0
        bigCandle = rng > 0 and rng >= p['dispAtr'] * A and body / rng * 100 >= p['dispBodyPct'] - e
        brkH, brkL = priorHigh, priorLow
        if p['legReset'] and cur is not None and cur['exit'] is not None and 0 < i - cur[p['legFrom']] < p['structLen']:
            if cur['dir'] == 1: brkH = max(H[cur['fill']:i])
            else: brkL = min(L[cur['fill']:i])
        bullShape = C[i] > O[i] and C[i] > brkH and bigCandle and (H[i] - C[i]) / rng * 100 <= p['dispClosePct'] + e
        bearShape = C[i] < O[i] and C[i] < brkL and bigCandle and (C[i] - L[i]) / rng * 100 <= p['dispClosePct'] + e
        if p['slopeCross'] and vwSlope is None and i >= p['slopeBars']:
            xs = V[i] - V[i - p['slopeBars']]; sU = xs > 0; sD = xs < 0
        else: sU, sD = slopeUp, slopeDn
        bullEvt = bullShape and sU; bearEvt = bearShape and sD
        bullImp = C[i] > O[i] and H[i] > priorHigh and bigCandle and (H[i] - C[i]) / rng * 100 <= p['dispClosePct'] + e and slopeUp
        bearImp = C[i] < O[i] and L[i] < priorLow and bigCandle and (C[i] - L[i]) / rng * 100 <= p['dispClosePct'] + e and slopeDn
        setupOk = vwBars >= p['minOpenBars'] and not (p['skipSunday'] and dow[i] == 6)
        if p['erMin'] > 0:
            nE = p['erLen'] or p['momLen']; pathE = sum(abs(C[j] - C[j - 1]) for j in range(i - nE + 1, i + 1)); netE = C[i] - C[i - nE]
            erUp = pathE > 0 and netE / pathE >= p['erMin']; erDn = pathE > 0 and -netE / pathE >= p['erMin']
        else: erUp = erDn = True
        bullDisp = setupOk and bullEvt and (not p['vwapFilter'] or C[i] > V[i]) and (p['momAtr'] <= 0 or momMove >= p['momAtr'] * A) and erUp
        bearDisp = setupOk and bearEvt and (not p['vwapFilter'] or C[i] < V[i]) and (p['momAtr'] <= 0 or -momMove >= p['momAtr'] * A) and erDn
        tightL = p['tightOn'] and bullN == 0 and prevNet is not None and prevNet <= -p['netMin']
        tightS = p['tightOn'] and bearN == 0 and prevNet is not None and prevNet >= p['netMin']
        if p['tightOut'] and pdH is not None:
            tightL = tightL or (p['tightOn'] and bullN == 0 and sesO < pdL)
            tightS = tightS or (p['tightOn'] and bearN == 0 and sesO > pdH)
        if bullImp: bullN += 1
        if bearImp: bearN += 1
        # 3. arm
        cooled = lastExit is None or i - lastExit >= max(p['cooldownBars'], 1)
        dayOpen = p['dayStopR'] <= 0 or dayRiskR > -p['dayStopR']
        canArm = abs(st) != 2 and cooled and dayFills < p['maxFills'] and dayOpen and A > 0
        keepArm = p['rearmKeep'] and ((st in (1, 3) and bullDisp) or (st in (-1, -3) and bearDisp))
        if canArm and (bullDisp or bearDisp) and not keepArm:
            isL = bullDisp; d = 1 if isL else -1
            base = max(bodyMid, entHigh) if isL else min(bodyMid, entLow)
            tight = tightL if isL else tightS
            baseStop = (min(base - p['tightAtr'] * A, L[i]) if isL else max(base + p['tightAtr'] * A, H[i])) if tight else base - d * p['stopAtr'] * A
            em, f = p['entryMode'], p['entryFib']
            legX = min(L[i - p['legLen'] + 1:i + 1]) if isL else max(H[i - p['legLen'] + 1:i + 1])
            if em == 'base': entry = base
            elif em == 'candle': entry = H[i] - f * rng if isL else L[i] + f * rng
            elif em == 'leg': entry = H[i] - f * (H[i] - legX) if isL else L[i] + f * (legX - L[i])
            elif em in ('vwap', 'vwapLive'): entry = V[i]
            elif em == 'atr': entry = C[i] - d * f * A
            else: raise ValueError(em)
            if p['deepOnly']: entry = min(entry, base) if isL else max(entry, base)
            if p['extK'] > 0:   # deepen only when the base entry is extended from the leg start / VWAP
                ref = legX if p['extRef'] == 'leg' else V[i]
                if d * (base - ref) / A <= p['extK']: entry = base
            sm = p['stopMode']
            if sm == 'atr':
                stop = (min(entry - p['tightAtr'] * A, L[i]) if isL else max(entry + p['tightAtr'] * A, H[i])) if tight else entry - d * p['stopAtr'] * A
            elif sm == 'basePx': stop = baseStop
            elif sm == 'candle': stop = L[i] - p['stopBuf'] * A if isL else H[i] + p['stopBuf'] * A
            elif sm == 'leg': stop = legX - d * p['stopBuf'] * A
            else: raise ValueError(sm)
            if p['stopMinAtr'] > 0: stop = min(stop, entry - p['stopMinAtr'] * A) if isL else max(stop, entry + p['stopMinAtr'] * A)
            if p['stopMaxAtr'] > 0: stop = max(stop, entry - p['stopMaxAtr'] * A) if isL else min(stop, entry + p['stopMaxAtr'] * A)
            risk = d * (entry - stop)
            if risk >= mt and rtick(stop, mt) != rtick(entry, mt):
                st = d; armBar = i; lim = entry; stp = stop; t4 = lim + d * p['tp4R'] * risk; tightArm = tight; dist = risk; armA = A
    return trades
