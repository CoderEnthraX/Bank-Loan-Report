import sys, io, contextlib
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/halfstop3')
with contextlib.redirect_stdout(io.StringIO()):
    import tab3
for r in tab3.rows:
    if r['m'] is None: continue
    F = r['F']; d = r['d']; same = F['bullN'] if d > 0 else F['bearN']; imp = F['bullImp'] if d > 0 else F['bearImp']
    if not (r['m']['half'] or r['lab'] == 'HALF'): continue
    P = r['P']; j = r['j']; A = r['A']; e = r['e']; s0 = j - F['vwBars']
    ext = min(P['L'][s0:j+1]) if d > 0 else max(P['H'][s0:j+1])
    ext0 = min(P['L'][s0:j]) if d > 0 and j > s0 else (max(P['H'][s0:j]) if j > s0 else None)
    print(f"{r['src']:7s} {P['sym'][:6]:6s} {r['ft']} {r['lab']:5s} m{'H' if r['m']['half'] else 'n'} logR {r['logR']:.2f} sesExtR {d*(e-ext)/A:.2f} sesExtExclR {d*(e-ext0)/A if ext0 is not None else float('nan'):.2f} k{F['vwBars']}")
