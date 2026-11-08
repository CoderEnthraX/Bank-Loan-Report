import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/agentA')
import lib, numpy as np, time
t=time.time()
b=lib.ctx('M15'); print(time.time()-t)
# sanity: random entries should be ~0
rng=np.random.default_rng(5); i=np.sort(rng.choice(np.flatnonzero(b['ok']&(b['split']!='test')),4000,replace=False)); d=rng.choice([-1,1],len(i))
e=b['C'][i]; st=e-d*1.8*b['atr'][i]
lib.run('M15',i,d,e,st,1,name='sanity random 1.8',save=False)
st=e-d*0.7*b['atr'][i]; lib.run('M15',i,d,e,st,1,name='sanity random 0.7',save=False)
print(time.time()-t)
