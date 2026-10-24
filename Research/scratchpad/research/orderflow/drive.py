import sys, json
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0,S+'/research')
import lib
M=S+'/research/orderflow/combo_of.py'
base=lib.run_all(); bn,be=lib.split(base)
def sm(v): s=lib.stats(v); return s
def line(name, opts, log=True):
    tr=lib.run_all(M, opts); tn,te=lib.split(tr)
    a,b,c=sm(tr),sm(tn),sm(te)
    lo,hi=lib.boot_diff(be,te)
    imp=0; ps=[]
    for s in lib.SYMS:
        x=[t for t in tr if t['sym']==s]; y=[t for t in base if t['sym']==s]
        ex=sum(t['res'] for t in x)/len(x) if x else 0; ey=sum(t['res'] for t in y)/len(y)
        imp+= ex>ey; ps.append('%s %+.2f>%+.2f'%(s[:6],ey,ex))
    out=(f"{name}: ALL n={a['n']} kept {a['n']/len(base):.0%} tot {a['totR2']:+.0f} hit1 {a['hit1']:.1%} hit15 {a['hit15']:.1%} hit2 {a['hit2']:.1%} E1 {a['E1']:+.3f} E15 {a['E15']:+.3f} E2 {a['E2']:+.3f} | "
         f"TRAIN n={b['n']} E1 {b['E1']:+.3f} E15 {b['E15']:+.3f} E2 {b['E2']:+.3f} | TEST n={c['n']} E1 {c['E1']:+.3f} E15 {c['E15']:+.3f} E2 {c['E2']:+.3f} "
         f"dE2 {c['E2']-lib.stats(be)['E2']:+.3f} CI[{lo:+.3f},{hi:+.3f}] | syms improved {imp}/10")
    print(out); print('    ', ' | '.join(ps)); sys.stdout.flush()
    if log: open(S+'/research/orderflow/progress.md','a').write('- '+out+'  opts='+json.dumps(opts)+'\n')
    return tr
if __name__=="__main__" and not sys.argv[0].endswith("randctl.py"):
    for arg in sys.argv[1:]:
        name,o=arg.split('::',1); line(name, json.loads(o))
