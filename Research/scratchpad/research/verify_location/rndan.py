import pickle, statistics as st
b={'ALL':0.150,'TR':0.131,'TE':0.180}
import pickle
bs=pickle.load(open('stab.pkl','rb'))[0]
for f,lab,obs in (('rnd41.pkl','q=0.41 (~80% kept) vs skipLossDir',dict(n=947,te2=0.269-bs['TEST']['E2'],te1=0.099-bs['TEST']['E1'],te15=0.168-bs['TEST']['E15'],tr2=0.137-bs['TRAIN']['E2'],all2=0.188-bs['ALL']['E2'])),
                  ('rnd28.pkl','q=0.28 (~88% kept) vs pdRoom',dict(n=1046,te2=0.197-bs['TEST']['E2'],te1=0.071-bs['TEST']['E1'],te15=0.111-bs['TEST']['E15'],tr2=0.149-bs['TRAIN']['E2'],all2=0.167-bs['ALL']['E2']))):
    R=pickle.load(open(f,'rb')); print(lab,'runs',len(R))
    ns=[r[2]['n'] for r in R]; print(' kept n mean %.0f sd %.0f (observed %d)'%(st.mean(ns),st.pstdev(ns),obs['n']))
    for key,idx,m,o in (('TEST dE2',4,'E2','te2'),('TEST dE1',4,'E1','te1'),('TEST dE1.5',4,'E15','te15'),('TRAIN dE2',3,'E2','tr2'),('ALL dE2',2,'E2','all2')):
        bb={'TEST':bs['TEST'],'TRAIN':bs['TRAIN'],'ALL':bs['ALL']}[{4:'TEST',3:'TRAIN',2:'ALL'}[idx]][m]
        d=sorted(r[idx][m]-bb for r in R); mu=st.mean(d); sd=st.pstdev(d)
        p=sum(1 for x in d if x>=obs[o])/len(d)
        print(' %-10s random mean %+.3f sd %.3f  5-95%% [%+.3f,%+.3f] max %+.3f | observed %+.3f  z=%.2f  one-sided p=%.3f  P(max of 23 draws>=obs)=%.2f'%(key,mu,sd,d[int(.05*len(d))],d[int(.95*len(d))],d[-1],obs[o],(obs[o]-mu)/sd,p,1-(1-p)**23))
    # joint: TRAIN d>=obs AND TEST d>=obs
    j=sum(1 for r in R if r[4]['E2']-bs['TEST']['E2']>=obs['te2'] and r[3]['E2']-bs['TRAIN']['E2']>=obs['tr2'])/len(R); print(' joint TRAIN&TEST both >= observed: %.3f'%j)
