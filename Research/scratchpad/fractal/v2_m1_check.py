"""v2 defaults on an M1 chart (the finest): strategies 4, 10 and 11 vs engine v1."""
import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fractal')
import engine as EN, pine_twin2 as TW
from final11 import ALL
from multiprocessing import Pool
B = EN.load()
def job(k):
    s = TW.twin2(B, 'M1', ALL[k], TW.P()); ref = EN.run(B, 'M1', *ALL[k])
    return k, len(ref), len(s.trades) == len(ref) and all(a[0] == int(b[0]) and a[1] == b[1] and a[2] == int(b[2]) and a[3] == b[3] and a[4] == int(b[4]) for a, b in zip(s.trades, ref))
if __name__ == '__main__':
    with Pool(3) as pool: res = pool.map(job, [3, 9, 10])
    for k, n, ok in res: print('M1 chart S%d: %d trades %s' % (k + 1, n, 'IDENTICAL' if ok else 'DIFFERENT'))
