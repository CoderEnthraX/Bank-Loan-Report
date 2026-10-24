"""Recover per-bar relative volume from the exported session VWAP (VWAP of hlc3), then VWAP stdev bands."""
import sys, os, math, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine2 import prepare
from arp_data import SYMS, DATA
def raw_vwap(sym):
    return [float(r['VWAP']) if r['VWAP'] not in ('', 'NaN') else None for r in csv.DictReader(open(os.path.join(DATA, SYMS[sym] + '.csv')))]
def recover(sym):
    P = prepare(sym)
    if 'vol' in P: return P
    Vw = raw_vwap(sym); H, L, C = P['H'], P['L'], P['C']; n = len(C)
    vol = [None] * n; W = None; bad = 0
    for i in range(n):
        p = (H[i] + L[i] + C[i]) / 3
        if P['daystart'][i] or W is None:
            vol[i] = 1.0; W = 1.0; continue
        den = Vw[i] - p
        if abs(den) < 1e-12 * max(1, abs(p)):
            vol[i] = None; bad += 1; continue
        v = W * (Vw[i - 1] - Vw[i]) / den
        if v < 0: v = 0.0; bad += 1
        vol[i] = v; W += v
    # stdev bands of the session VWAP
    sd = [None] * n; s1 = s2 = sw = 0.0
    for i in range(n):
        if P['daystart'][i]: s1 = s2 = sw = 0.0
        v = vol[i] if vol[i] is not None else 0.0
        p = (H[i] + L[i] + C[i]) / 3
        s1 += v * p; s2 += v * p * p; sw += v
        if sw > 0:
            m = s1 / sw; sd[i] = math.sqrt(max(s2 / sw - m * m, 0.0))
    P['vol'] = vol; P['vsd'] = sd; P['volbad'] = bad
    return P
if __name__ == '__main__':
    for s in ['GC', 'EURUSD', 'NASDAQ', 'US30', 'CRUDE', 'ETH', 'NIFTY', 'SENSEX']:
        P = recover(s); vols = [v for v in P['vol'] if v]
        print(s, 'bad', P['volbad'], 'median rel vol', sorted(vols)[len(vols)//2] if vols else None)
