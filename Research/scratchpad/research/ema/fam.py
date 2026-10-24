import sys, pickle
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0,S+'/research'); sys.path.insert(0,S+'/research/ema'); import lib, ev
rows=pickle.load(open('screen.pkl','rb'))
def fam(nm):
    if nm.startswith('h15') or nm.startswith('h60'):
        tf=nm[:3]; q=nm.split('_')[1]
        return tf+('-compress' if q in ('rw','asl','xc') else '-trend/location')
    p=nm.split('_')[0]
    return {'px':'5m price-vs-MA','sl':'5m slope','asl':'5m flatness','stk':'5m stack','rs':'5m ribbon signed','rw':'5m ribbon width','sp':'5m ribbon width','spr':'5m compression ratio',
            'xc':'crosses','pb':'pullback','ve':'VWAP-vs-EMA','ave':'VWAP-vs-EMA chop','en':'entry distance'}[p] + ('/SMA-HMA-KAMA' if any(k in nm for k in ('S20','S50','HMA','KAMA')) else '')
best={}
for r in rows:
    if r['ktr']<0.70 or r['str']<6: continue
    f=fam(r['nm'])
    if f not in best or r['dtr']>best[f]['dtr']: best[f]=r
for f,r in sorted(best.items(), key=lambda kv:-kv[1]['dtr']):
    print('%-32s %-20s %s %7.3f | TRAIN keep %.0f%% dE %+.3f syms %d | TEST keep %.0f%% dE %+.3f'%(f,r['nm'],r['op'],r['th'],100*r['ktr'],r['dtr'],r['str'],100*r['kte'],r['dte']))
pickle.dump(best,open('fam.pkl','wb'))
