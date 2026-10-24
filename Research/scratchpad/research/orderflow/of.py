"""Order-flow proxies from reconstructed relative volume (no bid/ask data: delta is APPROXIMATED from bar shape).
All per-bar features at index i use only bars <= i of the same session (causal). First (partial) session of a file -> None."""
import sys, math
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/fit')
from engine import prepare as eprep, rma
_c = {}

def weights(sym):
    """relative volume per bar (vs first bar of its session) backed out of the CSV session VWAP; VWAP unchanged -> 0 volume."""
    P = eprep(sym); R = P['rows']; D = P['daystart']; n = len(R); w = [1.0] * n; W = 0.0
    for i, r in enumerate(R):
        hl = (r['h'] + r['l'] + r['c']) / 3
        if D[i] or r['vwap'] is None or i == 0 or R[i - 1]['vwap'] is None: w[i] = 1.0; W = 1.0; continue
        den = hl - R[i - 1]['vwap']; num = r['vwap'] - R[i - 1]['vwap']
        if abs(num) <= 1e-9 * abs(hl): wi = 0.0                           # VWAP did not move -> zero-volume bar
        elif abs(den) <= 1e-7 * abs(hl): wi = W * 0.01
        else:
            rr = num / den
            wi = W * rr / (1 - rr) if 0 < rr < 1 else W * 0.01
        w[i] = wi; W += wi
    return P, w

def features(sym):
    if sym in _c: return _c[sym]
    P, w = weights(sym); R = P['rows']; D = P['daystart']; n = len(R)
    O = [r['o'] for r in R]; H = [r['h'] for r in R]; L = [r['l'] for r in R]; C = [r['c'] for r in R]; V = [r['vwap'] for r in R]
    A = rma(P['tr'], 14)
    sess = [0] * n; s = -1; sst = [0] * n
    for i in range(n):
        if D[i]: s += 1; st0 = i
        sess[i] = s; sst[i] = st0 if s >= 0 else 0
    valid = [sess[i] >= 1 for i in range(n)]              # skip the first partial session
    clv = [((2 * C[i] - H[i] - L[i]) / (H[i] - L[i])) if H[i] > L[i] else 0.0 for i in range(n)]
    sgn = lambda x: (x > 0) - (x < 0)
    dCLV = [w[i] * clv[i] for i in range(n)]
    dOC = [w[i] * sgn(C[i] - O[i]) for i in range(n)]
    dTick = [w[i] * (sgn(C[i] - C[i - 1]) if i and not D[i] else sgn(C[i] - O[i])) for i in range(n)]
    # session cumulative volume / deltas, VWAP variance (volume weighted)
    cw = [0.0] * n; cd = {k: [0.0] * n for k in ('clv', 'oc', 'tick')}; sd = [None] * n
    sw = s1 = s2 = 0.0; acc = {'clv': 0.0, 'oc': 0.0, 'tick': 0.0}
    for i in range(n):
        if D[i]: sw = s1 = s2 = 0.0; acc = {'clv': 0.0, 'oc': 0.0, 'tick': 0.0}
        tp = (H[i] + L[i] + C[i]) / 3
        sw += w[i]; s1 += w[i] * tp; s2 += w[i] * tp * tp
        acc['clv'] += dCLV[i]; acc['oc'] += dOC[i]; acc['tick'] += dTick[i]
        cw[i] = sw
        for k in acc: cd[k][i] = acc[k]
        if sw > 0:
            m = s1 / sw; var = max(s2 / sw - m * m, 0.0); sd[i] = math.sqrt(var)
    # relative volume: vs mean of previous N bars of the same session
    def rvN(i, N):
        a = max(sst[i], i - N)
        if i - a < min(N, 5) or not valid[i]: return None
        m = sum(w[a:i]) / (i - a)
        return w[i] / m if m > 0 else None
    # time-of-day profile: u(t) = median over up to 10 prior sessions of w/sessionMedian
    import statistics as stt
    sessions = []
    for i in range(n):
        if D[i]: sessions.append([i, i])
        elif sessions: sessions[-1][1] = i
    tkey = [R[i]['t'][11:16] for i in range(n)]
    rvT = [None] * n; hist = []   # list of dict tkey->norm w for completed sessions
    for si, (a, b) in enumerate(sessions):
        prof = {}
        for h in hist[-10:]:
            for k, v in h.items(): prof.setdefault(k, []).append(v)
        u = {k: stt.median(v) for k, v in prof.items() if len(v) >= 3}
        lev = []
        for i in range(a, b + 1):
            ui = u.get(tkey[i])
            if ui and ui > 0:
                if len(lev) >= 3 and valid[i]:
                    lv = stt.median(lev); rvT[i] = (w[i] / ui) / lv if lv > 0 else None
                lev.append(w[i] / ui)
        ws = [w[i] for i in range(a, b + 1) if w[i] > 0]
        md = stt.median(ws) if ws else 0
        if si >= 1 and md > 0: hist.append({tkey[i]: w[i] / md for i in range(a, b + 1)})
    # equal-weight (no volume) session sigma of hlc3 around the CSV VWAP, robustness check of the volume-weighted bands
    sdT = [None] * n; k0 = q1 = q2 = 0.0
    for i in range(n):
        if D[i]: k0 = q1 = q2 = 0.0
        tp = (H[i] + L[i] + C[i]) / 3; k0 += 1; q1 += tp; q2 += tp * tp
        if V[i] is not None: sdT[i] = math.sqrt(max(q2 / k0 - 2 * V[i] * q1 / k0 + V[i] * V[i], 0.0))
    F = dict(P=P, w=w, sdT=sdT, O=O, H=H, L=L, C=C, V=V, A=A, D=D, sst=sst, valid=valid, clv=clv, dCLV=dCLV, dOC=dOC, dTick=dTick,
             cw=cw, cd=cd, sd=sd, rvN=rvN, rvT=rvT)
    _c[sym] = F; return F

def vprofile(F, i, binAtr=0.25):
    """session-so-far volume profile up to bar i (inclusive). Returns (poc, vah, val, vol_at(price)->share of POC volume)."""
    a = F['sst'][i]; A0 = F['A'][a] or F['A'][i]; bs = binAtr * (A0 or 1.0)
    H, L, w = F['H'], F['L'], F['w']; bins = {}
    for j in range(a, i + 1):
        lo = math.floor(L[j] / bs); hi = math.floor(H[j] / bs); k = hi - lo + 1
        for b in range(lo, hi + 1): bins[b] = bins.get(b, 0.0) + w[j] / k
    tot = sum(bins.values())
    if tot <= 0: return None
    pb = max(bins, key=bins.get); lo = hi = pb; acc = bins[pb]
    while acc < 0.7 * tot:
        up = bins.get(hi + 1, 0.0); dn = bins.get(lo - 1, 0.0)
        if up == 0 and dn == 0 and (hi + 1 > max(bins)) and (lo - 1 < min(bins)): break
        if up >= dn: hi += 1; acc += up
        else: lo -= 1; acc += dn
    pv = bins[pb]
    return dict(poc=(pb + 0.5) * bs, vah=(hi + 1) * bs, val=lo * bs, at=lambda p: bins.get(math.floor(p / bs), 0.0) / pv)

def sig_features(F, i, d, entry=None, structLen=10):
    """features at signal bar i for direction d (+1 long/-1 short); positive values = 'in trade direction' where it applies."""
    if not F['valid'][i] or i - F['sst'][i] < 3: return None
    H, L, C, O, w, A, V = F['H'], F['L'], F['C'], F['O'], F['w'], F['A'][i], F['V']
    a = F['sst'][i]; rng = H[i] - L[i]
    x = {}
    import random as _r
    for sd_ in range(40): x['rand%d' % sd_] = _r.Random('%s:%d:%d' % (F['P']['sym'], i, sd_)).random()   # random-veto control
    x['rv10'] = F['rvN'](i, 10); x['rv20'] = F['rvN'](i, 20); x['rvS'] = F['rvN'](i, 10 ** 6); x['rvT'] = F['rvT'][i]
    # aggression: delta of the signal bar and of the last 3 bars, as share of their volume
    for k in ('clv', 'oc', 'tick'):
        dd = F['d' + {'clv': 'CLV', 'oc': 'OC', 'tick': 'Tick'}[k]]
        b3 = max(a, i - 2); v3 = sum(w[b3:i + 1])
        x['agg3_' + k] = d * sum(dd[b3:i + 1]) / v3 if v3 > 0 else None
        # CVD (session) normalised by session volume; slope over 10 bars; divergence vs prior 10-bar CVD extreme
        cv = F['cd'][k]; cw = F['cw'][i]
        x['cvd_' + k] = d * cv[i] / cw if cw > 0 else None
        b10 = max(a, i - 10); v10 = sum(w[b10 + 1:i + 1])
        x['cvdslope_' + k] = d * (cv[i] - cv[b10]) / v10 if v10 > 0 and i - b10 >= 3 else None
        if i - a >= structLen:
            prior = cv[i - structLen:i]; ext = max(prior) if d > 0 else min(prior)
            x['cvddiv_' + k] = d * (cv[i] - ext) / (sum(w[i - structLen:i + 1]) / (structLen + 1)) if sum(w[i - structLen:i + 1]) > 0 else None
        else: x['cvddiv_' + k] = None
    # effort vs result at the signal bar (absorption): relative volume per ATR of range
    x['effort'] = x['rv20'] / (rng / A) if x['rv20'] is not None and rng > 0 else None
    # absorption before the signal: bars in the last 5 that probed the breakout level with heavy volume and an opposite wick
    lvl = max(H[i - structLen:i]) if d > 0 else min(L[i - structLen:i])
    ab = 0.0; ab2 = 0.0
    for j in range(max(a + 1, i - 5), i):
        rj = H[j] - L[j]
        if rj <= 0: continue
        near = (abs(H[j] - lvl) <= 0.25 * A) if d > 0 else (abs(L[j] - lvl) <= 0.25 * A)
        wick = ((H[j] - max(O[j], C[j])) if d > 0 else (min(O[j], C[j]) - L[j])) / rj
        rvj = F['rvN'](j, 20)
        if near and rvj is not None:
            ab = max(ab, rvj * wick); ab2 = max(ab2, rvj / max(rj / A, 0.2))
    x['absorbWick'] = ab; x['absorbER'] = ab2
    # opposite wick of the signal bar weighted by its relative volume
    owk = ((H[i] - C[i]) if d > 0 else (C[i] - L[i])) / rng if rng > 0 else 0
    x['sigWickVol'] = owk * x['rv20'] if x['rv20'] is not None else None
    # exhaustion: extension of the run and climax volume
    lo20 = min(L[max(a, i - 20):i + 1]) if d > 0 else max(H[max(a, i - 20):i + 1])
    x['run20'] = d * (C[i] - lo20) / A
    x['vwapExt'] = d * (C[i] - V[i]) / A
    rvmax = 0.0
    for j in range(max(a + 1, i - 2), i + 1):
        r = F['rvN'](j, 20)
        if r is not None: rvmax = max(rvmax, r)
    x['rvmax3'] = rvmax
    # VWAP bands
    sd = F['sd'][i]
    x['z'] = d * (C[i] - V[i]) / sd if sd else None
    x['zT'] = d * (C[i] - V[i]) / F['sdT'][i] if F['sdT'][i] else None
    if entry is not None:
        x['zEntry'] = d * (entry - V[i]) / sd if sd else None
    # volume profile
    vp = vprofile(F, i)
    if vp:
        ref = entry if entry is not None else C[i]
        x['pocDist'] = d * (ref - vp['poc']) / A
        x['vaPos'] = d * (ref - (vp['vah'] if d > 0 else vp['val'])) / A    # >0: entry beyond the value area in trade direction
        x['node'] = vp['at'](ref)
        x['sigNode'] = vp['at'](C[i])
    return x
