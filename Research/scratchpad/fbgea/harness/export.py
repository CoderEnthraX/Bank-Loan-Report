"""bars.npz -> data/*.bin: [n][t int64][o][h][l][c] float64, times on the data's clock (New York + 7 h = a GMT+2 / +3 US-summer-time server)."""
import sys, numpy as np, os
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fractal')
import engine as EN
B = EN.load(); D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data'); os.makedirs(D, exist_ok=True)
def w(name, t, o, h, l, c):
    with open(os.path.join(D, name + '.bin'), 'wb') as f:
        np.array([len(t)], np.int64).tofile(f)
        for a, ty in ((t, np.int64), (o, np.float64), (h, np.float64), (l, np.float64), (c, np.float64)): np.asarray(a, ty).tofile(f)
w('M1', B['t'], B['O'], B['H'], B['L'], B['C'])
for tf in ('M5', 'M15', 'H1', 'H4', 'D1'):
    w(tf, B[tf + '_t'], B[tf + '_O'] if tf + '_O' in B else B[tf + '_H'], B[tf + '_H'], B[tf + '_L'] if tf + '_L' in B else B[tf + '_H'], B[tf + '_C'])
print('exported', D, {k: len(B[k + '_t']) for k in ('M5', 'M15', 'H1', 'H4', 'D1')}, 'M1', len(B['t']))
