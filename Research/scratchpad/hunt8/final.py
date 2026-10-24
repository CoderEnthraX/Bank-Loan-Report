"""Line-by-line replica of the FINAL Pine script (tight counter-bias stop, tie epsilons). Self-contained apart from engine.prepare/rma."""
import os, sys, datetime
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from engine import prepare as eprep, rma, rtick
IN = dict(structLen=10, entryLen=6, retestBars=5, dispAtr=0.8, dispBodyPct=55.0, dispClosePct=25.0, momLen=10, momAtr=0.85,
          rearmKeep=True, stopAtr=1.8, cooldownBars=2, maxFills=5, dayStopR=3.0, atrLen=14, vwapFilter=True, slopeBars=3,
          minOpenBars=1, skipSunday=True, tp4R=2.0, tightOn=True, tightAtr=0.9, netMin=3, eps=True, legReset=True, sameBarDayStop=False,
          slopeCross=False, tightOut=False, erMin=0.0, erLen=0, legFrom='fill',
          impBody=None, impClose=None, impAtr=None, impSlopeX=False, impNoSlope=False, impClosBrk=False, impNeedSlope=False, impMinK=0, tightFirst='imp', biasWin=0, netCur=False, cntReset=None, cntBoth=False, netCurMin=0, netHi=99, curOppMin=0, mcxSplit=None, earlyK=0, sinceSes=True, brkLen=0, s2Len=0, s2Far=0.0)
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
    impH = [0] * n
    sinceL = sinceS = 0
    if p['cntReset']:
        hh, mm = map(int, p['cntReset'].split(':')); off = datetime.timedelta(hours=hh, minutes=mm)
        ck = [(datetime.datetime.strptime(r['t'], '%Y-%m-%d %H:%M') - off).date() for r in R]
        cntNewA = [i == 0 or ck[i] != ck[i - 1] or (p['cntBoth'] and P['daystart'][i]) for i in range(n)]
    else: cntNewA = P['daystart']
    if p['mcxSplit'] and sym in ('CRUDE', 'MCX_NATURALGAS'):
        cntNewA = [P['daystart'][i] or (R[i]['t'][11:] >= p['mcxSplit'] and R[i - 1]['t'][11:] < p['mcxSplit']) for i in range(n)]
    sArm = [0, 0]; sFill = [0, 0]; sDisp = [0, 0]
    sesH = sesL = sesO = pdH = pdL = None
    for i in range(n):
        newAnchor = P['daystart'][i]; newDay = newAnchor
        vwBars = 0 if newAnchor else vwBars + 1
        if newDay:
            sArm = [0, 0]; sFill = [0, 0]; sDisp = [0, 0]
            dayFills = 0; dayR = 0.0; dayRiskR = 0.0
            pdH, pdL = sesH, sesL; sesH, sesL, sesO = H[i], L[i], O[i]
        else:
            sesH = H[i] if sesH is None else max(sesH, H[i]); sesL = L[i] if sesL is None else min(sesL, L[i])
        if cntNewA[i] and p['sinceSes']: sinceL = sinceS = 0
        if cntNewA[i]:
            if i > 0: prevNet = bullN - bearN
            bullN = bearN = 0
        # 1. live trade
        if abs(st) == 2 and i > fillBar:
            isL = st == 2
            stopHit = L[i] <= stp if isL else H[i] >= stp
            tp4Hit = H[i] >= t4 if isL else L[i] <= t4
            if stopHit or tp4Hit:
                win = not stopHit; res = p['tp4R'] if win else -1.0
                dayR += res; dayRiskR += res; lastExit = i; st = 0; cur.update(exit=i, res=res)
        # 2. armed limit
        if abs(st) == 1 and i > armBar:
            isL = st == 1
            touched = L[i] <= lim + 1e-3 * mt if isL else H[i] >= lim - 1e-3 * mt
            if touched and dayFills < p['maxFills']:
                st = 2 if isL else -2; fillBar = i; dayFills += 1; sFill[0 if isL else 1] += 1
                if isL: sinceS = 0
                else: sinceL = 0
                cur = dict(dir=1 if isL else -1, arm=armBar, fill=i, entry=lim, stop=stp, exit=None, res=None, tight=tightArm); trades.append(cur)
                if (L[i] <= stp if isL else H[i] >= stp):
                    dayR += -1.0; dayRiskR += -1.0 if p['sameBarDayStop'] else 0.0; lastExit = i; st = 0; cur.update(exit=i, res=-1.0)
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
        if p['brkLen']: brkH = max(H[i - p['brkLen']:i]); brkL = min(L[i - p['brkLen']:i])
        if p['legReset'] and cur is not None and cur['exit'] is not None and 0 < i - cur[p['legFrom']] < p['structLen']:
            if cur['dir'] == 1: brkH = max(H[cur['fill']:i])
            else: brkL = min(L[cur['fill']:i])
        bullShape = C[i] > O[i] and C[i] > brkH and bigCandle and (H[i] - C[i]) / rng * 100 <= p['dispClosePct'] + e
        bearShape = C[i] < O[i] and C[i] < brkL and bigCandle and (C[i] - L[i]) / rng * 100 <= p['dispClosePct'] + e
        if p['slopeCross'] and vwSlope is None and i >= p['slopeBars']:
            xs = V[i] - V[i - p['slopeBars']]; sU = xs > 0; sD = xs < 0
        else: sU, sD = slopeUp, slopeDn
        bullEvt = bullShape and sU; bearEvt = bearShape and sD
        ib = p['impBody'] if p['impBody'] is not None else p['dispBodyPct']; ic = p['impClose'] if p['impClose'] is not None else p['dispClosePct']; ia = p['impAtr'] if p['impAtr'] is not None else p['dispAtr']
        bigI = rng > 0 and rng >= ia * A and body / rng * 100 >= ib - e
        iU = sU if p['impSlopeX'] else slopeUp; iD = sD if p['impSlopeX'] else slopeDn
        if p['impNoSlope']: iU = iD = True
        if p['impNeedSlope'] and vwSlope is None: iU = iD = False
        if vwBars < p['impMinK']: iU = iD = False
        bullImp = C[i] > O[i] and (C[i] if p['impClosBrk'] else H[i]) > priorHigh and bigI and (H[i] - C[i]) / rng * 100 <= ic + e and iU
        bearImp = C[i] < O[i] and (C[i] if p['impClosBrk'] else L[i]) < priorLow and bigI and (C[i] - L[i]) / rng * 100 <= ic + e and iD
        setupOk = vwBars >= p['minOpenBars'] and not (p['skipSunday'] and dow[i] == 6)
        if p['erMin'] > 0:
            nE = p['erLen'] or p['momLen']; pathE = sum(abs(C[j] - C[j - 1]) for j in range(i - nE + 1, i + 1)); netE = C[i] - C[i - nE]
            erUp = pathE > 0 and netE / pathE >= p['erMin']; erDn = pathE > 0 and -netE / pathE >= p['erMin']
        else: erUp = erDn = True
        bullDisp = setupOk and bullEvt and (not p['vwapFilter'] or C[i] > V[i]) and (p['momAtr'] <= 0 or momMove >= p['momAtr'] * A) and erUp
        bearDisp = setupOk and bearEvt and (not p['vwapFilter'] or C[i] < V[i]) and (p['momAtr'] <= 0 or -momMove >= p['momAtr'] * A) and erDn
        if p['s2Len']:   # second signal type: deep pullback inside the 10-bar structure that breaks the 6-bar level (CRUDE #63)
            k = p['s2Len']; hk = max(H[i-k:i]); lk = min(L[i-k:i]); mk = C[i] - C[i-k]
            pk = sum(abs(C[j] - C[j-1]) for j in range(i-k+1, i+1))
            clsU = (H[i] - C[i]) / rng * 100 <= p['dispClosePct'] + e if rng > 0 else False
            clsD = (C[i] - L[i]) / rng * 100 <= p['dispClosePct'] + e if rng > 0 else False
            b2 = setupOk and C[i] > O[i] and C[i] > hk and bigCandle and clsU and sU and C[i] > V[i] and mk >= p['momAtr'] * A and pk > 0 and mk / pk >= p['erMin']
            s2_ = setupOk and C[i] < O[i] and C[i] < lk and bigCandle and clsD and sD and C[i] < V[i] and -mk >= p['momAtr'] * A and pk > 0 and -mk / pk >= p['erMin']
            b2 = b2 and priorHigh - C[i] >= p['s2Far'] * A; s2_ = s2_ and C[i] - priorLow >= p['s2Far'] * A
            bullDisp = bullDisp or b2; bearDisp = bearDisp or s2_
        tf = p['tightFirst']
        if p['biasWin'] > 0:
            prevNet = sum(impH[max(0, i - p['biasWin']):i])
        fstL = {'opp': sinceL == 0, 'imp': bullN == 0, 'arm': sArm[0] == 0, 'fill': sFill[0] == 0, 'disp': sDisp[0] == 0, 'imp&arm': bullN == 0 and sArm[0] == 0, 'imp|arm': bullN == 0 or sArm[0] == 0, 'any': True}[tf]
        fstS = {'opp': sinceS == 0, 'imp': bearN == 0, 'arm': sArm[1] == 0, 'fill': sFill[1] == 0, 'disp': sDisp[1] == 0, 'imp&arm': bearN == 0 and sArm[1] == 0, 'imp|arm': bearN == 0 or sArm[1] == 0, 'any': True}[tf]
        pnU = prevNet if prevNet is None or not p['netCur'] else prevNet + (bullN - bearN)
        tightL = p['tightOn'] and fstL and pnU is not None and pnU <= -p['netMin']
        tightS = p['tightOn'] and fstS and pnU is not None and pnU >= p['netMin']
        if p['earlyK'] and prevNet is not None and vwBars < p['earlyK']:
            tightL = tightL and prevNet <= -p['netHi']; tightS = tightS and prevNet >= p['netHi']
        if p['netCurMin'] and prevNet is not None:
            tot = prevNet + (bullN - bearN)
            tightL = tightL and (prevNet <= -p['netHi'] or (tot <= -p['netCurMin'] and bearN >= p['curOppMin']))
            tightS = tightS and (prevNet >= p['netHi'] or (tot >= p['netCurMin'] and bullN >= p['curOppMin']))
        if p['tightOut'] and pdH is not None:
            tightL = tightL or (p['tightOn'] and fstL and sesO < pdL)
            tightS = tightS or (p['tightOn'] and fstS and sesO > pdH)
        impH[i] = int(bullImp) - int(bearImp)
        if bullImp: sinceL += 1
        if bearImp: sinceS += 1
        if bullImp: bullN += 1
        if bearImp: bearN += 1
        # 3. arm
        if bullDisp: sDisp[0] += 1
        if bearDisp: sDisp[1] += 1
        cooled = lastExit is None or i - lastExit >= max(p['cooldownBars'], 1)
        dayOpen = p['dayStopR'] <= 0 or dayRiskR > -p['dayStopR']
        canArm = abs(st) != 2 and cooled and dayFills < p['maxFills'] and dayOpen and A > 0
        keepArm = p['rearmKeep'] and ((st == 1 and bullDisp) or (st == -1 and bearDisp))
        if canArm and (bullDisp or bearDisp) and not keepArm:
            isL = bullDisp; d = 1 if isL else -1
            entry = max(bodyMid, entHigh) if isL else min(bodyMid, entLow)
            tight = tightL if isL else tightS
            stop = (min(entry - p['tightAtr'] * A, L[i]) if isL else max(entry + p['tightAtr'] * A, H[i])) if tight else entry - d * p['stopAtr'] * A
            risk = d * (entry - stop)
            if risk >= mt and rtick(stop, mt) != rtick(entry, mt):
                sArm[0 if isL else 1] += 1
                st = d; armBar = i; lim = entry; stp = stop; t4 = lim + d * p['tp4R'] * risk; tightArm = tight
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
        tr, win = gtscore.load_gt(os.path.join('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit', '..', 'gt', 'final'))
        return gtscore.score({}, tr, [dict(w) for w in win], detail=detail)
    finally:
        gtscore.run = orig
if __name__ == '__main__':
    import json
    inp = json.loads(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].startswith('{') else {}
    r, rows = score(inp, True); print({k: r[k] for k in ('exact', 'miss', 'extra')})
    if 'd' in sys.argv[1:]: [print('  ', *x) for x in rows if x[0] != 'ok']
