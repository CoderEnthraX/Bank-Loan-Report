import sys, json, pickle, os
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/research')
import lib
from multiprocessing import Pool
R='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/research'
MOD=R+'/entry/combo_entry.py'
def job(o):
    return json.dumps(o,sort_keys=True), lib.run_all(MOD,o)
if __name__=='__main__':
    grid=[{}]
    for b in [0.5,0.6,0.8,1.0,1.25,1.5,1.75]: grid.append({'beR':b})
    for rb in [2,3,4,5,6,8,12]:
        grid.append({'retestBars':rb,'beR':1.0})
        if rb!=5: grid.append({'retestBars':rb})
    for rb in [3,4]:
        for b in [0.8,1.25,1.5]: grid.append({'retestBars':rb,'beR':b})
    with Pool(4) as p: res=dict(p.map(job,grid))
    pickle.dump(res,open('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/research/verify_entry/grid.pkl','wb'))
    print('done',len(res))
