import sys
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
import importlib.util
spec=importlib.util.spec_from_file_location('adxfit_mod','/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/adxfit.py')
src=open('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/adxfit.py').read().split('cache={}')[0]
exec(src)
P=prepare('NIFTY'); rows=P['rows']
dip,dim,adx=dmi(rows,14,14)
for t in sys.argv[1:]:
    i=find(rows,t); print(t,'ADX %.1f +DI %.1f -DI %.1f'%(adx[i],dip[i],dim[i]))
