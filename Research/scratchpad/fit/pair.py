import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
exec(open('fpfeat.py').read().split('rows = []')[0])
for s, a, d in [('NIFTY','2026-10-07 09:35',-1),('SENSEX','2026-10-07 09:35',-1),('NIFTY','2026-10-07 13:05',-1),('NIFTY','2026-10-08 12:15',-1),('SENSEX','2026-10-08 12:15',-1),('NIFTY','2026-10-09 10:05',1),('SENSEX','2026-10-09 10:05',1)]:
    P = recover(s); i = P['T'].index(a); dip, dim, adx = P['dmi'] if 'dmi' in P else (None, None, None)
    f = feat(s, a, d); dip, dim, adx = P['dmi']
    print(s, a, {k: round(v, 3) for k, v in f.items()}, 'DI+ %.1f DI- %.1f vsd/A %.3f' % (dip[i], dim[i], P['vsd'][i] / P[('atr', 14)][i]))
