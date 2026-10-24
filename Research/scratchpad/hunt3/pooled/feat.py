"""Feature table for signal candles of known extras vs known taken trades. Writes feat.json."""
import sys, os, json, math, datetime as dt
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/fit'); sys.path.insert(0, S + '/xl'); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pf
from engine2 import prepare
from engine import rma
import gtscore
from load_xl import load
INP = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {"dayStopR": 0}

def ema(x, n):
    a = 2 / (n + 1); out = []; e = None
    for v in x:
        e = v if e is None else e + a * (v - e); out.append(e)
    return out

TR = {}
def trades(sym):
    if sym not in TR: TR[sym] = (pf.run(sym, INP), list(pf.SIGS[sym]))
    return TR[sym]

# ---- labels
items = []  # (sym, armbar, dir, label, note)
gtscore.run = lambda P, cfg: (P.setdefault(('atr', 14), rma(P['tr'], 14)), trades(P['sym'])[0])[1]
gt, win = gtscore.load_gt(S + '/gt/final')
gt = [t for t in gt if not str(t.get('conf') or '').startswith('xl')]
ra, rows = gtscore.score({}, gt, [dict(w) for w in win], detail=True)
for r in rows:
    if r[0] in ('ok', 'EXTRA'):
        sym, t, d = r[1], r[2], (1 if r[3] == 'L' else -1)
        P = prepare(sym); fi = P['T'].index(t)
        m = next(m for m in trades(sym)[0] if m['fill'] == fi and m['dir'] == d)
        items.append((sym, m['arm'], d, 'takenA' if r[0] == 'ok' else 'extraA', t))
X = [x for x in load() if x['sym'] in ('SENSEX', 'CRUDE')]
fixT = {66: '09:40'}
for x in X:
    P = prepare(x['sym']); idx = {t: i for i, t in enumerate(P['T'])}
    f = idx.get(x['date'] + ' ' + fixT.get(x['n'], x['tin']))
    if f is None: continue
    best = None
    for m in trades(x['sym'])[0]:
        if m['dir'] == x['d'] and abs(m['fill'] - f) <= 1 and (best is None or abs(m['fill'] - f) < abs(best['fill'] - f)): best = m
    if best: items.append((x['sym'], best['arm'], x['d'], 'takenB', f"#{x['n']}"))
EXB = [('CRUDE', '2026-10-12 13:40', 'extraB'), ('CRUDE', '2026-10-15 18:30', 'extraB'), ('CRUDE', '2026-10-15 21:35', 'extraB'),
       ('CRUDE', '2026-10-16 11:40', 'extraB'), ('CRUDE', '2026-10-16 19:00', 'extraB0')]
MUST = [('ETH', '2026-10-11 00:15', 1), ('CRUDE', '2026-10-12 14:15', 1), ('CRUDE', '2026-10-15 18:50', 1), ('CRUDE', '2026-10-16 11:45', 1)]
if INP.get('veto'):
    items = [it for it in items if it[3] in ('takenA', 'takenB')]
    for v in INP['veto']:
        sym, t = v.split('|'); i = prepare(sym)['T'].index(t)
        d = -1 if sym == 'NIFTY' else 1
        items.append((sym, i, d, 'extraV', t))
else:
    for sym, t, lab in EXB:
        i = prepare(sym)['T'].index(t); items.append((sym, i, 1, lab, t))
    for sym, t, d in MUST:
        i = prepare(sym)['T'].index(t); items.append((sym, i, d, 'must', t))
# dedupe (A and B can overlap for SENSEX/CRUDE)
seen = {}
for it in items:
    k = (it[0], it[1], it[2])
    if k not in seen or it[3].startswith('extra'): seen[k] = it
items = list(seen.values())

# ---- features
CACHE = {}
def series(sym):
    if sym in CACHE: return CACHE[sym]
    P = prepare(sym); O, H, L, C, V, T = P['O'], P['H'], P['L'], P['C'], P['V'], P['T']; n = len(C)
    A = rma(P['tr'], 14)
    Q = dict(P=P, A=A, e9=ema(C, 9), e20=ema(C, 20), e50=ema(C, 50), e200=ema(C, 200))
    # session std of hlc3 around vwap (equal weights, no volume in data)
    sd = [None] * n; s2 = 0; k = 0
    for i in range(n):
        if P['daystart'][i]: s2 = 0; k = 0
        h3 = (H[i] + L[i] + C[i]) / 3; s2 += (h3 - V[i]) ** 2; k += 1
        sd[i] = math.sqrt(s2 / k)
    Q['sd'] = sd
    Q['atrsma20'] = [None if i < 20 or A[i] is None or A[i - 19] is None else sum(A[i - 19:i + 1]) / 20 for i in range(n)]
    Q['atrsma50'] = [None if i < 50 or A[i - 49] is None else sum(A[i - 49:i + 1]) / 50 for i in range(n)]
    Q['tt'] = [dt.datetime.strptime(t, '%Y-%m-%d %H:%M') for t in T]
    CACHE[sym] = Q; return Q

def htf(Q, i, mins, d):
    """direction of the last COMPLETED htf candle before bar i (clock-aligned), and of the forming one incl. bar i"""
    P = Q['P']; tt = Q['tt']; O, C = P['O'], P['C']
    def key(t): return (t - dt.datetime(2000, 1, 1)).total_seconds() // (mins * 60)
    kc = key(tt[i]); j = i
    while j > 0 and key(tt[j - 1]) == kc: j -= 1
    form = d * (C[i] - O[j])
    e = j - 1; b = e
    if e < 0: return None, form
    kp = key(tt[e])
    while b > 0 and key(tt[b - 1]) == kp: b -= 1
    return d * (C[e] - O[b]), form

def feats(sym, i, d):
    Q = series(sym); P = Q['P']; O, H, L, C, V = P['O'], P['H'], P['L'], P['C'], P['V']; A = Q['A'][i]; mt = P['mt']
    f = {}
    rng = H[i] - L[i]; body = abs(C[i] - O[i]); mid = (O[i] + C[i]) / 2
    ext = (H[i] if d > 0 else L[i])
    for N in range(3, 21):
        lvl = max(H[i - N:i]) if d > 0 else min(L[i - N:i])
        f[f'brk{N}'] = d * (C[i] - lvl) / A
        lc = max(C[i - N:i]) if d > 0 else min(C[i - N:i])
        f[f'brkC{N}'] = d * (C[i] - lc) / A
        f[f'hbrk{N}'] = d * (ext - lvl) / A
    lvl10 = max(H[i - 10:i]) if d > 0 else min(L[i - 10:i])
    f['brk10ticks'] = d * (C[i] - lvl10) / mt
    f['brk10_rng'] = d * (C[i] - lvl10) / rng
    f['open_vs10'] = d * (O[i] - lvl10) / A
    for k in range(1, 21): f[f'mom{k}'] = d * (C[i] - C[i - k]) / A
    f['body%'] = body / rng * 100; f['ext%'] = d * (ext - C[i]) / rng * 100 if d > 0 else (C[i] - L[i]) / rng * 100
    f['ext%'] = ((H[i] - C[i]) if d > 0 else (C[i] - L[i])) / rng * 100
    f['wickback%'] = ((O[i] - L[i]) if d > 0 else (H[i] - O[i])) / rng * 100
    f['rng/A'] = rng / A; f['body/A'] = body / A
    f['cv'] = d * (C[i] - V[i]) / A; f['ov'] = d * (O[i] - V[i]) / A; f['lv'] = d * ((L[i] if d > 0 else H[i]) - V[i]) / A
    for k in range(1, 7):
        f[f'vs{k}'] = d * (V[i] - V[i - k]) / A
    f['vs3_prev'] = d * (V[i - 1] - V[i - 4]) / A
    f['vsAll3'] = min(d * (V[i - k] - V[i - k - 1]) for k in range(3)) / A
    f['z'] = d * (C[i] - V[i]) / Q['sd'][i] if Q['sd'][i] else None
    f['since'] = P['sinceStart'][i]
    f['atr/sma20'] = A / Q['atrsma20'][i] if Q['atrsma20'][i] else None
    f['atr/sma50'] = A / Q['atrsma50'][i] if Q['atrsma50'][i] else None
    f['rng/prevrng'] = rng / max(H[i - 1] - L[i - 1], mt)
    e9, e20, e50, e200 = Q['e9'], Q['e20'], Q['e50'], Q['e200']
    f['e9-e20'] = d * (e9[i] - e20[i]) / A; f['e20-e50'] = d * (e20[i] - e50[i]) / A; f['c-e50'] = d * (C[i] - e50[i]) / A
    f['c-e200'] = d * (C[i] - e200[i]) / A; f['e50-e200'] = d * (e50[i] - e200[i]) / A
    f['e20slope3'] = d * (e20[i] - e20[i - 3]) / A; f['e50slope5'] = d * (e50[i] - e50[i - 5]) / A
    f['e9-e20prev'] = d * (e9[i - 1] - e20[i - 1]) / A
    f['emaOrder'] = int(d * (e9[i] - e20[i]) > 0) + int(d * (e20[i] - e50[i]) > 0)
    for mins in (15, 30, 60):
        a, b = htf(Q, i, mins, d); f[f'htf{mins}prev'] = None if a is None else a / A; f[f'htf{mins}form'] = b / A
    cs = 0; j = i - 1
    while j >= 0 and d * (C[j] - O[j]) > 0: cs += 1; j -= 1
    f['consecBefore'] = cs
    f['prevBarDir'] = d * (C[i - 1] - O[i - 1]) / A
    f['prevBarRng'] = (H[i - 1] - L[i - 1]) / A
    hh6 = max(H[i - 6:i]) if d > 0 else min(L[i - 6:i])
    f['lim6'] = int((d > 0 and hh6 > mid) or (d < 0 and hh6 < mid))
    lim = max(mid, hh6) if d > 0 else min(mid, hh6)
    f['c-lim'] = d * (C[i] - lim) / A
    f['mid-lvl6'] = d * (mid - hh6) / A
    f['lvl10-lvl6'] = d * (lvl10 - hh6) / A
    f['lvl10-V'] = d * (lvl10 - V[i]) / A
    # bars since last price on the other side of vwap
    j = i;
    while j > 0 and d * (C[j] - V[j]) > 0: j -= 1
    f['barsAboveV'] = i - j
    # bars since the 10-bar extreme was set
    seg = H[i - 10:i] if d > 0 else L[i - 10:i]
    k = (max(range(10), key=lambda q: seg[q]) if d > 0 else min(range(10), key=lambda q: seg[q]))
    f['ageExt10'] = 10 - k
    # day range position
    j = i
    while j > 0 and not P['daystart'][j]: j -= 1
    dh, dl = max(H[j:i + 1]), min(L[j:i + 1])
    f['dayPos'] = ((C[i] - dl) / (dh - dl) if d > 0 else (dh - C[i]) / (dh - dl)) if dh > dl else None
    f['newDayExt'] = int((H[i] >= dh) if d > 0 else (L[i] <= dl))
    f['prevDayExt'] = int(((max(H[j:i]) if i > j else -1e18) < H[i]) if d > 0 else ((min(L[j:i]) if i > j else 1e18) > L[i]))
    f['dayMove'] = d * (C[i] - O[j]) / A
    for kp in (1, 2, 3, 4, 5):
        for nth in (1, 2):
            cnt = 0; lvl = None; j = i - 1 - kp
            while j >= kp and j > i - 400:
                if d > 0: ok = all(H[j] > H[j - q] for q in range(1, kp + 1)) and all(H[j] >= H[j + q] for q in range(1, kp + 1))
                else: ok = all(L[j] < L[j - q] for q in range(1, kp + 1)) and all(L[j] <= L[j + q] for q in range(1, kp + 1))
                if ok:
                    cnt += 1; v = H[j] if d > 0 else L[j]
                    lvl = v if lvl is None else (max(lvl, v) if d > 0 else min(lvl, v))
                    if cnt == nth: break
                j -= 1
            f[f'piv{kp}_{nth}'] = d * (C[i] - lvl) / A if lvl is not None else None
            if nth == 1: f[f'pivAge{kp}'] = i - j
    # model state
    tr, sig = trades(sym)
    past = [m for m in tr if m['fill'] < i or (m['fill'] == i)]
    pastC = [m for m in tr if m['exit'] is not None and m['exit'] < i]
    f['sinceExit'] = i - pastC[-1]['exit'] if pastC else 999
    f['sinceFill'] = i - past[-1]['fill'] if past else 999
    f['prevTrDir'] = d * pastC[-1]['dir'] if pastC else 0
    f['prevTrRes'] = pastC[-1]['res'] if pastC else 0
    f['prevSameDay'] = int(bool(pastC) and P['sinceStart'][i] > i - pastC[-1]['exit'])
    ps = [s for s in sig if s[0] < i]
    opp = [s for s in ps if s[1] == -d]; same = [s for s in ps if s[1] == d]
    f['sinceOppSig'] = i - opp[-1][0] if opp else 999
    f['sinceSameSig'] = i - same[-1][0] if same else 999
    f['prevSigDir'] = d * ps[-1][1] if ps else 0
    f['nSameSig20'] = sum(1 for s in same if i - s[0] <= 20)
    f['nSigToday'] = sum(1 for s in ps if P['sinceStart'][i] >= i - s[0])
    f['nTrToday'] = sum(1 for m in tr if m['fill'] < i and P['sinceStart'][i] >= i - m['fill'])
    # previous same-dir trade's extreme reached / entry relation
    return f

out = []
for sym, i, d, lab, note in sorted(items):
    P = prepare(sym)
    out.append(dict(sym=sym, i=i, t=P['T'][i], d=d, lab=lab, note=note, f=feats(sym, i, d)))
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.environ.get('FEATOUT', 'feat.json')), 'w'), indent=0, default=str)
from collections import Counter
print(Counter(o['lab'] for o in out))
