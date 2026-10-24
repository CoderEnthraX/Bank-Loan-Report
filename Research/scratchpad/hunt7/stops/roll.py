import sys; sys.argv = sys.argv[:1]
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/hunt7/stops')
import tab
M = tab.M
for src, sym, ft, d, lab, m, P in tab.rows:
    if m is None: continue
    j = m['arm']; I = M.IMPS[sym]; ds = P['daystart']
    seq = [(i, v[0]) for i, v in sorted(I.items()) if i < j and v[0] != 0]
    out = []
    for N in (50, 100, 150, 200):
        s = sum(1 for i, v in seq if i >= j - N and v == d); o = sum(1 for i, v in seq if i >= j - N and v == -d); out.append(f"{N}:{s}/{o}")
    ls = next((j - i for i, v in reversed(seq) if v == d), 999); lo = next((j - i for i, v in reversed(seq) if v == -d), 999)
    last = ''.join('+' if v == d else '-' for i, v in seq[-12:])
    # session starts back
    ss = [i for i in range(j, max(j - 600, 0), -1) if ds[i]][:3]
    print(f"{src:10s} {sym[:8]:8s} {ft[5:]} {'L' if d>0 else 'S'} {lab:4s} m{'T' if m['tight'] else 'n'} k{j-ss[0]:3d} {' '.join(out)} lastSame {ls:3d} lastOpp {lo:3d} seq {last:>12s}")
