import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ev
from j import IN
def norm(c): return {k: v for k, v in sorted(c.items()) if IN.get(k, object()) != v}
base = json.loads(sys.argv[1])
def E(o):
    c = dict(IN); c.update(base); c.update(o); return ev.ev(norm(c))
B = E({}); print('BASE', B['line'])
for a in sys.argv[2:]:
    r = E(json.loads(a)); d = ev.diff(r, B); print(a, '->', r['line'])
    for x in d['fixed']: print('    + gained', x)
    for x in d['broke']: print('    - lost  ', x)
