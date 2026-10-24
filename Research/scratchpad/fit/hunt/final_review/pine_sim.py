"""Independent port of final.pine bar-by-bar semantics (na = nan, no early-bar skip, impulse counters on every bar,
steps in the order of the Pine text). Uses the exported VWAP column (no volume in the CSVs). Compared against pine_final.run."""
import sys, os, math, datetime
FIT = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'
sys.path.insert(0, FIT)
from engine import prepare as eprep, rma, rtick
nan = float('nan')
def isn(x): return x != x
def sim(sym, newday0=True, **ov):
    inp = dict(structLen=10, entryLen=6, retestBars=5, dispAtr=0.8, dispBodyPct=55.0, dispClosePct=25.0, momLen=10, momAtr=0.85,
               keep=True, stopAtr=1.8, halfOn=True, halfAtr=0.9, biasNet=3, cooldown=2, maxFills=5, dayStopR=3.0, atrLen=14,
               vwapFilter=True, slopeBars=3, minOpenBars=1, skipSunday=True, tp4R=2.0)
    inp.update(ov); g = inp
    P = eprep(sym); R = P['rows']; n = len(R); mt = P['mt']
    O = [r['o'] for r in R]; H = [r['h'] for r in R]; L = [r['l'] for r in R]; C = [r['c'] for r in R]
    V = [nan if r['vwap'] is None else r['vwap'] for r in R]
    ATR = [nan if a is None else a for a in rma(P['tr'], g['atrLen'])]
    dow = [(datetime.datetime.strptime(r['t'], '%Y-%m-%d %H:%M') - datetime.timedelta(hours=5, minutes=30)).weekday() for r in R]
    ds = list(P['daystart']); ds[0] = newday0
    def hi(a, ln, b):   # ta.highest(x, ln)[1] at bar b
        return max(a[b - ln:b]) if b >= ln else nan
    def lo(a, ln, b):
        return min(a[b - ln:b]) if b >= ln else nan
    bullN = bearN = 0; prevNet = None
    st = 0; armBar = fillBar = lastExit = None; lim = stp = t4 = nan; trRisk = nan
    dayFills = 0; dayR = 0.0; vwBars = 0; trades = []; cur = None
    for b in range(n):
        newDay = ds[b]
        # vwap section
        if newDay: vwBars = 0
        else: vwBars += 1
        A = ATR[b]
        priorHigh = hi(H, g['structLen'], b); priorLow = lo(L, g['structLen'], b)
        el = min(g['entryLen'], g['structLen'])
        entHigh = hi(H, el, b); entLow = lo(L, el, b)
        rng = H[b] - L[b]; body = abs(C[b] - O[b]); bodyMid = (O[b] + C[b]) / 2.0
        momMove = C[b] - C[b - g['momLen']] if b >= g['momLen'] else nan
        sb = g['slopeBars']
        vwSlope = (V[b] - V[b - sb] if b >= sb else nan) if (sb > 0 and vwBars >= sb) else nan
        slopeUp = isn(vwSlope) or vwSlope > 0; slopeDn = isn(vwSlope) or vwSlope < 0
        bigCandle = rng > 0 and rng >= g['dispAtr'] * A and body / rng * 100.0 >= g['dispBodyPct'] - 1e-7
        bullShape = C[b] > O[b] and bigCandle and (H[b] - C[b]) / rng * 100.0 <= g['dispClosePct'] + 1e-7 and slopeUp
        bearShape = C[b] < O[b] and bigCandle and (C[b] - L[b]) / rng * 100.0 <= g['dispClosePct'] + 1e-7 and slopeDn
        setupOk = vwBars >= g['minOpenBars'] and not (g['skipSunday'] and dow[b] == 6)
        bullDisp = setupOk and bullShape and C[b] > priorHigh and (not g['vwapFilter'] or C[b] > V[b]) and (g['momAtr'] <= 0 or momMove >= g['momAtr'] * A)
        bearDisp = setupOk and bearShape and C[b] < priorLow and (not g['vwapFilter'] or C[b] < V[b]) and (g['momAtr'] <= 0 or -momMove >= g['momAtr'] * A)
        bullImp = bullShape and H[b] > priorHigh
        bearImp = bearShape and L[b] < priorLow
        if newDay:
            if b > 0: prevNet = bullN - bearN
            bullN = 0; bearN = 0
        halfL = g['halfOn'] and bullN == 0 and prevNet is not None and prevNet <= -g['biasNet']
        halfS = g['halfOn'] and bearN == 0 and prevNet is not None and prevNet >= g['biasNet']
        if bullImp: bullN += 1
        if bearImp: bearN += 1
        if newDay:
            dayFills = 0; dayR = 0.0
        # 1. live trade
        if abs(st) == 2 and b > fillBar:
            isL = st == 2
            stopHit = (L[b] <= stp) if isL else (H[b] >= stp)
            tp4Hit = (H[b] >= t4) if isL else (L[b] <= t4)
            if stopHit or tp4Hit:
                win = not stopHit; res = g['tp4R'] if win else -1.0
                dayR += res; lastExit = b; st = 0; cur.update(exit=b, res=res)
        # 2. armed limit
        if abs(st) == 1 and b > armBar:
            isL = st == 1
            touched = (L[b] <= lim + mt * 0.001) if isL else (H[b] >= lim - mt * 0.001)
            if touched and True and dayFills < g['maxFills']:
                st = 2 if isL else -2; fillBar = b; dayFills += 1
                cur = dict(dir=1 if isL else -1, arm=armBar, fill=b, entry=lim, stop=stp, exit=None, res=None); trades.append(cur)
                if (L[b] <= stp) if isL else (H[b] >= stp):
                    dayR += -1.0; lastExit = b; st = 0; cur.update(exit=b, res=-1.0)
            elif b - armBar >= g['retestBars'] and True:
                st = 0
        # 3. arm
        cooled = lastExit is None or b - lastExit >= max(g['cooldown'], 1)
        dayOpen = g['dayStopR'] <= 0 or dayR > -g['dayStopR']
        canArm = True and True and abs(st) != 2 and cooled and dayFills < g['maxFills'] and dayOpen and A > 0
        keepArm = g['keep'] and ((st == 1 and bullDisp) or (st == -1 and bearDisp))
        if canArm and (bullDisp or bearDisp) and not keepArm:
            isL = bullDisp; d = 1.0 if isL else -1.0
            entry = (max(bodyMid, entHigh) if isL else min(bodyMid, entLow))
            half = (halfL if isL else halfS)
            cStop = entry - d * g['stopAtr'] * A
            hStop = min(entry - g['halfAtr'] * A, L[b]) if isL else max(entry + g['halfAtr'] * A, H[b])
            stop = hStop if half else cStop
            risk = d * (entry - stop)
            if risk >= mt and rtick(stop, mt) != rtick(entry, mt):
                st = 1 if isL else -1; armBar = b; lim = entry; stp = stop; trRisk = risk
                t4 = lim + d * g['tp4R'] * risk
    return trades
if __name__ == '__main__':
    from pine_final import run as pf_run
    key = lambda t: (t['dir'], t['arm'], t['fill'], t['entry'], t['stop'], t['exit'], t['res'])
    for nd0 in (True, False):
        tot = bad = 0
        for s in ['GC', 'EURUSD', 'NASDAQ', 'US30', 'CRUDE', 'NIFTY', 'SENSEX', 'ETH']:
            a = [key(t) for t in sim(s, nd0)]; bb = [key(t) for t in pf_run(s)]
            tot += len(bb)
            diff = [x for x in a if x not in bb] + [x for x in bb if x not in a]
            bad += len(diff)
            print('newday0', nd0, s, 'sim', len(a), 'pyreplica', len(bb), 'diff', len(diff), diff[:3])
        print('TOTAL newday0', nd0, 'trades', tot, 'diffs', bad)
