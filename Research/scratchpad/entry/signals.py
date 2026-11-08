"""Entry research kit, part 2: every raw signal of the engine (ref_g.py / the Pine SHARED ENGINE) on every bar, without the
position-dependent rules (one trade at a time, cooldown, re-anchored break, max fills, keep-armed). Default parameters = ref_g.IN."""
import numpy as np
from numba import njit
import data

P0 = dict(structLen=10, brkLen=6, entryLen=6, dispAtr=0.8, dispBodyPct=55.0, dispClosePct=25.0, momLen=10, momAtr=0.85, cmoMin=20.0,
          slopeBars=3, stopAtr=1.8, halfStopAtr=0.9, biasNet=3, impBodyPct=50.0, skipSunday=True)

@njit(cache=True)
def _scan(O, H, L, C, V, A, ds, vb, utc_wd, structLen, brkLen, entryLen, dispAtr, bodyP, closeP, momLen, momAtr, cmoMin,
          slopeBars, biasNet, impBodyP, skipSun):
    n = len(C); E = 1e-7
    bull = np.zeros(n, np.bool_); bear = np.zeros(n, np.bool_)
    entL = np.full(n, np.nan); entS = np.full(n, np.nan); halfL = np.zeros(n, np.bool_); halfS = np.zeros(n, np.bool_)
    sigH = np.full(n, np.nan); sigL = np.full(n, np.nan); erv = np.full(n, np.nan); prevNetA = np.full(n, np.nan)
    bullImpA = np.zeros(n, np.bool_); bearImpA = np.zeros(n, np.bool_)
    bullN = 0; bearN = 0; prevNet = 0; havePrev = False
    sesH = 0.0; sesL = 0.0; sesO = 0.0; pdH = 0.0; pdL = 0.0; havePd = False; haveSes = False
    warm0 = max(structLen, brkLen, entryLen, momLen, slopeBars, 6) + 1
    for i in range(n):
        if ds[i]:
            if i > 0: prevNet = bullN - bearN; havePrev = True
            bullN = 0; bearN = 0
            if haveSes: pdH = sesH; pdL = sesL; havePd = True
            sesH = H[i]; sesL = L[i]; sesO = O[i]; haveSes = True
        else:
            sesH = max(sesH, H[i]); sesL = min(sesL, L[i])
        if i < warm0 or np.isnan(A[i]):
            continue
        a = A[i]
        pH = H[i - structLen:i].max(); pL = L[i - structLen:i].min()
        sH = H[i - brkLen:i].max(); sL = L[i - brkLen:i].min()
        el = min(entryLen, structLen); eH = H[i - el:i].max(); eL = L[i - el:i].min()
        rng = H[i] - L[i]; body = abs(C[i] - O[i]); mid = (O[i] + C[i]) / 2
        mom = C[i] - C[i - momLen]
        den = 0.0
        for j in range(i - momLen + 1, i + 1): den += abs(C[j] - C[j - 1])
        er = mom / den if den > 0 else 0.0
        erUp = cmoMin <= 0 or (den > 0 and er >= cmoMin / 100.0)
        erDn = cmoMin <= 0 or (den > 0 and -er >= cmoMin / 100.0)
        if slopeBars > 0 and vb[i] >= slopeBars:
            vs = V[i] - V[i - slopeBars]; slUp = vs > 0; slDn = vs < 0
        else:
            slUp = True; slDn = True
        if slopeBars > 0:
            sg = V[i] - V[i - slopeBars]; sgUp = sg > 0; sgDn = sg < 0
        else:
            sgUp = True; sgDn = True
        big = rng > 0 and rng >= dispAtr * a and body / rng * 100 >= bodyP - E
        bigI = rng > 0 and rng >= dispAtr * a and body / rng * 100 >= impBodyP - E
        cHi = rng > 0 and (H[i] - C[i]) / rng * 100 <= closeP + E
        cLo = rng > 0 and (C[i] - L[i]) / rng * 100 <= closeP + E
        bImp = C[i] > O[i] and H[i] > pH and bigI and cHi and slUp
        sImp = C[i] < O[i] and L[i] < pL and bigI and cLo and slDn
        setupOk = not (skipSun and utc_wd[i] == 6)
        bb = setupOk and C[i] > O[i] and big and cHi and sgUp and C[i] > V[i] and (momAtr <= 0 or mom >= momAtr * a) and erUp
        sb = setupOk and C[i] < O[i] and big and cLo and sgDn and C[i] < V[i] and (momAtr <= 0 or -mom >= momAtr * a) and erDn
        hl = bullN == 0 and havePrev and prevNet <= -biasNet
        hs = bearN == 0 and havePrev and prevNet >= biasNet
        if havePd:
            hl = hl or (bullN == 0 and sesO < pdL)
            hs = hs or (bearN == 0 and sesO > pdH)
        if bImp: bullN += 1
        if sImp: bearN += 1
        bull[i] = bb and C[i] > sH; bear[i] = sb and C[i] < sL
        entL[i] = max(mid, eH); entS[i] = min(mid, eL); halfL[i] = hl; halfS[i] = hs
        sigH[i] = sH; sigL[i] = sL; erv[i] = er; prevNetA[i] = prevNet if havePrev else np.nan
        bullImpA[i] = bImp; bearImpA[i] = sImp
    return bull, bear, entL, entS, halfL, halfS, sigH, sigL, erv, prevNetA, bullImpA, bearImpA

def raw(tf, **kw):
    """every raw signal: dict of arrays (bar i, dir d, entry = model limit, stop = normal / half / half capped, half flag)"""
    p = dict(P0); p.update(kw); b = data.load(tf)
    bull, bear, entL, entS, halfL, halfS, sigH, sigL, erv, pn, bI, sI = _scan(
        b['O'], b['H'], b['L'], b['C'], b['V'], b['atr'], b['ds'], b['vb'], b['utc_wd'], p['structLen'], p['brkLen'], p['entryLen'],
        p['dispAtr'], p['dispBodyPct'], p['dispClosePct'], p['momLen'], p['momAtr'], p['cmoMin'], p['slopeBars'], p['biasNet'],
        p['impBodyPct'], p['skipSunday'])
    iL = np.flatnonzero(bull); iS = np.flatnonzero(bear)
    i = np.concatenate([iL, iS]); d = np.concatenate([np.ones(len(iL), np.int8), -np.ones(len(iS), np.int8)])
    o = np.argsort(i, kind='stable'); i = i[o]; d = d[o]
    A = b['atr'][i]; Hh = b['H'][i]; Ll = b['L'][i]
    ent = np.where(d == 1, entL[i], entS[i]); half = np.where(d == 1, halfL[i], halfS[i])
    cStop = ent - d * p['stopAtr'] * A
    hStop = np.where(d == 1, np.minimum(ent - p['halfStopAtr'] * A, Ll), np.maximum(ent + p['halfStopAtr'] * A, Hh))
    hCap = np.where(d == 1, np.maximum(hStop, cStop), np.minimum(hStop, cStop))
    return dict(i=i, d=d, entry=ent, half=half, stop_n=cStop, stop_h=np.where(half, hStop, cStop), stop_hc=np.where(half, hCap, cStop),
                sigH=sigH[i], sigL=sigL[i], er=erv[i], prevNet=pn[i], p=p,
                both=bull[i] & bear[i])
