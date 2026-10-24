import sys, pickle
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0,S+'/research'); sys.path.insert(0,S+'/research/ema'); import lib, ev
tab=pickle.load(open('tab.pkl','rb')); tn,te=lib.split(tab)
FL=[('h60_asl_E20_3',1.652),('sl_E200_10',0.547),('sp_9.20.50.100.200',6.218),('h15_sl_E200_3',0.201),('h15_rw_E20_E50',2.885),('h60_sl_E9_3',1.622)]
def nflag(x): return sum(1 for nm,th in FL if x['f'][nm] is not None and x['f'][nm]>th)
for k in range(1,7):
    a=[x for x in tn if nflag(x)<k]; b=[x for x in te if nflag(x)<k]; al=a+b
    print('veto if flags>=%d | TRAIN keep %.0f%% dE %+.3f | TEST keep %.0f%% dE %+.3f | ALL tot %+.0f syms %d/10'%(k,100*len(a)/len(tn),ev.E(a)-ev.E(tn),100*len(b)/len(te),ev.E(b)-ev.E(te),sum(x['res'] for x in al),ev.syms_better(tab,al)[0]))
# overlap with each other
import itertools
for (n1,t1),(n2,t2) in itertools.combinations(FL,2):
    s1={id(x) for x in tab if x['f'][n1] is not None and x['f'][n1]>t1}; s2={id(x) for x in tab if x['f'][n2] is not None and x['f'][n2]>t2}
    print('%s & %s jaccard %.2f'%(n1,n2,len(s1&s2)/len(s1|s2)))
