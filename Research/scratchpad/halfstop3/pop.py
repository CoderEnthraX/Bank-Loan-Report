"""Trigger population: labeled trades whose model signal is the session's first impulse in its direction with prev net >= 3 against (or open-outside), plus #6."""
import sys, io, contextlib
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/halfstop3')
with contextlib.redirect_stdout(io.StringIO()):
    import tab3
import r3
from engine import rma
IM = {}
def imps(sym):
    if sym not in IM:
        r3.IMPS = []; r3.run(sym, {}); IM[sym] = list(r3.IMPS); r3.IMPS = None
    return IM[sym]
for r in tab3.rows:
    if r['m'] is None: continue
    F = r['F']; d = r['d']; same = F['bullN'] if d > 0 else F['bearN']; imp = F['bullImp'] if d > 0 else F['bearImp']
    net = d * (F['prevNet'] or 0)
    trig = r['m']['half'] or (same == 1 and imp and net <= -2) or r['src'] in ('BNA#6',)
    if not trig: continue
    P = r['P']; j = r['j']; A = r['A']; T = P['T']; C, O, H, L, V = P['C'], P['O'], P['H'], P['L'], P['V']; ds = P['daystart']
    s0 = j - F['vwBars']; p0 = s0 - 1
    while p0 > 0 and not ds[p0]: p0 -= 1
    pc = C[s0 - 1]; pv = V[s0 - 1]
    gap = d * (O[s0] - pc) / A; ovw = d * (O[s0] - pv) / A
    Aat0 = rma(P['tr'], 14)[s0]; aprev = sum(P['tr'][p0:s0]) / max(1, s0 - p0)
    # prev-session impulses split in halves, last-N
    pim = [(i, s) for i, s, *_ in imps(P['sym']) if p0 <= i < s0]
    half2 = [s for i, s in pim if i >= (p0 + s0) / 2]
    last5 = [s for i, s in pim][-5:]
    cur = [s for i, s, *_ in imps(P['sym']) if s0 <= i < j]
    print(f"{r['src']:7s} {P['sym'][:6]:6s} {r['ft']} {'L' if d>0 else 'S'} {r['lab']:5s} m{'H' if r['m']['half'] else 'n'} k{F['vwBars']:3d} net{net:+3d} n2nd{d*sum(half2):+3d} last5{d*sum(last5):+3d} cur{d*sum(cur):+3d} gap{gap:+5.1f} oVW{ovw:+5.1f} A/A0 {A/Aat0:4.2f} A/prevTR {A/aprev:4.2f} rng{(H[j]-L[j])/A:4.2f} cVW{d*(C[j]-V[j])/A:+5.1f} prevLen{s0-p0}")
