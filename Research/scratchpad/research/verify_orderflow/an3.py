import pickle, random
R='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/research'
rows=pickle.load(open(R+'/verify_orderflow/base_tab.pkl','rb'))
SPL='2026-10-01'
for t in rows:
    f=t['fx']; t['kz']=f is None or f['z']<=2.4; t['kc']=f is None or f['cvd_clv']>=-0.006; t['kb']=t['kz'] and t['kc']
    t['e1']=1 if t['hit1'] else -1; t['e15']=1.5 if t['hit15'] else -1
def cl(S,by):
    d={}
    for t in S: d.setdefault(by(t),[]).append(t)
    return list(d.values())
def boot(S,kk,val,by,it=4000,seed=5):
    C=cl(S,by); rnd=random.Random(seed); ds=[]
    for _ in range(it):
        s=[C[rnd.randrange(len(C))] for _ in C]
        A=[t for c in s for t in c]; K=[t for t in A if t[kk]]
        if not A or not K: continue
        ds.append(sum(t[val] for t in K)/len(K)-sum(t[val] for t in A)/len(A))
    ds.sort(); return ds[int(.025*len(ds))],ds[int(.975*len(ds))], sum(1 for x in ds if x<=0)/len(ds)
te=[t for t in rows if t['t']>=SPL]; tr=[t for t in rows if t['t']<SPL]
for nm,kk in (('z<=2.4','kz'),('cvd','kc'),('both','kb')):
    for val in ('res','e1','e15'):
        o=sum(t[val] for t in te if t[kk])/sum(1 for t in te if t[kk])-sum(t[val] for t in te)/len(te)
        a=boot(te,kk,val,lambda t:t['t'][:10]); b=boot(te,kk,val,lambda t:(t['sym'],t['t'][:10]))
        o2=sum(t[val] for t in tr if t[kk])/sum(1 for t in tr if t[kk])-sum(t[val] for t in tr)/len(tr)
        c=boot(tr,kk,val,lambda t:t['t'][:10])
        print('%-7s %-4s TEST d %+.3f CI(calendar-day clusters) [%+.3f,%+.3f] p1side %.3f | (sym-day) [%+.3f,%+.3f] | TRAIN d %+.3f CI [%+.3f,%+.3f] p %.3f'%(nm,val,o,a[0],a[1],a[2],b[0],b[1],o2,c[0],c[1],c[2]))
# ALL-data
al=rows
for nm,kk in (('z<=2.4','kz'),):
    o=sum(t['res'] for t in al if t[kk])/sum(1 for t in al if t[kk])-sum(t['res'] for t in al)/len(al)
    print('ALL d %+.3f CI'%o,boot(al,kk,'res',lambda t:t['t'][:10]))
# leave-one-symbol-out on TEST and ALL
syms=sorted({t['sym'] for t in rows})
for s in syms:
    for nm,S in (('TEST',te),('ALL',rows)):
        R_=[t for t in S if t['sym']!=s]
        d=sum(t['res'] for t in R_ if t['kz'])/sum(1 for t in R_ if t['kz'])-sum(t['res'] for t in R_)/len(R_)
        print('  drop %-15s %s dE2 %+.3f'%(s,nm,d),end=' |')
    print()
# TEST-only symbols excluded (apples to apples, 8 symbols w/ TRAIN)
core=[t for t in rows if t['sym'] not in ('NSE_NIFTY1','MCX_NATURALGAS')]
for nm,S in (('TRAIN',[t for t in core if t['t']<SPL]),('TEST',[t for t in core if t['t']>=SPL])):
    d=sum(t['res'] for t in S if t['kz'])/sum(1 for t in S if t['kz'])-sum(t['res'] for t in S)/len(S); print('8-sym core',nm,'dE2 %+.3f'%d)
# total R by split
for nm,S in (('TRAIN',tr),('TEST',te),('ALL',rows)):
    print(nm,'total R base %+.0f z %+.0f cvd %+.0f both %+.0f'%(sum(t['res'] for t in S),sum(t['res'] for t in S if t['kz']),sum(t['res'] for t in S if t['kc']),sum(t['res'] for t in S if t['kb'])))
# by month TEST/TRAIN split halves for z: weekly stability
import collections
wk=collections.defaultdict(lambda:[0,0,0,0])
for t in rows:
    w=t['t'][:7]+('a' if int(t['t'][8:10])<=15 else 'b'); x=wk[w]; x[0]+=1; x[1]+=t['res']
    if t['kz']: x[2]+=1; x[3]+=t['res']
print('half-month: n base, E2 base | n kept, E2 kept')
for w in sorted(wk): x=wk[w]; print(' ',w,x[0],'%+.2f'%(x[1]/x[0]),'|',x[2],'%+.2f'%(x[3]/max(1,x[2])))
