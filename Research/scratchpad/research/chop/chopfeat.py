"""CAUSAL chop / consolidation features per bar (only bars <= i). feats(sym) -> dict name -> list (long view);
directional features also have name+'_S' (short view). Session = engine daystart."""
import sys, math
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/fit')
from engine2 import prepare
from engine import rma
DIRF = {'slp10', 'slp20', 'slp30', 'orb', 'dV', 'effSd', 'sideS', 'sideN24'}
_F = {}
def feats(sym):
    if sym in _F: return _F[sym]
    P = prepare(sym); O, H, L, C, V = P['O'], P['H'], P['L'], P['C'], P['V']; A = rma(P['tr'], 14); TR = P['tr']; n = len(C); ds = P['daystart']
    F = {}
    def arr(): return [None] * n
    names = ['xS0', 'xS2', 'xR2', 'x12_2', 'x24_2', 'x36_2', 'x24_0', 'bsx', 'near05S', 'near1S', 'near05_24', 'ov12', 'ov24', 'rngS', 'rngRel', 'rngRel5',
             'orbBoth', 'chop14', 'chop30', 'bbw', 'bbwP', 'pX2r', 'pNear', 'pEff', 'effS', 'er20', 'er30', 'vb']
    for k in names: F[k] = arr()
    for k in DIRF: F[k] = arr(); F[k + '_S'] = arr()
    a = 0; sgn0 = sgn2 = 0; xs0 = xs2 = 0; ev2 = []; ev0 = []; lastx = None; nearc05 = nearc1 = 0; sideU = 0
    sesH = sesL = None; orH = orL = None; orUp = orDn = False
    prevS = []   # completed sessions: dict(rng, x2r, near, eff)
    bbwHist = []
    for i in range(n):
        if ds[i] or i == 0:
            if i > 0 and i - a > 10:
                rg = sesH - sesL; nb = i - a
                prevS.append(dict(rng=rg, x2r=xs2 / nb * 100, near=nearc05 / nb, eff=abs(C[i - 1] - O[a]) / rg if rg else 0))
            a = i; sgn0 = sgn2 = 0; xs0 = xs2 = 0; ev2 = []; ev0 = []; lastx = None; nearc05 = nearc1 = 0; sideU = 0
            sesH, sesL = H[i], L[i]; orH, orL = H[i], L[i]; orUp = orDn = False
        else:
            sesH = max(sesH, H[i]); sesL = min(sesL, L[i])
        Ai = A[i] or TR[i] or 1e-9
        nb = i - a + 1
        if nb <= 6: orH = max(orH, H[i]); orL = min(orL, L[i])
        else:
            if C[i] > orH: orUp = True
            if C[i] < orL: orDn = True
        dev = (C[i] - V[i]) / Ai
        z0 = 1 if dev > 0 else -1 if dev < 0 else 0
        if z0:
            if sgn0 and z0 != sgn0: xs0 += 1; ev0.append(i); lastx = i
            sgn0 = z0
        z2 = 1 if dev > 0.2 else -1 if dev < -0.2 else 0
        if z2:
            if sgn2 and z2 != sgn2: xs2 += 1; ev2.append(i)
            sgn2 = z2
        nearc05 += abs(dev) <= 0.5; nearc1 += abs(dev) <= 1.0; sideU += C[i] > V[i]
        F['vb'][i] = nb
        F['xS0'][i] = xs0; F['xS2'][i] = xs2; F['xR2'][i] = xs2 / nb * 100
        F['x12_2'][i] = sum(1 for e in ev2 if e > i - 12); F['x24_2'][i] = sum(1 for e in ev2 if e > i - 24); F['x36_2'][i] = sum(1 for e in ev2 if e > i - 36)
        F['x24_0'][i] = sum(1 for e in ev0 if e > i - 24)
        F['bsx'][i] = (i - lastx) if lastx is not None else nb
        F['near05S'][i] = nearc05 / nb; F['near1S'][i] = nearc1 / nb
        j0 = max(a, i - 23); F['near05_24'][i] = sum(abs(C[j] - V[j]) <= 0.5 * (A[j] or Ai) for j in range(j0, i + 1)) / (i - j0 + 1)
        for N, k in ((12, 'ov12'), (24, 'ov24')):
            j0 = max(a, i - N + 1); F[k][i] = sum(L[j] <= V[j] <= H[j] for j in range(j0, i + 1)) / (i - j0 + 1)
        for N in (10, 20, 30):
            j = max(a, i - N); v = (V[i] - V[j]) / Ai; F['slp%d' % N][i] = v; F['slp%d_S' % N][i] = -v
        F['rngS'][i] = (sesH - sesL) / Ai
        F['rngRel'][i] = (sesH - sesL) / prevS[-1]['rng'] if prevS and prevS[-1]['rng'] else None
        if len(prevS) >= 3:
            m = sum(p['rng'] for p in prevS[-5:]) / len(prevS[-5:]); F['rngRel5'][i] = (sesH - sesL) / m if m else None
        F['orbBoth'][i] = 1 if (orUp and orDn) else 0
        if nb > 6:
            F['orb'][i] = 1 if C[i] > orH else -1 if C[i] < orL else 0; F['orb_S'][i] = -F['orb'][i]
        for N, k in ((14, 'chop14'), (30, 'chop30')):
            if i >= N:
                hh = max(H[i - N + 1:i + 1]); ll = min(L[i - N + 1:i + 1]); s = sum(TR[i - N + 1:i + 1])
                F[k][i] = 100 * math.log10(s / (hh - ll)) / math.log10(N) if hh > ll and s > 0 else None
        if i >= 19:
            w = C[i - 19:i + 1]; mu = sum(w) / 20; sd = math.sqrt(sum((x - mu) ** 2 for x in w) / 20); b = 4 * sd / Ai
            F['bbw'][i] = b; bbwHist.append(b)
            h = bbwHist[-120:]; F['bbwP'][i] = sum(x <= b for x in h) / len(h)
        if prevS:
            F['pX2r'][i] = prevS[-1]['x2r']; F['pNear'][i] = prevS[-1]['near']; F['pEff'][i] = prevS[-1]['eff']
        rg = sesH - sesL
        F['effS'][i] = abs(C[i] - O[a]) / rg if rg else 0
        F['effSd'][i] = (C[i] - O[a]) / rg if rg else 0; F['effSd_S'][i] = -F['effSd'][i]
        for N in (20, 30):
            if i >= N:
                den = sum(abs(C[j] - C[j - 1]) for j in range(i - N + 1, i + 1)); F['er%d' % N][i] = abs(C[i] - C[i - N]) / den if den else 0
        F['dV'][i] = dev; F['dV_S'][i] = -dev
        F['sideS'][i] = sideU / nb; F['sideS_S'][i] = 1 - sideU / nb
        j0 = max(a, i - 23); su = sum(C[j] > V[j] for j in range(j0, i + 1)) / (i - j0 + 1); F['sideN24'][i] = su; F['sideN24_S'][i] = 1 - su
    _F[sym] = F; return F
def get(sym, name, i, d):
    F = feats(sym); k = name + '_S' if (d < 0 and name in DIRF) else name; return F[k][i]
