import json
m=json.load(open('mine.json')); e=json.load(open('../expected.json'))
for k in m:
    d=[abs(a-b) for a,b in zip(m[k],e[k])]
    bad=[(i,e[k][i],m[k][i]) for i in range(70) if d[i]>0.01]
    print(k,'months',len(d),'differ>0.01:',len(bad),'maxdiff',max(d),'profit',sum(x>0 for x in m[k]),'loss',sum(x<0 for x in m[k]),'zero',sum(x==0 for x in m[k]))
    for i,a,b in bad[:5]: print('  ',i,a,b)
