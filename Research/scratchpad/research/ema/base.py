import sys, time, pickle
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0,S+'/research'); import lib
t=time.time(); tr=lib.run_all(S+'/build/score_ref.py',{}); print(time.time()-t)
a,b=lib.split(tr); print('ALL',lib.fmt(lib.stats(tr))); print('TRAIN',lib.fmt(lib.stats(a))); print('TEST',lib.fmt(lib.stats(b)))
pickle.dump(tr,open(S+'/research/ema/base.pkl','wb'))
P=lib.prepare('GC'); print(len(P['T']), P['T'][0], P['T'][-1], [k for k in P.keys()][:30])
