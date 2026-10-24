import sys, pickle, collections
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold'); import geng
EX = ['Exit at TP1 (0.6R)', 'Exit at TP2 (1R)', 'Exit at TP3 (1.5R)', 'Exit at TP4 (2R)', 'TP4 + breakeven at TP1', 'TP2 + breakeven at TP1', 'TP4 + breakeven at TP2', '50% at TP1 + breakeven, rest TP4']
def m(tr):
    n = len(tr); res = [x[1] for x in tr]; mw, ml, _ = geng.streaks(res)
    A = [x for x in tr if x[0].year <= 2023]; B = [x for x in tr if x[0].year >= 2024]
    ec = lambda q: sum(x[1] - x[4] / x[5] for x in q) / len(q) if q else 0.0
    yrs = collections.defaultdict(list)
    for x in tr: yrs[x[0].year].append(x)
    return dict(n=n, win=sum(1 for v in res if v > 0) / n, EA=ec(A), EB=ec(B), Ec=ec(tr), Rc=sum(x[1] - x[4] / x[5] for x in tr),
                ypos=sum(1 for y in yrs if sum(x[1] - x[4] / x[5] for x in yrs[y]) > 0), mw=mw, ml=ml,
                yml=max(geng.streaks([x[1] for x in yrs[y]])[1] for y in yrs), ymw=min(geng.streaks([x[1] for x in yrs[y]])[0] for y in yrs))
tf = sys.argv[1]; D = pickle.load(open(S + '/gold/stageC_%s.pkl' % tf, 'rb'))
for cn, _ in D['cands']:
    print('\n%s | %s' % (tf, cn))
    print('   %-34s %5s %5s | %6s | %-7s %-7s %-7s | %4s | %s' % ('exit', 'trades', '/day', 'win %', 'net/tr', '21-23', '24-26', 'yrs+', 'longest W/L streak (all years; worst single year L)'))
    for e in EX:
        q = m(D['res'][(cn, e)])
        print('   %-34s %5d %5.2f | %5.1f%% | %+.3f %+.3f %+.3f | %d/6 | %2d / %2d  (worst-year L %2d)  total net %+.0fR' % (e, q['n'], q['n'] / 1490, 100 * q['win'], q['Ec'], q['EA'], q['EB'], q['ypos'], q['mw'], q['ml'], q['yml'], q['Rc']))
