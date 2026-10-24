import sys, pickle, collections
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold'); import geng
D = pickle.load(open(S + '/gold/grid1.pkl', 'rb')); C = D['configs']; R = D['res']
DAYS = 1490
def m(tr):
    n = len(tr)
    if not n: return None
    res = [x[1] for x in tr]; mw, ml, _ = geng.streaks(res)
    return dict(n=n, win=sum(1 for x in tr if x[1] > 0) / n, tp=[sum(x[3][k] for x in tr) / n for k in range(4)], E=sum(res) / n,
                Ec=sum(x[1] - x[4] / x[5] for x in tr) / n, ml=ml, mw=mw)
def row(tf, name):
    tr = R[(tf, name)]; A = [x for x in tr if x[0].year <= 2023]; B = [x for x in tr if x[0].year >= 2024]
    yrs = collections.defaultdict(list)
    for x in tr: yrs[x[0].year].append(x)
    ypos = sum(1 for y in yrs if sum(x[1] for x in yrs[y]) > 0); yposc = sum(1 for y in yrs if sum(x[1] - x[4] / x[5] for x in yrs[y]) > 0)
    ymax = max(geng.streaks([x[1] for x in yrs[y]])[1] for y in yrs)
    return m(tr), m(A), m(B), ypos, yposc, ymax
for tf in ('M5', 'M15', 'H1'):
    print('\n==== %s   (A = 2021-23 choose, B = 2024-26 check; E = R/trade; net = after spread; maxL = longest losing streak; yrMaxL = worst single year)' % tf)
    print('%-22s %6s %5s | %-30s | %-30s | %s' % ('config', 'trades', '/day', 'A: win  TP1  E     net', 'B: win  TP1  E     net', 'yrs+ gross/net  maxL all/yrMax'))
    for name, _ in C:
        a, A, B, yp, ypc, ym = row(tf, name)
        print('%-22s %6d %5.2f | %4.1f%% %3.0f%% %+.3f %+.3f | %4.1f%% %3.0f%% %+.3f %+.3f | %d/6 %d/6   %2d / %2d' % (
            name, a['n'], a['n'] / DAYS, 100 * A['win'], 100 * A['tp'][0], A['E'], A['Ec'], 100 * B['win'], 100 * B['tp'][0], B['E'], B['Ec'], yp, ypc, a['ml'], ym))
