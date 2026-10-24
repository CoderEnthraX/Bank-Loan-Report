"""Well-known intraday strategies on the same 5-minute data, with fixed 1:1 / 1:2 brackets and their own ('native') exits.
Signal on a bar's close -> entry at the NEXT bar's open; stop first when a bar touches both levels; a gap through a level exits at
the open; every trade is closed at the end of its session (intraday). One position at a time, max 3 trades per day (ORB: 1).
No costs. R = result / stop distance."""
import sys, math, random, json
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/fit'); sys.path.insert(0, S + '/build')
from engine import prepare, rma
import ref
SY = ['GC', 'EURUSD', 'NASDAQ', 'US30', 'CRUDE', 'NIFTY', 'SENSEX', 'ETH', 'NSE_NIFTY1', 'MCX_NATURALGAS']
SPLIT = '2026-10-01'
# main market open in IST for the opening-range breakout (Sep-Oct 2026: US daylight time)
OPEN = {'GC': (17, 50), 'EURUSD': (12, 30), 'NASDAQ': (19, 0), 'US30': (19, 0), 'CRUDE': (9, 0), 'NIFTY': (9, 15), 'SENSEX': (9, 15),
        'ETH': (5, 30), 'NSE_NIFTY1': (9, 15), 'MCX_NATURALGAS': (9, 0)}
def ema(x, n):
    o = [None] * len(x); a = 2.0 / (n + 1); s = None
    for j in range(len(x)):
        if s is None:
            if j >= n - 1: s = sum(x[j - n + 1:j + 1]) / n
        else: s = a * x[j] + (1 - a) * s
        o[j] = s
    return o
def sma(x, n):
    o = [None] * len(x); s = 0.0
    for j in range(len(x)):
        s += x[j]
        if j >= n: s -= x[j - n]
        if j >= n - 1: o[j] = s / n
    return o
def stdev(x, n, m):
    return [None if m[j] is None else math.sqrt(max(sum((x[k] - m[j]) ** 2 for k in range(j - n + 1, j + 1)) / n, 0.0)) for j in range(len(x))]
def rsi(x, n):
    up = [0.0] + [max(x[j] - x[j - 1], 0.0) for j in range(1, len(x))]; dn = [0.0] + [max(x[j - 1] - x[j], 0.0) for j in range(1, len(x))]
    ru, rd = rma(up, n), rma(dn, n)
    return [None if (ru[j] is None or rd[j] is None) else (100.0 if rd[j] == 0 else 100.0 - 100.0 / (1 + ru[j] / rd[j])) for j in range(len(x))]
_D = {}
def data(sym):
    if sym in _D: return _D[sym]
    P = prepare(sym); R = P['rows']; n = len(R)
    O = [r['o'] for r in R]; H = [r['h'] for r in R]; L = [r['l'] for r in R]; C = [r['c'] for r in R]; V = [r['vwap'] for r in R]; T = [r['t'] for r in R]
    w = ref.weights(sym); ds = P['daystart']
    sd = [None] * n; sw = s1 = s2 = 0.0; sess = [0] * n; k = -1
    for j in range(n):
        if ds[j]: sw = s1 = s2 = 0.0; k += 1
        sess[j] = k; tp = (H[j] + L[j] + C[j]) / 3; sw += w[j]; s1 += w[j] * tp; s2 += w[j] * tp * tp
        sd[j] = math.sqrt(max(s2 / sw - (s1 / sw) ** 2, 0.0)) if sw > 0 else None
    last = [j + 1 >= n or ds[j + 1] for j in range(n)]
    D = dict(O=O, H=H, L=L, C=C, V=V, T=T, A=rma(P['tr'], 14), sd=sd, sess=sess, last=last, n=n, days=k + 1,
             E9=ema(C, 9), E21=ema(C, 21), E200=ema(C, 200), S20=sma(C, 20), S5=sma(C, 5), R2=rsi(C, 2))
    D['B20'] = stdev(C, 20, D['S20'])
    _D[sym] = D; return D
def signals(sym, name, D, rnd=None):
    """yield (bar, dir, stopDist, nativeExit) for every bar whose close gives a signal"""
    O, H, L, C, V, A, sd, E9, E21, E200, S20, B20, R2 = (D[k] for k in ('O', 'H', 'L', 'C', 'V', 'A', 'sd', 'E9', 'E21', 'E200', 'S20', 'B20', 'R2'))
    n = D['n']; out = []
    if name == 'orb':
        oh, om = OPEN[sym]; orH = orL = None; orEnd = None; done = set(); s_prev = -1
        for i in range(n):
            s = D['sess'][i]
            if s != s_prev: orH = orL = None; orEnd = None; s_prev = s
            hh, mm = int(D['T'][i][11:13]), int(D['T'][i][14:16]); m = hh * 60 + mm; m0 = oh * 60 + om
            if orEnd is None and m0 <= m < m0 + 30:
                orH = H[i] if orH is None else max(orH, H[i]); orL = L[i] if orL is None else min(orL, L[i])
                if m >= m0 + 25: orEnd = i
                continue
            if orEnd is not None and i > orEnd and s not in done and orH is not None and orH > orL:
                if C[i] > orH: out.append((i, 1, C[i] - orL, None)); done.add(s)
                elif C[i] < orL: out.append((i, -1, orH - C[i], None)); done.add(s)
        return out
    for i in range(1, n):
        a = A[i]
        if not a: continue
        if name == 'vwap2sd' and sd[i]:
            if C[i] < V[i] - 2 * sd[i]: out.append((i, 1, a, 'vwap'))
            elif C[i] > V[i] + 2 * sd[i]: out.append((i, -1, a, 'vwap'))
        elif name == 'bb' and B20[i] and B20[i - 1]:
            lo, lo1 = S20[i] - 2 * B20[i], S20[i - 1] - 2 * B20[i - 1]; hi, hi1 = S20[i] + 2 * B20[i], S20[i - 1] + 2 * B20[i - 1]
            if C[i - 1] < lo1 and C[i] > lo: out.append((i, 1, a, 'mid'))
            elif C[i - 1] > hi1 and C[i] < hi: out.append((i, -1, a, 'mid'))
        elif name == 'rsi2' and R2[i] is not None and E200[i]:
            if R2[i] < 10 and C[i] > E200[i]: out.append((i, 1, a, 'sma5'))
            elif R2[i] > 90 and C[i] < E200[i]: out.append((i, -1, a, 'sma5'))
        elif name == 'ema9_21' and E9[i - 1] and E21[i - 1] and E200[i]:
            if E9[i] > E21[i] and E9[i - 1] <= E21[i - 1] and C[i] > E200[i]: out.append((i, 1, a, 'cross'))
            elif E9[i] < E21[i] and E9[i - 1] >= E21[i - 1] and C[i] < E200[i]: out.append((i, -1, a, 'cross'))
        elif name == 'random' and rnd.random() < 0.03:
            out.append((i, 1 if rnd.random() < 0.5 else -1, a, None))
    return out
def backtest(sym, name, mode, tgtR=1.0, stopMult=1.0, maxDay=3, seed=0):
    """mode 'bracket' = stop stopMult x signal stop, target tgtR x that distance; 'native' = the strategy's own exit, with the stop as protection"""
    D = data(sym); O, H, L, C, V, S20, S5, E9, E21 = (D[k] for k in ('O', 'H', 'L', 'C', 'V', 'S20', 'S5', 'E9', 'E21'))
    sig = signals(sym, name, D, random.Random('%s%s%d' % (sym, name, seed)))
    trades = []; busyUntil = -1; perDay = {}; md = 1 if name == 'orb' else maxDay
    for (i, d, dist, nat) in sig:
        e = i + 1
        if i <= busyUntil or e >= D['n'] or D['sess'][e] != D['sess'][i] or perDay.get(D['sess'][i], 0) >= md: continue
        entry = O[e]; dist = dist * stopMult
        if dist <= 0: continue
        stop = entry - d * dist; tgt = entry + d * tgtR * dist if mode == 'bracket' else None
        j = e; exitPx = None; how = 'end'
        while True:
            if j > e and ((O[j] <= stop) if d > 0 else (O[j] >= stop)): exitPx = O[j]; how = 'stop'; break
            if (L[j] <= stop) if d > 0 else (H[j] >= stop): exitPx = stop; how = 'stop'; break
            if tgt is not None:
                if j > e and ((O[j] >= tgt) if d > 0 else (O[j] <= tgt)): exitPx = O[j]; how = 'tgt'; break
                if (H[j] >= tgt) if d > 0 else (L[j] <= tgt): exitPx = tgt; how = 'tgt'; break
            elif nat == 'vwap' and ((H[j] >= V[j]) if d > 0 else (L[j] <= V[j])): exitPx = V[j] if (O[j] < V[j] if d > 0 else O[j] > V[j]) else O[j]; how = 'own'; break
            elif nat == 'mid' and S20[j] and ((H[j] >= S20[j]) if d > 0 else (L[j] <= S20[j])): exitPx = S20[j] if (O[j] < S20[j] if d > 0 else O[j] > S20[j]) else O[j]; how = 'own'; break
            elif nat == 'sma5' and S5[j] and ((C[j] > S5[j]) if d > 0 else (C[j] < S5[j])): exitPx = C[j]; how = 'own'; break
            elif nat == 'cross' and j > e and ((E9[j] < E21[j]) if d > 0 else (E9[j] > E21[j])): exitPx = C[j]; how = 'own'; break
            if D['last'][j]: exitPx = C[j]; break
            j += 1
        r = d * (exitPx - entry) / dist
        cost = COST * (D['A'][i] or 0.0) / dist   # round-trip cost in R (0 before the ATR exists)
        trades.append(dict(sym=sym, t=D['T'][i], r=r, how=how, cost=cost)); busyUntil = j; perDay[D['sess'][i]] = perDay.get(D['sess'][i], 0) + 1
    return trades
COST = 0.1   # assumed round-trip cost (spread + commission) = 0.1 x the 5-minute ATR
def stats(tr, days):
    n = len(tr)
    if not n: return dict(n=0)
    w = [x['r'] for x in tr if x['r'] > 0]; l = [x['r'] for x in tr if x['r'] <= 0]
    tn = [x['r'] for x in tr if x['t'] < SPLIT]; te = [x['r'] for x in tr if x['t'] >= SPLIT]
    return dict(n=n, perDay=n / days, win=len(w) / n, tgt=sum(1 for x in tr if x['how'] == 'tgt') / n, end=sum(1 for x in tr if x['how'] == 'end') / n, own=sum(1 for x in tr if x['how'] == 'own') / n,
                Ec=sum(x['r'] - x['cost'] for x in tr) / n, E=sum(x['r'] for x in tr) / n, tot=sum(x['r'] for x in tr),
                avgW=sum(w) / len(w) if w else 0, avgL=sum(l) / len(l) if l else 0, Esep=sum(tn) / len(tn) if tn else 0, Eoct=sum(te) / len(te) if te else 0)
if __name__ == '__main__':
    days = sum(data(s)['days'] for s in SY)
    RUNS = [('Opening range breakout (30 min)', 'orb'), ('VWAP 2-sigma band reversion', 'vwap2sd'), ('Bollinger Band (20, 2) reversion', 'bb'),
            ('RSI(2) pullback in EMA200 trend (Connors-style)', 'rsi2'), ('EMA 9/21 cross with EMA200 trend', 'ema9_21'), ('Random entries (benchmark)', 'random')]
    res = []
    def show(tag, st, pos):
        print('   %-26s n %4d %.1f/day | target hit %4.1f%% | closed in profit %4.1f%% | own exit %4.1f%% | session close %4.1f%% | R/trade %+.3f (Sep %+.3f Oct %+.3f) | after costs %+.3f | positive on %d/10%s' % (
            tag, st['n'], st['perDay'], 100 * st['tgt'], 100 * st['win'], 100 * st['own'], 100 * st['end'], st['E'], st['Esep'], st['Eoct'], st['Ec'], pos,
            ('  [avg win %+.2fR, avg loss %+.2fR]' % (st['avgW'], st['avgL'])) if tag.startswith('own') else ''), flush=True)
    for label, nm in RUNS:
        print(label); row = dict(label=label)
        variants = [('1:1 (1 ATR stop)', 'bracket', 1.0, 1.0), ('1:2 (1 ATR stop)', 'bracket', 2.0, 1.0)]
        if nm not in ('orb', 'random'): variants += [('own exit, 1 ATR stop', 'native', None, 1.0), ('own exit, 3 ATR stop', 'native', None, 3.0)]
        if nm == 'orb': variants = [('1:1 (stop = other side)', 'bracket', 1.0, 1.0), ('1:2 (stop = other side)', 'bracket', 2.0, 1.0)]
        for tag, mode, t, sm in variants:
            tr = [x for s_ in SY for x in backtest(s_, nm, mode, tgtR=t or 1.0, stopMult=sm)]
            pos = sum(1 for s_ in SY if (lambda q: q and sum(q) / len(q) > 0)([x['r'] for x in tr if x['sym'] == s_]))
            st = stats(tr, days); row[tag] = dict(st, pos=pos); show(tag, st, pos)
        res.append(row)
    print('How a 70-80% win rate is usually made: a small target against a bigger stop')
    for t in (0.5, 0.3, 0.2):
        for label, nm in (('Random entries', 'random'), ('RSI(2) pullback', 'rsi2'), ('VWAP 2-sigma reversion', 'vwap2sd')):
            st = stats([x for s_ in SY for x in backtest(s_, nm, 'bracket', tgtR=t)], days)
            print('   target %.1fR vs 1R stop  %-24s n %4d  target hit %4.1f%%  R/trade %+.3f  after costs %+.3f' % (t, label, st['n'], 100 * st['tgt'], st['E'], st['Ec']))
    json.dump(res, open(S + '/research/classic/classic.json', 'w'))
    print('sessions in the data:', days)
