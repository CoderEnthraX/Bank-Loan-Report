"""Line-by-line replica of the FINAL Pine script (tight counter-bias stop, tie epsilons). Self-contained apart from engine.prepare/rma."""
import os, sys, datetime
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from engine import prepare as eprep, rma, rtick
IN = dict(structLen=10, entryLen=6, retestBars=5, dispAtr=0.8, dispBodyPct=55.0, dispClosePct=25.0, momLen=10, momAtr=0.85,
          rearmKeep=True, stopAtr=1.8, cooldownBars=2, maxFills=5, dayStopR=3.0, atrLen=14, vwapFilter=True, slopeBars=3,
          minOpenBars=1, skipSunday=True, tp4R=2.0, tightOn=True, tightAtr=0.9, netMin=3, eps=True, legReset=True, sameBarDayStop=False,
          slopeCross=False, tightOut=False, erMin=0.0, erLen=0, legFrom='fill',
          of_gate=None, of_confirm=False, of_confirmWait=False, of_confirmVol=0.0, of_phantom=False, of_bandK=0.0, of_bandStop='shift')
EPS = 1e-7
def run(sym, inp=None):
    p = dict(IN); p.update(inp or {}); e = EPS if p['eps'] else 0.0
    P = eprep(sym); R = P['rows']; n = len(R); mt = P['mt']
    OF = None
    if p['of_gate'] or p['of_confirm'] or p.get('of_veto') or p['of_bandK']:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import of as _of; OF = _of.features(sym)
    touchedOnce = False; phArm = False
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
        # 1. live trade
        if abs(st) == 2 and i > fillBar:
            isL = st == 2
            stopHit = L[i] <= stp if isL else H[i] >= stp
            tp4Hit = H[i] >= t4 if isL else L[i] <= t4
            if stopHit or tp4Hit:
                win = not stopHit; res = p['tp4R'] if win else -1.0
                dayR += res; dayRiskR += res; lastExit = i; st = 0; cur.update(exit=i, res=res)
        # 2. armed limit
        if abs(st) == 1 and i > armBar and p['of_confirm']:
            # ENTRY CONFIRMATION (decided at the close of bar i, entry at C[i]): the pullback bar touched the limit (or did so earlier
            # in this window when of_confirmWait), closed back beyond the limit, did not reach the stop, and (optional) its volume
            # is below of_confirmVol x the signal bar's volume.
            isL = st == 1; d = 1 if isL else -1
            touched = L[i] <= lim + 1e-3 * mt if isL else H[i] >= lim - 1e-3 * mt
            stopped = L[i] <= stp if isL else H[i] >= stp
            held = d * (C[i] - lim) >= 0
            volok = p['of_confirmVol'] <= 0 or OF['w'][armBar] <= 0 or OF['w'][i] <= p['of_confirmVol'] * OF['w'][armBar]
            cand = touched or (p['of_confirmWait'] and touchedOnce)
            if touched: touchedOnce = True
            if stopped: st = 0
            elif cand and held and volok and dayFills < p['maxFills']:
                st = 2 if isL else -2; fillBar = i; dayFills += 1; ent = C[i]; t4 = ent + d * p['tp4R'] * d * (ent - stp)
                cur = dict(dir=d, arm=armBar, fill=i, entry=ent, stop=stp, exit=None, res=None, tight=tightArm); trades.append(cur)
            elif touched and not p['of_confirmWait']: st = 0
            elif i - armBar >= p['retestBars']: st = 0
        elif abs(st) == 1 and i > armBar:
            isL = st == 1
            touched = L[i] <= lim + 1e-3 * mt if isL else H[i] >= lim - 1e-3 * mt
            if touched and dayFills < p['maxFills']:
                st = 2 if isL else -2; fillBar = i; dayFills += 1
                cur = dict(dir=1 if isL else -1, arm=armBar, fill=i, entry=lim, stop=stp, exit=None, res=None, tight=tightArm, phantom=phArm); trades.append(cur)
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
        keepArm = p['rearmKeep'] and ((st == 1 and bullDisp) or (st == -1 and bearDisp))
        if canArm and (bullDisp or bearDisp) and not keepArm:
            isL = bullDisp; d = 1 if isL else -1
            entry = max(bodyMid, entHigh) if isL else min(bodyMid, entLow)
            tight = tightL if isL else tightS
            stop = (min(entry - p['tightAtr'] * A, L[i]) if isL else max(entry + p['tightAtr'] * A, H[i])) if tight else entry - d * p['stopAtr'] * A
            if p['of_bandK'] > 0 and OF['valid'][i] and OF['sd'][i]:
                # BETTER ENTRY: never place the limit beyond VWAP +/- k sigma (volume-weighted session bands, known at the signal bar)
                band = V[i] + d * p['of_bandK'] * OF['sd'][i]
                if d * (entry - band) > 0:
                    if p['of_bandStop'] == 'shift': stop = stop - (entry - band)
                    entry = band
            risk = d * (entry - stop)
            gok = True
            if (p['of_gate'] or p.get('of_veto')) and risk >= mt:
                fx = _of.sig_features(OF, i, d, entry, p['structLen'])
                if fx is not None:
                    for (fk, side, thr) in (p['of_gate'] or []):
                        v = fx.get(fk)
                        if v is not None and ((side == 'le' and v > thr) or (side == 'ge' and v < thr)): gok = False
                    if p.get('of_veto'):   # reject when ALL listed conditions hold (e.g. climax: volume spike AND stretched)
                        if all(fx.get(fk) is not None and ((side == 'ge' and fx[fk] >= thr) or (side == 'le' and fx[fk] <= thr)) for (fk, side, thr) in p['of_veto']): gok = False
            phantom = (not gok) and p['of_phantom']   # vetoed setup still runs as a virtual (untaken) order/trade that blocks new ones
            if (gok or phantom) and risk >= mt and rtick(stop, mt) != rtick(entry, mt):
                st = d; armBar = i; lim = entry; stp = stop; t4 = lim + d * p['tp4R'] * risk; tightArm = tight; touchedOnce = False; phArm = phantom
    return [t for t in trades if not t.get('phantom')]
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
