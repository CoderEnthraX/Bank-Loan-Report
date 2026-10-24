"""Line-by-line replica of the FINAL Pine script (tight counter-bias stop, tie epsilons). Self-contained apart from engine.prepare/rma."""
import os, sys, datetime
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from engine import prepare as eprep, rma, rtick
IN = dict(structLen=10, entryLen=6, retestBars=5, dispAtr=0.8, dispBodyPct=55.0, dispClosePct=25.0, momLen=10, momAtr=0.85,
          rearmKeep=True, stopAtr=1.8, cooldownBars=2, maxFills=5, dayStopR=3.0, atrLen=14, vwapFilter=True, slopeBars=3,
          minOpenBars=1, skipSunday=True, tp4R=2.0, tightOn=True, tightAtr=0.9, netMin=3, eps=True, legReset=True, sameBarDayStop=False,
          slopeCross=False, tightOut=False, erMin=0.0, erLen=0, legFrom='fill', brkLen=0, impLen=0, typo37=False, cdLoss=-1, cdWin=-1, oppPolicy='replace', capMode='fills', sameDirAfterLoss=0, eodExit=False, eodCancel=False, legMax=False)
EPS = 1e-7
DBG = []
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
    sesH = sesL = sesO = pdH = pdL = None
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
        if newAnchor and i > 0:
            if p['eodExit'] and abs(st) == 2:
                isL = st == 2; mtm = (C[i-1] - cur['entry']) / (cur['entry'] - cur['stop']); lastExit = i - 1; st = 0; cur.update(exit=i - 1, res=mtm, eod=True)
            if p['eodCancel'] and abs(st) == 1: st = 0
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
                st = 2 if isL else -2; fillBar = i; dayFills += 0 if p['capMode'] == 'arms' else 1
                cur = dict(dir=1 if isL else -1, arm=armBar, fill=i, entry=lim, stop=stp, exit=None, res=None, tight=tightArm); trades.append(cur)
                if (L[i] <= stp if isL else H[i] >= stp):
                    dayR += -1.0; dayRiskR += -1.0 if p['sameBarDayStop'] else 0.0; lastExit = i; st = 0; cur.update(exit=i, res=-1.0)
                    if p['capMode'] == 'nosame': dayFills -= 1
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
            if cur['dir'] == 1: brkH = max(H[cur['fill']:i]) if not p['legMax'] else max(brkH, max(H[cur['fill']:i]))
            else: brkL = min(L[cur['fill']:i]) if not p['legMax'] else min(brkL, min(L[cur['fill']:i]))
        bullShape = C[i] > O[i] and C[i] > brkH and bigCandle and (H[i] - C[i]) / rng * 100 <= p['dispClosePct'] + e
        bearShape = C[i] < O[i] and C[i] < brkL and bigCandle and (C[i] - L[i]) / rng * 100 <= p['dispClosePct'] + e
        if p['slopeCross'] and vwSlope is None and i >= p['slopeBars']:
            xs = V[i] - V[i - p['slopeBars']]; sU = xs > 0; sD = xs < 0
        else: sU, sD = slopeUp, slopeDn
        bullEvt = bullShape and sU; bearEvt = bearShape and sD
        iH = max(H[i - p['impLen']:i]) if p['impLen'] else priorHigh; iL = min(L[i - p['impLen']:i]) if p['impLen'] else priorLow
        bullImp = C[i] > O[i] and H[i] > iH and bigCandle and (H[i] - C[i]) / rng * 100 <= p['dispClosePct'] + e and slopeUp
        bearImp = C[i] < O[i] and L[i] < iL and bigCandle and (C[i] - L[i]) / rng * 100 <= p['dispClosePct'] + e and slopeDn
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
        if DBG is not None and p.get('dbg'):
            DBG.append(dict(i=i,t=R[i]['t'],st=st,A=A,bullShape=bullShape,bearShape=bearShape,sU=sU,sD=sD,cvw=(C[i]-V[i])/A,mom=momMove/A,
              er=(erUp,erDn),bullDisp=bullDisp,bearDisp=bearDisp,brkH=(C[i]-brkH)/A,brkL=(brkL-C[i])/A,big=bigCandle,body=body/rng*100 if rng else 0,
              clsH=(H[i]-C[i])/rng*100 if rng else 0,clsL=(C[i]-L[i])/rng*100 if rng else 0,dayFills=dayFills,lastExit=lastExit,rng=rng/A,
              ent=(max(bodyMid,entHigh),min(bodyMid,entLow)),setupOk=setupOk,vwBars=vwBars,tight=(tightL,tightS)))
        # 3. arm
        cdN = p['cooldownBars']
        if cur is not None and cur['exit'] is not None:
            if cur['res'] < 0 and p['cdLoss'] >= 0: cdN = p['cdLoss']
            if cur['res'] > 0 and p['cdWin'] >= 0: cdN = p['cdWin']
        cooled = lastExit is None or i - lastExit >= max(cdN, 1)
        if p['sameDirAfterLoss'] and cur is not None and cur['exit'] is not None and cur['res'] < 0 and i - cur['exit'] < p['sameDirAfterLoss']:
            if cur['dir'] == 1: bullDisp = False
            else: bearDisp = False
        dayOpen = p['dayStopR'] <= 0 or dayRiskR > -p['dayStopR']
        canArm = abs(st) != 2 and cooled and dayFills < p['maxFills'] and dayOpen and A > 0
        keepArm = p['rearmKeep'] and ((st == 1 and bullDisp) or (st == -1 and bearDisp))
        if p['oppPolicy'] != 'replace' and abs(st) == 1 and ((st == 1 and bearDisp and not bullDisp) or (st == -1 and bullDisp and not bearDisp)):
            if p['oppPolicy'] == 'cancel': st = 0
            keepArm = True
        if canArm and (bullDisp or bearDisp) and not keepArm:
            isL = bullDisp; d = 1 if isL else -1
            entry = max(bodyMid, entHigh) if isL else min(bodyMid, entLow)
            tight = tightL if isL else tightS
            stop = (min(entry - p['tightAtr'] * A, L[i]) if isL else max(entry + p['tightAtr'] * A, H[i])) if tight else entry - d * p['stopAtr'] * A
            risk = d * (entry - stop)
            if risk >= mt and rtick(stop, mt) != rtick(entry, mt):
                st = d; armBar = i; lim = entry; dayFills += 1 if p['capMode'] == 'arms' else 0; stp = stop; t4 = lim + d * p['tp4R'] * risk; tightArm = tight
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
