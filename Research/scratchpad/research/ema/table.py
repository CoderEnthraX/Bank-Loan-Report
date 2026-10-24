import sys, pickle
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0,S+'/research/ema'); import feats
base=pickle.load(open('base.pkl','rb')); N=feats.names()
for x in base:
    F=feats.compute(x['sym']); x['f']={nm:feats.value(F,nm,x['arm'],x['dir'],x['entry']) for nm in N}
pickle.dump(base,open('tab.pkl','wb'))
miss={nm:sum(x['f'][nm] is None for x in base) for nm in N}
print({k:v for k,v in miss.items() if v})
