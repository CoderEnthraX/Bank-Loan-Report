"""v3 twin (gap rule at activation) vs engine v3 on an M1 chart: strategy 12 (M1 swing highs) and 4, 9, 10 with the defaults."""
import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fractal')
import engine as EN, pine_twin2 as TW
from final11 import ALL12
from multiprocessing import Pool
B = EN.load()
for _k in ('t', 'O', 'H', 'L', 'C'): B['M1_' + _k] = B[_k]
def job(k):
    s = TW.twin2(B, 'M1', ALL12[k], TW.P()); ref = EN.run(B, 'M1', *ALL12[k])
    return k, len(ref), len(s.trades) == len(ref) and all(a[0] == int(b[0]) and a[1] == b[1] and a[2] == int(b[2]) and a[3] == b[3] and a[4] == int(b[4]) for a, b in zip(s.trades, ref)), s.net
if __name__ == '__main__':
    with Pool(4) as pool: res = pool.map(job, [11, 3, 8, 9])
    for k, n, ok, net in res: print('M1 chart S%d: %d trades %s | money (Crooks F + ladder Medium) %+.0f $' % (k + 1, n, 'IDENTICAL' if ok else 'DIFFERENT', net))
