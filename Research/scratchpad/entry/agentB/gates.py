"""step 2: gating the raw signals (entries: base limit5 stop1.8, market at close, 1st pullback close above lvl). Each gate also
compared with random entries restricted to the same gate (g* columns) = does the signal add anything beyond the gate itself?"""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/agentB')
import numpy as np, lib, data, signals
F = 'gate'

def pullback(b, s):
    C, O = b['C'], b['O']; i, d = s['i'], s['d']; J = np.full(len(i), -1)
    for k in range(len(i)):
        for j in range(i[k] + 1, min(i[k] + 6, b['n'] - 1)):
            if d[k] * (C[j] - O[j]) < 0:
                if d[k] * (C[j] - s['entry'][k]) > 0: J[k] = j
                break
    return J

def entries(tf, s, sel, label, gate=None, which=('lim', 'mkt', 'pb')):
    b = data.load(tf); C, A = b['C'], b['atr']; i, d = s['i'][sel], s['d'][sel]
    if 'lim' in which: lib.ev(tf, i, d, s['entry'][sel], s['stop_n'][sel], mode=0, window=5, name='lim | ' + label, family=F, gate=gate)
    if 'mkt' in which: lib.ev(tf, i, d, C[i], C[i] - d * 1.8 * A[i], mode=1, name='mkt | ' + label, family=F, gate=gate)
    if 'pb' in which:
        J = s['_pb'][sel]; m = J >= 0; j = J[m]
        lib.ev(tf, j, d[m], C[j], C[j] - d[m] * 1.8 * A[j], mode=1, name='pb | ' + label, family=F, gate=gate)

def run(tf):
    b = data.load(tf); c = lib.ctx(tf); s = signals.raw(tf); s['_pb'] = pullback(b, s); i, d = s['i'], s['d']; n = b['n']
    T = np.ones(n, bool)
    nyh = c['nyh']
    # NY time windows
    shortWin = (nyh >= 7) & (nyh < 10); longWin = (nyh >= 14) & (nyh < 17)
    sel = np.where(d == 1, longWin[i], shortWin[i]); entries(tf, s, sel, 'NY L14-17 S07-10', gate=(longWin, shortWin))
    sel = np.where(d == 1, longWin[i], False); entries(tf, s, sel, 'NY L14-17 only', gate=(longWin, shortWin))
    sel = np.where(d == -1, shortWin[i], False); entries(tf, s, sel, 'NY S07-10 only', gate=(longWin, shortWin))
    nyday = (nyh >= 7) & (nyh < 17); sel = nyday[i]; entries(tf, s, sel, 'NY 07-17 both', gate=(nyday, nyday))
    # volatility regime
    for lo, hi, lab in ((0, 0.9, 'atr/atr100<0.9'), (0.9, 1.2, 'atr/atr100 0.9-1.2'), (1.2, 99, 'atr/atr100>1.2')):
        g = (c['atr_r100'] >= lo) & (c['atr_r100'] < hi); entries(tf, s, g[i], lab, gate=(g, g))
    if 'atr_vs_h1' in c:
        q = np.nanquantile(c['atr_vs_h1'][i[b['year'][i] <= 2023]], [1 / 3, 2 / 3])
        for lo, hi, lab in ((0, q[0], 'atr_vs_h1 low3'), (q[1], 99, 'atr_vs_h1 high3')):
            g = (c['atr_vs_h1'] >= lo) & (c['atr_vs_h1'] < hi); entries(tf, s, g[i], lab, gate=(g, g))
    # week / month VWAP side, daily trend (with the trade)
    for key, lab in (('vww', 'with week VWAP side'), ('vwm', 'with month VWAP side'), ('ema20_d', 'with daily EMA20 side'),
                     ('trend_d5', 'with 5-day trend')):
        gL = c[key] > 0; gS = c[key] < 0
        sel = np.where(d == 1, gL[i], gS[i]); entries(tf, s, sel, lab, gate=(gL, gS))
        sel = np.where(d == 1, gS[i], gL[i]); entries(tf, s, sel, lab.replace('with', 'AGAINST'), gate=(gS, gL))
    # stronger thresholds (raw params) -- signal subsets
    for kw, lab in ((dict(cmoMin=40.0), 'cmo>=40'), (dict(dispBodyPct=70.0), 'body>=70%'), (dict(dispClosePct=12.0), 'close<=12% from ext'),
                    (dict(dispAtr=1.3), 'range>=1.3ATR'), (dict(momAtr=1.5), 'mom>=1.5ATR')):
        s2 = signals.raw(tf, **kw); s2['_pb'] = pullback(b, s2)
        entries(tf, s2, np.ones(len(s2['i']), bool), lab)
    brk = np.where(d == 1, b['C'][i] - s['sigH'], s['sigL'] - b['C'][i]) / b['atr'][i]
    entries(tf, s, brk >= 0.3, 'break>=0.3ATR'); entries(tf, s, brk < 0.1, 'break<0.1ATR')

if __name__ == '__main__':
    for tf in sys.argv[1:]:
        print('=====', tf); run(tf)
