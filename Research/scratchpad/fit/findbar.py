"""Find bars whose high or low is near a price.  Usage:
python3 -I findbar.py SYMBOL 'YYYY-MM-DD' (high|low) PRICE TOL      e.g. findbar.py US30 2026-10-08 high 51509 3"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arp_data import load
sym, day, side, p, tol = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), float(sys.argv[5])
k = 'h' if side == 'high' else 'l'
for r in load(sym):
    if r['t'].startswith(day) and abs(r[k] - p) <= tol:
        print(r['i'], r['t'], 'O', r['o'], 'H', r['h'], 'L', r['l'], 'C', r['c'])
