"""agentB helpers: quiet evaluation + variant log (variants.csv), bar-level gating arrays, gate-matched random baseline."""
import sys, os, csv, pickle, numpy as np, pandas as pd
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
if S + '/entry' not in sys.path: sys.path.insert(0, S + '/entry')
import kit, data, signals, features, dataset
B = S + '/entry/agentB'; LOG = B + '/variants.csv'
COLS = ['family', 'name', 'tf', 'n_mo', 'nL_tr', 'nS_tr', 'nL_va', 'nS_va', 'trL', 'trS', 'vaL', 'vaS', 'tr_all', 'va_all',
        'trL_tp', 'trS_tp', 'vaL_tp', 'vaS_tp', 'E1_tr', 'E4_tr', 'E1_va', 'E4_va', 'gtrL', 'gtrS', 'gvaL', 'gvaS']

def ev(tf, i, d, entry, stop, mode=1, window=5, name='', family='', log=True, gate=None, show=True):
    """evaluate quietly; returns a row dict. gate = (maskL, maskS) bar-level boolean arrays: also report excess vs random entries
    restricted to those bars (does the signal add anything beyond the gate?)"""
    i = np.asarray(i, np.int64); d = np.asarray(d, np.int64)
    ok = np.isfinite(np.asarray(entry, float)) & np.isfinite(np.asarray(stop, float))
    i, d, entry, stop = i[ok], d[ok], np.asarray(entry, float)[ok], np.asarray(stop, float)[ok]
    if np.isscalar(mode) is False: mode = np.asarray(mode)[ok]
    r = kit.evaluate(tf, i, d, entry, stop, mode=mode, window=window, name=name, quiet=True)
    g = lambda s, l, k='avg_excess': r[(s, l)].get(k, np.nan) if r[(s, l)].get('n', 0) else np.nan
    tp = lambda s, l: ' '.join('%+.1f' % x for x in r[(s, l)]['excess']) if r[(s, l)].get('n', 0) else ''
    row = dict(family=family, name=name, tf=tf, n_mo=round(g('train', 'both', 'per_month'), 1),
               nL_tr=g('train', 'long', 'n'), nS_tr=g('train', 'short', 'n'), nL_va=g('valid', 'long', 'n'), nS_va=g('valid', 'short', 'n'),
               trL=round(g('train', 'long'), 2), trS=round(g('train', 'short'), 2), vaL=round(g('valid', 'long'), 2), vaS=round(g('valid', 'short'), 2),
               tr_all=round(g('train', 'both'), 2), va_all=round(g('valid', 'both'), 2),
               trL_tp=tp('train', 'long'), trS_tp=tp('train', 'short'), vaL_tp=tp('valid', 'long'), vaS_tp=tp('valid', 'short'),
               E1_tr=round(r[('train', 'both')]['E'][0], 3) if r[('train', 'both')].get('n') else np.nan,
               E4_tr=round(r[('train', 'both')]['E'][3], 3) if r[('train', 'both')].get('n') else np.nan,
               E1_va=round(r[('valid', 'both')]['E'][0], 3) if r[('valid', 'both')].get('n') else np.nan,
               E4_va=round(r[('valid', 'both')]['E'][3], 3) if r[('valid', 'both')].get('n') else np.nan)
    if gate is not None:
        gb = gate_base(tf, *gate)
        for s_, k in (('train', 'tr'), ('valid', 'va')):
            for lab, dd, kk in (('long', 1, 'L'), ('short', -1, 'S')):
                rr = r[(s_, lab)]
                row['g%s%s' % (k, kk)] = round(float(np.mean(rr['hit'] - gb[(s_, dd)])), 2) if rr.get('n') else np.nan
    row['_res'] = r
    if show:
        print('%-34s %-3s %6.1f/mo | tr L %+5.2f (%4s) S %+5.2f (%4s) | va L %+5.2f (%4s) S %+5.2f (%4s) | E1 %+.3f/%+.3f%s' % (
            name[:34], tf, row['n_mo'], row['trL'], row['nL_tr'], row['trS'], row['nS_tr'], row['vaL'], row['nL_va'], row['vaS'], row['nS_va'],
            row['E1_tr'], row['E1_va'], ('' if gate is None else ' | vs gate tr %+.2f %+.2f va %+.2f %+.2f' % (row['gtrL'], row['gtrS'], row['gvaL'], row['gvaS']))), flush=True)
    if log:
        new = not os.path.exists(LOG)
        with open(LOG, 'a', newline='') as f:
            w = csv.DictWriter(f, fieldnames=COLS, extrasaction='ignore')
            if new: w.writeheader()
            w.writerow(row)
    return row

_BARS = {}
def bars(tf):
    if tf not in _BARS: _BARS[tf] = pickle.load(open('%s/entry/bars_%s.pkl' % (S, tf), 'rb'))
    return _BARS[tf]

def gate_base(tf, maskL, maskS):
    """hit% TP1-4 of random market entries on bars where the gate holds (per split, direction)"""
    g = bars(tf); ii = g.i.to_numpy(); out = {}
    for sp in ('train', 'valid'):
        m0 = (g.split == sp).to_numpy()
        for dd, col, mk in ((1, 'mfeL', maskL), (-1, 'mfeS', maskS)):
            x = g[col].to_numpy()[m0 & mk[ii]]; x = x[~np.isnan(x)]
            out[(sp, dd)] = np.array([np.mean(x >= r - 1e-9) for r in kit.TPR]) * 100
    return out

_CTX = {}
def ctx(tf):
    """bar-level context arrays (all causal at bar close)"""
    if tf in _CTX: return _CTX[tf]
    b = data.load(tf); n = b['n']
    c = {}
    c['nym'] = kit.local_min(tf, 'ny'); c['nyh'] = c['nym'] // 60
    c['atr_r100'] = b['atr'] / data.rma(b['tr'], 100)
    ss = features.sessions(tf); sid = ss['sid']
    prv = lambda arr, k: np.where(sid - k >= 0, arr[np.maximum(sid - k, 0)], np.nan)
    datr = prv(ss['datr'], 1); c['datr'] = datr
    c['ema20_d'] = (b['C'] - prv(ss['dema20'], 1)) / datr          # >0 above daily EMA20 (previous completed session)
    c['ema50_d'] = (b['C'] - prv(ss['dema50'], 1)) / datr
    c['trend_d5'] = (b['C'] - prv(ss['dC'], 5)) / datr
    c['vww'] = (b['C'] - b['Vw']) / b['atr']; c['vwm'] = (b['C'] - b['Vm']) / b['atr']
    if tf != 'H1':
        h = data.load('H1'); hi = features.h1_context(tf); c['atr_vs_h1'] = b['atr'] / h['atr'][np.maximum(hi, 0)]
    c['atr_d'] = b['atr'] / datr
    _CTX[tf] = c; return c

def note(txt):
    with open(B + '/progress.md', 'a') as f: f.write(txt.rstrip() + '\n')

def m1_baseline(nsamp=300000, seed=11):
    """kit has no bars_M1.pkl: random market entries on M1 (stop 1.8 ATR), installed into kit's baseline cache, saved in agentB"""
    import outcomes
    f = B + '/base_M1.pkl'
    if os.path.exists(f): kit._BL['M1'] = pickle.load(open(f, 'rb')); return kit._BL['M1']
    b = data.load('M1'); n = b['n']; rng = np.random.default_rng(seed)
    ok = np.flatnonzero(~np.isnan(b['atr']) & (b['utc_wd'] != 6) & (np.arange(n) > 60) & (np.arange(n) < n - 5))
    i = np.sort(rng.choice(ok, nsamp, replace=False)); sp = dataset.split_of(b['utc'][i]); out = {}
    for dd in (1, -1):
        o = outcomes.simulate('M1', i, np.full(len(i), dd, np.int8), b['C'][i], b['C'][i] - dd * 1.8 * b['atr'][i], mode=1)
        for s_ in ('train', 'valid'):
            x = o['mfe_m'][(sp == s_) & (o['fill_m1'] >= 0)]
            out[(s_, dd)] = np.array([np.mean(x >= r - 1e-9) for r in kit.TPR]) * 100
    pickle.dump(out, open(f, 'wb')); kit._BL['M1'] = out; return out

def per_year(tf, i, d, entry, stop, mode=1, window=5, label=''):
    """avg excess (TP1-4) per year 2021..2025H1, longs / shorts, vs random entries of the same year (bars_TF.pkl; M5 used for M1)"""
    b = data.load(tf); i = np.asarray(i, np.int64); d = np.asarray(d, np.int64)
    o = kit.outcomes_of(tf, i, d, entry, stop, mode, window); f = o['fill_m1'] >= 0; mfe = o['mfe_m']
    t = b['utc'][i].astype('datetime64[s]'); keep = t < np.datetime64('2025-07-01'); yr = b['year'][i]
    g = bars(tf if tf != 'M1' else 'M5'); g = g[g.split != 'test']
    out = {}
    for y in (2021, 2022, 2023, 2024, 2025):
        gy = g[g.year == y]
        for dd, col in ((1, 'mfeL'), (-1, 'mfeS')):
            x = gy[col].to_numpy(); x = x[~np.isnan(x)]; ref = np.array([np.mean(x >= r - 1e-9) for r in kit.TPR]) * 100
            m = f & keep & (yr == y) & (d == dd)
            hit = np.array([np.mean(mfe[m] >= r - 1e-9) for r in kit.TPR]) * 100 if m.sum() else np.full(4, np.nan)
            out[(y, dd)] = (float(np.mean(hit - ref)), int(m.sum()))
    print('  per-year %-28s ' % label[:28] + ' '.join('%s L %+5.1f(%d) S %+5.1f(%d)' % (str(y) if y < 2025 else '25H1', out[(y, 1)][0], out[(y, 1)][1],
          out[(y, -1)][0], out[(y, -1)][1]) for y in (2021, 2022, 2023, 2024, 2025)), flush=True)
    return out
