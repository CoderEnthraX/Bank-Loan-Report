"""builds the variant table (markdown) from variants.csv -> table.md"""
import pandas as pd, numpy as np
B = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/agentB'
v = pd.read_csv(B + '/variants.csv'); v = v[v.family != 'detail'].copy()
v = v.drop_duplicates(subset=['tf', 'name', 'n_mo', 'trL', 'trS', 'vaL', 'vaS'])
MIN = dict(M1=20, M5=20, M15=8, H1=3)
ntr = v.nL_tr.fillna(0) + v.nS_tr.fillna(0); nva = v.nL_va.fillna(0) + v.nS_va.fillna(0)
v['z_tr'] = v.tr_all / (50 / np.sqrt(ntr)); v['z_va'] = v.va_all / (50 / np.sqrt(nva))
def verdict(r):
    cells = dict(trL=r.trL, trS=r.trS, vaL=r.vaL, vaS=r.vaS)
    if any(pd.isna(x) for x in cells.values()): return 'one direction only' + (' (both splits >0)' if all((x > 0) for x in cells.values() if not pd.isna(x)) else ' (fails)')
    neg = [k for k, x in cells.items() if x <= 0]
    few = r.n_mo < MIN[r.tf]
    if neg: return 'fail (%s <=0)' % ','.join(neg) + (', few trades' if few else '')
    if few: return 'all >0 but too few trades'
    if r.z_tr >= 3 and r.z_va >= 2: return '**all >0, train >=3 se, valid >=2 se**'
    return 'all >0 but weak (<3 se train or <2 se valid)'
v['verdict'] = v.apply(verdict, axis=1)
fam = {'mech': 'entry mechanics', 'gate': 'gates (lim / mkt / pb entries)', 'pb': 'pullback entry variants', 'combo': 'combinations + fades',
       'fadehours': 'fade by 3h NY block', 'fade2': 'NY-afternoon fade variants'}
out = ['| # | family | variant | TF | n/mo (train) | train L | train S | valid L | valid S | z train | z valid | verdict |', '|' + '---|' * 12]
for k, r in enumerate(v.itertuples(), 1):
    f = lambda x: '' if pd.isna(x) else '%+.2f' % x
    out.append('| %d | %s | %s | %s | %.1f | %s | %s | %s | %s | %.1f | %.1f | %s |' % (k, fam[r.family], r.name.replace('|', '/'), r.tf, r.n_mo,
               f(r.trL), f(r.trS), f(r.vaL), f(r.vaS), r.z_tr, r.z_va, r.verdict))
open(B + '/table.md', 'w').write('\n'.join(out) + '\n')
print(len(v), 'variants;', v.verdict.value_counts().to_dict())
