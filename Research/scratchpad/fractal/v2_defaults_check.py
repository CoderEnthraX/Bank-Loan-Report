"""v2 with its defaults (options off, Money on: Crooks F + ladder Medium, $500 cap clamp) gives the v1 trades on an M5 chart, all 11."""
import sys, numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fractal')
import engine as EN, pine_twin2 as TW
from final11 import ALL
from multiprocessing import Pool
B = EN.load()


def job(k):
    p = TW.P(); s = TW.twin2(B, 'M5', ALL[k], p); ref = EN.run(B, 'M5', *ALL[k])
    same = len(s.trades) == len(ref) and all(a[0] == int(b[0]) and a[1] == b[1] and a[2] == int(b[2]) and a[3] == b[3] and a[4] == int(b[4]) for a, b in zip(s.trades, ref))
    return k, len(ref), same, s.net, s.ddP, s.stopped


if __name__ == '__main__':
    with Pool(4) as pool: res = pool.map(job, range(len(ALL)))
    for k, n, same, net, ddp, st in res: print('S%-2d trades %4d %s | Crooks F + Medium on M5: net %+9.0f $, max DD %.1f %%, stopped %s' % (k + 1, n, 'IDENTICAL' if same else 'DIFFERENT', net, 100 * ddp, st))
    print('v2 defaults vs v1:', 'ALL IDENTICAL' if all(r[2] for r in res) else 'DIFFERENT', '| total net %+.0f $' % sum(r[3] for r in res))
