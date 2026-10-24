import sys, json, random
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/research/orderflow')
import drive, lib
nulls={f:[json.loads(l) for fn in __import__('glob').glob('rnd%d_*.txt'%f) for l in open(fn)] for f in (20,30)}
C={'z<=2.4':{"of_phantom":True,"of_gate":[["z","le",2.4]]},
   'cvd_clv>=-0.006':{"of_phantom":True,"of_gate":[["cvd_clv","ge",-0.006]]},
   'z<=2.4&cvd':{"of_phantom":True,"of_gate":[["z","le",2.4],["cvd_clv","ge",-0.006]]}}
bn,be=lib.split(drive.base)
def daypaired(be,te,key,it=2000):
    days=sorted({x['t'][:10] for x in be}); B={}; T={}
    for x in be: B.setdefault(x['t'][:10],[]).append(key(x))
    for x in te: T.setdefault(x['t'][:10],[]).append(key(x))
    rnd=random.Random(7); ds=[]
    for _ in range(it):
        s=[days[rnd.randrange(len(days))] for _ in days]
        b=[v for d in s for v in B.get(d,[])]; t=[v for d in s for v in T.get(d,[])]
        ds.append(sum(t)/len(t)-sum(b)/len(b))
    ds.sort(); return ds[int(.025*it)],ds[int(.975*it)]
for k,o in C.items():
    tr=lib.run_all(drive.M,o); tn,te=lib.split(tr); s=lib.stats(te); sn=lib.stats(tn)
    out=[k, 'TEST n=%d hit1 %.1f%% hit15 %.1f%% hit2 %.1f%% (base %.1f/%.1f/%.1f)'%(s['n'],100*s['hit1'],100*s['hit15'],100*s['hit2'],100*lib.stats(be)['hit1'],100*lib.stats(be)['hit15'],100*lib.stats(be)['hit2'])]
    for nm,key in (('E2',lambda x:x['res']),('E1',lambda x:1 if x['hit1'] else -1),('E15',lambda x:1.5 if x['hit15'] else -1)):
        lo,hi=lib.boot_diff([dict(res=key(x)) for x in be],[dict(res=key(x)) for x in te])
        plo,phi=daypaired(be,te,key)
        out.append('%s libCI[%+.3f,%+.3f] day-paired CI[%+.3f,%+.3f]'%(nm,lo,hi,plo,phi))
    frac=1-len(tr)/len(drive.base); f=20 if frac<0.25 else 30
    pt=sum(x['teE2']<s['E2'] for x in nulls[f])/len(nulls[f]); pn=sum(x['trE2']<sn['E2'] for x in nulls[f])/len(nulls[f])
    out.append('random-veto null (%d%%): TEST E2 pct %.0f%%, TRAIN E2 pct %.0f%%'%(f,100*pt,100*pn))
    print(' | '.join(out)); sys.stdout.flush()
