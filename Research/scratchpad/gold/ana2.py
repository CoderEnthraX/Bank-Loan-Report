"""Stage-2 walk-forward: rank by 2021-23 (A) after spread, check 2024-26 (B)."""
import sys, pickle, collections
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold'); import geng
D = pickle.load(open(S + '/gold/grid2.pkl', 'rb')); C = D['configs']; R = D['res']
MIN_A = {'H1': 100, 'M15': 250, 'M5': 400}
def stats(tr):
    n = len(tr)
    if not n: return None
    res = [x[1] for x in tr]
    return dict(n=n, win=sum(1 for x in tr if x[1] > 0) / n, tp1=sum(x[3][0] for x in tr) / n, E=sum(res) / n, Ec=sum(x[1] - x[4] / x[5] for x in tr) / n, ml=geng.streaks(res)[1])
def rank(xs):
    o = sorted(range(len(xs)), key=lambda i: xs[i]); r = [0] * len(xs)
    for k, i in enumerate(o): r[i] = k
    return r
summary = {}
for tf in ('M5', 'M15', 'H1'):
    rows = []
    for name, _ in C:
        tr = R[(tf, name)]; A = stats([x for x in tr if x[0].year <= 2023]); B = stats([x for x in tr if x[0].year >= 2024]); al = stats(tr)
        yrs = collections.defaultdict(list)
        for x in tr: yrs[x[0].year].append(x[1] - x[4] / x[5])
        ypos = sum(1 for y in yrs if sum(yrs[y]) > 0)
        if A and B: rows.append((name, A, B, al, ypos))
    ok = [r for r in rows if r[1]['n'] >= MIN_A[tf]]
    ra, rb = rank([r[1]['Ec'] for r in ok]), rank([r[2]['Ec'] for r in ok]); n = len(ok)
    rho = 1 - 6 * sum((a - b) ** 2 for a, b in zip(ra, rb)) / (n * (n * n - 1))
    ok.sort(key=lambda r: -r[1]['Ec'])
    posA = sum(1 for r in ok if r[1]['Ec'] > 0); top = ok[:20]; posBtop = sum(1 for r in top if r[2]['Ec'] > 0)
    print('\n==== %s: %d combinations with >= %d trades in 2021-23 | positive after spread in 2021-23: %d | of the 20 best in 2021-23, positive in 2024-26: %d | rank correlation A vs B: %+.2f' % (tf, n, MIN_A[tf], posA, posBtop, rho))
    print('%-46s | %-34s | %-34s | %s' % ('combination (ranked by 2021-23 after spread)', '2021-23: trades win  TP1  E  net', '2024-26: trades win  TP1  E  net', 'yrs+ net, longest losing streak'))
    for name, A, B, al, ypos in top[:15]:
        print('%-46s | %5d %4.1f%% %3.0f%% %+.3f %+.3f | %5d %4.1f%% %3.0f%% %+.3f %+.3f | %d/6  %2d' % (name, A['n'], 100 * A['win'], 100 * A['tp1'], A['E'], A['Ec'], B['n'], 100 * B['win'], 100 * B['tp1'], B['E'], B['Ec'], ypos, al['ml']))
    both = [r for r in ok if r[1]['Ec'] > 0 and r[2]['Ec'] > 0]
    print('  positive after spread in BOTH periods: %d combinations' % len(both))
    for name, A, B, al, ypos in sorted(both, key=lambda r: -min(r[1]['Ec'], r[2]['Ec']))[:10]:
        print('    %-46s A %+.3f (%d) B %+.3f (%d) yrs+ %d/6 streak %d' % (name, A['Ec'], A['n'], B['Ec'], B['n'], ypos, al['ml']))
    summary[tf] = dict(rows=rows, rho=rho)
pickle.dump(summary, open(S + '/gold/ana2.pkl', 'wb'))
