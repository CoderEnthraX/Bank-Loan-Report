"""Stage 2: combinations of stop size x kill zones x VWAP distance x EMA200 trend x breakeven, on M5 / M15 / H1."""
import sys, pickle, itertools, multiprocessing as mp
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
KZ = lambda a, l, n, c: dict(kzOn=True, kz=(a, l, n, c))
STOP = [('stop1.8', {}), ('stop2.2', dict(stopAtr=2.2)), ('stop2.5', dict(stopAtr=2.5))]
SESS = [('allhours', {}), ('KZ-NY', KZ(0, 0, 1, 0)), ('KZ-Ldn+NY', KZ(0, 1, 1, 0)), ('KZ-Asia', KZ(1, 0, 0, 0)), ('KZ-Ldn+NY+LC', KZ(0, 1, 1, 1))]
DIST = [('anydist', {}), ('nc1.5', dict(noChase=True, noChaseSig=1.5)), ('nc2.0', dict(noChase=True, noChaseSig=2.0)), ('band0.5-2', dict(noChase=True, noChaseSig=2.0, minVwOn=True, minVwAtr=0.5))]
TREND = [('notrend', {}), ('ema200', dict(emaPos=(200,)))]
EXIT = [('TP4', {}), ('BE@TP1', dict(mv1On=True, mv1R=0.0))]
C = []
for parts in itertools.product(STOP, SESS, DIST, TREND, EXIT):
    o = {}
    for _, d in parts: o.update(d)
    C.append((' '.join(n for n, _ in parts), o))
def job(arg):
    tf, name, o = arg
    import geng, ref_gs
    ref_gs.eprep = lambda t: geng.prepare(t); geng.ref_g = ref_gs
    tr = geng.run(tf, o)
    return tf, name, [(x['t'], x['res'], x['win'], tuple(x['hits']), x['sp'], x['risk'], x['be']) for x in tr]
if __name__ == '__main__':
    tasks = [(tf, n, o) for tf in ('H1', 'M15', 'M5') for n, o in C]
    out = {}
    with mp.Pool(4) as pool:
        for k, (tf, name, tr) in enumerate(pool.imap_unordered(job, tasks, chunksize=4)):
            out[(tf, name)] = tr
            if k % 60 == 0: print(k + 1, '/', len(tasks), flush=True)
    pickle.dump(dict(configs=C, res=out), open(S + '/gold/grid2.pkl', 'wb'))
    print('done', len(out))
