import sys, pickle; S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'; sys.path.insert(0,S+'/gold')
import anaA
tf=sys.argv[1]
D=pickle.load(open(S+'/gold/stageB_%s.pkl'%tf,'rb')); R=D['res']
d0=anaA.metrics(pickle.load(open(S+'/gold/sweep_%s.pkl'%tf,'rb'))['res']['default'])
rows=[(n,anaA.metrics(tr)) for n,tr in R.items() if tr]
rows=[r for r in rows if r[1] and r[1]['nA']>=0.15*d0['nA']]
rows.sort(key=lambda r:-r[1]['EcA'])
print('%s default: 2021-23 net %+.3f  2024-26 net %+.3f  (%d combinations)'%(tf,d0['EcA'],d0['EcB'],len(rows)))
for n,m in rows[:12]:
    print('  %-100s %5d | A %+.3f | B %+.3f | yrs+ %d/6 | win %.1f%% | streak W/L %d/%d'%(n[:100],m['n'],m['EcA'],m['EcB'],m['ypos'],100*m['win'],m['maxW'],m['maxL']))
pos=[r for r in rows if r[1]['EcA']>0]; print('  positive after spread in 2021-23: %d ; of those positive in 2024-26: %d'%(len(pos),sum(1 for r in pos if r[1]['EcB']>0)))
