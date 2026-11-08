import json, numpy as np, pandas as pd, sys
pd.set_option('display.width',250); pd.set_option('display.max_columns',30); pd.set_option('display.max_colwidth',44)
r=pd.DataFrame([json.loads(l) for l in open(sys.argv[1] if len(sys.argv)>1 else 'rows.jsonl')])
for s in 'tv':
    nl=r[s+'l_n'].fillna(0); ns=r[s+'s_n'].fillna(0); n=nl+ns
    r[s+'_comb']=(r[s+'l_avgex'].fillna(0)*nl+r[s+'s_avgex'].fillna(0)*ns)/n
    r[s+'_z']=r[s+'_comb']/(50/np.sqrt(n))
r['allpos']=(r[['tl_avgex','ts_avgex','vl_avgex','vs_avgex']]>0).all(axis=1)
r['pm']=r['tl_pm'].fillna(0)+r['ts_pm'].fillna(0)
r['minz']=r[['t_z','v_z']].min(axis=1)
print('rows',len(r),'all four cells positive:',r.allpos.sum(), 'expected by chance ~', round(len(r)/16,1))
c=['name','tf','pm','tl_avgex','ts_avgex','vl_avgex','vs_avgex','tl_avgpl','ts_avgpl','vl_avgpl','vs_avgpl','t_z','v_z']
print(r[r.allpos].sort_values('minz',ascending=False)[c].round(2).head(25).to_string())
