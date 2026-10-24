import json, random, sys
D = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/research/vwap_ema'
G = json.load(open(D + '/grid.json')); B = G[0]
SY = ['GC', 'EURUSD', 'NASDAQ', 'US30', 'CRUDE', 'NIFTY', 'SENSEX', 'ETH', 'NSE_NIFTY1', 'MCX_NATURALGAS']
def boot(dc, db, it=1000, seed=3):
    days = sorted(set(dc) | set(db)); r = random.Random(seed); out = []
    for _ in range(it):
        smp = [days[r.randrange(len(days))] for _ in days]
        a = [v for d in smp for v in dc.get(d, [])]; b = [v for d in smp for v in db.get(d, [])]
        if a and b: out.append(sum(a) / len(a) - sum(b) / len(b))
    out.sort(); return out[int(0.025 * len(out))], out[int(0.975 * len(out))]
def null_pct(dc, db, it=1000, seed=5):
    """configs whose trades are a subset of the baseline (skipped setups run invisibly): random subsets of the same size"""
    bv = [v for d in db.values() for v in d]; cv = [v for d in dc.values() for v in d]
    k = len(cv); obs = sum(cv) / k - sum(bv) / len(bv); r = random.Random(seed); cnt = 0
    for _ in range(it):
        s = r.sample(bv, k); cnt += (sum(s) / k - sum(bv) / len(bv)) < obs
    return cnt / it
rows = []
for c in G:
    rr = {}
    for key in ('r1', 'r2'):
        x = c[key]; b = B[key]
        better = sum(1 for s in SY if x['sym'][s].get('n', 0) and b['sym'][s].get('n', 0) and x['sym'][s]['E'] > b['sym'][s]['E'])
        lo, hi = boot(x['days'], b['days']) if c is not B else (0, 0)
        rr[key] = dict(n=x['all']['n'], win=x['all'].get('win', 0), E=x['all'].get('E', 0), tot=x['all'].get('tot', 0),
                       Etr=x['train'].get('E', 0), Ete=x['test'].get('E', 0), better=better, ci=(lo, hi))
        if 'invisibly' in c['name']: rr[key]['null'] = null_pct(x['days'], b['days'])
    rows.append((c, rr))
json.dump([(c['fam'], c['name'], rr) for c, rr in rows], open(D + '/analysis.json', 'w'))
for fam in 'ABCDE':
    print('\n== family', fam)
    for c, rr in rows:
        if c['fam'] != fam: continue
        a, b = rr['r1'], rr['r2']
        nl = ' null %2.0f%%' % (100 * b['null']) if 'null' in b else ''
        print('%-66s | 1:1 win %4.1f%% E %+.3f (Sep %+.3f Oct %+.3f) %d/10 | 1:2 n %4d win %4.1f%% E %+.3f (Sep %+.3f Oct %+.3f) %d/10 tot %+4.0f CI [%+.3f,%+.3f]%s' % (
            c['name'][:66], 100 * a['win'], a['E'], a['Etr'], a['Ete'], a['better'], b['n'], 100 * b['win'], b['E'], b['Etr'], b['Ete'], b['better'], b['tot'], b['ci'][0], b['ci'][1], nl))
