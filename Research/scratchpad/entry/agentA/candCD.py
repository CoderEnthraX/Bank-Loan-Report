"""candidates C (round-number break) and D (far-from-VWAP fade) sensitivity"""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/agentA')
import lib, numpy as np
lib.OUT = lib.A + '/rows_cand.jsonl'
def C_(tf, step=50.0, k=1.8, gap_h=1.0, mode='break'):
    b = lib.ctx(tf); H, L, C, A = b['H'], b['L'], b['C'], b['atr']; ok = b['ok'] & (b['ny_wd'] < 5)
    pc = np.r_[C[0], C[:-1]]; up = (np.floor(pc / step) + 1) * step; dn = np.floor(pc / step) * step
    gap = max(1, int(gap_h * 60 / b['tfmin']))
    il = lib.decluster(np.flatnonzero(ok & (C > up)), gap); is_ = lib.decluster(np.flatnonzero(ok & (C < dn)), gap)
    i = np.r_[il, is_]; d = np.r_[np.ones(len(il)), -np.ones(len(is_))].astype(int); c = C[i]; a = A[i]
    lib.run(tf, i, d, c, c - d * k * a, 1, name='C round $%d break %.1fATR declust %.0fh' % (step, k, gap_h), family='candC')
def D_(tf, kk=6.0, k=1.8):
    b = lib.ctx(tf); C, A, V = b['C'], b['atr'], b['V']; ok = b['ok'] & (b['ny_wd'] < 5); per_h = 60 // b['tfmin']
    dist = (C - V) / A; pd_ = np.r_[0, dist[:-1]]
    il = lib.decluster(np.flatnonzero(ok & (dist < -kk) & (pd_ >= -kk)), per_h); is_ = lib.decluster(np.flatnonzero(ok & (dist > kk) & (pd_ <= kk)), per_h)
    i = np.r_[il, is_]; d = np.r_[np.ones(len(il)), -np.ones(len(is_))].astype(int); c = C[i]; a = A[i]
    lib.run(tf, i, d, c, c - d * k * a, 1, name='D |C-VWAP|>%.0fATR fade %.1fATR' % (kk, k), family='candD')
for tf in sys.argv[1].split(','):
    for step in (25.0, 50.0, 100.0): C_(tf, step)
    C_(tf, 50.0, k=1.0); C_(tf, 50.0, k=3.0); C_(tf, 50.0, gap_h=4.0)
    for kk in ({'M5': (5.0, 6.0, 7.0, 8.0), 'M15': (3.0, 4.0, 5.0), 'H1': (2.0, 3.0)}[tf]): D_(tf, kk)
