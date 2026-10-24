"""Line-by-line replica of the FINAL Pine script (tight counter-bias stop, tie epsilons). Self-contained apart from engine.prepare/rma."""
import os, sys, datetime
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
LOG = []
from engine import prepare as eprep, rma, rtick
IN = dict(structLen=10, entryLen=6, retestBars=5, dispAtr=0.8, dispBodyPct=55.0, dispClosePct=25.0, momLen=10, momAtr=0.85,
          rearmKeep=True, stopAtr=1.8, cooldownBars=2, maxFills=5, dayStopR=3.0, atrLen=14, vwapFilter=True, slopeBars=3,
          minOpenBars=1, skipSunday=True, tp4R=2.0, tightOn=True, tightAtr=0.9, netMin=3, eps=True, structSrc='wick', H=None, sameBarDayR=True, sameBarCool=True, netBlock=0, structReset=None, resetAnchor='exit', resetDir='any', resetLossOnly=False, legReset=0, slopeAll=False)
EPS = 1e-7
def run(sym, inp=None):
    p = dict(IN); p.update(inp or {}); e = EPS if p['eps'] else 0.0
    P = eprep(sym); R = P['rows']; n = len(R); mt = P['mt']
    atr = rma(P['tr'], p['atrLen'])
    O = [r['o'] for r in R]; H = [r['h'] for r in R]; L = [r['l'] for r in R]; C = [r['c'] for r in R]; V = [r['vwap'] for r in R]
    dow = [(datetime.datetime.strptime(r['t'], '%Y-%m-%d %H:%M') - datetime.timedelta(hours=5, minutes=30)).weekday() for r in R]
    st = 0; armBar = fillBar = lastExit = None; lim = stp = t4 = None
    dayFills = 0; dayR = 0.0; vwBars = 0; trades = []; cur = None
    # counter-bias state
    bullN = bearN = 0; prevNet = None
    for i in range(n):
        newAnchor = P['daystart'][i]; newDay = newAnchor
        vwBars = 0 if newAnchor else vwBars + 1
        if newDay:
            dayFills = 0; dayR = 0.0
            if i > 0: prevNet = bullN - bearN
            bullN = bearN = 0
        # 1. live trade
        if abs(st) == 2 and i > fillBar:
            isL = st == 2
            stopHit = L[i] <= stp if isL else H[i] >= stp
            tp4Hit = H[i] >= t4 if isL else L[i] <= t4
            if stopHit or tp4Hit:
                win = not stopHit; res = p['tp4R'] if win else -1.0
                dayR += res; lastExit = i; st = 0; cur.update(exit=i, res=res)
        # 2. armed limit
        if abs(st) == 1 and i > armBar:
            isL = st == 1
            touched = L[i] <= lim + 1e-3 * mt if isL else H[i] >= lim - 1e-3 * mt
            if touched and dayFills < p['maxFills']:
                st = 2 if isL else -2; fillBar = i; dayFills += 1
                cur = dict(dir=1 if isL else -1, arm=armBar, fill=i, entry=lim, stop=stp, exit=None, res=None, tight=tightArm); trades.append(cur)
                if (L[i] <= stp if isL else H[i] >= stp):
                    dayR += -1.0 if p['sameBarDayR'] else 0.0; lastExit = i if p['sameBarCool'] else lastExit; st = 0; cur.update(exit=i, res=-1.0)
            elif i - armBar >= p['retestBars']:
                st = 0
        if i < max(p['structLen'], p['entryLen'], p['momLen'], p['slopeBars']) + 1 or atr[i] is None: continue
        A = atr[i]
        priorHigh = max(H[i - p['structLen']:i]); priorLow = min(L[i - p['structLen']:i])
        entHigh = max(H[i - min(p['entryLen'], p['structLen']):i]); entLow = min(L[i - min(p['entryLen'], p['structLen']):i])
        rng = H[i] - L[i]; body = abs(C[i] - O[i]); bodyMid = (O[i] + C[i]) / 2
        momMove = C[i] - C[i - p['momLen']]
        vwSlope = V[i] - V[i - p['slopeBars']] if p['slopeBars'] > 0 and vwBars >= p['slopeBars'] else None
        slopeUp = vwSlope is None or vwSlope > 0; slopeDn = vwSlope is None or vwSlope < 0
        if p['slopeAll'] and vwSlope is not None:
            slopeUp = slopeUp and all(V[j] > V[j - 1] for j in range(i - p['slopeBars'] + 1, i + 1)); slopeDn = slopeDn and all(V[j] < V[j - 1] for j in range(i - p['slopeBars'] + 1, i + 1))
        bigCandle = rng > 0 and rng >= p['dispAtr'] * A and body / rng * 100 >= p['dispBodyPct'] - e
        if p['structSrc'] == 'close': sH = max(C[i - p['structLen']:i]); sL = min(C[i - p['structLen']:i])
        elif p['structSrc'] == 'body': sH = max(max(O[j], C[j]) for j in range(i - p['structLen'], i)); sL = min(min(O[j], C[j]) for j in range(i - p['structLen'], i))
        else: sH = priorHigh; sL = priorLow
        if p['structReset'] and lastExit is not None and 0 < i - lastExit < p['structLen'] and cur is not None and (not p['resetLossOnly'] or cur['res'] < 0):
            a0 = (lastExit if p['resetAnchor'] == 'exit' else cur['fill']) + (1 if p['structReset'] == 'excl' else 0)
            if a0 < i:
                if p['resetDir'] != 'same' or cur['dir'] == 1: sH = max(H[a0:i])
                if p['resetDir'] != 'same' or cur['dir'] == -1: sL = min(L[a0:i])
        if p['legReset'] and cur is not None and 0 < i - cur['fill'] < p['structLen'] and (cur['exit'] is not None):
            a0 = cur['fill']
            if cur['dir'] == 1 or p['legReset'] == 2: sH = max(H[a0:i])
            if cur['dir'] == -1 or p['legReset'] == 2: sL = min(L[a0:i])
        bullShape = C[i] > O[i] and C[i] > sH and bigCandle and (H[i] - C[i]) / rng * 100 <= p['dispClosePct'] + e
        bearShape = C[i] < O[i] and C[i] < sL and bigCandle and (C[i] - L[i]) / rng * 100 <= p['dispClosePct'] + e
        bullEvt = bullShape and slopeUp; bearEvt = bearShape and slopeDn
        bullImp = C[i] > O[i] and H[i] > priorHigh and bigCandle and (H[i] - C[i]) / rng * 100 <= p['dispClosePct'] + e and slopeUp
        bearImp = C[i] < O[i] and L[i] < priorLow and bigCandle and (C[i] - L[i]) / rng * 100 <= p['dispClosePct'] + e and slopeDn
        setupOk = vwBars >= p['minOpenBars'] and not (p['skipSunday'] and dow[i] == 6)
        bullDisp = setupOk and bullEvt and (not p['vwapFilter'] or C[i] > V[i]) and (p['momAtr'] <= 0 or momMove >= p['momAtr'] * A)
        bearDisp = setupOk and bearEvt and (not p['vwapFilter'] or C[i] < V[i]) and (p['momAtr'] <= 0 or -momMove >= p['momAtr'] * A)
        tightL = p['tightOn'] and bullN == 0 and prevNet is not None and prevNet <= -p['netMin']
        tightS = p['tightOn'] and bearN == 0 and prevNet is not None and prevNet >= p['netMin']
        if bullImp: bullN += 1
        if bearImp: bearN += 1
        # 3. arm
        cooled = lastExit is None or i - lastExit >= max(p['cooldownBars'], 1)
        dayOpen = p['dayStopR'] <= 0 or dayR > -p['dayStopR']
        canArm = abs(st) != 2 and cooled and dayFills < p['maxFills'] and dayOpen and A > 0
        keepArm = p['rearmKeep'] and ((st == 1 and bullDisp) or (st == -1 and bearDisp))
        if bullDisp or bearDisp: LOG.append((sym, R[i]['t'], 'SIG', 'L' if bullDisp else 'S', dict(st=st, canArm=canArm, keep=keepArm, cooled=cooled, dayOpen=dayOpen, dayR=dayR, dayFills=dayFills)))
        if canArm and (bullDisp or bearDisp) and not keepArm:
            isL = bullDisp; d = 1 if isL else -1
            entry = max(bodyMid, entHigh) if isL else min(bodyMid, entLow)
            tight = tightL if isL else tightS
            if p['netBlock'] and d * (bullN - bearN) <= -p['netBlock']: continue
            stop = (min(entry - p['tightAtr'] * A, L[i]) if isL else max(entry + p['tightAtr'] * A, H[i])) if tight else entry - d * p['stopAtr'] * A
            risk = d * (entry - stop)
            if risk >= mt and rtick(stop, mt) != rtick(entry, mt):
                st = d; armBar = i; lim = entry; stp = stop; t4 = lim + d * p['tp4R'] * risk; tightArm = tight
                LOG.append((sym, R[i]['t'], 'ARM', d, dict(entry=entry, stop=stop, tight=tight, rA=risk/A, prevNet=prevNet, bullN=bullN, bearN=bearN)))
    return trades
def score(inp=None, detail=False):
    import gtscore
    from engine2 import prepare as p2
    orig = gtscore.run
    def _r(P, cfg):
        if ('atr', 14) not in P: P[('atr', 14)] = rma(P['tr'], 14)
        return run(P['sym'], inp)
    gtscore.run = _r
    try:
        tr, win = gtscore.load_gt('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/../gt/final')
        return gtscore.score({}, tr, [dict(w) for w in win], detail=detail)
    finally:
        gtscore.run = orig
if __name__ == '__main__':
    import json
    inp = json.loads(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].startswith('{') else {}
    r, rows = score(inp, True); print({k: r[k] for k in ('exact', 'miss', 'extra')})
    if 'd' in sys.argv[1:]: [print('  ', *x) for x in rows if x[0] != 'ok']
