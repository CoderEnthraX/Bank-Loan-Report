"""Labeled stop table: A (tightdata, measured stops) + B logs (logged stops). Uses r3.shown(). rows -> list of dicts; pickled to tab3.pkl."""
import sys, json, io, contextlib, pickle, os
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S+'/fit'); sys.path.insert(0, S+'/xl'); sys.path.insert(0, S+'/halfstop3')
from load_xl import load
from engine2 import prepare
from engine import rma
with contextlib.redirect_stdout(io.StringIO()):
    import tightdata
import r3
import os; inp = json.loads(os.environ.get('INP', '{}'))
DS = {'NIFTY': 'NSE_NIFTY1', 'NATGAS': 'MCX_NATURALGAS', 'SENSEX': 'SENSEX', 'CRUDE': 'CRUDE'}
FIX = {('NATGAS', 2): (None, '19:45'), ('NATGAS', 3): ('2026-10-12', None), ('NATGAS', 4): ('2026-10-12', None), ('NATGAS', 5): ('2026-10-12', None), ('NIFTY', 37): (None, '10:50')}
labels = []
for t in tightdata.TRADES: labels.append(('A', t['sym'], t['fill'], t['d'], t['entry'], t['stop']))
for x in load():
    d0, t0 = FIX.get((x['sym'], x['n']), (None, None))
    labels.append(('B%s#%d' % (x['sym'][:2], x['n']), DS[x['sym']], (d0 or x['date']) + ' ' + (t0 or x['tin']), x['d'], x['entry'], x['stop']))
cache = {}; rows = []
for src, sym, ft, d, le, ls in labels:
    if sym not in cache:
        P = prepare(sym); cache[sym] = (P, r3.run(sym, inp), {t: i for i, t in enumerate(P['T'])}, rma(P['tr'], 14))
    P, tr, idx, A_ = cache[sym]; f = idx.get(ft); m = None
    for z in tr:
        if f is not None and z['dir'] == d and abs(z['fill'] - f) <= 1 and (m is None or abs(z['fill'] - f) < abs(m['fill'] - f)): m = z
    if m is None: rows.append(dict(src=src, sym=sym, ft=ft, d=d, m=None)); continue
    F = m['feat']; j = F['j']; A = F['A']; e = m['entry']
    logR = d * (e - ls) / A
    norm = abs(logR - 1.8) <= 0.12; half = abs(ls - F['hStop']) / A <= 0.12
    lab = 'norm' if norm and not half else 'HALF' if half and not norm else 'both' if half else 'other'
    rows.append(dict(src=src, sym=sym, ft=ft, d=d, m=m, F=F, j=j, A=A, e=e, logStop=ls, logE=le, logR=logR, lab=lab, P=P))
if __name__ == '__main__':
    for r in rows:
        if r['m'] is None: print(r['src'], r['sym'], r['ft'], 'NOMODEL'); continue
        m = r['m']; F = r['F']
        flag = '' if (r['lab'] == 'HALF') == m['half'] or r['lab'] in ('both',) else ' <== '
        if r['lab'] == 'other': flag = ' ?? '
        print(f"{r['src']:9s} {r['sym']:14s} {r['ft']} {'L' if r['d']>0 else 'S'} {r['lab']:5s} m{'H' if m['half'] else 'n'} logR {r['logR']:.2f} hR {r['d']*(r['e']-F['hStop'])/r['A']:.2f}{flag}")
