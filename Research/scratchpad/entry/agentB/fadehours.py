"""step 5: is the fade a time-of-day effect or a signal effect? fade (market at signal close, 1.8 ATR) by 3-hour NY block, compared
with random entries in the same block (g*). Also the raw signal (non-fade) per block for symmetry."""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/agentB')
import numpy as np, lib, data, signals, kit
F = 'fadehours'
def run(tf):
    if tf == 'M1': lib.m1_baseline()
    b = data.load(tf); C, A = b['C'], b['atr']; s = signals.raw(tf); i, d = s['i'], s['d'].astype(np.int64)
    nyh_all = lib.ctx(tf)['nyh'] if tf != 'M1' else kit.local_min('M1', 'ny') // 60
    nyh = nyh_all[i]
    for h0 in range(0, 24, 3):
        g = (nyh_all >= h0) & (nyh_all < h0 + 3); m = (nyh >= h0) & (nyh < h0 + 3)
        lib.ev(tf, i[m], -d[m], C[i[m]], C[i[m]] + d[m] * 1.8 * A[i[m]], mode=1, name='FADE NY %02d-%02d' % (h0, h0 + 3), family=F,
               gate=None if tf == 'M1' else (g, g))
if __name__ == '__main__':
    for tf in sys.argv[1:]:
        print('=====', tf); run(tf)
