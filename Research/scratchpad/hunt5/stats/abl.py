import json, subprocess, re
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
D=S+'/hunt5/stats'
C={"slopeCross":True,"minOpenBars":0,"cooldownBars":1,"dayStopR":0,"tightOut":True,"erMin":0.2}
DEF={"slopeCross":False,"minOpenBars":1,"cooldownBars":2,"dayStopR":3.0,"tightOut":False,"erMin":0.0}
cfgs=[('CANDIDATE',C)]+[('drop '+k,{**C,k:DEF[k]}) for k in C]+[('none ({} baseline)',{})]
for name,o in cfgs:
    j=json.dumps(o)
    a=subprocess.run(['python3','-I','score2.py',D+'/combo.py',j,'d'],cwd=S+'/xl',capture_output=True,text=True).stdout
    b=subprocess.run(['python3','-I','extrasB.py',D+'/combo.py',j],cwd=S+'/xl',capture_output=True,text=True).stdout
    m=subprocess.run(['python3','-I',S+'/hunt4/modelday.py',j],capture_output=True,text=True).stdout
    A=re.search(r"'exact': (\d+), 'near': (\d+), 'miss': (\d+), 'extra': (\d+)",a).groups()
    B=re.search(r'time-matched (\d+), missed (\d+), stop correct (\d+)/',a).groups()
    px=[l for l in b.splitlines() if l.startswith('PROV')]
    md=re.search(r'matched (\d+) / 6',m).group(1)
    bad=[l.split(':')[0] for l in m.splitlines() if l.startswith('BAD')]
    print(f"{name:22s} A {A[0]}/{A[2]}/{A[3]}  B match {B[0]}/42 stop {B[2]}  provB {len(px)}  MODELDAY {md}/6 {bad}")
    print('    Alist:',[l.strip() for l in a.splitlines() if l.startswith('   A')])
    print('    Blist:',[l.strip()[:60] for l in a.splitlines() if l.startswith('   B')])
    print('    prov:',[l[15:60] for l in px])
