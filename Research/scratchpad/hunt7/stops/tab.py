"""Labeled dataset: A (80, tight flag measured) + B logs (step-1 decisions). Prints features of model trades at their arm bar."""
import sys, json, importlib.util, io, contextlib
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S+'/fit'); sys.path.insert(0, S+'/xl')
from load_xl import load
from engine2 import prepare
with contextlib.redirect_stdout(io.StringIO()):
    import tightdata
mod = sys.argv[1] if len(sys.argv) > 1 else S+'/hunt7/stops/combo_f.py'
inp = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {"slopeCross":True,"minOpenBars":0,"cooldownBars":1,"dayStopR":0,"tightOut":True,"erMin":0.2}
spec = importlib.util.spec_from_file_location('m', mod); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
HALF_B = {('CRUDE',45),('CRUDE',49),('CRUDE',51),('CRUDE',56),('NATGAS',6),('NATGAS',13)}
AMBIG_B = {('NATGAS',3),('CRUDE',52)}
DS = {'NIFTY': 'NSE_NIFTY1', 'NATGAS': 'MCX_NATURALGAS', 'SENSEX': 'SENSEX', 'CRUDE': 'CRUDE'}
FIX = {('NATGAS', 2): (None, '19:45'), ('NATGAS', 3): ('2026-10-12', None), ('NATGAS', 4): ('2026-10-12', None), ('NATGAS', 5): ('2026-10-12', None), ('SENSEX',66):(None,'09:40')}
labels = []  # (src, dsym, fillTime, dir, label)
for t in tightdata.TRADES: labels.append(('A', t['sym'], t['fill'], t['d'], 'HALF' if t['tight'] else 'norm'))
for x in load():
    d0, t0 = FIX.get((x['sym'], x['n']), (None, None))
    lab = 'HALF' if (x['sym'], x['n']) in HALF_B else ('??' if (x['sym'], x['n']) in AMBIG_B else 'norm')
    labels.append(('B%s#%d' % (x['sym'][:2], x['n']), DS[x['sym']], (d0 or x['date']) + ' ' + (t0 or x['tin']), x['d'], lab))
cache = {}
rows = []
for src, sym, ft, d, lab in labels:
    if sym not in cache:
        P = prepare(sym); cache[sym] = (P, M.run(sym, inp), {t: i for i, t in enumerate(P['T'])})
    P, tr, idx = cache[sym]; f = idx.get(ft)
    m = None
    for z in tr:
        if f is not None and z['dir'] == d and abs(z['fill'] - f) <= 1 and (m is None or abs(z['fill'] - f) < abs(m['fill'] - f)): m = z
    rows.append((src, sym, ft, d, lab, m, P))
if __name__ == '__main__':
    for src, sym, ft, d, lab, m, P in rows:
        if m is None: print(f"{src:10s} {sym:14s} {ft} {'L' if d>0 else 'S'} {lab:4s} -- model has no trade"); continue
        F = m['feat']; A = F['A']; same = F['bullN'] if d > 0 else F['bearN']; opp = F['bearN'] if d > 0 else F['bullN']
        net = F['prevNet'] if F['prevNet'] is not None else 0
        gap = (F['sesO'] - F['pdC']) / A if F['pdC'] else 0
        outside = ('BELOW' if F['sesO'] < F['pdL'] else 'ABOVE' if F['sesO'] > F['pdH'] else 'in') if F['pdH'] else '-'
        pdir = ('up' if F['pdC'] > F['pdO'] else 'dn') if F['pdC'] else '-'
        vpos = (F['C'] - F['pdV']) / A if F['pdV'] else 0
        mt = 'T' if m['tight'] else 'n'
        flag = '' if (lab == 'HALF') == m['tight'] or lab == '??' else '  <== WRONG'
        print(f"{src:10s} {sym:14s} {ft} {'L' if d>0 else 'S'} {lab:4s} m{mt} k{F['k']:3d} net{d*net:+3d} pB{F['pBull']}/{F['pBear']} pD{F['pdBull']}/{F['pdBear']} imp s{same}o{opp} disp {F['dBull']}/{F['dBear']} sig{F['sigTr']} gap{d*gap:+6.1f} {outside:5s} pdir {pdir} vpos{d*vpos:+5.1f} rngA {F['rngA']:.2f} prev {F['prevDir']},{F['prevRes']},{'S' if F['prevSameSes'] else 'o'} selfImp {int(F['bullImp'] if d>0 else F['bearImp'])}{flag}")
