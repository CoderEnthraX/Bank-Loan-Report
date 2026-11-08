"""Independent implementations of the holdout finalists (see holdout_plan.md). gen_X(tf) -> (i, d, entry, stop, mode, window)."""
import sys, numpy as np, pandas as pd
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'; sys.path.insert(0, S + '/entry')
import kit, data, signals

def ny_ctx(tf):
    b = data.load(tf)
    if '_tday' not in b:
        t = pd.to_datetime(b['utc'], unit='s', utc=True).tz_convert(kit.NY).tz_localize(None)
        b['_nym'] = (t.hour * 60 + t.minute).to_numpy()
        td = (t + pd.Timedelta(hours=6)).normalize()                    # NY trading day: starts at 18:00 New York
        b['_tday'] = td.to_numpy().astype('datetime64[D]').astype(np.int64); b['_twd'] = td.dayofweek.to_numpy()
        b['_ok'] = ~np.isnan(b['atr']) & (np.arange(b['n']) > 60) & (np.arange(b['n']) < b['n'] - 10)
    return b

def gen_c1(tf, long_only=False, a=720, z=1080):
    b = data.load(tf); s = signals.raw(tf); i = s['i']; d = -s['d'].astype(int)
    nym = ny_ctx(tf)['_nym'][i]
    nogap = np.r_[b['utc'][1:] - b['utc'][:-1] == 60 * b['tfmin'], False][i]
    k = (nym >= a) & (nym < z) & nogap
    if long_only: k &= d == 1
    i, d = i[k], d[k]; C = b['C'][i]; A = b['atr'][i]
    return i, d, C, C - d * 1.8 * A, 1, 1

def gen_orb(tf):
    b = ny_ctx(tf); nm = b['_nym']; wd = b['_twd'] < 5; H, L, A = b['H'], b['L'], b['atr']
    inr = (nm >= 570) & (nm < 600) & wd
    df = pd.DataFrame(dict(day=b['_tday'], i=np.arange(b['n']), h=H, l=L))[inr]
    g = df.groupby('day').agg(h=('h', 'max'), l=('l', 'min'), last=('i', 'max'))
    g = g[(nm[g['last'].to_numpy()] + b['tfmin']) == 600]                 # the range is complete (its last bar ends at 10:00)
    last = g['last'].to_numpy(); ok = b['_ok'][last]; last = last[ok]; hi = g['h'].to_numpy()[ok]; lo = g['l'].to_numpy()[ok]
    a = A[last]; win = (780 - 600) // b['tfmin']
    i = np.r_[last, last]; d = np.r_[np.ones(len(last)), -np.ones(len(last))].astype(int)
    e = np.r_[hi + 0.05 * a, lo - 0.05 * a]; aa = np.r_[a, a]
    return i, d, e, e - d * 1.8 * aa, 2, win

def gen_sweep(tf):
    b = ny_ctx(tf); H, L, C, A = b['H'], b['L'], b['C'], b['atr']; day = b['_tday']
    dd = pd.DataFrame(dict(day=day, h=H, l=L)).groupby('day').agg(h=('h', 'max'), l=('l', 'min')).shift(1)
    pdh = pd.Series(day).map(dd['h']).to_numpy(); pdl = pd.Series(day).map(dd['l']).to_numpy()
    base = (b['_twd'] < 5) & b['_ok']
    def first(cond):
        idx = np.flatnonzero(cond); k = day[idx]
        return idx[np.r_[True, k[1:] != k[:-1]]] if len(idx) else idx
    is_ = first(base & ~np.isnan(pdh) & (H > pdh) & (C < pdh)); il = first(base & ~np.isnan(pdl) & (L < pdl) & (C > pdl))
    i = np.r_[il, is_]; d = np.r_[np.ones(len(il)), -np.ones(len(is_))].astype(int); a = A[i]
    ext = np.where(d == 1, L[i], H[i]); e = np.where(d == 1, H[i] + 0.05 * a, L[i] - 0.05 * a)
    st = np.where(d == 1, np.minimum(ext - 0.1 * a, e - 0.5 * a), np.maximum(ext + 0.1 * a, e + 0.5 * a))
    return i, d, e, st, 2, 3

def gen_season(tf):
    b = ny_ctx(tf); nm = b['_nym']; ok = b['_ok'] & (b['utc_wd'] != 6); C, A = b['C'], b['atr']
    il = np.flatnonzero(ok & (nm >= 780) & (nm < 1020)); is_ = np.flatnonzero(ok & (nm >= 420) & (nm < 600))
    i = np.r_[il, is_]; d = np.r_[np.ones(len(il)), -np.ones(len(is_))].astype(int)
    return i, d, C[i], C[i] - d * 1.8 * A[i], 1, 1

def gen_indicator(tf):
    s = signals.raw(tf); return s['i'], s['d'].astype(int), s['entry'], s['stop_h'], 0, 5

FINALISTS = [('C1 fade NY 12-18 (PRIMARY)', 'M5', lambda: gen_c1('M5')), ('C1L fade, longs only', 'M5', lambda: gen_c1('M5', True)),
             ('ORB NY 09:30-10:00', 'M15', lambda: gen_orb('M15')), ('SWEEP prev-day H/L', 'M15', lambda: gen_sweep('M15')),
             ('ref: time-of-day bias', 'M15', lambda: gen_season('M15')), ('ref: time-of-day bias', 'M5', lambda: gen_season('M5')),
             ('ref: indicator as is', 'M5', lambda: gen_indicator('M5')), ('ref: indicator as is', 'M15', lambda: gen_indicator('M15'))]

if __name__ == '__main__':
    test = len(sys.argv) > 1 and sys.argv[1] == 'TEST'
    for name, tf, fn in FINALISTS:
        i, d, e, st, mode, win = fn()
        print('--', name, tf)
        kit.evaluate(tf, i, d, e, st, mode=mode, window=win, name=name, allow_test=test)
