import sys; sys.path.insert(0,"/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/research/verify_location")
from drv import *
import pickle
def ev2(o):
    tr=lib.run_all(MP,o); a,b=lib.split(tr)
    return (o['randRej'][0],o['randRej'][1],lib.stats(tr),lib.stats(a),lib.stats(b))
if __name__=='__main__':
    q=float(sys.argv[1]); N=int(sys.argv[2]); out=sys.argv[3]
    opts=[{"randRej":[q,s]} for s in range(N)]
    res=[]
    with Pool(4) as p:
        for r in p.imap_unordered(ev2,opts):
            res.append(r)
            if len(res)%20==0: pickle.dump(res,open(out,'wb')); print(len(res),flush=True)
    pickle.dump(res,open(out,'wb'))
