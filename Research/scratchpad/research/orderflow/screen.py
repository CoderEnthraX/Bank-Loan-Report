import sys, pickle
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0,S+'/research'); sys.path.insert(0,S+'/research/orderflow')
import lib, of
tr=lib.run_all()
for x in tr:
    F=of.features(x['sym']); x['f']=of.sig_features(F,x['arm'],x['dir'],x['entry'])
pickle.dump(tr,open('base_feats.pkl','wb'))
print(len(tr), sum(1 for x in tr if x['f'] is None))
