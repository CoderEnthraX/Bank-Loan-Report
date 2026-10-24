import pickle,sys
tr=pickle.load(open('base_feats.pkl','rb'))
SPL='2026-10-01'
keys=sorted({k for x in tr if x['f'] for k in x['f']})
def E(v): return (sum(x['res'] for x in v)/len(v), sum(x['hit1'] for x in v)/len(v)) if v else (0,0)
for k in keys:
    tn=[x for x in tr if x['f'] and x['f'].get(k) is not None and x['t']<SPL]
    te=[x for x in tr if x['f'] and x['f'].get(k) is not None and x['t']>=SPL]
    vals=sorted(x['f'][k] for x in tn); q=[vals[int(len(vals)*j/5)] for j in range(1,5)]
    def b(x): return sum(x['f'][k]>=c for c in q)
    row=[]
    for g in range(5):
        a=[x for x in tn if b(x)==g]; c=[x for x in te if b(x)==g]
        row.append('%+.2f/%+.2f' % (E(a)[0], E(c)[0]))
    print('%-16s q=%s | TRAIN/TEST E2 by quintile: %s' % (k, ' '.join('%.2f'%v for v in q), '  '.join(row)))
