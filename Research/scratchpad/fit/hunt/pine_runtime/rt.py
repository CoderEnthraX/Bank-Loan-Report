"""Extended replica of the Pine (pine_v2 logic) tracking bestPx, R-level stats (rounded vs unrounded),
expiries/replacements, object counts and display rounding of unrounded levels."""
import os, sys, math, datetime
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from engine import prepare as eprep, rma, rtick
import pine_v2
IN = dict(pine_v2.IN); IN.update(tp1R=0.6, tp2R=1.0, tp3R=1.5, rr=(1.0, 1.5, 2.0))
def dec_of(mt):
    s = ('%.10f' % mt).rstrip('0'); return len(s.split('.')[1]) if '.' in s else 0
def fmt(p, mt): return round(p, dec_of(mt))
def run(sym, inp=None):
    p = dict(IN); p.update(inp or {})
    P = eprep(sym); R = P['rows']; n = len(R); mt = P['mt']
    atr = rma(P['tr'], p['atrLen'])
    O = [r['o'] for r in R]; H = [r['h'] for r in R]; L = [r['l'] for r in R]; C = [r['c'] for r in R]; V = [r['vwap'] for r in R]
    dow = [(datetime.datetime.strptime(r['t'], '%Y-%m-%d %H:%M') - datetime.timedelta(hours=5, minutes=30)).weekday() for r in R]
    st = 0; armBar = fillBar = lastExit = None; lim = stp = t4 = None; risk = None; best = None
    dayFills = 0; dayR = 0.0; vwBars = 0; trades = []; cur = None
    ev = dict(arms=0, expiries=0, replaced_opp=0, replaced_same=0, rr_round=[0,0,0], rr_unr=[0,0,0], closed=0, wins=0, offgrid=0)
    for i in range(n):
        newAnchor = P['daystart'][i]; newDay = newAnchor
        vwBars = 0 if newAnchor else vwBars + 1
        if newDay: dayFills = 0; dayR = 0.0
        def record(isL, win):
            d = 1 if isL else -1
            for k, lvR in enumerate(p['rr']):
                lvlr = rtick(lim + d * lvR * risk, mt); lvlu = lim + d * lvR * risk
                if (lvR <= p['tp4R']) if win else (d * (lvlr - lim) > 0 and d * (best - lvlr) >= 0): ev['rr_round'][k] += 1
                if (lvR <= p['tp4R']) if win else (d * (best - lvlu) >= 0): ev['rr_unr'][k] += 1
            ev['closed'] += 1; ev['wins'] += win
        if abs(st) == 2 and i > fillBar:
            isL = st == 2
            stopHit = L[i] <= stp if isL else H[i] >= stp
            tp4Hit = H[i] >= t4 if isL else L[i] <= t4
            if not stopHit: best = max(best, H[i]) if isL else min(best, L[i])
            if stopHit or tp4Hit:
                win = not stopHit; res = p['tp4R'] if win else -1.0
                record(isL, win)
                dayR += res; lastExit = i; st = 0; cur.update(exit=i, res=res, best=best)
        if abs(st) == 1 and i > armBar:
            isL = st == 1
            touched = L[i] <= lim if isL else H[i] >= lim
            if touched and dayFills < p['maxFills']:
                st = 2 if isL else -2; fillBar = i; dayFills += 1; best = lim
                cur = dict(dir=1 if isL else -1, arm=armBar, fill=i, entry=lim, stop=stp, t4=t4, exit=None, res=None, risk=risk, t=R[i]['t'])
                trades.append(cur)
                if (L[i] <= stp if isL else H[i] >= stp):
                    record(isL, False); dayR += -1.0; lastExit = i; st = 0; cur.update(exit=i, res=-1.0)
            elif i - armBar >= p['retestBars']:
                st = 0; ev['expiries'] += 1
        if i < max(p['structLen'], p['entryLen'], p['momLen'], p['slopeBars']) + 1 or atr[i] is None: continue
        priorHigh = max(H[i - p['structLen']:i]); priorLow = min(L[i - p['structLen']:i])
        entHigh = max(H[i - p['entryLen']:i]); entLow = min(L[i - p['entryLen']:i])
        rng = H[i] - L[i]; body = abs(C[i] - O[i]); bodyMid = (O[i] + C[i]) / 2
        momMove = C[i] - C[i - p['momLen']]
        vwSlope = V[i] - V[i - p['slopeBars']] if p['slopeBars'] > 0 and vwBars >= p['slopeBars'] else None
        slopeUp = vwSlope is None or vwSlope > 0; slopeDn = vwSlope is None or vwSlope < 0
        A = atr[i]
        bigCandle = rng > 0 and rng >= p['dispAtr'] * A and body / rng * 100 >= p['dispBodyPct']
        setupOk = vwBars >= p['minOpenBars'] and not (p['skipSunday'] and dow[i] == 6)
        bullDisp = setupOk and C[i] > O[i] and C[i] > priorHigh and bigCandle and (H[i] - C[i]) / rng * 100 <= p['dispClosePct'] and (not p['vwapFilter'] or C[i] > V[i]) and slopeUp and (p['momAtr'] <= 0 or momMove >= p['momAtr'] * A)
        bearDisp = setupOk and C[i] < O[i] and C[i] < priorLow and bigCandle and (C[i] - L[i]) / rng * 100 <= p['dispClosePct'] and (not p['vwapFilter'] or C[i] < V[i]) and slopeDn and (p['momAtr'] <= 0 or -momMove >= p['momAtr'] * A)
        cooled = lastExit is None or i - lastExit >= max(p['cooldownBars'], 1)
        dayOpen = p['dayStopR'] <= 0 or dayR > -p['dayStopR']
        canArm = abs(st) != 2 and cooled and dayFills < p['maxFills'] and dayOpen and A > 0
        keepArm = p['rearmKeep'] and ((st == 1 and bullDisp) or (st == -1 and bearDisp))
        if canArm and (bullDisp or bearDisp) and not keepArm:
            isL = bullDisp; d = 1 if isL else -1
            entry = max(bodyMid, entHigh) if isL else min(bodyMid, entLow)
            stop = entry - d * p['stopAtr'] * A; rk = d * (entry - stop)
            if rk >= mt and rtick(stop, mt) != rtick(entry, mt):
                if abs(st) == 1: ev['replaced_opp' if st != d else 'replaced_same'] += 1
                st = d; armBar = i; lim = entry; stp = stop; risk = rk; t4 = lim + d * p['tp4R'] * risk; ev['arms'] += 1
    return trades, ev, P
if __name__ == '__main__':
    tot = dict(tr=0, mis_lim=0, mis_stop=0, mis_t4=0)
    for sym in ['GC','EURUSD','NASDAQ','US30','CRUDE','NIFTY','SENSEX','ETH']:
        tr, ev, P = run(sym); mt = P['mt']
        # display check: format.mintick shows round(x, decimals). Does that printed price trigger the level?
        ml = ms = mtp = 0
        for t in tr:
            d = t['dir']
            # long limit fills if low <= lim ; shown price s: a print at s fills iff s <= lim
            s = fmt(t['entry'], mt); ml += (d * (s - t['entry']) > 1e-12)  # long: shown above lim -> print at shown price does not fill
            s = fmt(t['stop'], mt); ms += (d * (s - t['stop']) > 1e-12)
            s = fmt(t['t4'], mt); mtp += (d * (t['t4'] - s) > 1e-12)
        tot['tr'] += len(tr); tot['mis_lim'] += ml; tot['mis_stop'] += ms; tot['mis_t4'] += mtp
        print(f"{sym:7s} bars={len(P['rows'])} mt={mt} trades={len(tr)} arms={ev['arms']} exp={ev['expiries']} repl_opp={ev['replaced_opp']} "
              f"closed={ev['closed']} wins={ev['wins']} rrRound={ev['rr_round']} rrUnr={ev['rr_unr']} shownNotTrig lim/stop/tp4={ml}/{ms}/{mtp}")
    print(tot)
