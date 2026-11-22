"""A line-by-line Python copy of the Pine Sniper ENGINE (build/sn_pine_parts.py, with Pine's na rules), run on the simulator's M5 bars and
M1 intrabars with the EA's VWAP (SNBAR lines of s_sn.log): its signals must equal the EA's SNSIG lines. Run: python3 -I sn_mirror.py [log]"""
import sys, math, numpy as np
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
LOG = sys.argv[1] if len(sys.argv) > 1 else S + '/obt/s_sn.log'
NA = float('nan')
def na(x): return x != x
def nz(x, y=0.0): return y if na(x) else x
def pmax(*a): return NA if any(na(x) for x in a) else max(a)
def pmin(*a): return NA if any(na(x) for x in a) else min(a)
# inputs (defaults)
aggRatio, absSens, volLen, atrLen, absLen, divMin, wickPct, aggRelV, aggBody = 2.2, 1.2, 20, 14, 5, 15.0, 40.0, 1.0, 50.0
expiry, zoneMode, bandMult, zoneAtr, maxDist, cvd, cvdLen, slopeOn, slopeLen, cool = 10, 'band', 1.0, 0.75, 2.5, 'roll', 3, False, 5, 3
entryMode, offset, slMode, slAtr, slPts, slPct, slBuf, swingLen, minRisk, maxRisk, mintick = 'close', 0.0, 'struct', 1.5, 5.0, 0.25, 0.15, 5, 0.3, 4.0, 0.01
d = dict(np.load(S + '/entry/cache_M1.npz'))
m = (d['srv'] >= 1780275600) & (d['srv'] < 1790985600)
SRV, O, H, L, C, V = d['srv'][m], d['O'][m], d['H'][m], d['L'][m], d['C'][m], d['TV'][m]
bars = {}; order = []
for i, s in enumerate(SRV):
    k = int(s) // 300 * 300
    if k not in bars: bars[k] = [O[i], H[i], L[i], C[i], 0.0, []]; order.append(k)
    b = bars[k]; b[1] = max(b[1], H[i]); b[2] = min(b[2], L[i]); b[3] = C[i]; b[4] += float(V[i]); b[5].append(i)
vw = {}
for l in open(LOG):
    if ' SNBAR ' in l:
        p = l.split(' SNBAR ')[1].split(); vw[int(p[0])] = (float(p[1]), float(p[2]), p[3] == '1')
seq = [k for k in order if k in vw]
assert seq == sorted(seq) and order[order.index(seq[0]):][:len(seq)] == seq, 'EA bars not contiguous with the data'
st = dict(cvdS=0.0, bullArm=None, bullLo=NA, bullHi=NA, bearArm=None, bearLo=NA, bearHi=NA, last=None, atr=NA, trs=[])
hist = []   # per bar dict
out = []
for bi, k in enumerate(seq):
    o, h, l, c, v, mi = bars[k]; vwap, vwSd, newA = vw[k]
    prev = hist[-1] if hist else None
    tr = h - l if prev is None else max(max(h - l, abs(h - prev['c'])), abs(l - prev['c']))
    if len(st['trs']) < atrLen:
        st['trs'].append(tr)
        if len(st['trs']) == atrLen: st['atr'] = sum(st['trs']) / atrLen
    else: st['atr'] = (1.0 / atrLen) * tr + (1.0 - 1.0 / atrLen) * st['atr']
    atr = st['atr']
    vols = [x['v'] for x in hist] + [v]
    avg = sum(vols[-volLen:]) / volLen if len(vols) >= volLen else NA
    relV = v / avg if avg > 0 else 0.0
    rng = h - l; bodyP = abs(c - o) / rng if rng > 0 else 0.0; clPos = (c - l) / rng if rng > 0 else 0.5
    loW = min(o, c) - l; upW = h - max(o, c)
    bv = sv = 0.0
    for j in mi:
        pc = C[j - 1] if j > 0 else C[j]
        dr = 1.0 if C[j] > O[j] else -1.0 if C[j] < O[j] else (1.0 if C[j] - pc > 0 else -1.0 if C[j] - pc < 0 else 0.0)
        vv = float(V[j])
        bv += vv if dr > 0 else 0.0 if dr < 0 else vv * 0.5
        sv += vv if dr < 0 else 0.0 if dr > 0 else vv * 0.5
    intra = len(mi) >= 2
    if intra: buyV, sellV = bv, sv
    else:
        buyV = v * (c - l) / rng if rng > 0 else v * 0.5; sellV = v - buyV
    totV = buyV + sellV; delta = buyV - sellV
    bullR = buyV / max(sellV, totV * 0.01, 0.000001); bearR = sellV / max(buyV, totV * 0.01, 0.000001)
    st['cvdS'] = delta if newA else st['cvdS'] + delta
    cur = dict(o=o, h=h, l=l, c=c, v=v, d=delta, tv=totV, vw=vwap)
    H2 = hist + [cur]
    def win(key, n): return [x[key] for x in H2[-n:]] if len(H2) >= n else None
    def wsum(key, n):
        w = win(key, n); return NA if w is None else sum(w)
    roll = wsum('d', cvdLen)
    bullAg = c > o and bullR >= aggRatio and relV >= aggRelV and bodyP * 100.0 >= aggBody
    bearAg = c < o and bearR >= aggRatio and relV >= aggRelV and bodyP * 100.0 >= aggBody
    wl = win('l', absLen); wh = win('h', absLen)
    loL = NA if wl is None else min(wl); hiH = NA if wh is None else max(wh)
    winD = wsum('d', absLen); winV = wsum('tv', absLen); winRV = wsum('v', absLen)
    winDP = 100.0 * winD / winV if winV > 0 else 0.0
    winRel = winRV / (avg * absLen) if avg > 0 else 0.0
    back = H2[-1 - absLen]['c'] if len(H2) > absLen else NA
    effort = relV >= absSens
    bullAb = (effort and loW >= rng * wickPct / 100.0 and clPos >= 0.5) or (intra and effort and delta < 0 and c >= o) or (relV >= absSens * 1.5 and rng <= atr * 0.7 and l <= loL) or (winDP <= -divMin and c >= back and winRel >= 1.0)
    bearAb = (effort and upW >= rng * wickPct / 100.0 and clPos <= 0.5) or (intra and effort and delta > 0 and c <= o) or (relV >= absSens * 1.5 and rng <= atr * 0.7 and h >= hiH) or (winDP >= divMin and c <= back and winRel >= 1.0)
    basis = vwSd; up1 = vwap + basis * bandMult; lo1 = vwap - basis * bandMult
    zw = zoneAtr * atr
    def touch(lv, z): return (not na(lv)) and l <= lv + z and h >= lv - z
    bullCtx = c >= vwap - zw and (zoneMode == 'any' or touch(vwap, zw) or (zoneMode == 'band' and touch(up1, zw)))
    bearCtx = c <= vwap + zw and (zoneMode == 'any' or touch(vwap, zw) or (zoneMode == 'band' and touch(lo1, zw)))
    dist = abs(c - vwap) / atr if atr > 0 else 0.0
    distOk = maxDist <= 0 or dist <= maxDist
    slope = vwap - H2[-1 - slopeLen]['vw'] if len(H2) > slopeLen else NA
    sl_ = win('l', swingLen); sh_ = win('h', swingLen)
    swLo = NA if sl_ is None else min(sl_); swHi = NA if sh_ is None else max(sh_)
    bullArmed = st['bullArm'] is not None and bi - st['bullArm'] <= expiry
    bearArmed = st['bearArm'] is not None and bi - st['bearArm'] <= expiry
    if bullArmed and (c < vwap - zw or c < st['bullLo']): st['bullArm'] = None; bullArmed = False
    if bearArmed and (c > vwap + zw or c > st['bearHi']): st['bearArm'] = None; bearArmed = False
    if bullAb and bullCtx:
        if bullArmed: st['bullLo'] = min(st['bullLo'], l); st['bullHi'] = max(st['bullHi'], h)
        else: st['bullLo'] = l; st['bullHi'] = h
        st['bullArm'] = bi; bullArmed = True
    if bearAb and bearCtx:
        if bearArmed: st['bearLo'] = min(st['bearLo'], l); st['bearHi'] = max(st['bearHi'], h)
        else: st['bearLo'] = l; st['bearHi'] = h
        st['bearArm'] = bi; bearArmed = True
    coolOk = st['last'] is None or bi - st['last'] >= cool
    bullF = c > vwap and distOk and (not slopeOn or slope > 0) and (cvd == 'off' or (roll > 0 if cvd == 'roll' else st['cvdS'] > 0)) and coolOk
    bearF = c < vwap and distOk and (not slopeOn or slope < 0) and (cvd == 'off' or (roll < 0 if cvd == 'roll' else st['cvdS'] < 0)) and coolOk
    buy = bullF and (bullArmed and bullAg)
    sell = bearF and not buy and (bearArmed and bearAg)
    if buy or sell:
        sd = 1 if buy else -1
        hasZ = bullArmed if sd == 1 else bearArmed
        zExt = st['bullLo'] if sd == 1 else st['bearHi']
        base = c
        ent = base - sd * offset
        sStr = (pmin(zExt, l) if hasZ else swLo) - slBuf * atr if sd == 1 else (pmax(zExt, h) if hasZ else swHi) + slBuf * atr
        risk = sd * (ent - sStr)
        risk = pmax(minRisk * atr, pmin(maxRisk * atr, nz(risk, minRisk * atr)))
        if not (risk > 0): risk = max(nz(atr) * 0.5, mintick * 10)
        out.append('%d %d %.5f %.5f' % (k, sd, ent, ent - sd * risk))
        st['last'] = bi
        if sd == 1: st['bullArm'] = None
        else: st['bearArm'] = None
    hist.append(cur)
    if len(hist) > 300: hist.pop(0)
ea = [l.split(' SNSIG ')[1].strip() for l in open(LOG) if ' SNSIG ' in l]
A, B = set(out), set(ea)
print('Pine copy %d signals, EA %d, only Pine copy %d, only EA %d' % (len(A), len(B), len(A - B), len(B - A)))
for x in sorted(A - B)[:4]: print('  pine', x)
for x in sorted(B - A)[:4]: print('  ea  ', x)
