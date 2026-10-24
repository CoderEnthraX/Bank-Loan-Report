import sys, pickle, json
R='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/research'
sys.path.insert(0,R); import lib
rows=pickle.load(open(R+'/verify_orderflow/base_tab.pkl','rb'))
key=lambda t:(t['sym'],t['arm'],t['fill'])
bk={key(t) for t in rows}
for name,opts,fn in [('z',{"of_phantom":True,"of_gate":[["z","le",2.4]]}, lambda f: f['z'] is None or f['z']<=2.4),
                     ('cvd',{"of_phantom":True,"of_gate":[["cvd_clv","ge",-0.006]]}, lambda f: f['cvd_clv'] is None or f['cvd_clv']>=-0.006)]:
    tr=lib.run_all(R+'/orderflow/combo_of.py',opts)
    k={key(t) for t in tr}
    pred={key(t) for t in rows if t['fx'] is None or fn(t['fx'])}
    print(name,'run n',len(k),'subset of base',k<=bk,'pred n',len(pred),'equal',k==pred, 'diff', len(k^pred))
