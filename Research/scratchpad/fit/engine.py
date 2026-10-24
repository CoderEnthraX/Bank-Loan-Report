"""Bar-by-bar replica of the Pine 'Auction Retest Model' state machine, parameterised for rule fitting."""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arp_data import load

def mintick_of(rows):
    best = 0
    for r in rows[:3000]:
        for k in ('o', 'h', 'l', 'c'):
            s = repr(r[k])
            if '.' in s:
                d = len(s.split('.')[1].rstrip('0'))
                best = max(best, d)
    return 10 ** -best if best else 1.0

def rtick(x, mt):
    return math.floor(x / mt + 0.5) * mt

def tr_series(rows):
    out = [rows[0]['h'] - rows[0]['l']]
    for a, b in zip(rows, rows[1:]):
        out.append(max(b['h'] - b['l'], abs(b['h'] - a['c']), abs(b['l'] - a['c'])))
    return out

def rma(x, n):
    o = [None] * len(x); s = None
    for i in range(len(x)):
        if i < n - 1: continue
        s = sum(x[i - n + 1:i + 1]) / n if s is None else (s * (n - 1) + x[i]) / n
        o[i] = s
    return o

def day_starts(rows):
    """VWAP resets on a new trading day: the first bar's VWAP equals its hlc3."""
    st = [False] * len(rows); st[0] = True
    for i, r in enumerate(rows):
        if i and r['vwap'] is not None and abs(r['vwap'] - (r['h'] + r['l'] + r['c']) / 3) <= 1e-9 * max(1, abs(r['vwap'])) * 10:
            st[i] = True
    return st

DEFAULT = dict(structLen=6, retest=5, dispAtr=0.8, bodyPct=60.0, closePct=30.0, stopAtr=1.8, cooldown=2,
               maxFills=5, atrLen=14, tp4=2.0, vwapFilter=True)

MINTICK = {'GC': 0.1, 'EURUSD': 1e-5, 'NASDAQ': 0.1, 'US30': 0.01, 'CRUDE': 1.0, 'NIFTY': 0.05, 'SENSEX': 0.01, 'ETH': 0.1}

def prepare(sym):
    rows = load(sym)
    pt = mintick_of(rows)
    return dict(sym=sym, rows=rows, mt=MINTICK.get(sym) or pt, tr=tr_series(rows), daystart=day_starts(rows))

def run(P, cfg=None, hooks=None):
    """Returns list of trades: dict(dir, arm, fill, entry, stop, exit, res)."""
    c = dict(DEFAULT); c.update(cfg or {})
    H = hooks or {}
    rows, mt = P['rows'], P['mt']
    atr = P.setdefault(('atr', c['atrLen']), rma(P['tr'], c['atrLen']))
    n = len(rows); L = c['structLen']
    st = 0; armBar = fillBar = lastExit = None; lim = stp = t4 = None; risk = None
    dayFills = 0; trades = []; cur = None
    for i in range(n):
        r = rows[i]
        if P['daystart'][i]: dayFills = 0
        # 1. manage live trade
        if abs(st) == 2 and i > fillBar:
            isL = st == 2
            sh = r['l'] <= stp if isL else r['h'] >= stp
            th = r['h'] >= t4 if isL else r['l'] <= t4
            if sh or th:
                cur.update(exit=i, res=(-1.0 if sh else c['tp4'])); lastExit = i; st = 0
        # 2. armed limit
        if abs(st) == 1 and i > armBar:
            isL = st == 1
            touched = r['l'] <= lim if isL else r['h'] >= lim
            if touched and dayFills < c['maxFills']:
                st = 2 if isL else -2; fillBar = i; dayFills += 1
                cur = dict(dir=1 if isL else -1, arm=armBar, fill=i, entry=lim, stop=stp, t4=t4, exit=None, res=None, risk=risk)
                trades.append(cur)
                if (r['l'] <= stp if isL else r['h'] >= stp):
                    cur.update(exit=i, res=-1.0); lastExit = i; st = 0
            elif i - armBar >= c['retest']:
                st = 0
        # 3. arm
        if i < L + 1 or atr[i] is None: continue
        cooled = lastExit is None or i - lastExit >= c['cooldown']
        if not (abs(st) != 2 and cooled and dayFills < c['maxFills'] and atr[i] > 0): continue
        ph = max(x['h'] for x in rows[i - L:i]); pl = min(x['l'] for x in rows[i - L:i])
        rng = r['h'] - r['l']; body = abs(r['c'] - r['o']); mid = (r['o'] + r['c']) / 2
        vw = r['vwap']
        big = rng > 0 and rng >= c['dispAtr'] * atr[i] and body / rng * 100 >= c['bodyPct']
        bull = r['c'] > r['o'] and r['c'] > ph and big and (r['h'] - r['c']) / rng * 100 <= c['closePct'] and (not c['vwapFilter'] or (vw is not None and r['c'] > vw))
        bear = r['c'] < r['o'] and r['c'] < pl and big and (r['c'] - r['l']) / rng * 100 <= c['closePct'] and (not c['vwapFilter'] or (vw is not None and r['c'] < vw))
        if 'disp' in H:
            bull, bear = H['disp'](P, i, c, atr, bull, bear, ph, pl)
        if not (bull or bear): continue
        d = 1 if bull else -1
        entry = max(mid, ph) if bull else min(mid, pl)
        if 'entry' in H: entry = H['entry'](P, i, c, atr, d, entry, ph, pl)
        stop = entry - d * c['stopAtr'] * atr[i]
        if 'stop' in H: stop = H['stop'](P, i, c, atr, d, entry, stop)
        rk = d * (entry - stop)
        if rk >= mt and rtick(stop, mt) != rtick(entry, mt):
            st = d; armBar = i; lim = rtick(entry, mt); stp = rtick(stop, mt); risk = rk
            t4 = rtick(lim + d * c['tp4'] * rk, mt)
    return trades
