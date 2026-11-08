"""family 2: liquidity sweeps -> reversal: previous day high/low, intraday day high/low (old level), London range swept in NY"""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/agentA')
import lib, numpy as np, pandas as pd
FAM = 'sweep'

def prev_day_hl(b):
    df = pd.DataFrame(dict(k=b['tday'], h=b['H'], l=b['L']))
    g = df.groupby('k').agg(h=('h', 'max'), l=('l', 'min'))
    g2 = g.shift(1)
    return df['k'].map(g2['h']).to_numpy(), df['k'].map(g2['l']).to_numpy()

def day_running(b, min_age):
    """running high/low of the trading day up to bar i-1, but only levels set at least min_age bars before i"""
    n = b['n']; H, L = b['H'], b['L']; k = b['tday']
    rh = np.full(n, np.nan); rl = np.full(n, np.nan)
    df = pd.DataFrame(dict(k=k, h=H, l=L))
    # running max of the day lagged by min_age bars within the same day
    cmh = df.groupby('k')['h'].cummax().to_numpy(); cml = df.groupby('k')['l'].cummin().to_numpy()
    lag = np.arange(n) - min_age
    ok = (lag >= 0)
    same = np.zeros(n, bool); same[ok] = k[lag[ok]] == k[ok]
    rh[same] = cmh[lag[same]]; rl[same] = cml[lag[same]]
    # also require that bars lag+1..i-1 did not exceed that level (the level is untouched since) -> max of last min_age-1 bars
    mx = pd.Series(H).shift(1).rolling(min_age - 1).max().to_numpy(); mn = pd.Series(L).shift(1).rolling(min_age - 1).min().to_numpy()
    rh[~(mx < rh)] = np.nan; rl[~(mn > rl)] = np.nan
    return rh, rl

def sweep_eval(tf, name, hi, lo, win, first_only=True):
    b = lib.ctx(tf); H, L, C = b['H'], b['L'], b['C']; A = b['atr']
    S = win & ~np.isnan(hi) & (H > hi + 0.0) & (C < hi) & b['ok']
    Lg = win & ~np.isnan(lo) & (L < lo) & (C > lo) & b['ok']
    if first_only: is_ = lib.first_per_day(b, S); il = lib.first_per_day(b, Lg)
    else: is_ = lib.decluster(np.flatnonzero(S), 6); il = lib.decluster(np.flatnonzero(Lg), 6)
    i = np.r_[il, is_]; d = np.r_[np.ones(len(il)), -np.ones(len(is_))].astype(int)
    c = C[i]; a = A[i]; ext = np.where(d == 1, L[i], H[i])
    st = np.where(d == 1, np.minimum(ext - 0.1 * a, c - 0.5 * a), np.maximum(ext + 0.1 * a, c + 0.5 * a))
    lib.run(tf, i, d, c, st, 1, name=name + ' mkt stop=ext', family=FAM)
    lib.run(tf, i, d, c, c - d * 1.8 * a, 1, name=name + ' mkt 1.8ATR', family=FAM)
    # confirmation: stop entry through the sweep bar's other extreme within 3 bars, stop beyond the sweep extreme
    oth = np.where(d == 1, H[i] + 0.05 * a, L[i] - 0.05 * a)
    st2 = np.where(d == 1, np.minimum(ext - 0.1 * a, oth - 0.5 * a), np.maximum(ext + 0.1 * a, oth + 0.5 * a))
    lib.run(tf, i, d, oth, st2, 2, window=3, name=name + ' stopentry(conf) stop=ext', family=FAM)

if __name__ == '__main__':
  for tf in sys.argv[1].split(','):
    b = lib.ctx(tf); nm = b['ny_min']; wd = b['ny_wd'] < 5
    pdh, pdl = prev_day_hl(b)
    sweep_eval(tf, 'PDH/PDL sweep any time', pdh, pdl, wd)
    sweep_eval(tf, 'PDH/PDL sweep NY 03-12', pdh, pdl, wd & (nm >= 180) & (nm < 720))
    age = {'M5': 24, 'M15': 8, 'H1': 3, 'M1': 60}[tf]
    rh, rl = day_running(b, age)
    sweep_eval(tf, 'day-high/low(old>=2h) sweep 03-16', rh, rl, wd & (nm >= 180) & (nm < 960), first_only=False)
    # London session (03:00-08:00 NY) range swept during NY 08:00-12:00
    hi, lo, _ = lib.win_range(b, (nm >= 180) & (nm < 480) & wd)
    sweep_eval(tf, 'London range sweep in NY 08-12', hi, lo, wd & (nm >= 480) & (nm < 720))
