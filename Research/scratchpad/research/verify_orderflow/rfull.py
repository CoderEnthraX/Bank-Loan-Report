import sys, pickle, random, json
R='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/research'
sys.path.insert(0,R); import lib
rows=pickle.load(open(R+'/verify_orderflow/base_tab.pkl','rb'))
key=lambda t:(t['sym'],t['arm'],t['fill'])
out=[]
for k in range(int(sys.argv[1]),int(sys.argv[2])):
    tr=lib.run_all(R+'/orderflow/combo_of.py',{"of_phantom":True,"of_gate":[["rand%d"%k,"ge",0.25]]})
    got={key(t) for t in tr}
    pred={key(t) for t in rows if t['fx'] is None or random.Random('%s:%d:%d'%(t['sym'],t['arm'],k)).random()>=0.25}
    tn,te=lib.split(tr); bn,be=lib.split(rows)
    print(json.dumps(dict(k=k,n=len(tr),equal=got==pred,teE2=lib.stats(te)['E2'],trE2=lib.stats(tn)['E2'],dTE=lib.stats(te)['E2']-lib.stats(be)['E2'])),flush=True)
