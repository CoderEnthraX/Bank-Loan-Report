import sys, pickle, json, glob, collections, statistics as stt
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/research'); sys.path.insert(0, S + '/research/chop'); sys.path.insert(0, S + '/xl')
import lib, daytype
from engine2 import prepare
tr = pickle.load(open(S + '/research/chop/base.pkl', 'rb'))
# attach day features (session of the ARM bar)
def day_of(sym, i):
    ss, sidx = daytype.sessions(sym); return ss[sidx[i]]
for x in tr: x['day'] = day_of(x['sym'], x['arm'])
tr = [x for x in tr if x['day']]
# per-instrument terciles of the crossing rate and near share (bars per session differ)
allday = {s: [d for d in daytype.sessions(s)[0] if d] for s in lib.SYMS}
def terc(s, key, v):
    vals = sorted(d[key] for d in allday[s]); q1 = vals[len(vals) // 3]; q2 = vals[2 * len(vals) // 3]
    return 'lo' if v < q1 else ('mid' if v < q2 else 'hi')
def cls(d, sym):
    # composite: RANGE = eff<0.35 and crossing-rate tercile not lo ; TREND = eff>=0.6 and crossing tercile lo/mid ; else MIXED
    t = terc(sym, 'x2', d['x2'])
    if d['eff'] < 0.35 and t != 'lo': return 'RANGE'
    if d['eff'] >= 0.6 and t != 'hi': return 'TREND'
    return 'MIXED'
def row(name, g):
    if not g: return f'{name:28s} n=0'
    n = len(g); w = sum(x['res'] > 0 for x in g) / n; e = sum(x['res'] for x in g) / n; h1 = sum(x['hit1'] for x in g) / n
    return f'{name:28s} n={n:4d} hit2R {w:5.1%} hit1R {h1:5.1%} E2 {e:+.3f} totR {e*n:+6.0f}'
def table(title, keyf, trs):
    print('==', title)
    gs = collections.defaultdict(list)
    for x in trs: gs[keyf(x)].append(x)
    for k in sorted(gs): print(row(str(k), gs[k]))
print(row('ALL model trades', tr))
table('composite day type', lambda x: cls(x['day'], x['sym']), tr)
table('efficiency |C-O|/range', lambda x: '0 <0.25' if x['day']['eff'] < .25 else '1 0.25-0.5' if x['day']['eff'] < .5 else '2 0.5-0.75' if x['day']['eff'] < .75 else '3 >=0.75', tr)
table('VWAP crosses (0.2ATR hyst), tercile per instr', lambda x: terc(x['sym'], 'x2', x['day']['x2']), tr)
table('share of bars within 0.5 ATR of VWAP, tercile', lambda x: terc(x['sym'], 'near05', x['day']['near05']), tr)
table('|close-VWAP| at session end, ATR', lambda x: '0 <1' if x['day']['clV'] < 1 else '1 1-3' if x['day']['clV'] < 3 else '2 >=3', tr)
table('day range / ATR tercile', lambda x: terc(x['sym'], 'rngA', x['day']['rngA']), tr)
# trade direction vs day's final direction (hindsight)
def withday(x):
    d = x['day']; P = prepare(x['sym']); dirday = 1 if P['C'][d['b']] > P['O'][d['a']] else -1
    return 'with day dir' if dirday == x['dir'] else 'against day dir'
table('trade dir vs day close-open', withday, tr)
table('split x composite', lambda x: ('TRAIN' if x['t'] < lib.SPLIT else 'TEST') + ' ' + cls(x['day'], x['sym']), tr)
print('== per instrument E2 by composite (RANGE / MIXED / TREND)')
for s in lib.SYMS:
    g = [x for x in tr if x['sym'] == s]; parts = []
    for c in ('RANGE', 'MIXED', 'TREND'):
        h = [x for x in g if cls(x['day'], s) == c]; parts.append(f"{c} n={len(h):3d} E2 {sum(x['res'] for x in h)/len(h) if h else 0:+.2f}")
    print(f'  {s:15s}', ' | '.join(parts))
dc = collections.Counter(cls(d, s) for s in lib.SYMS for d in allday[s]); print('sessions by type', dict(dc))
# trades per day by type
for c in ('RANGE', 'MIXED', 'TREND'):
    nd = sum(1 for s in lib.SYMS for d in allday[s] if cls(d, s) == c); nt = sum(1 for x in tr if cls(x['day'], x['sym']) == c); print(f'  {c}: {nd} sessions, {nt/nd:.2f} trades/session')
# ===== ORIGINAL indicator trades
orig = []
def locate(sym_candidates, ts, entry):
    for s in sym_candidates:
        P = prepare(s); idx = {t: i for i, t in enumerate(P['T'])}
        i = idx.get(ts)
        if i is None: continue
        if entry is None or P['L'][i] - abs(entry) * 0.002 <= entry <= P['H'][i] + abs(entry) * 0.002: return s, i
    return None, None
CAND = {'NIFTY': ['NIFTY', 'NSE_NIFTY1'], 'SENSEX': ['SENSEX'], 'GC': ['GC'], 'EURUSD': ['EURUSD'], 'ETH': ['ETH'], 'NASDAQ': ['NASDAQ'], 'US30': ['US30'], 'CRUDE': ['CRUDE']}
seen = set()
for f in sorted(glob.glob(S + '/gt/final/*.json')):
    for o in json.load(open(f)).get('orig_trades', []):
        if o.get('outcome') not in ('tp4', 'stop'): continue
        e = o.get('entry_exact') or o.get('entry_measured'); s, i = locate(CAND.get(o['symbol'], [o['symbol']]), o['fill_bar'], e)
        key = (o['symbol'], o['fill_bar'], o['dir'])
        if s is None or key in seen: continue
        seen.add(key); orig.append(dict(src='gt', sym=s, i=i, dir=1 if o['dir'] == 'long' else -1, res=2.0 if o['outcome'] == 'tp4' else -1.0, hit1=True if o['outcome'] == 'tp4' else False))
import load_xl
FIX = {('NATGAS', 2): (None, '19:45'), ('NATGAS', 3): ('2026-10-12', None), ('NATGAS', 4): ('2026-10-12', None), ('NATGAS', 5): ('2026-10-12', None), ('NIFTY', 37): (None, '10:50')}
XM = {'NIFTY': ['NSE_NIFTY1'], 'NATGAS': ['MCX_NATURALGAS'], 'CRUDE': ['CRUDE'], 'SENSEX': ['SENSEX']}
nx = 0
for x in load_xl.load():
    dt, tm = FIX.get((x['sym'], x['n']), (None, None)); dt = dt or str(x['date'])[:10]; tm = tm or x['tin']
    s, i = locate(XM[x['sym']], f'{dt} {tm}', None)
    if s is None: continue
    nx += 1
    res = 2.0 if x['maxtp'] == 'TP 4' else -1.0 if x['maxtp'] == 'SL' else None
    orig.append(dict(src='xl', sym=s, i=i, dir=x['d'], res=res, netrr=x['netrr'], hit1=x['maxtp'] != 'SL'))
print('original trades located: gt', sum(o['src'] == 'gt' for o in orig), 'xl', nx)
for o in orig: o['day'] = day_of(o['sym'], o['i']); o['t'] = prepare(o['sym'])['T'][o['i']]
orig = [o for o in orig if o['day']]
def orow(name, g):
    g2 = [o for o in g if o['res'] is not None]
    if not g: return f'{name:28s} n=0'
    w = sum(o['res'] > 0 for o in g2) / len(g2) if g2 else 0; e = sum(o['res'] for o in g2) / len(g2) if g2 else 0
    nr = [o['netrr'] for o in g if o.get('netrr') is not None]
    return f'{name:28s} n={len(g):3d} (TP4/SL n={len(g2):3d}) TP4-rate {w:5.1%} E2 {e:+.3f}' + (f'  student netRR mean {stt.mean(nr):+.2f} (n={len(nr)})' if nr else '')
def otable(title, keyf):
    print('== ORIGINAL:', title); gs = collections.defaultdict(list)
    for o in orig: gs[keyf(o)].append(o)
    for k in sorted(gs): print(orow(str(k), gs[k]))
print(orow('ALL original trades', orig))
otable('composite day type', lambda o: cls(o['day'], o['sym']))
otable('efficiency', lambda o: '0 <0.35' if o['day']['eff'] < .35 else '1 0.35-0.6' if o['day']['eff'] < .6 else '2 >=0.6')
otable('VWAP crosses tercile', lambda o: terc(o['sym'], 'x2', o['day']['x2']))
otable('near-VWAP share tercile', lambda o: terc(o['sym'], 'near05', o['day']['near05']))
pickle.dump(orig, open(S + '/research/chop/orig.pkl', 'wb'))
