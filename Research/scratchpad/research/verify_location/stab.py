import sys; sys.path.insert(0,"/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/research/verify_location")
from drv import *
import pickle
grid=[{}]
grid+= [{"skipLossDir":n} for n in (1,3,6,12,24,48,100,1000)]
grid+= [{"skipLossOpp":1000},{"skipLossAny":1000},{"skipLossAny":24}]
grid+= [{"loc":[["pdRoom","ge",-t]]} for t in (2,2.5,3,3.4,4,4.5,5,6,8)]
res=pmap(grid)
pickle.dump(res,open('stab.pkl','wb'))
b=res[0]
for r in res:
    f=lambda k:r[k]['E2']
    s=sum(1 for sy in lib.SYMS if r['sym'][sy]['n'] and b['sym'][sy]['n'] and r['sym'][sy]['E2']>b['sym'][sy]['E2'])
    st=sum(1 for sy in lib.SYMS if r['sym'][sy]['n'] and r['sym'][sy]['totR2']>b['sym'][sy]['totR2'])
    print(json.dumps(r['opts']),'n',r['ALL']['n'],'| TRAIN n%d E2 %+.3f d%+.3f | TEST n%d E2 %+.3f d%+.3f (E1 d%+.3f E15 d%+.3f) | ALL tot %+.0f sym/trade %d sym/tot %d'%(
      r['TRAIN']['n'],f('TRAIN'),f('TRAIN')-b['TRAIN']['E2'],r['TEST']['n'],f('TEST'),f('TEST')-b['TEST']['E2'],r['TEST']['E1']-b['TEST']['E1'],r['TEST']['E15']-b['TEST']['E15'],r['ALL']['totR2'],s,st))
