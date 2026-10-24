"""Usage: python3 -I bars.py SYMBOL 'YYYY-MM-DD HH:MM' 'YYYY-MM-DD HH:MM'
Prints every 5m bar in the range: index, IST time, O H L C, body mid, the VWAP of MY indicator, and MY fills (L/S)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arp_data import load
sym, a, b = sys.argv[1], sys.argv[2], sys.argv[3]
for r in load(sym):
    if a <= r['t'] <= b:
        mark = ('MY-LONG-FILL' if r['lf'] else '') + ('MY-SHORT-FILL' if r['sf'] else '')
        print(f"{r['i']:6d} {r['t']}  O {r['o']:<10g} H {r['h']:<10g} L {r['l']:<10g} C {r['c']:<10g} mid {round((r['o']+r['c'])/2,6):<10g} myVWAP {r['vwap'] if r['vwap'] is None else round(r['vwap'],5)} {mark}")
