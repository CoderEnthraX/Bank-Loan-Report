import json, sys
sys.path.insert(0,'.')
import pf
from feat import prepare, rma
D=json.load(open('featV.json'))
V=[o['sym']+'|'+o['t'] for o in D if o['lab']=='extraV']
TR={}
rows=[]
for o in D:
    s=o['sym']; P=prepare(s); H,L,C=P['H'],P['L'],P['C']; A=rma(P['tr'],14)
    if s not in TR: TR[s]=pf.run(s,{"dayStopR":0,"veto":V})
    i=o['i']; d=o['d']; a=A[i]
    past=[m for m in TR[s] if m['fill']<i]
    same=[m for m in past if m['dir']==d]
    f={}
    for nm,lst in (('same',same),('any',past)):
        if lst:
            m=lst[-1]; j=m['fill']
            ext=max(H[j:i]) if d>0 else min(L[j:i])
            f[nm]=d*(C[i]-ext)/a; f[nm+'Age']=i-j; f[nm+'Exited']=m['exit'] is not None and m['exit']<i
            # extreme since exit
            if m['exit'] is not None and m['exit']<i:
                e=m['exit']; ext2=max(H[e:i]) if d>0 else min(L[e:i]); f[nm+'X']=d*(C[i]-ext2)/a
            else: f[nm+'X']=None
        else: f[nm]=None; f[nm+'Age']=None; f[nm+'X']=None
    rows.append((o['lab'],s,o['t'],d,f))
for r in sorted(rows,key=lambda r:(r[4]['same'] if r[4]['same'] is not None else 99)):
    f=r[4]
    if f['same'] is None or f['same']<0.6 or r[0]=='extraV':
        print('%-7s %-6s %s %+d same %s age %s | any %s age %s | sameX %s anyX %s'%(r[0],r[1],r[2],r[3],None if f['same'] is None else round(f['same'],3),f['sameAge'],None if f['any'] is None else round(f['any'],3),f['anyAge'],None if f['sameX'] is None else round(f['sameX'],3),None if f['anyX'] is None else round(f['anyX'],3)))
