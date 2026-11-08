"""step 6: candidate 'fade the raw signal in the NY afternoon'. Rule (decidable at the signal bar's close): raw signal of the indicator,
bar open time NY local in [h0, h1), next bar contiguous (not the last bar before the 17:00 NY break / weekend) -> trade AGAINST it at
market (signal close), stop 1.8 ATR beyond the close; targets 0.6/1/1.5/2 R."""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/agentB')
import numpy as np, lib, data, signals, kit
F = 'fade2'

def fade_set(tf, h0, h1, contiguous=True, **kw):
    b = data.load(tf); s = signals.raw(tf, **kw); i, d = s['i'], s['d'].astype(np.int64)
    nym = kit.local_min(tf, 'ny')[i]
    m = (nym >= h0 * 60) & (nym < h1 * 60)
    if contiguous: m &= (b['utc'][np.minimum(i + 1, b['n'] - 1)] - b['utc'][i]) == 60 * b['tfmin']
    return s, i[m], -d[m], m

def run(tf, detail=False):
    if tf == 'M1': lib.m1_baseline()
    b = data.load(tf); C, A, H, L = b['C'], b['atr'], b['H'], b['L']
    nyh_all = kit.local_min(tf, 'ny') // 60
    for h0, h1, cont in ((12, 18, False), (12, 18, True), (12, 15, True), (15, 18, True), (13, 17, True), (11, 18, True), (12, 21, True)):
        s, i, fd, m = fade_set(tf, h0, h1, cont)
        g = (nyh_all >= h0) & (nyh_all < h1)
        nm = 'FADE NY %02d-%02d%s mkt 1.8' % (h0, h1, '' if cont else ' (incl. pre-break bar)')
        lib.ev(tf, i, fd, C[i], C[i] - fd * 1.8 * A[i], mode=1, name=nm, family=F, gate=None if tf == 'M1' else (g, g))
        if (h0, h1, cont) == (12, 18, True):
            if detail: lib.per_year(tf, i, fd, C[i], C[i] - fd * 1.8 * A[i], 1, 5, nm)
            # entry / stop variants of the same rule
            lib.ev(tf, i, fd, C[i], C[i] - fd * 1.2 * A[i], mode=1, name='FADE NY 12-18 mkt 1.2', family=F)
            lib.ev(tf, i, fd, C[i], C[i] - fd * 2.5 * A[i], mode=1, name='FADE NY 12-18 mkt 2.5', family=F)
            ext = np.where(fd == -1, H[i], L[i]) - fd * 0.3 * A[i]                 # beyond the signal candle's extreme
            ext = np.where(fd == -1, np.maximum(ext, C[i] + 0.5 * A[i]), np.minimum(ext, C[i] - 0.5 * A[i]))
            lib.ev(tf, i, fd, C[i], ext, mode=1, name='FADE NY 12-18 mkt stop sig-ext+0.3', family=F)
            e2 = s['entry'][m]
            lib.ev(tf, i, fd, e2, e2 - fd * 1.8 * A[i], mode=2, window=5, name='FADE NY 12-18 stop-entry @retest lvl', family=F)
            lim = C[i] - fd * 0.3 * A[i]                                           # sell higher: limit 0.3 ATR beyond the close
            lib.ev(tf, i, fd, lim, lim - fd * 1.8 * A[i], mode=0, window=3, name='FADE NY 12-18 limit +0.3ATR W3', family=F)
            # confirmation: next bar closes against the signal
            j = np.minimum(i + 1, b['n'] - 1); ok = fd * (C[j] - b['O'][j]) > 0
            lib.ev(tf, j[ok], fd[ok], C[j[ok]], C[j[ok]] - fd[ok] * 1.8 * A[j[ok]], mode=1, name='FADE NY 12-18 after counter bar', family=F)
            for kw, lab in ((dict(cmoMin=40.0), 'cmo40'), (dict(dispAtr=1.2), 'range>=1.2ATR')):
                s2, i2, fd2, _ = fade_set(tf, h0, h1, True, **kw)
                lib.ev(tf, i2, fd2, C[i2], C[i2] - fd2 * 1.8 * A[i2], mode=1, name='FADE NY 12-18 ' + lab, family=F)
            # random-direction control: every bar in the window, the 'fade' direction of a coin flip -> must be ~0
if __name__ == '__main__':
    for tf in sys.argv[1:]:
        print('=====', tf); run(tf, detail=True)
