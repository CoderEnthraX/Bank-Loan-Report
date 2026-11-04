"""Crooks C over N wins (N = 1, 2, 3, 4) on gold 2021-2026: every catalogue strategy that is profitable at fixed $50, $500 cap (Start again / Clamp)
and no cap, whole run and each half, 200 random orders for the $500 Start again case. Output: crooks_cn.pkl + crooks_cn.txt."""
import sys, pickle, random
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
import recovery as RC, crooks
out = {}; L = []
for tf in crooks.TFS:
    for i, d in enumerate(crooks.sources(tf)):
        seq = crooks.sequence(d['trades'], d['cfg']); xr = crooks.exit_r(d['cfg'])
        trs = [(res, c, parts) for _, res, c, parts in seq]
        off = RC.simulate(trs, 'Off', exitR=xr)
        if off['net'] <= 0: continue
        A = [(r, c, p) for t, r, c, p in seq if t.year <= 2023]; B = [(r, c, p) for t, r, c, p in seq if t.year >= 2024]
        rng = random.Random(5 + i); orders = []
        for _ in range(200):
            q = list(trs); rng.shuffle(q); orders.append(q)
        row = {}
        for n in (1, 2, 3, 4):
            for cap, act in ((500.0, 'reset'), (500.0, 'clamp'), (0.0, 'clamp')):
                kw = dict(cap=cap, capAction=act, exitR=xr, cN=n)
                r = dict(all=RC.simulate(trs, 'Crooks C', **kw), A=RC.simulate(A, 'Crooks C', **kw), B=RC.simulate(B, 'Crooks C', **kw))
                if (cap, act) == (500.0, 'reset') or cap == 0:
                    nets = sorted(RC.simulate(q, 'Crooks C', **kw)['net'] for q in orders); sims = [RC.simulate(q, 'Crooks C', **kw) for q in orders[:100]]
                    r['med'] = nets[len(nets) // 2]; r['ruin'] = sum(1 for z in sims if z['ruined']) / len(sims)
                row[(n, cap, act)] = r
        out[(tf, i)] = dict(name=d['name'], off=off, rows=row)
        L.append('%s S%d %-28s fixed $50 %+7.0f (fall %3.0f%%)' % (tf, i, d['name'][:28], off['net'], 100 * off['maxDDpct']))
        for n in (1, 2, 3, 4):
            a = row[(n, 500.0, 'reset')]; b = row[(n, 0.0, 'clamp')]
            L.append('   N=%d  $500 start again: %+8.0f fall %3.0f%% max risk $%4.0f | 21-23 %+7.0f 24-26 %+7.0f | median %+7.0f | no cap: %+9.0f fall %3.0f%% blown in %3.0f%% of orders' % (
                n, a['all']['net'], 100 * a['all']['maxDDpct'], a['all']['maxRisk'], a['A']['net'], a['B']['net'], a['med'], b['all']['net'], 100 * b['all']['maxDDpct'], 100 * b['ruin']))
pickle.dump(out, open(S + '/gold/crooks_cn.pkl', 'wb'))
open(S + '/gold/crooks_cn.txt', 'w').write('\n'.join(L) + '\n')
# summary over the profitable strategies
for n in (1, 2, 3, 4):
    a = [v['rows'][(n, 500.0, 'reset')] for v in out.values()]; b = [v['rows'][(n, 0.0, 'clamp')] for v in out.values()]
    o = [v['off'] for v in out.values()]
    print('N=%d | %d strategies | $500 start again: total %+8.0f, avg fall %4.1f%%, both halves positive on %2d, better ratio than fixed $50 on %2d | no cap: blown in %4.1f%% of random orders (avg), worst %3.0f%%' % (
        n, len(a), sum(x['all']['net'] for x in a), 100 * sum(x['all']['maxDDpct'] for x in a) / len(a), sum(1 for x in a if x['A']['net'] > 0 and x['B']['net'] > 0),
        sum(1 for x, y in zip(a, o) if x['all']['net'] / max(1e-9, x['all']['maxDD']) > y['net'] / max(1e-9, y['maxDD'])),
        100 * sum(x['ruin'] for x in b) / len(b), 100 * max(x['ruin'] for x in b)))
print('fixed $50 total %+.0f' % sum(v['off']['net'] for v in out.values()))
