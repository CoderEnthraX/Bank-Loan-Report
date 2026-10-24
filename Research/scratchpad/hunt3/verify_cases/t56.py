import sys, importlib.util
sys.path[:0]=['/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit','/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/xl']
from engine2 import prepare
from load_xl import load
spec=importlib.util.spec_from_file_location('m','/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/hunt3/keycases/kc.py');M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
for x in load():
    if x['n'] in (56,): print(x)
T=prepare('CRUDE')['T']
for nm in (3,2,1):
    print('netMin',nm)
    for t in M.run('CRUDE',{"dayStopR":0,"netMin":nm}):
        if T[t['fill']].startswith('2026-10-14'): print('  ',T[t['arm']],T[t['fill']],t['dir'],t['entry'],round(t['stop'],2),T[t['exit']],t['res'])
