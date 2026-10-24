import sys, os, pickle
HERE = os.path.dirname(os.path.abspath(__file__))
B = pickle.load(open(os.path.join(HERE, ''+os.environ.get("BANK","pbank.pkl")+''), 'rb'))
SUBK = os.environ.get('SUBK', 'first_vsl_M')
cols = sys.argv[1].split(',')
sub = [(t, f) for t, f in B if f.get(SUBK, 1) == 1]
print(f"{'trade':28s}" + ''.join(f'{c[-11:]:>12s}' for c in cols))
for t, f in sorted(sub, key=lambda x: (not x[0]['tight'], x[0]['sym'], x[0]['fill'])):
    print(f"{t['sym']:6s} {t['fill']} {'L' if t['d']>0 else 'S'} {'T' if t['tight'] else ' '}" + ''.join(f'{f.get(c, float("nan")):12.3f}' for c in cols))
