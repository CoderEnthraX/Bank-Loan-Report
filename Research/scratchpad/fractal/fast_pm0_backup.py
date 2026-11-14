"""Fast evaluator for the settings search: the same rules as engine.sim, computed from first passages.
Entries (breakouts) do not depend on the exits: every level is used up by its first up-cross (a trade opens only when flat), so the
breakout events are listed once per (fractal TF, right, left, offset). For each event the first passage of every grid level after the
fill is found once (block skips over the M1 bars), then every exit combination is a race between those passages plus the one-position-
at-a-time pass. Positions on the path: key = bar * 4 + sub, sub 0 = the open (gap), 1..3 = the bar's three path segments."""
import numpy as np, numba as nb
INF = np.int64(1) << 62


@nb.njit(cache=True)
def blocks(H, L):
    n = len(H); nb1 = (n + 63) >> 6; nb2 = (n + 4095) >> 12
    BH1 = np.full(nb1, -np.inf); BL1 = np.full(nb1, np.inf); BH2 = np.full(nb2, -np.inf); BL2 = np.full(nb2, np.inf)
    for k in range(n):
        if H[k] > BH1[k >> 6]: BH1[k >> 6] = H[k]
        if L[k] < BL1[k >> 6]: BL1[k >> 6] = L[k]
        if H[k] > BH2[k >> 12]: BH2[k >> 12] = H[k]
        if L[k] < BL2[k >> 12]: BL2[k >> 12] = L[k]
    return BH1, BL1, BH2, BL2


@nb.njit(cache=True)
def next_up(H, BH1, BH2, j, u):
    n = len(H); k = j + 1
    while k < n:
        if (k & 4095) == 0 and BH2[k >> 12] < u:
            k += 4096; continue
        if (k & 63) == 0 and BH1[k >> 6] < u:
            k += 64; continue
        if H[k] >= u:
            return k
        k += 1
    return n


@nb.njit(cache=True)
def next_dn(L, BL1, BL2, j, d):
    n = len(L); k = j + 1
    while k < n:
        if (k & 4095) == 0 and BL2[k >> 12] > d:
            k += 4096; continue
        if (k & 63) == 0 and BL1[k >> 6] > d:
            k += 64; continue
        if L[k] <= d:
            return k
        k += 1
    return n


@nb.njit(cache=True)
def seg(o, h, l, c, s):
    """start and end price of path segment s (1..3) of a bar"""
    if (h - o) < (o - l):
        a = h; b = l
    else:
        a = l; b = h
    if s == 1:
        return o, a
    if s == 2:
        return a, b
    return b, c


@nb.njit(cache=True)
def fp_up(O, H, L, C, BH1, BH2, j, s, u):
    """first position after (bar j, sub s) - the point lies on segment s (or at the open for s = 0) and below u - where the price is
    >= u. Returns (key, fill price); key INF if never."""
    n = len(O)
    if s >= 1:
        x, y = seg(O[j], H[j], L[j], C[j], s)
        if y > x and y >= u:
            return j * 4 + s, u
    for s2 in range(s + 1, 4):
        x, y = seg(O[j], H[j], L[j], C[j], s2)
        if y > x and y >= u:
            return j * 4 + s2, u
    k = next_up(H, BH1, BH2, j, u)
    if k >= n:
        return INF, 0.0
    if O[k] >= u:
        return k * 4, O[k]
    return k * 4 + (1 if (H[k] - O[k]) < (O[k] - L[k]) else 2), u


@nb.njit(cache=True)
def fp_dn(O, H, L, C, BL1, BL2, j, s, d):
    n = len(O)
    if s >= 1:
        x, y = seg(O[j], H[j], L[j], C[j], s)
        if y < x and y <= d:
            return j * 4 + s, d
    for s2 in range(s + 1, 4):
        x, y = seg(O[j], H[j], L[j], C[j], s2)
        if y < x and y <= d:
            return j * 4 + s2, d
    k = next_dn(L, BL1, BL2, j, d)
    if k >= n:
        return INF, 0.0
    if O[k] <= d:
        return k * 4, O[k]
    return k * 4 + (1 if not ((H[k] - O[k]) < (O[k] - L[k])) else 2), d


@nb.njit(cache=True)
def events(O, H, L, C, kk, ph, off):
    """every breakout: the level's first up-cross (the level logic of engine.sim without positions). Returns bar, sub, fill price, level."""
    n = len(O); ej = np.empty(n // 2 + 10, np.int64); es = np.empty(n // 2 + 10, np.int64); eF = np.empty(n // 2 + 10); eH = np.empty(n // 2 + 10)
    m = 0; lvlOn = False; E = 0.0; lvlH = 0.0; prevC = np.nan
    for i in range(n):
        lvlNew = False
        if i == 0 or kk[i] != kk[i - 1]:
            v = ph[kk[i]]
            if not np.isnan(v):
                lvlOn = True; lvlH = v; E = v * (1.0 + off / 100.0); lvlNew = True
        o = O[i]
        if lvlOn and not lvlNew and prevC < E and o >= E:
            ej[m] = i; es[m] = 0; eF[m] = o; eH[m] = lvlH; m += 1; lvlOn = False
        if lvlOn:
            for s in range(1, 4):
                x, y = seg(o, H[i], L[i], C[i], s)
                if y > x and x < E and E <= y:
                    ej[m] = i; es[m] = s; eF[m] = E; eH[m] = lvlH; m += 1; lvlOn = False
                    break
        prevC = C[i]
    return ej[:m], es[:m], eF[:m], eH[:m]


@nb.njit(cache=True)
def passages(O, H, L, C, BH1, BL1, BH2, BL2, ej, es, eF, ups, dns, bes, svs):
    """per event: first passage of F (1 + u%) for u in ups, F (1 - d%) for d in dns; for each BE level b (index into ups via bes) the
    first price <= F after its trigger; for each salvage level (index into dns via svs) the first price >= F after its trigger."""
    m = len(ej); nu = len(ups); nd = len(dns)
    KU = np.empty((m, nu), np.int64); XU = np.empty((m, nu)); KD = np.empty((m, nd), np.int64); XD = np.empty((m, nd))
    KB = np.empty((m, len(bes)), np.int64); XB = np.empty((m, len(bes))); KS = np.empty((m, len(svs)), np.int64); XS = np.empty((m, len(svs)))
    for e in range(m):
        j = ej[e]; s = es[e]; F = eF[e]
        for q in range(nu):
            KU[e, q], XU[e, q] = fp_up(O, H, L, C, BH1, BH2, j, s, F * (1.0 + ups[q] / 100.0))
        for q in range(nd):
            KD[e, q], XD[e, q] = fp_dn(O, H, L, C, BL1, BL2, j, s, F * (1.0 - dns[q] / 100.0))
        for q in range(len(bes)):
            k = KU[e, bes[q]]
            if k >= INF:
                KB[e, q] = INF; XB[e, q] = 0.0
            else:
                KB[e, q], XB[e, q] = fp_dn(O, H, L, C, BL1, BL2, k >> 2, k & 3, F)
        for q in range(len(svs)):
            k = KD[e, svs[q]]
            if k >= INF:
                KS[e, q] = INF; XS[e, q] = 0.0
            else:
                KS[e, q], XS[e, q] = fp_up(O, H, L, C, BH1, BH2, k >> 2, k & 3, F)
    return KU, XU, KD, XD, KB, XB, KS, XS


@nb.njit(cache=True)
def outcome(e, iT, iS, iB, iV, KU, XU, KD, XD, KB, XB, KS, XS, upsB, dnsV):
    """exit of event e for TP = ups[iT], SL = dns[iS], BE = ups[upsB[iB]] (iB < 0: off), salvage = dns[dnsV[iV]] (iV < 0: off).
    Returns (key, price, reason 1 TP / 2 SL / 3 BE / 4 SALV, up-move exit)."""
    kT = KU[e, iT]; kS = KD[e, iS]
    kB = KU[e, upsB[iB]] if iB >= 0 else INF
    kV = KD[e, dnsV[iV]] if iV >= 0 else INF
    beF = kB < kT                    # the BE trigger comes strictly before the TP (same segment: the TP is reached too)
    svF = kV < kS                    # the salvage trigger comes strictly before the SL
    fu = kB if beF else kT
    fd = kV if svF else kS
    if fu >= INF and fd >= INF:
        return INF, 0.0, 0, False
    if fu < fd:
        if beF:
            kb = KB[e, iB]
            if kT < kb:
                return kT, XU[e, iT], 1, True
            if kb >= INF:
                return INF, 0.0, 0, False
            return kb, XB[e, iB], 3, False
        return kT, XU[e, iT], 1, True
    if svF:
        ks = KS[e, iV]
        if kS < ks:
            return kS, XD[e, iS], 2, False
        if ks >= INF:
            return INF, 0.0, 0, False
        return ks, XS[e, iV], 4, True
    return kS, XD[e, iS], 2, False


@nb.njit(cache=True)
def trades_one(ej, es, eF, iT, iS, iB, iV, KU, XU, KD, XD, KB, XB, KS, XS, upsB, dnsV, out):
    """the one-position-at-a-time pass for one exit combination; rows: event, exit key, exit price, reason"""
    m = len(ej); nt = 0; lastK = np.int64(-1); lastX = 0.0; lastUp = False
    for e in range(m):
        ke = ej[e] * 4 + es[e]
        if ke < lastK:
            continue
        if ke == lastK and not (es[e] == 0 or (lastUp and eF[e] >= lastX)):
            continue
        k, X, r, up = outcome(e, iT, iS, iB, iV, KU, XU, KD, XD, KB, XB, KS, XS, upsB, dnsV)
        if k >= INF:
            break
        out[nt, 0] = e; out[nt, 1] = k; out[nt, 2] = X; out[nt, 3] = r; nt += 1
        lastK = k; lastX = X; lastUp = up
    return nt


@nb.njit(cache=True, parallel=False)
def grid(ej, es, eF, eyr, KU, XU, KD, XD, KB, XB, KS, XS, ups, dns, upsB, dnsV, tps, sls, bes_i, svs_i, cost, ny, ysplit=3):
    """stats for every combination (tps x sls x bes_i x svs_i, indices; -1 = off). Per combo: [n, sumR, ddR, gross win R, gross loss R,
    max losing streak, wins] for the whole period and per year (sumR, n, ddR) for years 0..ny-1 (eyr = year index of each event)."""
    nc = len(tps) * len(sls) * len(bes_i) * len(svs_i)
    res = np.zeros((nc, 9 + 3 * ny)); c = 0     # + train / test drawdown (years < ysplit / >= ysplit) at columns 7 + 3 ny, 8 + 3 ny
    m = len(ej)
    for a in range(len(tps)):
        for b in range(len(sls)):
            for g in range(len(bes_i)):
                for h in range(len(svs_i)):
                    iT = tps[a]; iS = sls[b]; iB = bes_i[g]; iV = svs_i[h]
                    slp = dns[iS] / 100.0
                    lastK = np.int64(-1); lastX = 0.0; lastUp = False
                    cum = 0.0; peak = 0.0; dd = 0.0; st = 0; mst = 0
                    ycum = np.zeros(ny); ypk = np.zeros(ny); hc = np.zeros(2); hp = np.zeros(2); hd = np.zeros(2)
                    for e in range(m):
                        ke = ej[e] * 4 + es[e]
                        if ke < lastK:
                            continue
                        if ke == lastK and not (es[e] == 0 or (lastUp and eF[e] >= lastX)):
                            continue
                        k, X, r, up = outcome(e, iT, iS, iB, iV, KU, XU, KD, XD, KB, XB, KS, XS, upsB, dnsV)
                        if k >= INF:
                            break
                        F = eF[e]; R = (X - F - cost) / (F * slp)
                        res[c, 0] += 1; res[c, 1] += R
                        if R > 0:
                            res[c, 3] += R; res[c, 6] += 1; st = 0
                        else:
                            res[c, 4] -= R; st += 1
                            if st > mst: mst = st
                        cum += R
                        if cum > peak: peak = cum
                        if peak - cum > dd: dd = peak - cum
                        y = eyr[e]
                        res[c, 7 + 3 * y] += R; res[c, 8 + 3 * y] += 1
                        ycum[y] += R
                        if ycum[y] > ypk[y]: ypk[y] = ycum[y]
                        if ypk[y] - ycum[y] > res[c, 9 + 3 * y]: res[c, 9 + 3 * y] = ypk[y] - ycum[y]
                        hh = 0 if y < ysplit else 1
                        hc[hh] += R
                        if hc[hh] > hp[hh]: hp[hh] = hc[hh]
                        if hp[hh] - hc[hh] > hd[hh]: hd[hh] = hp[hh] - hc[hh]
                        lastK = k; lastX = X; lastUp = up
                    res[c, 2] = dd; res[c, 5] = mst; res[c, 7 + 3 * ny] = hd[0]; res[c, 8 + 3 * ny] = hd[1]
                    c += 1
    return res
