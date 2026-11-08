import sys; S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'; sys.path.insert(0,S+'/entry')
import pickle, numpy as np, kit
for tf in ('M5','M15'):
    df=pickle.load(open(S+'/entry/ds_%s.pkl'%tf,'rb'))
    print(tf, df.shape); print(list(df.columns))
    f=df[df.filled & (df.split!='test')]
    print(f.fill_delay.value_counts().sort_index().to_dict(), 'fill rate', df[df.split!='test'].filled.mean())
    print(f.groupby(['split','dir']).size().to_dict())
    print(kit.baseline(tf))
