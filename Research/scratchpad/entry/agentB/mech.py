"""step 1: entry mechanics on the indicator's raw signals (M5, M15). Every variant decidable at a bar close."""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/agentB')
import numpy as np, lib, data, signals
F = 'mech'

def confirm(b, s, W, need_bull=True, need_beyond=True):
    """first bar j in i+1..i+W where the retest level has been touched (bars i+1..j) and j closes back in the trade direction
    (bullish bar for a long, C beyond the level). returns j (or -1) and the extreme of the pullback (lowest low / highest high)"""
    O, H, L, C = b['O'], b['H'], b['L'], b['C']; n = b['n']
    J = np.full(len(s['i']), -1); X = np.full(len(s['i']), np.nan)
    for k, (i, d, lv) in enumerate(zip(s['i'], s['d'], s['entry'])):
        t = False; ext = np.inf if d == 1 else -np.inf
        for j in range(i + 1, min(i + 1 + W, n - 1)):
            ext = min(ext, L[j]) if d == 1 else max(ext, H[j])
            if (d == 1 and L[j] <= lv) or (d == -1 and H[j] >= lv): t = True
            if t and (not need_bull or d * (C[j] - O[j]) > 0) and (not need_beyond or d * (C[j] - lv) > 0):
                J[k] = j; X[k] = ext; break
    return J, X

def run(tf):
    b = data.load(tf); s = signals.raw(tf); i, d = s['i'], s['d']; A = b['atr']; C, O, H, L = b['C'], b['O'], b['H'], b['L']
    E = lambda *a, **k: lib.ev(tf, *a, family=F, **k)
    E(i, d, s['entry'], s['stop_h'], mode=0, window=5, name='base limit5 stop_h')
    E(i, d, s['entry'], s['stop_n'], mode=0, window=5, name='base limit5 stop1.8')
    E(i, d, C[i], C[i] - d * 1.8 * A[i], mode=1, name='market at signal close')
    for w in (1, 2, 3):
        E(i, d, s['entry'], s['stop_n'], mode=0, window=w, name='limit window %d' % w)
    for f in (0.25, 0.5, 0.75, 1.0):
        lv = C[i] - d * f * (H[i] - L[i])
        E(i, d, lv, lv - d * 1.8 * A[i], mode=0, window=5, name='limit depth %.0f%% of range' % (100 * f))
    # confirmation
    for W in (3, 5, 8):
        J, X = confirm(b, s, W); m = J >= 0; j = J[m]; dd = d[m]
        E(j, dd, C[j], C[j] - dd * 1.8 * A[j], mode=1, name='confirm W%d mkt stop1.8' % W)
        if W == 5:
            st = X[m] - dd * 0.1 * A[j]; st = np.where(dd == 1, np.minimum(st, C[j] - 0.5 * A[j]), np.maximum(st, C[j] + 0.5 * A[j]))
            E(j, dd, C[j], st, mode=1, name='confirm W5 mkt stop struct')
            st2 = np.where(dd == 1, L[i[m]], H[i[m]]) - dd * 0.1 * A[j]
            st2 = np.where(dd == 1, np.minimum(st2, C[j] - 0.5 * A[j]), np.maximum(st2, C[j] + 0.5 * A[j]))
            E(j, dd, C[j], st2, mode=1, name='confirm W5 mkt stop sigcandle')
            E(j, dd, C[j], C[j] - dd * 1.0 * A[j], mode=1, name='confirm W5 mkt stop1.0')
            E(j, dd, C[j], C[j] - dd * 3.0 * A[j], mode=1, name='confirm W5 mkt stop3.0')
            # break of the confirmation bar
            ent = np.where(dd == 1, H[j], L[j]) + dd * 0.02 * A[j]
            E(j, dd, ent, ent - dd * 1.8 * A[j], mode=2, window=3, name='confirm W5 break-of-bar stop1.8')
    J, X = confirm(b, s, 5, need_bull=False); m = J >= 0; j = J[m]; dd = d[m]
    E(j, dd, C[j], C[j] - dd * 1.8 * A[j], mode=1, name='confirm W5 close-beyond only')
    # market after no fill
    for N in (1, 2, 3):
        for X_ in (0.0, 0.3):
            k = np.minimum(i + N, b['n'] - 2)
            nofill = np.ones(len(i), bool)
            for q in range(1, N + 1):
                jj = np.minimum(i + q, b['n'] - 1)
                nofill &= np.where(d == 1, L[jj] > s['entry'], H[jj] < s['entry'])
            m = nofill & (d * (C[k] - C[i]) >= X_ * A[i])
            E(k[m], d[m], C[k[m]], C[k[m]] - d[m] * 1.8 * A[k[m]], mode=1, name='nofill N%d mkt if beyond %.1fATR' % (N, X_))
    # second displacement in the same direction within K bars
    for K in (6, 12, 24):
        sec = np.zeros(len(i), bool); last = {1: -10 ** 9, -1: -10 ** 9}
        for k in range(len(i)):
            sec[k] = i[k] - last[d[k]] <= K; last[d[k]] = i[k]
        E(i[sec], d[sec], s['entry'][sec], s['stop_n'][sec], mode=0, window=5, name='2nd disp K%d limit' % K)
        E(i[sec], d[sec], C[i[sec]], C[i[sec]] - d[sec] * 1.8 * A[i[sec]], mode=1, name='2nd disp K%d market' % K)
        if K == 12:
            E(i[~sec], d[~sec], C[i[~sec]], C[i[~sec]] - d[~sec] * 1.8 * A[i[~sec]], mode=1, name='1st disp only K12 market')
    # first pullback bar's close
    for keep in (False, True):
        J = np.full(len(i), -1)
        for k in range(len(i)):
            for j in range(i[k] + 1, min(i[k] + 6, b['n'] - 1)):
                if d[k] * (C[j] - O[j]) < 0:
                    if not keep or d[k] * (C[j] - s['entry'][k]) > 0: J[k] = j
                    break
        m = J >= 0; j = J[m]
        E(j, d[m], C[j], C[j] - d[m] * 1.8 * A[j], mode=1, name='1st pullback close%s' % (' above lvl' if keep else ''))
    # fades
    E(i, -d, C[i], C[i] + d * 1.8 * A[i], mode=1, name='FADE market')
    E(i, -d, s['entry'], s['entry'] + d * 1.8 * A[i], mode=2, window=5, name='FADE stop-entry at retest lvl')

if __name__ == '__main__':
    for tf in sys.argv[1:]:
        print('=====', tf); run(tf)
