"""Group trades by how flat the VWAP was at the signal candle; failed = stopped before TP1."""
import sys, pickle, statistics
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
D = pickle.load(open(S + '/gold/flat_vwap.pkl', 'rb'))
def summ(q):
    n = len(q)
    if not n: return None
    return dict(n=n, fail=sum(1 for x in q if not x['tp1']) / n, win=sum(1 for x in q if x['win']) / n, E=sum(x['res'] - x['c'] for x in q) / n)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 10
for key, tr in D.items():
    tf, nm = key
    ok = [x for x in tr if x['slope'][N] is not None]; early = [x for x in tr if x['slope'][N] is None]
    v = sorted(x['slope'][N] for x in ok); qs = [v[int(len(v) * k / 5)] for k in range(1, 5)]
    edges = [-9e9] + qs + [9e9]
    print('\n%s %s | %d trades | VWAP slope over %d bars, in ATR (+ = VWAP moving the trade\'s way) | ATR = %.3f%% of price (median)' % (
        tf, nm, len(tr), N, statistics.median(x['atrpct'] for x in tr)))
    a = summ(tr); print('   all trades                        %5d  failed %4.1f%%  win %4.1f%%  R/trade %+.3f' % (a['n'], 100 * a['fail'], 100 * a['win'], a['E']))
    e = summ(early)
    if e: print('   first %2d bars after VWAP reset    %5d  failed %4.1f%%  win %4.1f%%  R/trade %+.3f' % (N, e['n'], 100 * e['fail'], 100 * e['win'], e['E']))
    for lo, hi in zip(edges[:-1], edges[1:]):
        q = [x for x in ok if lo <= x['slope'][N] < hi]; s = summ(q)
        pc = [x['pct10'] for x in q if x['pct10'] is not None]
        lab = 'slope %s to %s ATR' % ('-inf' if lo < -1e9 else '%+.2f' % lo, '+inf' if hi > 1e9 else '%+.2f' % hi)
        print('   %-34s %5d  failed %4.1f%%  win %4.1f%%  R/trade %+.3f   (VWAP 10-bar move %s%% of price)' % (lab, s['n'], 100 * s['fail'], 100 * s['win'], s['E'],
              ('%.3f' % statistics.median(pc)) if pc and N == 10 else '-'))
