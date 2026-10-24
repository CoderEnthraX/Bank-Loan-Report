import json,sys
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0,S+'/fit')
from engine2 import prepare
D=json.load(open(S+'/hunt3/pooled/featV.json'))
def er(o,n=10):
    C=prepare(o['sym'])['C']; i=o['i']; d=o['d']
    p=sum(abs(C[j]-C[j-1]) for j in range(i-n+1,i+1)); return d*(C[i]-C[i-n])/p
from collections import Counter
print(Counter(o['lab'] for o in D))
pos=sorted((er(o),o['lab'],o['sym'],o['t']) for o in D if o['lab'] in('takenA','takenB','must'))
print([ (round(a,3),c,t[5:]) for a,b,c,t in pos[:12]])
import statistics
print('median pos',statistics.median(x[0] for x in pos), 'n<0.3',sum(1 for x in pos if x[0]<0.3),'n<0.25',sum(1 for x in pos if x[0]<0.25))
neg=sorted((er(o),o['lab'],o['sym'],o['t']) for o in D if o['lab'].startswith('extra'))
print([(round(a,3),b,c,t[5:]) for a,b,c,t in neg])
# by-label split of positives
for lab in ('takenA','takenB','must'):
    v=[x[0] for x in pos if x[1]==lab]; 
    if v: print(lab,len(v),'min %.3f'%min(v))
