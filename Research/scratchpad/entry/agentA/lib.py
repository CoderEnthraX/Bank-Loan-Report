"""agentA helpers: time context, session ranges, evaluation with (a) the kit's excess (random market 1.8 ATR, same dir/split)
and (b) a PLACEBO excess: same order geometry (entry offset, stop distance in ATR, mode, window), same direction, same split,
same New York hour of day, K random bars per signal. Rows appended to rows.jsonl."""
import sys, os, json
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
if S + '/entry' not in sys.path: sys.path.insert(0, S + '/entry')
import numpy as np, pandas as pd
import kit, data, outcomes, dataset
A = S + '/entry/agentA'
OUT = A + '/rows.jsonl'
TPR = kit.TPR
_C = {}

def ctx(tf):
    """bars + ny_min, lon_min, tday (NY trading day id, day starts 18:00 NY), ny_wd (weekday of the trading day, Mon=0), split"""
    if tf in _C: return _C[tf]
    b = data.load(tf)
    t = pd.to_datetime(b['utc'], unit='s', utc=True)
    ny = t.tz_convert(kit.NY); lon = t.tz_convert(kit.LON)
    nyl = ny.tz_localize(None)
    b['ny_min'] = (ny.hour * 60 + ny.minute).to_numpy()
    b['lon_min'] = (lon.hour * 60 + lon.minute).to_numpy()
    td = (nyl + pd.Timedelta(hours=6)).normalize()
    b['tday'] = (td.to_numpy().astype('datetime64[D]').astype(np.int64))
    b['ny_wd'] = td.dayofweek.to_numpy()
    b['split'] = dataset.split_of(b['utc'])
    b['ok'] = ~np.isnan(b['atr']) & (np.arange(b['n']) > 60) & (np.arange(b['n']) < b['n'] - 10)
    _C[tf] = b; return b

def win_range(b, mask, key=None):
    """for each bar: high / low / end index of the masked bars of the SAME trading day (key = day id, default tday),
    only known after the last masked bar -> returns hi, lo, last_idx arrays (nan / -1 where the window has not finished)"""
    key = b['tday'] if key is None else key
    idx = np.flatnonzero(mask)
    df = pd.DataFrame(dict(k=key[idx], h=b['H'][idx], l=b['L'][idx], i=idx))
    g = df.groupby('k').agg(h=('h', 'max'), l=('l', 'min'), last=('i', 'max'), first=('i', 'min'))
    hi = np.full(b['n'], np.nan); lo = np.full(b['n'], np.nan); last = np.full(b['n'], -1)
    pos = pd.Series(np.arange(len(g)), index=g.index)
    kk = pd.Series(key).map(pos).to_numpy()
    has = ~np.isnan(kk); kk2 = np.where(has, kk, 0).astype(int)
    L = g['last'].to_numpy()[kk2]
    after = has & (np.arange(b['n']) > L)
    hi[after] = g['h'].to_numpy()[kk2][after]; lo[after] = g['l'].to_numpy()[kk2][after]; last[after] = L[after]
    return hi, lo, last

def first_per_day(b, cond, key=None, per_dir=None):
    """indexes of the first bar per day where cond holds"""
    key = b['tday'] if key is None else key
    idx = np.flatnonzero(cond)
    if len(idx) == 0: return idx
    k = key[idx]; keep = np.ones(len(idx), bool); keep[1:] = k[1:] != k[:-1]
    return idx[keep]

def decluster(i, gap):
    """keep signals at least `gap` bars after the previous kept one (i sorted)"""
    i = np.sort(np.asarray(i)); out = []; last = -10**9
    for x in i:
        if x - last >= gap: out.append(x); last = x
    return np.array(out, np.int64)

_POOL = {}
def _pool(tf):
    if tf in _POOL: return _POOL[tf]
    b = ctx(tf); ok = b['ok'] & (b['split'] != 'test')
    P = {}
    for sp in ('train', 'valid'):
        for h in range(24):
            P[(sp, h)] = np.flatnonzero(ok & (b['split'] == sp) & (b['ny_min'] // 60 == h))
    _POOL[tf] = P; return P

def hits(mfe):
    return np.array([np.mean(mfe >= r - 1e-9) for r in TPR]) * 100 if len(mfe) else np.full(4, np.nan)

def placebo(tf, i, d, entry, stop, mode, window, K=3, seed=0):
    b = ctx(tf); P = _pool(tf); rng = np.random.default_rng(seed)
    a = b['atr'][i]; eo = (entry - b['C'][i]) / a; so = (stop - entry) / a
    sp = b['split'][i]; h = b['ny_min'][i] // 60
    J = []; D = []; EO = []; SO = []; M = []; SPL = []
    md = np.broadcast_to(np.asarray(mode), (len(i),))
    for s in range(len(i)):
        if sp[s] == 'test': continue
        pool = P[(sp[s], h[s])]
        j = rng.choice(pool, K); J.append(j); D += [d[s]] * K; EO += [eo[s]] * K; SO += [so[s]] * K; M += [md[s]] * K; SPL += [sp[s]] * K
    J = np.concatenate(J); D = np.array(D); EO = np.array(EO); SO = np.array(SO); M = np.array(M); SPL = np.array(SPL)
    e = b['C'][J] + EO * b['atr'][J]; e = np.where(M == 1, b['C'][J], e); st = e + SO * b['atr'][J]
    o = outcomes.simulate(tf, J, D, e, st, mode=M, window=window)
    f = o['fill_m1'] >= 0
    out = {}
    for s_ in ('train', 'valid'):
        for lab, dd in (('long', 1), ('short', -1)):
            m = f & (SPL == s_) & (D == dd)
            out[(s_, lab)] = hits(o['mfe_m'][m])
    return out

def run(tf, i, d, entry, stop, mode=1, window=5, name='', family='', K=3, save=True, show=True):
    i = np.asarray(i, np.int64); d = np.asarray(d, np.int64); entry = np.asarray(entry, float); stop = np.asarray(stop, float)
    b = ctx(tf)
    good = (b['split'][i] != 'test') & ~np.isnan(stop) & ~np.isnan(entry) & (d * (entry - stop) > 0)
    i, d, entry, stop = i[good], d[good], entry[good], stop[good]
    md = np.broadcast_to(np.asarray(mode), (len(good),))[good] if np.ndim(mode) else mode
    if len(i) < 30:
        if show: print('%-40s %s too few (%d)' % (name, tf, len(i)))
        return None
    r = kit.evaluate(tf, i, d, entry, stop, mode=md, window=window, name=name, quiet=True)
    pl = placebo(tf, i, d, entry, stop, md, window, K=K)
    row = dict(name=name, family=family, tf=tf, mode=int(np.max(md)), risk_atr=float(np.median(d * (entry - stop) / b['atr'][i])))
    for s_ in ('train', 'valid'):
        for lab in ('long', 'short'):
            x = r[(s_, lab)]; k = s_[0] + lab[0]
            if x.get('n', 0) == 0: row[k + '_n'] = 0; continue
            row[k + '_n'] = x['n']; row[k + '_pm'] = x['per_month']; row[k + '_hit'] = list(np.round(x['hit'], 1))
            row[k + '_ex'] = list(np.round(x['excess'], 2)); row[k + '_avgex'] = round(x['avg_excess'], 2)
            pe = x['hit'] - pl[(s_, lab)]; row[k + '_plex'] = list(np.round(pe, 2)); row[k + '_avgpl'] = round(float(np.mean(pe)), 2)
            row[k + '_E1'] = round(float(x['E'][0]), 3); row[k + '_E4'] = round(float(x['E'][3]), 3); row[k + '_se'] = round(x['se'], 2)
            row[k + '_fill'] = round(x['fill_rate'], 3)
    if show:
        def g(k, f): return row.get(k + '_' + f, float('nan'))
        print('%-42s %-3s pm %5.1f | TR ex L %+5.1f S %+5.1f pl L %+5.1f S %+5.1f | VA ex L %+5.1f S %+5.1f pl L %+5.1f S %+5.1f | nL %d nS %d E1 %+.2f/%+.2f' % (
            name[:42], tf, g('tl', 'pm') + g('ts', 'pm'), g('tl', 'avgex'), g('ts', 'avgex'), g('tl', 'avgpl'), g('ts', 'avgpl'),
            g('vl', 'avgex'), g('vs', 'avgex'), g('vl', 'avgpl'), g('vs', 'avgpl'), g('tl', 'n'), g('ts', 'n'), g('tl', 'E1'), g('ts', 'E1')), flush=True)
    if save:
        with open(OUT, 'a') as f: f.write(json.dumps(row, default=float) + '\n')
    return row

def per_year(tf, i, d, entry, stop, mode=1, window=5):
    """excess (kit baseline, per split) per year and per direction, for finalists; 2025 = H1 only"""
    b = ctx(tf); i = np.asarray(i); d = np.asarray(d)
    o = kit.outcomes_of(tf, i, d, entry, stop, mode, window); bl = kit.baseline(tf)
    yr = b['year'][i]; sp = b['split'][i]; f = o['fill_m1'] >= 0; out = {}
    for y in range(2021, 2026):
        for dd in (1, -1):
            m = f & (yr == y) & (d == dd) & (sp != 'test')
            if m.sum() < 10: continue
            h = hits(o['mfe_m'][m]); ref = bl[(sp[m][0], dd)]
            out[(y, dd)] = (int(m.sum()), float(np.mean(h - ref)))
    return out
