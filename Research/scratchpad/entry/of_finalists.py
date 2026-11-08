"""Independent implementations of the order-flow finalists (of_holdout_plan.md). gen(...) -> (i, d, entry, stop, mode, window)."""
import sys, numpy as np
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'; sys.path.insert(0, S + '/entry')
import kit, data, signals, of, features

def gen_ofa_c1(tf='M5', thr=7.5):
    b = data.load(tf); s = signals.raw(tf); i = s['i']; f = of.flow(tf)
    k = ((f['pvah'] - f['pval'])[i] / b['atr'][i]) <= thr
    return i[k], s['d'][k].astype(int), s['entry'][k], s['stop_h'][k], 0, 5

def gen_ofa_c1b(tf='M5', thr=16.8):
    b = data.load(tf); s = signals.raw(tf); i = s['i']; ss = features.sessions(tf); sid = ss['sid'][i]; pv = np.maximum(sid - 1, 0)
    w = np.where(sid > 0, ss['dH'][pv] - ss['dL'][pv], np.nan) / b['atr'][i]
    k = w <= thr
    return i[k], s['d'][k].astype(int), s['entry'][k], s['stop_h'][k], 0, 5

def _decluster(i, d, gap):
    keep = np.zeros(len(i), bool); last = {1: -10 ** 9, -1: -10 ** 9}
    for q in np.argsort(i, kind='stable'):
        if i[q] - last[d[q]] >= gap: keep[q] = True; last[d[q]] = i[q]
    return keep

def gen_ofb_c3(tf='M5', thr=5.8, min_minutes=180, gap=12):
    b = data.load(tf); s = signals.raw(tf); i = s['i']; d0 = s['d'].astype(int); f = of.flow(tf)
    dist = (b['C'][i] - f['dpoc'][i]) / b['atr'][i]
    away = d0 * dist >= thr                                         # the signal points away from the developing POC, far from it
    late = b['vb'][i] * b['tfmin'] >= min_minutes
    wd = ((b['srv'][i] // 86400) + 3) % 7 < 5                       # server-day Monday..Friday
    k = away & late & wd
    i, d = i[k], -d0[k]                                              # the opposite trade
    kk = _decluster(i, d, gap); i, d = i[kk], d[kk]
    C = b['C'][i]; A = b['atr'][i]
    return i, d, C, C - d * 1.8 * A, 1, 1

def gen_ofb_c1l(tf='M5', thr=8.6, min_minutes=180, gap=12):
    b = data.load(tf); f = of.flow(tf); n = b['n']
    ok = ~np.isnan(b['atr']) & (b['utc_wd'] != 6) & (np.arange(n) > 60) & (np.arange(n) < n - 5)
    dist = (b['C'] - f['dpoc']) / b['atr']
    i = np.flatnonzero(ok & (dist <= -thr) & (b['vb'] * b['tfmin'] >= min_minutes)); d = np.ones(len(i), int)
    kk = _decluster(i, d, gap); i = i[kk]; d = d[kk]
    C = b['C'][i]; A = b['atr'][i]
    return i, d, C, C - 1.8 * A, 1, 1

FIN = [('OFA-C1 narrow prior value area', 'M5', gen_ofa_c1), ('OFA-C1b narrow prior range (no volume)', 'M5', gen_ofa_c1b),
       ('OFB-C3 fade extension from POC', 'M5', gen_ofb_c3), ('OFB-C1L long far below POC', 'M5', gen_ofb_c1l)]
if __name__ == '__main__':
    test = len(sys.argv) > 1 and sys.argv[1] == 'TEST'
    for name, tf, fn in FIN:
        print('--', name, tf); kit.evaluate(tf, *fn(tf)[:4], mode=fn(tf)[4], window=fn(tf)[5], name=name, allow_test=test)
