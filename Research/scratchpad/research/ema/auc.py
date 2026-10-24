import sys, pickle
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0,S+'/research'); sys.path.insert(0,S+'/research/ema'); import lib, ev, feats
tab=pickle.load(open('tab.pkl','rb')); tn,te=lib.split(tab)
def auc(tr,nm):
    w=[x['f'][nm] for x in tr if x['f'][nm] is not None and x['res']>0]; l=[x['f'][nm] for x in tr if x['f'][nm] is not None and x['res']<0]
    if not w or not l: return float('nan')
    allv=sorted([(v,1) for v in w]+[(v,0) for v in l]); r=0; i=0; ranks={}
    # rank-sum with ties
    vals=[v for v,_ in allv]; import bisect
    s=0.0
    for v in w: s+=bisect.bisect_left(vals,v)+ (bisect.bisect_right(vals,v)-bisect.bisect_left(vals,v)+1)/2
    U=s-len(w)*(len(w)+1)/2; return U/(len(w)*len(l))
R=[(nm,auc(tn,nm),auc(te,nm),auc(tab,nm)) for nm in feats.names()]
R.sort(key=lambda r:-abs(r[3]-0.5))
print('AUC winners(+2R) vs losers by feature (0.5 = no separation; <0.5 = losers have higher values)')
for r in R[:25]: print('%-22s TRAIN %.3f TEST %.3f ALL %.3f'%r)
both=[r for r in R if (r[1]-0.5)*(r[2]-0.5)>0 and min(abs(r[1]-.5),abs(r[2]-.5))>=0.03]
print('same sign on both halves and |AUC-0.5|>=0.03 on both:',[(r[0],round(r[1],3),round(r[2],3)) for r in both])
import statistics as st; print('median |AUC-0.5| ALL %.3f; max %.3f'%(st.median(abs(r[3]-.5) for r in R),max(abs(r[3]-.5) for r in R)))
# chop regime
ch=lambda x: x['f']['xc_C_E20_24'] is not None and x['f']['xc_C_E20_24']>=6 and x['f']['asl_E20_5'] is not None and x['f']['asl_E20_5']<0.35
a=[x for x in tab if ch(x)]; b=[x for x in tab if not ch(x)]
print('chop regime (>=6 close/EMA20 crosses in 24 bars AND |EMA20 slope5|<0.35ATR): n=%d E %+.3f (TR %+.3f TE %+.3f) | rest n=%d E %+.3f'%(len(a),ev.E(a),ev.E([x for x in a if x in tn]),ev.E([x for x in a if x in te]),len(b),ev.E(b)))
