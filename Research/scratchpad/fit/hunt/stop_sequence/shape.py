import sys
sys.path.insert(0, D := '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
from pfeat import *
for t in sorted(TRADES, key=lambda t: not t['tight']):
    P = prepare(t['sym']); i = t['arm_i']; d = t['d']; A = P[('atr', 14)][i]; O, H, L, C = P['O'], P['H'], P['L'], P['C']
    ref = t['entry']
    def nb(j):
        o, h, l, c = [d * (x - ref) / A for x in (O[j], H[j], L[j], C[j])]
        if d < 0: h, l = l, h
        return f"[{o:+.1f} {h:+.1f} {l:+.1f} {c:+.1f}]"
    print(f"{t['sym']:6s} {t['fill'][5:]} {'L' if d>0 else 'S'} {'T' if t['tight'] else ' '} {t['out']:4s}", ' '.join(nb(j) for j in range(i - 5, i + 1)), '|', nb(t['fill_i']))
