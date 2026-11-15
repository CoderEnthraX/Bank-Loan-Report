import json, datetime, sys
import openpyxl
from money import run, SETTINGS
V='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/mcej2/'
D=json.load(open(V+'verify/trades_user.json'))
for k,v in D.items():
    for t in v['trades']: t['_exitR']=v['exitR']
MONTHS=[(2021+(i//12), i%12+1) for i in range(70)]
def ym(s): return (int(s[:4]), int(s[5:7]))
def monthly(trades, rule, lvl, key):
    pn = run(trades, rule, lvl)
    res = {m:0.0 for m in MONTHS}
    for t,p in zip(trades,pn):
        m = ym(t[key])
        if m in res: res[m]+=p
        else: print('month outside',m)
    return res
def find_block5(ws):
    for r in range(1,ws.max_row+1):
        v=ws.cell(r,1).value
        if isinstance(v,str) and v.startswith('5. Each month ON ITS OWN'): return r+4
def compare(wbfile, sheet, key, block, name):
    wb=openpyxl.load_workbook(V+'out/'+wbfile,data_only=True)
    ws=wb[sheet]
    setup = 'off' if 'AllFiltersOff' in wbfile else 'on'
    tf, tp = sheet.split()
    trades = D[f'{tf}|{setup}|{tp}']['trades']
    if block==1: r0=8
    else: r0=find_block5(ws)
    n=0; bad=[]; mx=0
    # verify month labels
    for i,m in enumerate(MONTHS):
        a=ws.cell(r0+i,1).value
        assert (a.year,a.month)==m,(sheet,r0+i,a,m)
    for si,(rule,lvl) in enumerate(SETTINGS):
        col=5+si
        if block==1:
            res=monthly(trades,rule,lvl,'exit')
        else:
            res={}
            for m in MONTHS:
                sub=[t for t in trades if ym(t['entry'])==m]
                res[m]=sum(run(sub,rule,lvl)) if sub else 0.0
        for i,m in enumerate(MONTHS):
            w=ws.cell(r0+i,col).value
            if w is None: w=float('nan')
            d=abs(w-res[m]); n+=1
            if not d<=0.01: bad.append((sheet,ws.cell(r0+i,col).coordinate,w,res[m],d))
            if d==d: mx=max(mx,d)
    print(name, sheet, 'block',block,'row0',r0,'cells',n,'bad',len(bad),'maxdiff',mx)
    for b in bad[:5]: print('   ',b)
    return n,len(bad),mx
if __name__=='__main__':
    w1='Gold_Monthly_YourSettings_1_AllFiltersOff.xlsx'; w2='Gold_Monthly_YourSettings_2_YourFilters.xlsx'
    which=sys.argv[1]
    if which=='1': compare(w1,'M15 TP2','exit',1,'check1')
    if which=='2a': compare(w2,'M5 TP1','exit',1,'check2')
    if which=='2b': compare(w2,'M15 TP1','exit',1,'check2')
    if which=='3': compare(w2,'M5 TP2','entry',5,'check3')
