import sys; S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'; sys.path.insert(0,S+'/research')
import lib
M=S+'/build/score_ref.py'
base=lib.run_all(M,{}); btn,bte=lib.split(base)
print('base  ALL %+.3f TR %+.3f TE %+.3f n %d tot %+.0f'%(lib.stats(base)['E2'],lib.stats(btn)['E2'],lib.stats(bte)['E2'],len(base),sum(x['res'] for x in base)))
for mx in (9.0,10.0,11.0,11.8,12.0,12.5,13.0,14.0,16.0):
    f=lib.run_all(M,{"chopOn":True,"chopMax":mx}); tn,te=lib.split(f)
    imp=sum((sum(x['res'] for x in f if x['sym']==s)/max(1,sum(1 for x in f if x['sym']==s)))>(sum(x['res'] for x in base if x['sym']==s)/max(1,sum(1 for x in base if x['sym']==s))) for s in lib.SYMS)
    ng=[x['res'] for x in f if x['sym']=='MCX_NATURALGAS']
    print('max %5.1f ALL %+.3f TR %+.3f TE %+.3f kept %.0f%% tot %+.0f improved %d/10 NG %+.3f'%(mx,lib.stats(f)['E2'],lib.stats(tn)['E2'],lib.stats(te)['E2'],100*len(f)/len(base),sum(x['res'] for x in f),imp,sum(ng)/max(1,len(ng))))
