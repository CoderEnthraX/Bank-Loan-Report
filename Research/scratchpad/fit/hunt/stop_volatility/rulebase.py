"""Shared helpers for stop_volatility hookeval rule modules."""
import sys, math
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
def tight_stop(P, i, d, entry, A):
    ext = P['L'][i] if d > 0 else P['H'][i]
    return entry - d * max(0.9 * A, d * (entry - ext))
def chop(P, i, N):
    H, L, tr = P['H'], P['L'], P['tr']
    if i < N: return 100.0
    hi = max(H[i - N + 1:i + 1]); lo = min(L[i - N + 1:i + 1]); s = sum(tr[i - N + 1:i + 1])
    return 100 * math.log10(s / (hi - lo)) / math.log10(N) if hi > lo else 0
def first_in_session(P, i, d):
    from sig import raw
    S = raw(P); ds = i - P['sinceStart'][i]
    return not any(S[j] == d for j in range(ds, i))
