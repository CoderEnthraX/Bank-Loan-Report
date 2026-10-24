import sys, pickle
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0,S+'/research'); sys.path.insert(0,S+'/research/ema'); import lib, ev
tab=pickle.load(open('tab.pkl','rb'))
F=['rw_E9_E21','sp_9.21.50','spr_9.21.50_48','asl_E20_5','asl_E50_5','asl_KAMA_5','xc_C_E20_24','xc_C_E20_48','xc_E9_E21_48','xc_C_V_48','ave_E20','ave_E50','h15_rw_E9_E21','h15_rw_E20_E50','h15_asl_E20_3','h15_xc_16','h60_rw_E20_E50','h60_asl_E20_3','h60_xc_16',
   'px_E20','px_E50','px_E200','en_E20','sl_E20_5','sl_E50_5','stk_9.21.50','stk_9.20.50.100.200','h15_px_E20','h15_stk_9.21.50','h60_stk_9.21.50','h60_px_E20','pb_E20_6','pb_E9_6','ve_E20']
def q(tr,nm,k=5):
    v=sorted(set(x['f'][nm] for x in tr if x['f'][nm] is not None))
    xs=sorted((x for x in tr if x['f'][nm] is not None), key=lambda x:x['f'][nm]); n=len(xs); out=[]
    for j in range(k):
        s=xs[j*n//k:(j+1)*n//k]; out.append((s[0]['f'][nm], s[-1]['f'][nm], len(s), ev.E(s), sum(x['hit2'] for x in s)/len(s)))
    return out
tn,te=lib.split(tab)
print('E2 per quintile (low -> high feature value); ALL | TRAIN | TEST ; hit2R%% ALL')
for nm in F:
    a=q(tab,nm); b=q(tn,nm); c=q(te,nm)
    print('%-22s ALL '%nm+' '.join('%+.2f'%r[3] for r in a)+' | TR '+' '.join('%+.2f'%r[3] for r in b)+' | TE '+' '.join('%+.2f'%r[3] for r in c)+
          ' | hit '+' '.join('%2.0f'%(100*r[4]) for r in a)+' | edges '+' '.join('%.2f'%r[1] for r in a[:4]))
