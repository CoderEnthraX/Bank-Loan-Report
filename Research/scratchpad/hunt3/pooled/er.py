import json, sys
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0,S+'/fit')
from engine2 import prepare
D=json.load(open(sys.argv[1] if len(sys.argv)>1 else 'featV.json'))
def er(o,n,src='C'):
    P=prepare(o['sym']); C=P['C']; i=o['i']; d=o['d']
    path=sum(abs(C[j]-C[j-1]) for j in range(i-n+1,i+1))
    return d*(C[i]-C[i-n])/path if path else 0
pos=[o for o in D if o['lab'] in ('takenA','takenB','must')]; neg=[o for o in D if o['lab'].startswith('extra')]
for n in range(5,21):
    pv=sorted((er(o,n),o['sym'],o['t']) for o in pos); nv=[(round(er(o,n),3),o['sym'][:2]+o['t'][5:]) for o in neg]
    print(n,'pos min %.3f %s %s, 2nd %.3f %s %s'%(pv[0]+pv[1]),'| neg',' '.join('%s:%.3f'%(b[-11:],a) for a,b in nv), '| rejected', sum(1 for a,b in nv if a<pv[0][0]))
