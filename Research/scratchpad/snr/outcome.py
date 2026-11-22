"""Outcomes of Sniper signals on M1 (the minute after the signal bar onwards): a minute that touches the stop is a loss (stop first; a gap
through the stop loses from the open), otherwise its high / low adds to the best excursion; the scan ends at the stop, at 3R, or (force
close) at 23:55 IST. Limit entries wait for a touch for the retest window (5 chart bars) and the fill minute only checks the stop.
Costs 0.23 per oz (spread 0.16 + $7 a lot): a win at X R nets (X r - 0.23) / (r + 0.23), a stop -1 (or the gap loss)."""
import numpy as np, numba as nb, datetime as dt
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
LEVELS = np.array([0.1, 0.2, 0.3, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0])
COST = 0.23
TEST0 = int(dt.datetime(2024, 1, 1, tzinfo=dt.timezone.utc).timestamp())
_M1 = {}


def m1():
    if not _M1:
        d = dict(np.load(S + '/snr/m1.npz'))
        u = d['utc']
        # force close: the first minute at / after the next 23:55 IST (18:25 UTC) after each minute
        ist = u + 19800
        day = ist // 86400
        cut_t = day * 86400 + (23 * 60 + 55) * 60
        cut_t = np.where(ist % 86400 >= (23 * 60 + 55) * 60, cut_t + 86400, cut_t) - 19800
        d['fc'] = np.searchsorted(u, cut_t)
        _M1.update(d)
    return _M1


@nb.njit(cache=True)
def scan(O, H, L, C, FC, js, dirs, ents, stps, lim, wait, usecut, cap):
    n = len(js); N = len(O)
    mfe = np.full(n, np.nan); end = np.full(n, -1, np.int64); lossR = np.full(n, np.nan); exitR = np.full(n, np.nan); jend = np.full(n, -1, np.int64)
    filled = np.zeros(n, np.bool_)
    for t in range(n):
        j = js[t]; d = dirs[t]; e = ents[t]; s = stps[t]; r = abs(e - s)
        if r <= 0 or j >= N:
            continue
        k = j
        if lim[t]:
            ok = False
            while k < N and k < j + wait[t]:
                if (d == 1 and L[k] <= e) or (d == -1 and H[k] >= e):
                    ok = True
                    break
                k += 1
            if not ok:
                continue
            filled[t] = True
            # the fill minute: only the stop counts
            if (d == 1 and L[k] <= s) or (d == -1 and H[k] >= s):
                mfe[t] = 0.0; end[t] = 0; lossR[t] = -1.0; jend[t] = k
                continue
            k += 1
        else:
            filled[t] = True
        cut = FC[j] if usecut else N
        best = 0.0
        done = False
        while k < N:
            if k >= cut:
                mfe[t] = best / r; end[t] = 2; exitR[t] = d * (C[k - 1] - e) / r; jend[t] = k - 1; done = True
                break
            if (d == 1 and L[k] <= s) or (d == -1 and H[k] >= s):
                px = s
                if d == 1 and O[k] < s:
                    px = O[k]
                if d == -1 and O[k] > s:
                    px = O[k]
                mfe[t] = best / r; end[t] = 0; lossR[t] = min(-1.0, d * (px - e) / r); jend[t] = k; done = True
                break
            ex = H[k] - e if d == 1 else e - L[k]
            if ex > best:
                best = ex
            if best >= cap * r:
                mfe[t] = best / r; end[t] = 1; jend[t] = k; done = True
                break
            k += 1
        if not done:
            mfe[t] = best / r; end[t] = 3; jend[t] = N - 1
    return mfe, end, lossR, exitR, jend, filled


def outcomes(tf, si, sd, se, ss, entry_mode=0, usecut=False, cap=3.0):
    """per signal: mfe R, end (0 stop, 1 cap, 2 force close, 3 data end, -1 not filled), loss R, exit R, end minute, risk"""
    import engine as E
    b = E.load(tf); M = m1()
    js = b['j1'][si] + 1
    lim = np.full(len(si), entry_mode != 0) & (np.abs(se - b['c'][si]) > 1e-9)
    wait = np.full(len(si), 5 * tf, np.int64)
    mfe, end, lossR, exitR, jend, filled = scan(M['o'], M['h'], M['l'], M['c'], M['fc'], js, sd.astype(np.int64), se, ss, lim, wait, usecut, cap)
    return dict(mfe=mfe, end=end, lossR=lossR, exitR=exitR, jend=jend, filled=filled, r=np.abs(se - ss), t=b['ue'][si], js=js)


def net_at(o, X, cost=COST):
    """net R per trade at target X (nan = not filled / unresolved)"""
    r = o['r']; hit = o['mfe'] >= X - 1e-12
    out = np.full(len(r), np.nan)
    out[hit] = (X * r[hit] - cost) / (r[hit] + cost)
    st = (~hit) & (o['end'] == 0); out[st] = (o['lossR'][st] * r[st] - cost) / (r[st] + cost)
    ct = (~hit) & (o['end'] == 2); out[ct] = (o['exitR'][ct] * r[ct] - cost) / (r[ct] + cost)
    return out, hit


def summary(o, mask=None, levels=LEVELS):
    """per level: trades, accuracy (target before the stop), net R per trade, total net R"""
    ok = o['filled'] & (o['end'] >= 0)
    if mask is not None:
        ok = ok & mask
    rows = []
    for X in levels:
        net, hit = net_at(o, X)
        m = ok & ~np.isnan(net)
        n = int(m.sum())
        rows.append((X, n, hit[m].mean() if n else np.nan, net[m].mean() if n else np.nan, net[m].sum() if n else 0.0))
    return rows
