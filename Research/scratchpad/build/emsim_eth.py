"""Model of TradingView's broker emulator + the strategy's EXECUTION layer (default settings, qty 1).
Emulator: orders placed at a bar's close act from the next bar; intrabar path O-H-L-C if the high is closer to the open than the low,
else O-L-H-C; limits fill on touch (gap -> at the open); stops trigger when crossed (gap -> at the open); exits attached to an entry become
active from the moment it fills, on the same bar. Compares executed trades with the engine's shown trades."""
import sys, math
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/build'); sys.path.insert(0, S + '/fit')
import ref_ev
from engine import prepare as eprep
def floorT(x, mt): return round(math.floor(x / mt + 1e-6) * mt, 10)
def ceilT(x, mt): return round(math.ceil(x / mt - 1e-6) * mt, 10)
def path(o, h, l, c): return [o, h, l, c] if abs(h - o) < abs(o - l) else [o, l, h, c]
def run(sym, opts=None):
    ev = []; eng = [x for x in ref_ev.run(sym, opts, ev) if not x['ghost']]
    P = eprep(sym); R = P['rows']; mt = 0.01 if sym == 'ETH' else P['mt']; market = (opts or {}).get('entryMode') == 'market'
    O = [r['o'] for r in R]; H = [r['h'] for r in R]; L = [r['l'] for r in R]; C = [r['c'] for r in R]
    # broker state
    entry = None   # (dir, limitPx or None for market)
    stopPx = tgtPx = None; posDir = 0; posFill = None; exe = []; cur = None
    exState = 0; missN = 0
    for i in range(len(R)):
        # ---- emulator processes bar i with the orders placed at the close of bar i-1 ----
        pts = path(O[i], H[i], L[i], C[i]); filledNow = closedNow = False
        k0 = 0; px = None
        if entry is not None and posDir == 0:
            d, lp = entry
            if lp is None: px = O[i]; k0 = 0
            else:
                if (d > 0 and O[i] <= lp) or (d < 0 and O[i] >= lp): px = O[i]; k0 = 0
                else:
                    for k in range(1, 4):
                        a, b = pts[k - 1], pts[k]
                        if (d > 0 and min(a, b) <= lp <= max(a, b) and b < a) or (d < 0 and min(a, b) <= lp <= max(a, b) and b > a):
                            px = lp; k0 = k - 1; break
                        if (d > 0 and b <= lp) or (d < 0 and b >= lp): px = lp; k0 = k - 1; break
            if px is not None:
                posDir = d; posFill = i; filledNow = True; entry = None
                cur = dict(dir=d, fill=i, entry=px, exit=None); exe.append(cur)
        if posDir != 0:
            d = posDir
            # walk the remaining path from the fill point (or from the open on later bars)
            seq = [px if filledNow else O[i]] + pts[k0 + 1:] if filledNow else pts
            hit = None
            if not filledNow:
                if stopPx is not None and ((d > 0 and O[i] <= stopPx) or (d < 0 and O[i] >= stopPx)): hit = ('stop', O[i])
                elif tgtPx is not None and ((d > 0 and O[i] >= tgtPx) or (d < 0 and O[i] <= tgtPx)): hit = ('tgt', O[i])
            if hit is None:
                for k in range(1, len(seq)):
                    a, b = seq[k - 1], seq[k]
                    lo, hi = min(a, b), max(a, b)
                    # in path order: whichever level is met first along a -> b
                    cands = []
                    if stopPx is not None and lo <= stopPx <= hi and ((d > 0 and b < a) or (d < 0 and b > a) or a == stopPx): cands.append((abs(stopPx - a), 'stop', stopPx))
                    if tgtPx is not None and lo <= tgtPx <= hi and ((d > 0 and b > a) or (d < 0 and b < a) or a == tgtPx): cands.append((abs(tgtPx - a), 'tgt', tgtPx))
                    if cands: cands.sort(); hit = (cands[0][1], cands[0][2]); break
            if hit is not None:
                cur.update(exit=i, how=hit[0]); posDir = 0; closedNow = True; stopPx = tgtPx = None
        # ---- the strategy script runs at the close of bar i (mirrors the Pine EXECUTION part, defaults) ----
        e = ev[i]
        if exState == 1 and posDir != 0: exState = 2
        exClosed = (exState == 1 and posDir == 0 and closedNow) or (exState == 2 and posDir == 0)
        if exClosed: exState = 0; entry = None; stopPx = tgtPx = None
        if exState == 1 and e['cancel']: entry = None; stopPx = None; exState = 0
        if e['fill'] and exState == 1 and posDir == 0 and not exClosed: entry = None; stopPx = None; exState = 0; missN += 1
        st, lim, stp, tF, gh = e.get('state', (0, None, None, None, False))
        if exState == 2 and (e['fill'] or e['move']):
            d = posDir; tl = mt * 0.001; stopPx = floorT(stp + tl, mt) if d > 0 else ceilT(stp - tl, mt); tgtPx = ceilT(tF - tl, mt) if d > 0 else floorT(tF + tl, mt)
        if e['exit'] and exState == 2 and posDir != 0:
            cur.update(exit=i + 1, how='sync'); posDir = 0; stopPx = tgtPx = None   # close_all fills at the next open
        if e['arm']:
            d, lim, stp, tF = e['arm']
            if exState == 0 and posDir == 0:
                entry = (d, None if market else (floorT(lim + mt * 0.001, mt) if d > 0 else ceilT(lim - mt * 0.001, mt)))
                stopPx = floorT(stp + mt * 0.001, mt) if d > 0 else ceilT(stp - mt * 0.001, mt); tgtPx = None; exState = 1
    A = [(x['dir'], x['fill'], x['exit']) for x in eng]; B = [(x['dir'], x['fill'], x['exit']) for x in exe]
    sa, sb = set(A), set(B)
    return eng, exe, len(sa & sb), sorted(sa - sb), sorted(sb - sa), missN
if __name__ == '__main__':
    import json
    opts = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    tot = same = 0
    for sym in ['GC', 'EURUSD', 'NASDAQ', 'US30', 'CRUDE', 'NIFTY', 'SENSEX', 'ETH', 'NSE_NIFTY1', 'MCX_NATURALGAS']:
        eng, exe, ok, onlyE, onlyX, miss = run(sym, opts)
        tot += len(eng); same += ok
        hows = {}
        for x in exe: hows[x.get('how')] = hows.get(x.get('how'), 0) + 1
        print(f'{sym:15s} engine {len(eng):4d}  executed {len(exe):4d}  same (dir, fill bar, exit bar) {ok:4d}  engine-only {len(onlyE)}  exec-only {len(onlyX)}  missed fills {miss}  exits {hows}')
        if onlyE: print('      engine-only', onlyE[:4], ' exec-only', onlyX[:4])
    print(f'TOTAL engine trades {tot}, executed identically {same} ({100 * same / tot:.2f}%)')
