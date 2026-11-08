import json, numpy as np, pandas as pd
rows=[json.loads(l) for f in ('rows.jsonl','rows_cand.jsonl') for l in open(f)]
r=pd.DataFrame(rows).drop_duplicates(['name','tf']).reset_index(drop=True)
for c in ('tl','ts','vl','vs'):
    r[c+'_n']=r[c+'_n'].fillna(0)
N=r.tl_n+r.ts_n+r.vl_n+r.vs_n
r['pooled']=sum(r[c+'_n']*r[c+'_avgex'].fillna(0) for c in ('tl','ts','vl','vs'))/N
r['pz']=r.pooled/(50/np.sqrt(N))
r['pm']=(r.tl_n+r.ts_n)/36.0
TH={'M5':20,'M15':8,'H1':3}
fam={'orb':'1 ORB / Asian range','sweep':'2 Liquidity sweeps','vwap':'3 VWAP','time':'4 Data bars / momentum / TOD','mr':'5 Mean reversion / NR7 / gaps / round numbers',
     'stopgen':'6 Generic stop-entry controls','candA':'7 Sensitivity A (NY open range)','candB':'8 Sensitivity B (PDH/PDL sweep)','candC':'9 Sensitivity C (round $ break)','candD':'9 Sensitivity D (VWAP distance fade)'}
def verdict(x):
    cells=[x[c+'_avgex'] for c in ('tl','ts','vl','vs')]
    one=any(pd.isna(v) for v in cells)
    if one: return 'one-direction TOD reference'
    allp=all(v>0 for v in cells)
    few=x.pm<TH[x.tf]
    v='FAIL' if not allp else ('all 4 > 0, z %.1f (noise level)'%x.pz if x.pz<2 else 'all 4 > 0, pooled z %.1f'%x.pz)
    return v+(' ; few trades' if few else '')
r['verdict']=r.apply(verdict,axis=1)
f=lambda v: '' if pd.isna(v) else '%+.1f'%v
out=['| # | family | setup (variant) | TF | n/mo (train, filled) | train L | train S | valid L | valid S | placebo-adj train L/S | placebo-adj valid L/S | verdict |','|---|---|---|---|---|---|---|---|---|---|---|---|']
for k,x in r.iterrows():
    out.append('| %d | %s | %s | %s | %.1f | %s | %s | %s | %s | %s / %s | %s / %s | %s |'%(k+1,fam.get(x.family,x.family),x['name'],x.tf,x.pm,f(x.tl_avgex),f(x.ts_avgex),f(x.vl_avgex),f(x.vs_avgex),
        f(x.tl_avgpl),f(x.ts_avgpl),f(x.vl_avgpl),f(x.vs_avgpl),x.verdict))
open('table.md','w').write('\n'.join(out)+'\n')
print(len(r),'rows; FAIL',(r.verdict.str.startswith('FAIL')).sum(),'; all4>0',(r.verdict.str.startswith('all')).sum(),'; z>=2',(r.verdict.str.contains('pooled')).sum())
print(r[r.verdict.str.contains('pooled')][['name','tf','pm','pz']].round(2).to_string())
