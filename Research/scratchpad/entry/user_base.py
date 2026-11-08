"""The user's v4.0 settings (engine part) on gold: exact engine trades (one at a time), TP1-TP4 hit rates on the chart convention,
per period. exitAt=4 here so TP2-TP4 can be seen (the user exits at TP1: their win rate = TP1 hit)."""
import sys, numpy as np
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold'); sys.path.insert(0, S + '/entry')
import geng, dataset, data
USER = dict(halfCap=True, maxFills=10, dayOn=True, days=(False, True, True, True, False, False, False), hoursOn=True, hoursSess=(600, 2300),
            kzOn=True, kz=(True, True, True, False), kzAuto=True, exitAt=4)
for tf in sys.argv[1:]:
    for name, o in (('default engine', dict(exitAt=4)), ('your v4.0 settings', USER)):
        tr = geng.run(tf, o)
        t = np.array([int((x['t'] - __import__('datetime').datetime(1970, 1, 1)).total_seconds()) - 19800 for x in tr])
        sp = dataset.split_of(t); H = np.array([x['hits'] for x in tr])
        for s_ in ('train', 'valid'):
            m = sp == s_
            print('%-4s %-20s %-5s n %5d (%5.1f/mo) TP1-TP4 hit %s' % (tf, name, s_, m.sum(), m.sum() / (36 if s_ == 'train' else 18),
                  ' '.join('%5.1f' % (100 * H[m, k].mean()) for k in range(4))))
