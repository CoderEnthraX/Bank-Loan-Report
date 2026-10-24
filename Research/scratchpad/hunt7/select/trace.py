"""trace.py SYM 'from' 'to' '{json}' : per-bar model state and signal conditions"""
import sys, json, importlib.util, os
d=os.path.dirname(os.path.abspath(__file__))
spec=importlib.util.spec_from_file_location('m',os.path.join(d,'sel.py')); M=importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
sym,a,b=sys.argv[1:4]; inp=json.loads(sys.argv[4]) if len(sys.argv)>4 else {}
inp=dict(inp); inp['dbg']=True
tr=M.run(sym,inp)
for r in M.DBG:
    if a<=r['t']<=b:
        print(f"{r['t'][5:]} st{r['st']:+d} df{r['dayFills']} lx{r['lastExit']} rng{r['rng']:.2f} body{r['body']:.0f} cH{r['clsH']:.0f} cL{r['clsL']:.0f} brkH{r['brkH']:+.2f} brkL{r['brkL']:+.2f} mom{r['mom']:+.2f} cvw{r['cvw']:+.2f} sU{int(r['sU'])}sD{int(r['sD'])} er{int(r['er'][0])}{int(r['er'][1])} BULL{int(r['bullDisp'])} BEAR{int(r['bearDisp'])} entL{r['ent'][0]:.6g} entS{r['ent'][1]:.6g} i{r['i']}")
for t in tr:
    if a<=M.eprep(sym)['rows'][t['fill']]['t']<=b or True:
        pass
P=M.eprep(sym)['rows']
for t in tr:
    if a<=P[t['fill']]['t']<=b: print('TRADE', 'L' if t['dir']>0 else 'S', 'arm',P[t['arm']]['t'],'fill',P[t['fill']]['t'],'e',round(t['entry'],2),'s',round(t['stop'],2),'exit',P[t['exit']]['t'] if t['exit'] is not None else None,t['res'],'tight',t['tight'])
