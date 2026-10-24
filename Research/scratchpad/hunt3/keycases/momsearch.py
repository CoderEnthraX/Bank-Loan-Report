import sys, csv
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from engine2 import prepare
from engine import rma
rows = [r for r in csv.DictReader(open('feats.tsv'), delimiter='\t') if r['lab'] != '-']
cache = {}
def P_(s):
    if s not in cache:
        P = prepare(s); cache[s] = (P, {t: i for i, t in enumerate(P['T'])}, rma(P['tr'], 14))
    return cache[s]
res = []
for ref in ('C', 'O', 'HL2', 'ext', 'ohlc4'):
    for k in range(3, 21):
        for an in ('A', 'A1', 'Ak'):
            ok = []; X = []
            for r in rows:
                P, idx, A = P_(r['sym']); i = idx[r['arm']]; C, O, H, L = P['C'], P['O'], P['H'], P['L']
                d = 1 if C[i] > O[i] else -1
                j = i - k
                base = {'C': C[j], 'O': O[j + 1], 'HL2': (H[j] + L[j]) / 2, 'ext': (min(L[j:i]) if d > 0 else max(H[j:i])), 'ohlc4': (O[j]+H[j]+L[j]+C[j])/4}[ref]
                a = {'A': A[i], 'A1': A[i - 1], 'Ak': A[j]}[an]
                v = d * (C[i] - base) / a
                (X if r['lab'].startswith('X') else ok).append((v, r['sym'][:3] + r['arm'][5:]))
            mo = min(ok)[0]; xs = sorted(v for v, n in X if v < mo)
            res.append((len(xs), mo, ref, k, an, [n for v, n in X if v < mo]))
res.sort(key=lambda x: -x[0])
for x in res[:25]: print(x)
