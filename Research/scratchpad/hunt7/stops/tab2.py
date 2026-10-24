import sys, json
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/hunt7/stops')
sys.argv = [sys.argv[0], '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/hunt7/stops/combo_f.py', json.dumps({"slopeCross":True,"minOpenBars":0,"cooldownBars":1,"dayStopR":0,"tightOut":True,"erMin":0.2,"impBody":50})]
import tab
for src, sym, ft, d, lab, m, P in tab.rows:
    if m is None: continue
    F = m['feat']; A = F['A']; same = F['bullN'] if d > 0 else F['bearN']
    if same != 0 and lab != 'HALF': continue
    net = d * (F['prevNet'] or 0)
    f = lambda x: d * x / A
    pr = F['pdH'] - F['pdL']
    print(f"{src:8s} {sym[:8]:8s} {ft[5:]} {'L' if d>0 else 'S'} {lab:4s} m{'T' if m['tight'] else 'n'} k{F['k']:3d} net{net:+3d} n{F['pBull']+F['pBear']:2d} | pdC-pdV{f(F['pdC']-F['pdV']):+5.1f} pdC-pdO{f(F['pdC']-F['pdO']):+5.1f} O-pdC{f(F['sesO']-F['pdC']):+5.1f} O-pdV{f(F['sesO']-F['pdV']):+5.1f} C-pdV{f(F['C']-F['pdV']):+5.1f} C-sesO{f(F['C']-F['sesO']):+5.1f} pdCloc{(F['pdC']-F['pdL'])/pr if d>0 else (F['pdH']-F['pdC'])/pr:4.2f} pdRngA{pr/A:5.1f} Cloc{(F['C']-F['pdL'])/pr if d>0 else (F['pdH']-F['C'])/pr:5.2f} rngA{F['rngA']:.2f} prev{F['prevDir']},{F['prevRes']}")
