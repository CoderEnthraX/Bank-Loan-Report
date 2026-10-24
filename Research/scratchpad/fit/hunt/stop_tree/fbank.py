"""Feature bank for the 80 original trades (stop_tree). feats(P, i, d, entry, fi, ctxfeat) -> dict of numeric features.
Prefixes: a_ = displacement (arm) bar i, b_ = bar before (i-1), f_ = fill bar, s_ = session/prev-session, q_ = signal sequence
(stateless), g_ = teacher-forced original-trade history, e_ = in-engine state (best model).  Directional features are
d-normalised (positive = in trade direction)."""
import sys, os, math, pickle
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fbase import FIT, base, sessions, sigs, core_sig
sys.path.insert(0, FIT)


def _cap(x, c=1000): return min(x, c)


def feats(P, i, d, entry, fi=None):
    O, H, L, C, V, T = P['O'], P['H'], P['L'], P['C'], P['V'], P['T']
    A = P[('atr', 14)][i]; f = {}
    o, h, l, c = O[i], H[i], L[i], C[i]; rng = h - l; body = abs(c - o)
    fav = h if d > 0 else l; adv = l if d > 0 else h
    # ---------- displacement candle
    f['a_rngA'] = rng / A; f['a_bodyA'] = body / A; f['a_bodyPct'] = body / rng
    f['a_closePos'] = (c - l) / rng if d > 0 else (h - c) / rng
    f['a_favWickA'] = d * (fav - c) / A; f['a_advWickA'] = d * (o - adv) / A
    f['a_trA'] = P['tr'][i] / A; f['a_gapA'] = d * (o - C[i - 1]) / A
    for n in (6, 10, 20, 50):
        ext = max(H[i - n:i]) if d > 0 else min(L[i - n:i])
        f[f'a_brk{n}A'] = d * (c - ext) / A
    for n in (1, 3, 5, 10, 20, 50):
        f[f'a_mom{n}A'] = d * (c - C[i - n]) / A
    for n in (5, 10, 20):
        f[f'a_rngXmean{n}'] = rng / (sum(H[k] - L[k] for k in range(i - n, i)) / n)
    # breakout look-back: bars back until a bar exceeds the close
    k = 1
    while k < 1000 and i - k >= 0 and not ((H[i - k] >= c) if d > 0 else (L[i - k] <= c)): k += 1
    f['a_brkLook'] = k
    # ---------- VWAP
    vw = V[i]; sd = P['vsd'][i]
    f['a_vwA'] = d * (c - vw) / A; f['a_openVwA'] = d * (o - vw) / A; f['a_entVwA'] = d * (entry - vw) / A
    f['a_stopVwA'] = d * (entry - d * 1.8 * A - vw) / A
    f['a_z'] = d * (c - vw) / sd if sd else 0.0; f['a_vsdA'] = (sd or 0) / A
    for n in (1, 3, 5, 10):
        f[f'a_vsl{n}A'] = d * (vw - V[i - n]) / A if V[i - n] is not None else 0.0
    # bars since the close was last on the other side of VWAP
    k = 1
    while k < 500 and i - k >= 0 and V[i - k] is not None and d * (C[i - k] - V[i - k]) > 0: k += 1
    f['a_vwRun'] = k
    # ---------- ATR / volatility
    f['a_atrBps'] = A / c * 1e4; f['a_atr5x14'] = P['st_atr5'][i] / A; f['a_atr14x50'] = A / P['st_atr50'][i]
    f['a_atrXtr100'] = A / P['st_trs100'][i]; f['a_atrXtr288'] = A / P['st_trs288'][i]
    f['a_atrX10'] = A / P[('atr', 14)][i - 10]; f['a_atrX1'] = A / P[('atr', 14)][i - 1]
    f['a_sd20A'] = P['st_sd20'][i] / A
    f['a_bbPos'] = d * (c - P['st_sma20'][i]) / (2 * P['st_sd20'][i]) if P['st_sd20'][i] else 0.0
    # ---------- DMI / oscillators
    for L_ in (7, 14, 28):
        dip, dim, adx = P[('st_dmi', L_)]
        f[f'a_adx{L_}'] = adx[i]; f[f'a_di{L_}'] = d * (dip[i] - dim[i]); f[f'a_diSame{L_}'] = dip[i] if d > 0 else dim[i]
        f[f'a_diOpp{L_}'] = dim[i] if d > 0 else dip[i]; f[f'a_adxSl{L_}'] = adx[i] - adx[i - 5]
        f[f'b_adx{L_}'] = adx[i - 1]; f[f'b_di{L_}'] = d * (dip[i - 1] - dim[i - 1])
    r = P[('st_rsi', 14)][i]; f['a_rsi'] = r if d > 0 else 100 - r
    f['a_macdhA'] = d * P['st_macdh'][i] / A
    for n in (9, 20, 50, 100, 200):
        e = P[('st_ema', n)]; f[f'a_ema{n}A'] = d * (c - e[i]) / A
        f[f'a_ema{n}slA'] = d * (e[i] - e[i - 5]) / A
    f['a_ema50x200A'] = d * (P[('st_ema', 50)][i] - P[('st_ema', 200)][i]) / A
    f['a_ema20x50A'] = d * (P[('st_ema', 20)][i] - P[('st_ema', 50)][i]) / A
    # ---------- volume (recovered relative volume)
    vol = P['vol']; vv = lambda k: vol[k] if vol[k] is not None else 0.0
    for n in (5, 10, 20, 50):
        m = sum(vv(k) for k in range(i - n, i)) / n
        f[f'a_rvol{n}'] = vv(i) / m if m > 0 else 0.0
    ss = i - P['sinceStart'][i]; tot = sum(vv(k) for k in range(ss, i + 1))
    f['a_volShare'] = vv(i) / tot if tot > 0 else 0.0
    f['b_rvol10'] = vv(i - 1) / (sum(vv(k) for k in range(i - 11, i - 1)) / 10 or 1)
    # ---------- time
    hh, mm = int(T[i][11:13]), int(T[i][14:16]); f['t_ist'] = hh + mm / 60.0
    f['t_utc'] = (f['t_ist'] - 5.5) % 24; f['t_dowutc'] = P['dowutc'][i]
    import datetime as dt
    f['t_dowist'] = dt.datetime.strptime(T[i][:10], '%Y-%m-%d').weekday()
    f['t_since'] = P['sinceStart'][i]
    # ---------- session / previous session (raw and merged sessions)
    for tag, merge in (('', False), ('m', True)):
        S, idx = sessions(P, merge); k = idx[i]; a, b = S[k]
        so = O[a]; sh = max(H[a:i + 1]); sl = min(L[a:i + 1]); shx = max(H[a:i]) if i > a else h; slx = min(L[a:i]) if i > a else l
        f[f's{tag}_since'] = i - a
        f[f's{tag}_openA'] = d * (c - so) / A
        f[f's{tag}_rngA'] = (sh - sl) / A
        f[f's{tag}_pos'] = ((c - sl) / (sh - sl) if d > 0 else (sh - c) / (sh - sl)) if sh > sl else 0.5
        f[f's{tag}_favExA'] = d * ((shx if d > 0 else slx) - c) / A    # room to the prior session extreme (neg = new extreme)
        f[f's{tag}_advExA'] = d * (c - (slx if d > 0 else shx)) / A
        if k >= 1:
            pa, pb = S[k - 1]; po, pc = O[pa], C[pb - 1]; ph, pl = max(H[pa:pb]), min(L[pa:pb])
            f[f's{tag}_pdBodyA'] = d * (pc - po) / A; f[f's{tag}_pdRngA'] = (ph - pl) / A
            f[f's{tag}_pdClosePos'] = ((pc - pl) / (ph - pl) if d > 0 else (ph - pc) / (ph - pl)) if ph > pl else 0.5
            f[f's{tag}_pdBodyFrac'] = d * (pc - po) / (ph - pl) if ph > pl else 0.0
            f[f's{tag}_vsPdcA'] = d * (c - pc) / A; f[f's{tag}_vsPdoA'] = d * (c - po) / A
            f[f's{tag}_vsPdFavA'] = d * (c - (ph if d > 0 else pl)) / A; f[f's{tag}_vsPdAdvA'] = d * (c - (pl if d > 0 else ph)) / A
            f[f's{tag}_gapA'] = d * (so - pc) / A
            f[f's{tag}_pdVwA'] = d * (pc - V[pb - 1]) / A if V[pb - 1] is not None else 0.0
            f[f's{tag}_pdLen'] = pb - pa
            f[f's{tag}_vsPdVwA'] = d * (c - V[pb - 1]) / A if V[pb - 1] is not None else 0.0
        else:
            for nm in ('pdBodyA', 'pdRngA', 'pdClosePos', 'pdBodyFrac', 'vsPdcA', 'vsPdoA', 'vsPdFavA', 'vsPdAdvA', 'gapA', 'pdVwA', 'pdLen', 'vsPdVwA'):
                f[f's{tag}_{nm}'] = float('nan')
        if k >= 2:
            qa, qb = S[k - 2]; pa, pb = S[k - 1]
            f[f's{tag}_pd2BodyA'] = d * (C[pb - 1] - O[qa]) / A
            f[f's{tag}_ppdBodyA'] = d * (C[qb - 1] - O[qa]) / A
        else:
            f[f's{tag}_pd2BodyA'] = f[f's{tag}_ppdBodyA'] = float('nan')
        # ---------- signal sequence within the session (stateless)
        for nm in ('core', 'vsl', 'full', 'arm'):
            sg = sigs(P, nm)
            ns = sum(1 for j in range(a, i) if sg[j] == d); no = sum(1 for j in range(a, i) if sg[j] == -d)
            f[f'q{tag}_{nm}Same'] = ns; f[f'q{tag}_{nm}Opp'] = no
            last = 0
            for j in range(i - 1, a - 1, -1):
                if sg[j]: last = 1 if sg[j] == d else -1; break
            f[f'q{tag}_{nm}Last'] = last
            if k >= 1:
                pa, pb = S[k - 1]
                f[f'q{tag}_{nm}PdNet'] = sum(sg[j] for j in range(pa, pb)) * d
            else:
                f[f'q{tag}_{nm}PdNet'] = float('nan')
    for nm in ('core', 'vsl', 'full', 'arm'):
        sg = sigs(P, nm)
        bs = next((k for k in range(1, 3000) if i - k >= 0 and sg[i - k] == d), 3000)
        bo = next((k for k in range(1, 3000) if i - k >= 0 and sg[i - k] == -d), 3000)
        f[f'q_{nm}BarsSame'] = bs; f[f'q_{nm}BarsOpp'] = bo
        f[f'q_{nm}Same48'] = sum(1 for j in range(i - 48, i) if sg[j] == d); f[f'q_{nm}Opp48'] = sum(1 for j in range(i - 48, i) if sg[j] == -d)
    # ---------- bar before
    o1, h1, l1, c1 = O[i - 1], H[i - 1], L[i - 1], C[i - 1]; r1 = h1 - l1
    f['b_rngA'] = r1 / A; f['b_bodyA'] = d * (c1 - o1) / A
    f['b_closePos'] = (((c1 - l1) / r1) if d > 0 else ((h1 - c1) / r1)) if r1 > 0 else 0.5
    f['b_vwA'] = d * (c1 - V[i - 1]) / A if V[i - 1] is not None else 0.0
    f['b_mom1A'] = d * (c1 - C[i - 2]) / A
    f['b_sig'] = sigs(P, 'core')[i - 1] * d
    f['b_brk10A'] = d * (c1 - (max(H[i - 11:i - 1]) if d > 0 else min(L[i - 11:i - 1]))) / A
    f['b_favWickA'] = d * ((h1 if d > 0 else l1) - (max(o1, c1) if d > 0 else min(o1, c1))) / A
    f['b_advWickA'] = d * ((min(o1, c1) if d > 0 else max(o1, c1)) - (l1 if d > 0 else h1)) / A
    # ---------- entry geometry
    mid = (o + c) / 2; lvl = max(H[i - 6:i]) if d > 0 else min(L[i - 6:i])
    f['a_entMid'] = 1.0 if d * (mid - lvl) >= 0 else 0.0
    f['a_entOffA'] = d * (entry - mid) / A; f['a_closeEntA'] = d * (c - entry) / A
    f['a_entAdvA'] = d * (entry - adv) / A     # distance entry -> displacement extreme
    f['a_entOpenA'] = d * (entry - o) / A
    # ---------- fill bar
    if fi is not None:
        of, hf, lf, cf = O[fi], H[fi], L[fi], C[fi]; Af = P[('atr', 14)][fi]
        f['f_bars'] = fi - i; f['f_openEntA'] = d * (of - entry) / A
        f['f_penA'] = d * (entry - (lf if d > 0 else hf)) / A; f['f_rngA'] = (hf - lf) / A
        f['f_closeEntA'] = d * (cf - entry) / A; f['f_vwA'] = d * (cf - V[fi]) / A if V[fi] is not None else 0.0
        f['f_atrX'] = Af / A; f['f_gapA'] = d * (of - C[fi - 1]) / A
        f['f_entVwA'] = d * (entry - V[fi]) / A if V[fi] is not None else 0.0
        f['f_prevCloseEntA'] = d * (C[fi - 1] - entry) / A
        f['f_runA'] = d * ((max(H[i + 1:fi + 1]) if d > 0 else min(L[i + 1:fi + 1])) - c) / A if fi > i else 0.0
        f['f_since'] = P['sinceStart'][fi]; f['f_newSess'] = 1.0 if fi - P['sinceStart'][fi] > i else 0.0
        f['f_bodyA'] = d * (cf - of) / A
    return f


def build():
    from tightdata import TRADES
    from gtscore import load_gt, covered
    from engine2 import run
    BEST = {"brkLen": 10, "entryLen": 6, "bodyPct": 55, "closePct": 25, "maxDayR": 3, "vsLag": 3, "noSunUTC": 1, "momMin": 0.85,
            "roundLevels": False, "rearm": "samedir", "minBars": 1}
    tr, win = load_gt(os.path.join(FIT, '..', 'gt', 'final'))
    eng = {}
    out = []
    for t in TRADES:
        P = base(t['sym']); i = t['arm_i']; d = t['d']
        f = feats(P, i, d, t['entry'], t['fill_i'])
        T = P['T']; idx = {x: k for k, x in enumerate(T)}
        # ---- teacher-forced original-trade history (same symbol)
        G = sorted([g for g in tr if g['sym'] == t['sym'] and g['fill'] in idx], key=lambda g: g['fill'])
        prev = [g for g in G if g['fill'] < t['fill']]
        S, sidx = sessions(P, False); a = S[sidx[i]][0]
        res = lambda g: 2.0 if g.get('out') == 'tp4' else (-1.0 if g.get('out') == 'stop' else 0.0)
        if prev:
            p = prev[-1]; px = idx.get(p['exit']) if p.get('exit') else None
            f['g_prevRes'] = res(p); f['g_prevSame'] = 1.0 if p['d'] == d else 0.0
            f['g_prevGap'] = (i - px) if px is not None else 3000
            f['g_prevSameSess'] = 1.0 if idx[p['fill']] >= a else 0.0
            f['g_prevResSigned'] = res(p) * (1 if p['d'] == d else -1)
            cont = all(covered(win, t['sym'], T[k]) for k in range(idx[p['fill']], i + 1, 6))
            f['g_contig'] = 1.0 if cont else 0.0
        else:
            f['g_prevRes'] = 0.0; f['g_prevSame'] = 0.5; f['g_prevGap'] = 3000; f['g_prevSameSess'] = 0.0; f['g_prevResSigned'] = 0.0; f['g_contig'] = 0.0
        f['g_prev2Res'] = res(prev[-2]) if len(prev) >= 2 else 0.0
        f['g_nSess'] = sum(1 for g in prev if idx[g['fill']] >= a)
        f['g_rSess'] = sum(res(g) for g in prev if idx[g['fill']] >= a)
        f['g_n'] = len(prev)
        # ---- in-engine state of the best model at bar i
        if t['sym'] not in eng: eng[t['sym']] = run(P, BEST)
        E = eng[t['sym']]
        done = [m for m in E if m['exit'] is not None and m['exit'] < i]
        f['e_dayFills'] = sum(1 for m in E if a <= m['fill'] < i)
        f['e_dayR'] = sum(m['res'] for m in done if m['exit'] >= a)
        if done:
            m = done[-1]; f['e_lastRes'] = m['res']; f['e_lastGap'] = i - m['exit']; f['e_lastSame'] = 1.0 if m['dir'] == d else 0.0
            f['e_lastSameSess'] = 1.0 if m['exit'] >= a else 0.0
        else:
            f['e_lastRes'] = 0.0; f['e_lastGap'] = 3000; f['e_lastSame'] = 0.5; f['e_lastSameSess'] = 0.0
        f['e_armed'] = 1.0 if any(m['arm'] == i for m in E) else 0.0
        out.append((t, f))
    pickle.dump(out, open(os.path.join(HERE, 'feat.pkl'), 'wb'))
    return out


if __name__ == '__main__':
    out = build()
    print(len(out), 'trades', len(out[0][1]), 'features')
    import collections
    nan = collections.Counter(k for _, f in out for k, v in f.items() if v != v)
    print('nan counts', dict(nan))
