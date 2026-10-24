import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from engine2 import prepare
from engine import rma
sym, t0, t1 = sys.argv[1], sys.argv[2], sys.argv[3]
P = prepare(sym); T = P['T']; O, H, L, C, V = P['O'], P['H'], P['L'], P['C'], P['V']; A = rma(P['tr'], 14); ds = P['daystart']
k = 0
for i in range(len(T)):
    k = 0 if ds[i] else k + 1
    if not (t0 <= T[i] <= t1): continue
    a = A[i]; rng = H[i] - L[i]; body = abs(C[i] - O[i])
    pH = max(H[i-10:i]); pL = min(L[i-10:i])
    up = C[i] > O[i]
    cp = (H[i] - C[i]) / rng * 100 if up else (C[i] - L[i]) / rng * 100
    sl = V[i] - V[i-3]
    tag = ''
    big = rng >= 0.8 * a and body / rng >= 0.55
    if big and cp <= 25:
        if up and H[i] > pH: tag = 'BULLIMP' + ('c' if C[i] > pH else 'w')
        if not up and L[i] < pL: tag = 'BEARIMP' + ('c' if C[i] < pL else 'w')
    print(f"{T[i]} k{k:3d} O{O[i]:.2f} H{H[i]:.2f} L{L[i]:.2f} C{C[i]:.2f} rngA{rng/a:.2f} body{body/rng*100 if rng else 0:3.0f}% cp{cp:3.0f} brkH{(H[i]-pH)/a:+.2f} brkL{(pL-L[i])/a:+.2f} slope{sl/a:+.3f} V{V[i]:.2f} mom{(C[i]-C[i-10])/a:+.2f} {tag}")
