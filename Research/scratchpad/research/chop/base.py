import sys, time, pickle
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/research'); import lib
t0 = time.time(); tr = lib.run_all(S + '/build/score_ref.py', {}); print('sec', time.time() - t0)
tn, te = lib.split(tr)
for k, v in (('ALL', tr), ('TRAIN', tn), ('TEST', te)): print(k, lib.fmt(lib.stats(v)))
pickle.dump(tr, open(S + '/research/chop/base.pkl', 'wb'))
