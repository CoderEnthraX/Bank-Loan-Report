import json, numpy as np, pandas as pd
pd.set_option('display.width',250); pd.set_option('display.max_colwidth',50)
rows=[json.loads(l) for f in ('rows.jsonl','rows_cand.jsonl') for l in open(f)]
r=pd.DataFrame(rows).drop_duplicates(['name','tf'])
n=0; s=0
for c in ('tl','ts','vl','vs'):
    r[c+'_n']=r[c+'_n'].fillna(0); r[c+'_avgex']=r[c+'_avgex'].fillna(0)
N=r.tl_n+r.ts_n+r.vl_n+r.vs_n
r['pooled']=(r.tl_n*r.tl_avgex+r.ts_n*r.ts_avgex+r.vl_n*r.vl_avgex+r.vs_n*r.vs_avgex)/N
r['pz']=r.pooled/(50/np.sqrt(N))
print('variants:',len(r),' pooled z mean %.2f sd %.2f'%(r.pz.mean(),r.pz.std()))
print('count pz>2: %d  pz>2.5: %d  pz>3: %d'%((r.pz>2).sum(),(r.pz>2.5).sum(),(r.pz>3).sum()))
r['all4']=(r[['tl_avgex','ts_avgex','vl_avgex','vs_avgex']]>0).all(axis=1)
print(r.sort_values('pz',ascending=False)[['name','tf','pooled','pz','all4']].head(20).round(2).to_string())
