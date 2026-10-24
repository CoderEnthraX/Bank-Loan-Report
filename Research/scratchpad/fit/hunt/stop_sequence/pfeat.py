"""Generic price features at the arm bar for all 80 GT trades."""
import sys
FIT='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'
sys.path.insert(0, FIT); sys.path.insert(0, FIT + '/hunt/stop_sequence')
from engine2 import prepare
from tightdata import TRADES
from adxfit import dmi
from sig import raw
from engine import rma
def pf(t):
    P = prepare(t['sym']); i = t['arm_i']; d = t['d']; A = P[('atr', 14)][i]
    O, H, L, C, V = P['O'], P['H'], P['L'], P['C'], P['V']
    if 'dmi' not in P: P['dmi'] = dmi(P['rows'], 14, 14)
    dip, dim, adx = P['dmi']; S = raw(P)
    ds = i - P['sinceStart'][i]; f = {}
    rng = H[i] - L[i]; body = abs(C[i] - O[i])
    f['rng'] = rng / A; f['body'] = body / A; f['bodyPct'] = body / rng
    f['wickFav'] = ((H[i] - C[i]) if d > 0 else (C[i] - L[i])) / rng
    f['wickAdv'] = ((O[i] - L[i]) if d > 0 else (H[i] - O[i])) / rng
    f['mom10'] = d * (C[i] - C[i - 10]) / A; f['mom5'] = d * (C[i] - C[i - 5]) / A; f['mom20'] = d * (C[i] - C[i - 20]) / A
    f['brk10'] = d * (C[i] - (max(H[i-10:i]) if d > 0 else min(L[i-10:i]))) / A
    f['brk20'] = d * (C[i] - (max(H[i-20:i]) if d > 0 else min(L[i-20:i]))) / A
    f['brk50'] = d * (C[i] - (max(H[i-50:i]) if d > 0 else min(L[i-50:i]))) / A
    f['dVW'] = d * (C[i] - V[i]) / A; f['vwSl3'] = d * (V[i] - V[i - 3]) / A if P['sinceStart'][i] >= 3 else 0
    f['oVW'] = d * (O[i] - V[i]) / A
    f['adx'] = adx[i] or 0; f['diAl'] = ((dip[i] - dim[i]) * d) if dip[i] is not None else 0; f['adxSl'] = (adx[i] - adx[i - 3]) if adx[i] and adx[i-3] else 0
    f['since'] = P['sinceStart'][i]
    f['atrRel50'] = A / (sum(P['tr'][i-50:i]) / 50); f['trRel'] = P['tr'][i] / A
    f['dOpen'] = d * (C[i] - O[ds]) / A; f['gapO'] = d * (O[ds] - C[ds - 1]) / A; f['dPDC'] = d * (C[i] - C[ds - 1]) / A
    hod = max(H[ds:i]) if i > ds else H[i]; lod = min(L[ds:i]) if i > ds else L[i]
    f['brkDay'] = d * (C[i] - (hod if d > 0 else lod)) / A; f['dayRng'] = (hod - lod) / A
    f['entExt'] = d * (t['entry'] - (L[i] if d > 0 else H[i])) / A
    f['entC'] = d * (C[i] - t['entry']) / A
    mid = (O[i] + C[i]) / 2; f['srcLvl'] = int(abs(t['entry'] - mid) > 1e-9 * max(1, abs(mid)) and d * (t['entry'] - mid) > 0)
    f['prevBarDir'] = d * (1 if C[i-1] > O[i-1] else -1); f['prevRng'] = (H[i-1] - L[i-1]) / A
    k = 0
    for j in range(i - 1, i - 30, -1):
        if d * (C[j] - O[j]) > 0: k += 1
        else: break
    f['runBars'] = k
    f['sameSigDay'] = sum(1 for j in range(ds, i) if S[j] == d); f['oppSigDay'] = sum(1 for j in range(ds, i) if S[j] == -d)
    f['sameSig48'] = sum(1 for j in range(i-48, i) if S[j] == d); f['oppSig48'] = sum(1 for j in range(i-48, i) if S[j] == -d)
    ls = [j for j in range(0, i) if S[j] == d]; f['barsSame'] = i - ls[-1] if ls else 9999
    lo = [j for j in range(0, i) if S[j] == -d]; f['barsOpp'] = i - lo[-1] if lo else 9999
    f['dirL'] = int(d > 0)
    # retrace before: distance from the session extreme opposite
    f['fromOppExt'] = d * (C[i] - (lod if d > 0 else hod)) / A
    f['hr'] = int(P['T'][i][11:13])
    return f
