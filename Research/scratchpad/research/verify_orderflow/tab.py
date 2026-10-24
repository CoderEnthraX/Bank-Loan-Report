import sys, pickle, json
R='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/research'
sys.path.insert(0,R); sys.path.insert(0,R+'/orderflow')
import lib, of
base=lib.run_all()
rows=[]
Fc={}
for t in base:
    F=of.features(t['sym']); fx=of.sig_features(F,t['arm'],t['dir'],t['entry'],10)
    t=dict(t); t['fx']=None if fx is None else {k:fx[k] for k in ('z','zT','cvd_clv','zEntry')}
    t['bars']=t['arm']-F['sst'][t['arm']]
    rows.append(t)
pickle.dump(rows,open(R+'/verify_orderflow/base_tab.pkl','wb'))
print(len(rows), sum(1 for r in rows if r['fx'] is None))
