import json, sys, openpyxl
from sim import *
base='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/mcej/'
ars=json.load(open(base+'verify/trades_ars.json')); grid=json.load(open(base+'verify/trades_grid.json'))
wa=openpyxl.load_workbook(base+'out/Gold_Monthly_Crooks_EJ_Auction_Retest.xlsx',data_only=True)
wg=openpyxl.load_workbook(base+'out/Gold_Monthly_Crooks_EJ_Fractal_Grid.xlsx',data_only=True)
col=lambda i: openpyxl.utils.get_column_letter(5+i)
def blk5row(ws):
    for r in range(1,ws.max_row+1):
        v=ws.cell(r,1).value
        if isinstance(v,str) and v.startswith('5. Each month ON ITS OWN'): return r+4
class Rep:
    def __init__(s,n): s.n=n; s.cnt=0; s.bad=0; s.mx=0; s.ex=[]
    def add(s,sheet,cell,wbv,mine):
        s.cnt+=1; d=abs((wbv or 0)-mine)
        if d>s.mx: s.mx=d
        if d>0.01:
            s.bad+=1
            if len(s.ex)<5: s.ex.append((sheet,cell,wbv,mine))
    def show(s): print(s.n,'cells',s.cnt,'>0.01:',s.bad,'maxdiff %.6f'%s.mx, s.ex)
def cmp_block(rep,ws,sheet,r0,fn,idxs=range(31)):
    for i in idxs:
        rule,lv=SETTINGS[i]; vals=fn(rule,lv)
        for k in range(70):
            rep.add(sheet,f'{col(i)}{r0+k}',ws.cell(r0+k,5+i).value,vals[k])
def datecheck(ws,r0):
    d=ws.cell(r0,1).value; e=ws.cell(r0+69,1).value
    print('  dates',ws.title,r0,d,e)
reps=[]
r=Rep('1 Auction block1 M5-S2 + M15-S7')
for s in ['M5-S2','M15-S7']:
    ws=wa[s]; datecheck(ws,8); cmp_block(r,ws,s,8,lambda ru,lv:block1(ars[s],ru,lv))
r.show()
r=Rep('2 Auction block5 M5-S1'); ws=wa['M5-S1']; r0=blk5row(ws); datecheck(ws,r0)
cmp_block(r,ws,'M5-S1',r0,lambda ru,lv:block5(ars['M5-S1'],ru,lv)); r.show()
r=Rep('3 Grid M5 chart block1'); ws=wg['M5 chart']; datecheck(ws,8)
def gsum(f,ch):
    out=[0.0]*70
    for a in grid[ch].values():
        v=f(a); out=[x+y for x,y in zip(out,v)]
    return out
cmp_block(r,ws,'M5 chart',8,lambda ru,lv:gsum(lambda a:block1(a,ru,lv),'M5')); r.show()
r=Rep('4 Grid M15 chart block5 F'); ws=wg['M15 chart']; r0=blk5row(ws); datecheck(ws,r0)
cmp_block(r,ws,'M15 chart',r0,lambda ru,lv:gsum(lambda a:block5(a,ru,lv),'M15'),range(1,7)); r.show()
r=Rep('5 Ladder target test'); ws=wa['Ladder target test']
for sname,row in [('M5-S2',11),('M15-S1',26)]:
    assert ws.cell(row,1).value==sname and ws.cell(row,3).value=='Crooks F'
    a=ars[sname]
    r.add('Ladder target test',f'D{row}',ws.cell(row,4).value,total(a,'F','Off',1000.0))
    for ti,T in enumerate([1000,2000,3000,5000]):
        for li,lv in enumerate(LEVELS[1:]):
            c=5+ti*5+li
            r.add('Ladder target test',f'{openpyxl.utils.get_column_letter(c)}{row}',ws.cell(row,c).value,total(a,'F',lv,float(T)))
r.show()
