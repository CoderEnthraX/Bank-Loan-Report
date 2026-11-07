import pickle,json,random
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter as L
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
D=pickle.load(open(S+'/gold/monthly.pkl','rb')); R=json.load(open(S+'/gold/monthly_readme.json'))
VN=[v[0] for v in D['variants']]; st=D['strategies']; mo=D['months']; random.seed(1)
for fk in ('file1','file2'):
    wb=load_workbook(S+'/'+R['files'][fk]['filename'],data_only=True); res=D['res'][fk]
    base=7 if fk=='file2' else 6; n=bad=0; fields=['net','maxDD','maxLoss','trades']
    for _ in range(60):
        si=random.randrange(19); i=random.randrange(70); k=random.randrange(17); b=random.randrange(4)
        s=st[si]; nm=R['names'][s['key']]; v=res[s['key']][mo[i]][1][VN[k]]
        exp=v[fields[b]]; got=wb[nm].cell(6+i,base+1+b*17+k).value
        n+=1; bad+= abs(got-exp)>=.01
        # by-month
        if b==0:
            ws=wb[('By month - '+R['labels'][VN[k]].replace('/','-'))[:31]]; g2=ws.cell(4+i,2+si).value; n+=1; bad+=abs(g2-exp)>=.01
    for _ in range(10):
        si=random.randrange(19);k=random.randrange(17);s=st[si];nm=R['names'][s['key']]
        tot=sum(res[s['key']][m][1][VN[k]]['net'] for m in mo)
        pr=sum(res[s['key']][m][1][VN[k]]['net']>0 for m in mo)
        bl=sum(res[s['key']][m][1][VN[k]]['ruined'] for m in mo)
        ws=wb['Summary']
        for off,e in ((0,tot),(1,pr),(3,bl)):
            g=ws.cell(3+off*22+si,3+k).value; n+=1; bad+=abs(g-e)>=.01
        g=ws.cell(3+2*22+si,3+k).value; e=min(res[s['key']][m][1][VN[k]]['net'] for m in mo); n+=1; bad+=abs(g-e)>=.01
    print(fk,'checked',n,'bad',bad,wb.sheetnames.__len__())
