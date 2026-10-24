import sys, io, contextlib
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/halfstop3')
with contextlib.redirect_stdout(io.StringIO()):
    import tab3
flt = sys.argv[1] if len(sys.argv) > 1 else ''
for r in tab3.rows:
    if r['m'] is None or flt not in r['src'] + r['sym']: continue
    P = r['P']; j = r['j']; F = r['F']; d = r['d']; A = r['A']; e = r['e']; L, H = P['L'], P['H']
    lows = [round(d * (e - (min(L[j-N+1:j+1]) if d > 0 else max(H[j-N+1:j+1]))) / A, 2) for N in (1, 2, 3, 4, 5, 6)]
    same = F['bullN'] if d > 0 else F['bearN']; opp = F['bearN'] if d > 0 else F['bullN']
    net = d * (F['prevNet'] or 0)
    out = '-' if F['pdH'] is None else ('below' if F['sesO'] < F['pdL'] else 'above' if F['sesO'] > F['pdH'] else 'in')
    imp = F['bullImp'] if d > 0 else F['bearImp']
    print(f"{r['src']:8s} {r['sym'][:8]:8s} {r['ft']} {'L' if d>0 else 'S'} {r['lab']:5s} m{'H' if r['m']['half'] else 'n'} logR {r['logR']:.2f} k{F['vwBars']:3d} netFor{net:+3d} imp same{same} opp{opp} self{int(imp)} open {out:5s} rng {(H[j]-L[j])/A:.2f} lowsN1-6 {lows}")
