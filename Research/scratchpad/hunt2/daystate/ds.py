"""Line-by-line replica of the FINAL Pine script (tight counter-bias stop, tie epsilons). Self-contained apart from engine.prepare/rma."""
import os, sys, datetime
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from engine import prepare as eprep, rma, rtick
IN = dict(structLen=10, entryLen=6, retestBars=5, dispAtr=0.8, dispBodyPct=55.0, dispClosePct=25.0, momLen=10, momAtr=0.85,
          rearmKeep=True, stopAtr=1.8, cooldownBars=2, maxFills=5, dayStopR=3.0, atrLen=14, vwapFilter=True, slopeBars=3,
          minOpenBars=1, skipSunday=True, tp4R=2.0, tightOn=True, tightAtr=0.9, netMin=3, eps=True, legReset=True, sameBarDayStop=False,
          dsMode='R', dsStrict=False, dsLoss=3, eveReset=None, eveSyms=('CRUDE',), eodFlat=False, eodCancel=False, minOpenBarsSyms=None)
EPS = 1e-7
def run(sym, inp=None):
    p = dict(IN); p.update(inp or {}); e = EPS if p['eps'] else 0.0
    P = eprep(sym); R = P['rows']; n = len(R); mt = P['mt']
    atr = rma(P['tr'], p['atrLen'])
    O = [r['o'] for r in R]; H = [r['h'] for r in R]; L = [r['l'] for r in R]; C = [r['c'] for r in R]; V = [r['vwap'] for r in R]
    dow = [(datetime.datetime.strptime(r['t'], '%Y-%m-%d %H:%M') - datetime.timedelta(hours=5, minutes=30)).weekday() for r in R]
    st = 0; armBar = fillBar = lastExit = None; lim = stp = t4 = None
    dayFills = 0; dayR = 0.0; dayRiskR = 0.0; vwBars = 0; trades = []; cur = None
    # counter-bias state
    bullN = bearN = 0; prevNet = None
    dayLoss = {1: 0, -1: 0}; dayLossAll = 0
    eveHM = p['eveReset'] if (p['eveReset'] and sym in p['eveSyms']) else None
    def book(res, d, sameBar):
        nonlocal dayLossAll
        if res < 0 and not sameBar: dayLoss[d] += 1; dayLossAll += 1
    for i in range(n):
        newAnchor = P['daystart'][i]
        newDay = newAnchor or (eveHM is not None and R[i]['t'][11:] == eveHM)
        if p['eodCancel'] and newAnchor and abs(st) == 1: st = 0
        vwBars = 0 if newAnchor else vwBars + 1
        if newDay:
            dayFills = 0; dayR = 0.0; dayRiskR = 0.0; dayLoss = {1: 0, -1: 0}; dayLossAll = 0
        if newAnchor:
            if i > 0: prevNet = bullN - bearN
            bullN = bearN = 0
        # 1. live trade
        if abs(st) == 2 and i > fillBar:
            isL = st == 2
            stopHit = L[i] <= stp if isL else H[i] >= stp
            tp4Hit = H[i] >= t4 if isL else L[i] <= t4
            risk0 = abs(cur['entry'] - cur['stop'])
            if stopHit or tp4Hit:
                win = not stopHit; res = p['tp4R'] if win else -1.0
                if p['dsMode'] == 'netR' and not win:
                    k = int(cur.get('mfe', 0.0) / (0.5 * risk0) + 1e-9) if risk0 > 0 else 0
                    res = 0.5 * min(k, 3) if k >= 1 else -1.0
                dayR += res; dayRiskR += res; lastExit = i; st = 0; cur.update(exit=i, res=res); book(res, cur['dir'], False)
            else:
                cur['mfe'] = max(cur.get('mfe', 0.0), (H[i] - cur['entry']) if isL else (cur['entry'] - L[i]))
            if st != 0 and p['eodFlat'] and i + 1 < n and P['daystart'][i + 1]:
                res = (C[i] - cur['entry']) / risk0 * (1 if isL else -1) if risk0 > 0 else 0.0
                dayR += res; dayRiskR += res; lastExit = i; st = 0; cur.update(exit=i, res=res, eod=True)
        # 2. armed limit
        if abs(st) == 1 and i > armBar:
            isL = st == 1
            touched = L[i] <= lim + 1e-3 * mt if isL else H[i] >= lim - 1e-3 * mt
            if touched and dayFills < p['maxFills']:
                st = 2 if isL else -2; fillBar = i; dayFills += 1
                cur = dict(dir=1 if isL else -1, arm=armBar, fill=i, entry=lim, stop=stp, exit=None, res=None, tight=tightArm, info=armInfo); trades.append(cur)
                if (L[i] <= stp if isL else H[i] >= stp):
                    dayR += -1.0; dayRiskR += -1.0 if p['sameBarDayStop'] else 0.0; lastExit = i; st = 0; cur.update(exit=i, res=-1.0); book(-1.0, cur['dir'], not p['sameBarDayStop'])
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
        bigCandle = rng > 0 and rng >= p['dispAtr'] * A and body / rng * 100 >= p['dispBodyPct'] - e
        # leg reset: shortly after a closed trade, a new signal in its direction must break the extreme since its fill bar
        brkH, brkL = priorHigh, priorLow
        if p['legReset'] and cur is not None and cur['exit'] is not None and 0 < i - cur['fill'] < p['structLen']:
            if cur['dir'] == 1: brkH = max(H[cur['fill']:i])
            else: brkL = min(L[cur['fill']:i])
        bullShape = C[i] > O[i] and C[i] > brkH and bigCandle and (H[i] - C[i]) / rng * 100 <= p['dispClosePct'] + e
        bearShape = C[i] < O[i] and C[i] < brkL and bigCandle and (C[i] - L[i]) / rng * 100 <= p['dispClosePct'] + e
        bullEvt = bullShape and slopeUp; bearEvt = bearShape and slopeDn
        bullImp = C[i] > O[i] and H[i] > priorHigh and bigCandle and (H[i] - C[i]) / rng * 100 <= p['dispClosePct'] + e and slopeUp
        bearImp = C[i] < O[i] and L[i] < priorLow and bigCandle and (C[i] - L[i]) / rng * 100 <= p['dispClosePct'] + e and slopeDn
        setupOk = vwBars >= (p['minOpenBars'] if not (p['minOpenBarsSyms'] and sym in p['minOpenBarsSyms']) else 0) and not (p['skipSunday'] and dow[i] == 6)
        bullDisp = setupOk and bullEvt and (not p['vwapFilter'] or C[i] > V[i]) and (p['momAtr'] <= 0 or momMove >= p['momAtr'] * A)
        bearDisp = setupOk and bearEvt and (not p['vwapFilter'] or C[i] < V[i]) and (p['momAtr'] <= 0 or -momMove >= p['momAtr'] * A)
        tightL = p['tightOn'] and bullN == 0 and prevNet is not None and prevNet <= -p['netMin']
        tightS = p['tightOn'] and bearN == 0 and prevNet is not None and prevNet >= p['netMin']
        if bullImp: bullN += 1
        if bearImp: bearN += 1
        # 3. arm
        cooled = lastExit is None or i - lastExit >= max(p['cooldownBars'], 1)
        if p['dsMode'] in ('R', 'netR'):
            dayOpen = p['dayStopR'] <= 0 or (dayRiskR >= -p['dayStopR'] if p['dsStrict'] else dayRiskR > -p['dayStopR'])
        elif p['dsMode'] == 'loss':
            dayOpen = dayLossAll < p['dsLoss']
        else: dayOpen = True
        canArm = abs(st) != 2 and cooled and dayFills < p['maxFills'] and dayOpen and A > 0
        keepArm = p['rearmKeep'] and ((st == 1 and bullDisp) or (st == -1 and bearDisp))
        if p['dsMode'] == 'lossDir':
            if bullDisp and dayLoss[1] >= p['dsLoss']: bullDisp = False
            if bearDisp and dayLoss[-1] >= p['dsLoss']: bearDisp = False
        if canArm and (bullDisp or bearDisp) and not keepArm:
            isL = bullDisp; d = 1 if isL else -1
            entry = max(bodyMid, entHigh) if isL else min(bodyMid, entLow)
            tight = tightL if isL else tightS
            stop = (min(entry - p['tightAtr'] * A, L[i]) if isL else max(entry + p['tightAtr'] * A, H[i])) if tight else entry - d * p['stopAtr'] * A
            risk = d * (entry - stop)
            if risk >= mt and rtick(stop, mt) != rtick(entry, mt):
                st = d; armBar = i; lim = entry; stp = stop; t4 = lim + d * p['tp4R'] * risk; tightArm = tight; armInfo = (prevNet, bullN, bearN, round((L[i] if isL else H[i]), 2))
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
        tr, win = gtscore.load_gt(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'gt', 'final'))
        return gtscore.score({}, tr, [dict(w) for w in win], detail=detail)
    finally:
        gtscore.run = orig
if __name__ == '__main__':
    import json
    inp = json.loads(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].startswith('{') else {}
    r, rows = score(inp, True); print({k: r[k] for k in ('exact', 'miss', 'extra')})
    if 'd' in sys.argv[1:]: [print('  ', *x) for x in rows if x[0] != 'ok']
