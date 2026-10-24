"""Gold grid: every config on M5 / M15 / H1 (4 processes). Saves the compact trade lists per (tf, config)."""
import sys, pickle, multiprocessing as mp
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
KZ = lambda a, l, n, c: dict(kzOn=True, kz=(a, l, n, c))
C = [('base', {})]
C += [('noChase %.1f' % s, dict(noChase=True, noChaseSig=s)) for s in (1.5, 2.0, 2.4, 3.0)]
C += [('minVw %.1f' % m, dict(minVwOn=True, minVwAtr=m)) for m in (0.5, 1.0, 1.5)]
C += [('band %.1f..%.1f' % (m, s), dict(noChase=True, noChaseSig=s, minVwOn=True, minVwAtr=m)) for m, s in ((1.0, 2.0), (1.0, 2.4), (0.5, 2.0), (1.0, 3.0))]
C += [('chop 12', dict(chopOn=True)), ('ema 1.65', dict(emaOn=True)), ('halfCap', dict(halfCap=True)), ('lossBlock', dict(lossBlock=True)),
      ('deepOn', dict(deepOn=True)), ('halfStrict', dict(halfStrict=True)), ('no half stop', dict(halfStopOn=False)), ('rearm newest', dict(rearmKeep=False))]
C += [('KZ Asia', KZ(1, 0, 0, 0)), ('KZ London', KZ(0, 1, 0, 0)), ('KZ NY', KZ(0, 0, 1, 0)), ('KZ LdnClose', KZ(0, 0, 0, 1)),
      ('KZ London+NY', KZ(0, 1, 1, 0)), ('KZ Ldn+NY+LC', KZ(0, 1, 1, 1)), ('KZ all four', KZ(1, 1, 1, 1))]
C += [('no Monday', dict(dayOn=True, days=(False, True, True, True, True, True, True))), ('no Friday', dict(dayOn=True, days=(True, True, True, True, False, True, True)))]
C += [('maxFills %d' % m, dict(maxFills=m)) for m in (1, 2, 3)]
C += [('stop %.1f ATR' % s, dict(stopAtr=s)) for s in (1.5, 2.2, 2.5)]
C += [('cooldown %d' % c, dict(cooldownBars=c)) for c in (3, 6)]
C += [('dayStop %dR' % r, dict(dayStopR=float(r))) for r in (2, 3)]
C += [('exit TP%d' % k, dict(exitAt=k)) for k in (1, 2, 3)]
C += [('BE at TP1', dict(mv1On=True, mv1R=0.0)), ('BE at TP2', dict(mv2On=True, mv2R=0.0)), ('lock TP1 at TP2', dict(mv2On=True, mv2R=0.6)),
      ('BE at TP1, exit TP2', dict(mv1On=True, mv1R=0.0, exitAt=2))]
def job(arg):
    tf, name, o = arg
    import geng
    tr = geng.run(tf, o)
    return tf, name, [(x['t'], x['res'], x['win'], tuple(x['hits']), x['sp'], x['risk'], x['be']) for x in tr]
if __name__ == '__main__':
    tasks = [(tf, n, o) for tf in ('M5', 'M15', 'H1') for n, o in C]
    out = {}
    with mp.Pool(4) as pool:
        for k, (tf, name, tr) in enumerate(pool.imap_unordered(job, tasks)):
            out[(tf, name)] = tr
            if k % 10 == 0: print(k + 1, '/', len(tasks), flush=True)
    pickle.dump(dict(configs=C, res=out), open(S + '/gold/grid1.pkl', 'wb'))
    print('done', len(out))
