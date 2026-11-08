"""of_agentA helpers: order-flow features for the indicator's signals (all causal at the signal bar's close), M1-level pullback
cancel rules (decided at each 1-minute or chart-bar close strictly before the fill minute), fast subset stats vs kit.baseline.
Outcomes come from ds_TF.pkl (signals.raw, stop_h, mode 0 window 5, 1-minute path): a filter / cancel rule only REMOVES trades,
so the kept trades' outcomes are unchanged."""
import os, sys, json, pickle
os.environ.setdefault('NUMBA_NUM_THREADS', '2')
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
if S + '/entry' not in sys.path: sys.path.insert(0, S + '/entry')
import numpy as np, pandas as pd
from numba import njit
import kit, data, of
A = S + '/entry/of_agentA'
TPR = kit.TPR
ROWS = A + '/rows.jsonl'

def ds(tf):
    df = pickle.load(open('%s/entry/ds_%s.pkl' % (S, tf), 'rb'))
    return df[df.split != 'test'].reset_index(drop=True)

def _tod_ratio(vol, utc_min, tfmin, sid, nback=20):
    """vol / mean vol of the same time-of-day slot over the previous `nback` sessions (causal)"""
    slot = utc_min // tfmin
    s = pd.DataFrame(dict(v=vol, slot=slot))
    m = s.groupby('slot')['v'].transform(lambda x: x.shift(1).rolling(nback, min_periods=5).mean()).to_numpy()
    return vol / np.where(m > 0, m, np.nan)

_FE = {}
def feats(tf):
    """DataFrame aligned with ds(tf): order-flow features (direction-signed: + = in favour of the trade)"""
    if tf in _FE: return _FE[tf]
    cache = '%s/feats_%s.pkl' % (A, tf)
    if os.path.exists(cache):
        _FE[tf] = pickle.load(open(cache, 'rb')); return _FE[tf]
    df = ds(tf); b = data.load(tf); f = of.flow(tf)
    i = df.i.to_numpy().astype(np.int64); d = df.dir.to_numpy().astype(float); n = b['n']
    vol = f['vol']; dtk = f['dtk']; dcl = f['dcl']; A_ = b['atr']; H, L, C = b['H'], b['L'], b['C']
    G = np.cumsum(dtk); Gc = np.cumsum(dcl); cv = np.r_[0.0, np.cumsum(vol)]
    vm20 = pd.Series(vol).rolling(20, min_periods=5).mean().shift(1).to_numpy()
    vtod = _tod_ratio(vol, b['utc_min'], b['tfmin'], f['sid'])
    E = df.entry.to_numpy(); ST = df.stop.to_numpy(); R = d * (E - ST)
    a = A_[i]; o = {}
    # ---- signal bar ----
    o['d_pct'] = d * dtk[i] / np.maximum(vol[i], 1)              # tick-rule delta % of volume, signed
    o['dcl_pct'] = d * dcl[i] / np.maximum(vol[i], 1)
    o['v_r20'] = vol[i] / vm20[i]
    o['v_tod'] = vtod[i]
    rng = (H[i] - L[i]) / a
    o['eff_res'] = o['v_tod'] / rng                                # effort / result: high = absorption (big volume, small range)
    o['vmax3_tod'] = np.nanmax(np.c_[vtod[i], vtod[i - 1], vtod[i - 2]], 1)
    # pre-signal / CVD trend (global running sum, no session reset)
    for k in (5, 20):
        o['cvd%d_pct' % k] = d * (G[i] - G[np.maximum(i - k, 0)]) / np.maximum(cv[i + 1] - cv[np.maximum(i + 1 - k, 0)], 1)
    o['pre5_pct'] = d * (G[i - 1] - G[np.maximum(i - 6, 0)]) / np.maximum(cv[i] - cv[np.maximum(i - 5, 0)], 1)
    sfirst = f['sfirst'][f['sid'][i]]
    o['scvd_pct'] = d * f['cvd_tk'][i] / np.maximum(cv[i + 1] - cv[sfirst], 1)   # session CVD as % of session volume
    o['scvd_cl_pct'] = d * f['cvd_cl'][i] / np.maximum(cv[i + 1] - cv[sfirst], 1)
    # CVD divergence: price makes a new N-bar extreme (signals always do on 6 bars), CVD does not
    for N in (6, 20):
        ext = np.array([(G[max(j - N, 0):j].max() if dd > 0 else G[max(j - N, 0):j].min()) for j, dd in zip(i, d)])
        pext = np.array([(H[max(j - N, 0):j].max() if dd > 0 else L[max(j - N, 0):j].min()) for j, dd in zip(i, d)])
        newp = np.where(d > 0, H[i] > pext, L[i] < pext)
        o['cvd_new%d' % N] = d * (G[i] - ext) / np.maximum(vm20[i], 1)        # > 0: CVD confirms the new extreme
        o['pnew%d' % N] = newp.astype(float)
    # ---- profile location ----
    ppoc, pvah, pval = f['ppoc'][i], f['pvah'][i], f['pval'][i]
    dpoc, dvah, dval = f['dpoc'][i], f['dvah'][i], f['dval'][i]
    def loc(p, vah, val):     # +1 beyond value in the trade direction, 0 inside, -1 beyond on the other side
        up = np.where(d > 0, p > vah, p < val); dn = np.where(d > 0, p < val, p > vah)
        return np.where(np.isnan(vah), np.nan, np.where(up, 1.0, np.where(dn, -1.0, 0.0)))
    o['loc_e_prior'] = loc(E, pvah, pval); o['loc_c_prior'] = loc(C[i], pvah, pval)
    o['loc_e_dev'] = loc(E, dvah, dval); o['loc_c_dev'] = loc(C[i], dvah, dval)
    o['e_ppoc_a'] = d * (E - ppoc) / a; o['e_dpoc_a'] = d * (E - dpoc) / a
    o['e_pva_edge_a'] = np.minimum(np.abs(E - pvah), np.abs(E - pval)) / a
    o['e_dva_edge_a'] = np.minimum(np.abs(E - dvah), np.abs(E - dval)) / a
    o['pva_w_a'] = (pvah - pval) / a
    o['rvp_e_dev'] = of.rvp(tf, i, E, 'dev'); o['rvp_e_prior'] = of.rvp(tf, i, E, 'prior')
    o['rvp_s_dev'] = of.rvp(tf, i, ST, 'dev'); o['rvp_s_prior'] = of.rvp(tf, i, ST, 'prior')
    for which in ('dev', 'prior'):
        for k, r in ((1, 0.6), (4, 2.0)):
            mn, mx, me = of.path_rvp(tf, i, E + d * 0.5 * of.W, E + d * r * R, which)
            o['p%d_max_%s' % (k, which)] = mx; o['p%d_mean_%s' % (k, which)] = me
        mn, mx, me = of.path_rvp(tf, i, E - d * 0.5 * of.W, ST, which)
        o['ps_max_%s' % which] = mx; o['ps_mean_%s' % which] = me
    out = pd.DataFrame(o)
    pickle.dump(out, open(cache, 'wb')); _FE[tf] = out; return out

# ---------------- pullback cancel rules (1-minute running stats before the fill minute) ----------------
@njit(cache=True)
def _cancel(ii, dd, fm, hi_sig, O1, C1, TV1, sigvpm, isclose, kind, thr, kmin, chart_only):
    """for every filled signal: True if the rule fires at some (1-minute or chart-bar) close strictly before the fill minute.
    kind 0: pullback volume rate (tick vol per minute so far / signal bar's vol per minute) > thr
    kind 1: pullback delta AGAINST the trade, % of pullback volume, > thr (with >= kmin minutes)
    kind 2: pullback volume rate < thr (very quiet; opposite test)
    kind 3: pullback delta IN FAVOUR of the trade % > thr (buyers already back before the fill)"""
    n = len(ii); out = np.zeros(n, np.bool_)
    for s in range(n):
        if fm[s] < 0: continue
        v = 0.0; dl = 0.0; k = 0
        for q in range(hi_sig[s], fm[s]):
            v += TV1[q]; k += 1
            if C1[q] > O1[q]: dl += TV1[q]
            elif C1[q] < O1[q]: dl -= TV1[q]
            if chart_only and not isclose[q]: continue
            if k < kmin: continue
            if kind == 0: x = (v / k) / sigvpm[s]; fire = x > thr
            elif kind == 2: x = (v / k) / sigvpm[s]; fire = x < thr
            elif kind == 1: x = -dd[s] * dl / max(v, 1.0); fire = x > thr
            else: x = dd[s] * dl / max(v, 1.0); fire = x > thr
            if fire: out[s] = True; break
    return out

_PB = {}
def pb_ctx(tf):
    if tf in _PB: return _PB[tf]
    df = ds(tf); b = data.load(tf); m = data.load('M1'); lo, hi = data.m1_map(tf); f = of.flow(tf)
    i = df.i.to_numpy().astype(np.int64)
    isclose = np.zeros(m['n'], np.bool_); isclose[np.maximum(hi - 1, 0)] = True
    sigvpm = f['vol'][i] / np.maximum(hi[i] - lo[i], 1)
    _PB[tf] = dict(i=i, d=df.dir.to_numpy().astype(np.int64), fm=df.fill_m1.to_numpy().astype(np.int64), hs=hi[i].astype(np.int64),
                   O1=m['O'], C1=m['C'], TV1=m['TV'], sigvpm=sigvpm, isclose=isclose)
    return _PB[tf]

def cancel(tf, kind, thr, kmin=1, chart_only=False):
    c = pb_ctx(tf)
    return _cancel(c['i'], c['d'], c['fm'], c['hs'], c['O1'], c['C1'], c['TV1'], c['sigvpm'], c['isclose'], kind, float(thr), int(kmin), chart_only)

# ---------------- stats ----------------
def stats(tf, keep, df=None, name='', tag='', log=True, quiet=False):
    """keep = boolean mask over ds(tf) rows (kept signals; unfilled ones are ignored). Excess vs kit.baseline per split / dir."""
    df = ds(tf) if df is None else df
    bl = kit.baseline(tf); mfe = df.mfe_m.to_numpy(); fill = df.filled.to_numpy(); sp = df.split.to_numpy(); d = df.dir.to_numpy()
    cost = df.cost_fill.to_numpy(); res = dict(name=name, tf=tf, tag=tag)
    for s_ in ('train', 'valid'):
        for lab, dd in (('both', 0), ('long', 1), ('short', -1)):
            m = keep & fill & (sp == s_) & ((d == dd) if dd else True)
            nn = int(m.sum())
            if nn == 0: res['%s_%s' % (s_, lab)] = dict(n=0, ex=np.nan); continue
            hit = np.array([np.mean(mfe[m] >= r - 1e-9) for r in TPR]) * 100
            nl = int((m & (d == 1)).sum()); ref = (bl[(s_, 1)] * nl + bl[(s_, -1)] * (nn - nl)) / nn
            E = hit / 100 * TPR - (1 - hit / 100) - np.mean(cost[m])
            res['%s_%s' % (s_, lab)] = dict(n=nn, pm=nn / kit.MONTHS[s_], hit=[round(x, 2) for x in hit], exk=[round(x, 2) for x in hit - ref],
                                            ex=round(float(np.mean(hit - ref)), 2), E=[round(x, 3) for x in E], se=round(50 / np.sqrt(nn), 2))
    if not quiet:
        g = lambda k: res[k]['ex']
        print('%-44s %-4s n/mo %6.1f | tr L %+5.2f S %+5.2f | va L %+5.2f S %+5.2f | all tr %+5.2f va %+5.2f' % (
            name[:44], tf, (res['train_both'].get('n', 0) + res['valid_both'].get('n', 0)) / 54.0,
            g('train_long'), g('train_short'), g('valid_long'), g('valid_short'), g('train_both'), g('valid_both')))
    if log:
        with open(ROWS, 'a') as fh: fh.write(json.dumps(res) + '\n')
    return res

def verdict(r, tf):
    mins = {'M1': 60, 'M5': 20, 'M15': 8, 'H1': 3}[tf]
    pm = (r['train_both'].get('n', 0) / 36.0)
    cells = [r[k]['ex'] for k in ('train_long', 'train_short', 'valid_long', 'valid_short')]
    if any(np.isnan(cells)): return 'n/a'
    if pm < mins: return 'too few'
    return 'PASS4' if all(c > 0 for c in cells) else ('%d/4' % sum(c > 0 for c in cells))

def tercile_screen(tf, x, name, df=None, min_frac=0.33):
    """keep x >= train 67th pct ('hi') / x <= 33rd ('lo'), thresholds from TRAIN only"""
    df = ds(tf) if df is None else df; tr = (df.split == 'train').to_numpy() & df.filled.to_numpy()
    ok = ~np.isnan(x)
    q1, q2 = np.nanquantile(x[tr & ok], [min_frac, 1 - min_frac])
    r_hi = stats(tf, ok & (x >= q2), df, '%s >= %.3g' % (name, q2), tag='terc')
    r_lo = stats(tf, ok & (x <= q1), df, '%s <= %.3g' % (name, q1), tag='terc')
    return r_hi, r_lo
