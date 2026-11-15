"""Every strategy on every chart it can run on: the rules' exits (how many at break-even), the TradingView broker model's trades, the
next-open exits / entries, and every trade that differs from the rules, sorted by cause. Usage: audit_all.py CHART ..."""
import sys, collections, json
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fractal')
import sync_why as SW, pine_twin2 as TW, engine as EN
from final11 import ALL12
from multiprocessing import Pool
COMM = 0.115


def job(a):
    ctf, k = a
    mt, tt, _ = SW.run_tag(ctf, k, TW.P())
    key = lambda x: (x[0], round(x[1], 6), x[2], round(x[3], 6))
    ms = set(key(x) for x in mt); ts = set(key(x) for x in tt)
    byE = {(x[0], round(x[1], 6)): x for x in mt}
    cause = collections.Counter()
    for x in tt:
        if key(x) in ms: continue
        if x[6] == 'catch-up': cause['entry at next open'] += 1
        elif x[5] == 'close' and x[7] not in ('TIME', 'WKND'): cause['exit at next open (' + x[7] + ')'] += 1
        elif (x[0], round(x[1], 6)) not in byE: cause['entry the rules do not have'] += 1
        else: cause['same entry, other exit: ' + x[7]] += 1
    missing = sum(1 for x in mt if key(x) not in ts and (x[0], round(x[1], 6)) not in set((y[0], round(y[1], 6)) for y in tt))
    mr = collections.Counter(SW.RS[x[4]] for x in mt)
    nx = sum(1 for x in tt if x[5] == 'close' and x[7] not in ('TIME', 'WKND'))
    ne = sum(1 for x in tt if x[6] == 'catch-up')
    p = ALL12[k]; sl = p[4]
    mU = sum(0 for _ in [])
    tvU = sum(x[4] * (x[3] - x[1]) - 2 * COMM * x[4] for x in tt)
    return dict(chart=ctf, s=k + 1, model=len(mt), tv=len(tt), same=len(ms & ts), reasons=dict(mr), nextExit=nx, nextEntry=ne, causes=dict(cause), missing=missing, tvUsd=tvU)


if __name__ == '__main__':
    jobs = [(c, k) for c in sys.argv[1:] for k in range(12) if EN.TF_SEC[ALL12[k][0]] >= EN.TF_SEC[c]]
    with Pool(4) as pool: res = pool.map(job, jobs)
    json.dump(res, open('labels/audit_all.json', 'w'), indent=1)
    for r in res:
        n = max(1, r['model']); be = r['reasons'].get('BE', 0) + r['reasons'].get('SALV', 0)
        print('%-3s S%-2d rules %4d trades: TP %4d SL %4d BE %4d SALV %4d (break-even %4.1f%%) | TradingView %4d, same %5.1f%%, next-open exits %3d (%4.1f%%), entries %2d, rules trades missing %d | %s' % (
            r['chart'], r['s'], r['model'], r['reasons'].get('TP', 0), r['reasons'].get('SL', 0), r['reasons'].get('BE', 0), r['reasons'].get('SALV', 0), 100.0 * be / n,
            r['tv'], 100.0 * r['same'] / n, r['nextExit'], 100.0 * r['nextExit'] / max(1, r['tv']), r['nextEntry'], r['missing'], r['causes']))
