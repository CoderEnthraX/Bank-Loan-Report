import sys, json
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0,S+'/fit')
from engine2 import prepare
from engine import rma
D=json.load(open('feat.json'))
pos=[o for o in D if o['lab'] in('takenA','takenB','must')]; neg=[o for o in D if o['lab'].startswith('extra')]
C2={}
def get(sym):
    if sym in C2: return C2[sym]
    P=prepare(sym); A={n:rma(P['tr'],n) for n in (7,10,14,20,28)}
    tr=P['tr']; sm={n:[None if i<n else sum(tr[i-n+1:i+1])/n for i in range(len(tr))] for n in (14,20)}
    C2[sym]=(P,A,sm); return C2[sym]
def fam(o):
    P,A,sm=get(o['sym']); i=o['i']; d=o['d']; O,H,L,C=P['O'],P['H'],P['L'],P['C']; a=A[14][i]; out={}
    for k in range(5,16):
        out[f'C-C{k}']=d*(C[i]-C[i-k])/a
        out[f'C-O{k}']=d*(C[i]-O[i-k])/a
        out[f'C-hl2{k}']=d*(C[i]-(H[i-k]+L[i-k])/2)/a
        out[f'C-ext{k}']=d*(C[i]-(min(L[i-k:i]) if d>0 else max(H[i-k:i])))/a
        out[f'C-sma{k}']=d*(C[i]-sum(C[i-k+1:i+1])/k)/a
        out[f'C-smaPrev{k}']=d*(C[i]-sum(C[i-k:i])/k)/a
        out[f'C-C{k}/atrk']=d*(C[i]-C[i-k])/A[14][i-k]
        out[f'C-C{k}/atr1']=d*(C[i]-C[i-k])/A[14][i-1]
        out[f'O-C{k}']=d*(O[i]-C[i-k])/a
        out[f'C1-C{k+1}']=d*(C[i-1]-C[i-k-1])/a
        for n in (7,10,20,28): out[f'C-C{k}/atr{n}']=d*(C[i]-C[i-k])/A[n][i]
        for n in (14,20): out[f'C-C{k}/smaTR{n}']=d*(C[i]-C[i-k])/sm[n][i]
        out[f'pct{k}']=d*(C[i]/C[i-k]-1)*1e4
        out[f'H-H{k}' if d>0 else f'H-H{k}']=d*((H[i]-H[i-k]) if d>0 else (L[i]-L[i-k]))/a
        out[f'L-L{k}']=d*((L[i]-L[i-k]) if d>0 else (H[i]-H[i-k]))/a
    return out
F=[fam(o) for o in pos]; G=[fam(o) for o in neg]
res=[]
for k in F[0]:
    lo=min(f[k] for f in F); hi=max(f[k] for f in F)
    b=[neg[j]['sym'][:2]+neg[j]['t'][5:] for j,g in enumerate(G) if g[k]<lo]
    a=[neg[j]['sym'][:2]+neg[j]['t'][5:] for j,g in enumerate(G) if g[k]>hi]
    res.append((max(len(a),len(b)),k,'<%.3g'%lo if len(b)>=len(a) else '>%.3g'%hi, b if len(b)>=len(a) else a))
res.sort(key=lambda r:-r[0])
for r in res[:20]: print(r)
