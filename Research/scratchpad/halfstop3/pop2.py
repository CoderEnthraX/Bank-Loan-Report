"""All labeled trades: run features. oppRun = consecutive opposite impulses (any session) immediately before this signal's impulse; sesOpp = opposite impulses this session before; firstSes = first d-impulse this session."""
import sys, io, contextlib, json, os
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/halfstop3')
with contextlib.redirect_stdout(io.StringIO()):
    import tab3
import r3
IM = {}
def imps(sym):
    if sym not in IM:
        r3.IMPS = []; r3.run(sym, tab3.inp); IM[sym] = list(r3.IMPS); r3.IMPS = None
    return IM[sym]
out = []
for r in tab3.rows:
    if r['m'] is None: continue
    F = r['F']; d = r['d']; P = r['P']; j = r['j']; A = r['A']; C, O = P['C'], P['O']
    s0 = j - F['vwBars']; gap = d * (O[s0] - C[s0 - 1]) / A
    seq = [s for i, s, *_ in imps(P['sym']) if i < j]
    run = 0
    for s in reversed(seq):
        if s == -d: run += 1
        else: break
    sameSes = F['bullN'] if d > 0 else F['bearN']; imp = F['bullImp'] if d > 0 else F['bearImp']
    sesOpp = F['bearN'] if d > 0 else F['bullN']
    out.append((r, run, gap, sameSes - (1 if imp else 0), sesOpp, imp))
    lab = r['lab']
    print(f"{r['src']:7s} {P['sym'][:6]:6s} {r['ft']} {'L' if d>0 else 'S'} {lab:5s} m{'H' if r['m']['half'] else 'n'} k{F['vwBars']:3d} net{d*(F['prevNet'] or 0):+3d} imp{int(imp)} sameBefore{sameSes - (1 if imp else 0)} sesOpp{sesOpp:2d} oppRun{run:2d} gap{gap:+5.1f}")
