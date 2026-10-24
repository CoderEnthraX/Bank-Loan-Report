import sys, pickle, statistics as st
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0,S+'/research/ema')
rows=pickle.load(open('screen.pkl','rb'))
for kmin in (0.6,0.7,0.8):
    r=[x for x in rows if x['ktr']>=kmin]; xs=[x['dtr'] for x in r]; ys=[x['dte'] for x in r]
    mx,my=st.mean(xs),st.mean(ys); c=sum((a-mx)*(b-my) for a,b in zip(xs,ys))/((sum((a-mx)**2 for a in xs)*sum((b-my)**2 for b in ys))**.5)
    r.sort(key=lambda x:-x['dtr'])
    print('keep>=%.1f n=%d corr %.3f | top10 TRAIN mean dTEST %+.3f | top50 %+.3f | bottom50 %+.3f | all %+.3f'%(kmin,len(r),c,st.mean(x['dte'] for x in r[:10]),st.mean(x['dte'] for x in r[:50]),st.mean(x['dte'] for x in r[-50:]),my))
# split by op: caps (le) vs floors (ge)
for op in ('le','ge'):
    r=[x for x in rows if x['op']==op and x['ktr']>=0.7]; print(op,'n=%d mean dTRAIN %+.3f mean dTEST %+.3f share both>0 %.2f'%(len(r),st.mean(x['dtr'] for x in r),st.mean(x['dte'] for x in r),sum(x['dtr']>0 and x['dte']>0 for x in r)/len(r)))
