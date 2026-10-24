import sys, pickle
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0,S+'/research'); sys.path.insert(0,S+'/research/ema'); import lib, ev, feats
tab=pickle.load(open('tab.pkl','rb')); tn,te=lib.split(tab)
for x in tab:
    F=feats.compute(x['sym'])
    for tf in ('h60','h6s','h6a','h6b'): x['f'][tf+'_asl_E20_3']=feats.value(F,tf+'_asl_E20_3',x['arm'],x['dir'],x['entry'])
print('check h60 unchanged:', sum(1 for x in tab if x['f']['h60_asl_E20_3']!=pickle.load(open('tab.pkl','rb'))[0]['f']['h60_asl_E20_3']) >= 0)
for tf,lab in (('h60','UTC-aligned, completed incl. closing bar'),('h6s','UTC-aligned, strictly previous 1h bar'),('h6a','session-anchored, completed incl. closing bar'),('h6b','session-anchored, strictly previous')):
    nm=tf+'_asl_E20_3'
    for th in (1.4,1.65,2.0):
        a=[x for x in tn if x['f'][nm] is None or x['f'][nm]<=th]; b=[x for x in te if x['f'][nm] is None or x['f'][nm]<=th]; al=a+b
        print('%-46s <=%.2f TRAIN keep %.0f%% dE %+.3f | TEST keep %.0f%% dE %+.3f | tot %+.0f syms %d/10'%(lab,th,100*len(a)/len(tn),ev.E(a)-ev.E(tn),100*len(b)/len(te),ev.E(b)-ev.E(te),sum(x['res'] for x in al),ev.syms_better(tab,al)[0]))
