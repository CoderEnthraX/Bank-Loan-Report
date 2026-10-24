import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
exec(open('fpfeat.py').read().split('rows = []')[0])
for t in tr:
    P = recover(t['sym']); T = P['T']
    if t['fill'] not in T or not t['entry']: continue
    a = arm_of(t); f = feat(t['sym'], a, t['d'])
    if f['ov'] < 0.05 or f['z'] < 0.6: print(t['sym'], a, t['d'], {k: round(v, 2) for k, v in f.items()})
