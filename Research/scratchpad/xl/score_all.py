"""ONE score over every ground truth. Usage: python3 -I score_all.py [module.py] ['{json}'] [d]
  A   = 80 screenshot trades (exact/near/miss/extra; extras are TRUE extras)
  B1  = student log SENSEX+CRUDE (42), B2 = student log NIFTY futures NSE:NIFTY1! (20), B3 = student log MCX NATURALGAS (18, typo fixes)
        (time-matched = same direction, fill within +-1 bar; stop ok = within 0.06 ATR + rounding; prov = model trades provably absent in the
        original because they overlap/block a logged trade)
  MD  = 6 MODEL DAY table readings of the original
  OBJ = 3*A.exact - 2*A.miss - 2*A.extra + sum(B matched + B stops ok) - 2*sum(prov) + 3*MD"""
import sys, os, json, subprocess
X = os.path.dirname(os.path.abspath(__file__)); S = os.path.dirname(X)
args = sys.argv[1:]
mod = next((a for a in args if a.endswith('.py')), os.path.join(S, 'fit', 'pine_final.py'))
o = next((a for a in args if a.startswith('{')), '{}')
det = 'd' in args
def run(cmd, cwd=X): return subprocess.run(['python3', '-I'] + cmd, cwd=cwd, capture_output=True, text=True, timeout=900).stdout
a = run(['score2.py', mod, o] + (['d'] if det else [])); b = run(['score3.py', mod, o] + (['d'] if det else []))
pb1 = run(['extrasB.py', mod, o]).count('PROVABLE'); pb2 = run(['extrasNF.py', mod, o]).count('PROVABLE'); pb3 = run(['extrasNG.py', mod, o]).count('PROVABLE')
md = run([os.path.join(S, 'hunt4', 'modelday.py'), o, mod], cwd=os.path.join(S, 'hunt4'))
md = md.replace('modelday', '')
import re
A = eval(a.split('(80):')[1].split('\n')[0])
def bl(txt, key):
    m = re.search(key + r'.*?time-matched (\d+), missed (\d+), stop correct (\d+)/(\d+)', txt); return int(m.group(1)), int(m.group(3))
b1 = bl(a, 'SENSEX\\+CRUDE'); b2 = bl(b, 'NIFTY on'); b3 = bl(b, 'NATGAS on')
mdn = int(re.search(r'matched (\d+) / 6', md).group(1)) if re.search(r'matched (\d+) / 6', md) else -1
# NOTE: modelday.py loads hunt4/combo.py; for other modules MD is only meaningful if the module is combo.py-compatible
obj = 3 * A['exact'] - 2 * A['miss'] - 2 * A['extra'] + sum(b1) + sum(b2) + sum(b3) - 2 * (pb1 + pb2 + pb3) + 3 * mdn
print(f"A {A['exact']}/{A['miss']}/{A['extra']} | B1 SENSEX+CRUDE {b1[0]}/42 stops {b1[1]} prov {pb1} | B2 NIFTYF {b2[0]}/20 stops {b2[1]} prov {pb2} | B3 NATGAS {b3[0]}/18 stops {b3[1]} prov {pb3} | MD {mdn}/6 | OBJ {obj}")
if det: print(a); print(b)
