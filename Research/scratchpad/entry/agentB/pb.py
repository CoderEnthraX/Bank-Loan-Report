"""step 3b: the 'pullback' entry family on raw signals: after the signal bar, the first counter-direction bar (close vs open against
the trade) within W bars; if its close is still beyond a level, enter (market at its close, or stop entry on a break of that bar)."""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/agentB')
import numpy as np, lib, data, signals
F = 'pb'

def pb_bars(b, s, W=5, level='lvl'):
    C, O = b['C'], b['O']; i, d = s['i'], s['d']; J = np.full(len(i), -1)
    lv = {'lvl': s['entry'], 'mid': (O[i] + C[i]) / 2, 'none': None}[level]
    for k in range(len(i)):
        for j in range(i[k] + 1, min(i[k] + 1 + W, b['n'] - 1)):
            if d[k] * (C[j] - O[j]) < 0:
                if lv is None or d[k] * (C[j] - lv[k]) > 0: J[k] = j
                break
    return J

def stops(b, j, d, kind):
    C, H, L, A = b['C'], b['H'], b['L'], b['atr']
    if kind == '1.8': return C[j] - d * 1.8 * A[j]
    if kind == '2.5': return C[j] - d * 2.5 * A[j]
    if kind == 'struct':
        st = np.where(d == 1, L[j], H[j]) - d * 0.1 * A[j]
        return np.where(d == 1, np.minimum(st, C[j] - 0.5 * A[j]), np.maximum(st, C[j] + 0.5 * A[j]))

def run(tf, yearly=False):
    if tf == 'M1': lib.m1_baseline()
    b = data.load(tf); s = signals.raw(tf); C, H, L, A = b['C'], b['H'], b['L'], b['atr']
    rows = []
    for W, lev, ent, stk in ((5, 'lvl', 'close', '1.8'), (3, 'lvl', 'close', '1.8'), (8, 'lvl', 'close', '1.8'), (5, 'mid', 'close', '1.8'),
                             (5, 'none', 'close', '1.8'), (5, 'lvl', 'break', '1.8'), (5, 'lvl', 'close', 'struct'), (5, 'lvl', 'close', '2.5'),
                             (5, 'lvl', 'break', 'struct')):
        J = pb_bars(b, s, W, lev); m = J >= 0; j = J[m]; d = s['d'][m].astype(np.int64)
        nm = 'pb W%d %s %s stop%s' % (W, lev, ent, stk)
        if ent == 'close':
            e = C[j]; st = stops(b, j, d, stk); mode = 1; win = 5
        else:
            e = np.where(d == 1, H[j], L[j]) + d * 0.02 * A[j]
            st = e - d * 1.8 * A[j] if stk == '1.8' else np.where(d == 1, np.minimum(L[j] - 0.1 * A[j], e - 0.5 * A[j]), np.maximum(H[j] + 0.1 * A[j], e + 0.5 * A[j]))
            mode = 2; win = 3
        lib.ev(tf, j, d, e, st, mode=mode, window=win, name=nm, family=F)
        if yearly and (W, lev, ent, stk) == (5, 'lvl', 'close', '1.8'):
            lib.per_year(tf, j, d, e, st, mode, win, nm)

if __name__ == '__main__':
    for tf in sys.argv[1:]:
        print('=====', tf); run(tf, yearly=True)
