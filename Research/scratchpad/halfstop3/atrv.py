import sys
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S+'/fit')
from engine2 import prepare
from engine import rma
P = prepare(sys.argv[1]); T = P['T']; tr = P['tr']; A = rma(tr, 14); H, L, C = P['H'], P['L'], P['C']
i = T.index(sys.argv[2]); n = int(sys.argv[3])
for k in range(i - n, i + 1):
    print(T[k], 'TR %.2f HL %.2f ATR %.3f %s' % (tr[k], H[k] - L[k], A[k], 'START' if P['daystart'][k] else ''))
