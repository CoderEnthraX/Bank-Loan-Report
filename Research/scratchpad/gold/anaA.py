"""Stage A analysis: per setting, 2021-23 (A) and 2024-26 (B) after spread, TP1-TP4 hit rates and streaks, vs the default settings."""
import sys, os, pickle, collections, json
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold'); import geng
def runs(bools):
    """longest run of True and of False"""
    bt = bf = ct = cf = 0
    for b in bools:
        if b: ct += 1; cf = 0; bt = max(bt, ct)
        else: cf += 1; ct = 0; bf = max(bf, cf)
    return bt, bf
def sweep_metrics(tf):
    """(configs, {setting name: metrics}) of the stage-A sweep, from sweep_<tf>.pkl or the slim checkpoint copy slim_sweep_<tf>.pkl"""
    fn = S + '/gold/sweep_%s.pkl' % tf
    if os.path.exists(fn):
        D = pickle.load(open(fn, 'rb')); return D['configs'], {n: metrics(t) for n, t in D['res'].items() if t}
    D = pickle.load(open(S + '/gold/slim_sweep_%s.pkl' % tf, 'rb')); return D['configs'], D['metrics']
def metrics(tr):
    n = len(tr)
    if not n: return None
    res = [x[1] for x in tr]; mw, ml, _ = geng.streaks(res)
    A = [x for x in tr if x[0].year <= 2023]; B = [x for x in tr if x[0].year >= 2024]
    ec = lambda q: sum(x[1] - x[4] / x[5] for x in q) / len(q) if q else 0.0
    eg = lambda q: sum(x[1] for x in q) / len(q) if q else 0.0
    yrs = collections.defaultdict(list)
    for x in tr: yrs[x[0].year].append(x[1] - x[4] / x[5])
    tps = []
    for k in range(4):
        w, l = runs([x[3][k] for x in tr]); tps.append(dict(rate=sum(x[3][k] for x in tr) / n, maxW=w, maxL=l))
    return dict(n=n, nA=len(A), nB=len(B), EA=eg(A), EB=eg(B), EcA=ec(A), EcB=ec(B), Ec=ec(tr), E=eg(tr), win=sum(1 for x in tr if x[1] > 0) / n,
                maxW=mw, maxL=ml, ypos=sum(1 for y in yrs if sum(yrs[y]) > 0), tps=tps, R=sum(res), Rc=sum(x[1] - x[4] / x[5] for x in tr))
if __name__ == '__main__':
    out = {}
    for tf in sys.argv[1].split(','):
        D = pickle.load(open(S + '/gold/sweep_%s.pkl' % tf, 'rb')); C = D['configs']; R = D['res']
        rows = [(name, metrics(R[name])) for name, _ in C if R.get(name)]
        rows = [(n_, m) for n_, m in rows if m]
        d0 = dict(rows)['default']; out[tf] = rows
        print('\n==== %s  default: %d trades, 2021-23 net %+.3f, 2024-26 net %+.3f, win %.1f%%, TP1-4 %s, longest losing streak %d' % (
            tf, d0['n'], d0['EcA'], d0['EcB'], 100 * d0['win'], ' '.join('%.0f%%' % (100 * t['rate']) for t in d0['tps']), d0['maxL']))
        print('%-48s %6s | %-15s | %-15s | %4s | %-23s | %s' % ('setting (sorted by 2021-23 after spread)', 'trades', '2021-23 net (d)', '2024-26 net (d)', 'yrs+', 'TP1  TP2  TP3  TP4', 'longest W/L streak at TP4; TP1 W/L'))
        for name, m in sorted(rows, key=lambda r: -r[1]['EcA'])[:40]:
            print('%-48s %6d | %+.3f (%+.3f) | %+.3f (%+.3f) | %d/6 | %s | %2d/%2d  TP1 %2d/%2d' % (
                name[:48], m['n'], m['EcA'], m['EcA'] - d0['EcA'], m['EcB'], m['EcB'] - d0['EcB'], m['ypos'], ' '.join('%3.0f%%' % (100 * t['rate']) for t in m['tps']),
                m['maxW'], m['maxL'], m['tps'][0]['maxW'], m['tps'][0]['maxL']))
    pickle.dump(out, open(S + '/gold/anaA_%s.pkl' % sys.argv[1].replace(',', '_'), 'wb'))
