import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ev, groups
from j import IN
base = json.loads(sys.argv[1]); G = groups.G()
def norm(c): return {k: v for k, v in sorted(c.items()) if IN.get(k, object()) != v}
b = dict(IN); b.update(base); b = norm(b); B = ev.CACHE.get(ev.key(b))
rows = []
for gn, alts in G.items():
    for a in alts:
        c = dict(IN); c.update(b); c.update(a); c = norm(c)
        if c == b: continue
        r = ev.CACHE.get(ev.key(c))
        if r: rows.append((r['obj'], gn, json.dumps(a), r))
rows.sort(key=lambda x: -x[0])
print('BASE', B['line'])
for o, gn, a, r in rows[:int(sys.argv[2]) if len(sys.argv) > 2 else 999]:
    d = ev.diff(r, B); print(f"{o:5d} {gn:11s} {a:60s} {r['line']}  +{len(d['fixed'])}/-{len(d['broke'])}")
