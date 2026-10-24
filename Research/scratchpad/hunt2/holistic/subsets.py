import sys, json, os, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ev import ev, fmt
CH = [('slopeCross', True), ('minOpenBars', 0), ('cooldownBars', 1), ('dayStopR', 0), ('netMin', 2)]
b = ev({}); print('BASE', fmt(b))
for n in range(1, 6):
    for S in itertools.combinations(CH, n):
        c = dict(S); r = ev(c)
        print(' + '.join(f'{k}={v}' for k, v in S), '|', fmt(r), '| GAIN', sorted(b['bad'] - r['bad']), '| LOSE', sorted(r['bad'] - b['bad']), flush=True)
