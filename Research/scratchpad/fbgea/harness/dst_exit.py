"""The time exit across the broker clock's summer-time switches: tExitH 4 / 24 / 72 h (all 12 strategies), and random set 5 of seed 13."""
import sys, numpy as np
sys.argv = [sys.argv[0], '0', '0']
import parity as P
bad = 0
for h in (4.0, 24.0, 72.0):
    bad += P.compare(dict(tExitH=h), 'time exit %g h' % h) > 0
rng = np.random.default_rng(13)
for it in range(5): kw = P.random_kw(rng)
bad += P.compare(kw, 'seed 13 random set 5') > 0
print('DST TIME EXIT: %s' % ('ALL IDENTICAL' if bad == 0 else '%d sets with mismatches' % bad))
