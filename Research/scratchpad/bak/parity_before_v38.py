"""parity.py - EA engine (compiled harness) vs Python reference (S/build/ref.py), trade for trade. Run: python3 -I parity.py [SYM ...]"""
import sys, os, subprocess, datetime, calendar
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
RUN = S + '/mq5check/run'
sys.path.insert(0, S + '/build')
import ref
from multiprocessing import Pool

SYMS = ['GC', 'EURUSD', 'NASDAQ', 'US30', 'CRUDE', 'NIFTY', 'SENSEX', 'ETH', 'NSE_NIFTY1', 'MCX_NATURALGAS']
ORIG_EPREP = ref.eprep
ORIG_WEIGHTS = ref.weights
TOL = 1e-9

# name: (ref options, EA inputs)
CONFIGS = [
    ('default', {}, {}),
    ('halfCap', dict(halfCap=True), dict(InpHalfCap=1)),
    ('chopOn+chopMax12', dict(chopOn=True, chopMax=12.0), dict(InpChopOn=1, InpChopMax=12)),
    ('emaOn+emaMax1.65', dict(emaOn=True, emaMax=1.65), dict(InpEmaOn=1, InpEmaMax=1.65)),
    ('noChase', dict(noChase=True), dict(InpNoChase=1)),
    ('noChase+skipFirstSess', dict(noChase=True, _skipFirstSess=True), dict(InpNoChase=1)),
    ('mv2On+mv2R0', dict(mv2On=True, mv2R=0.0), dict(InpMv2On=1, InpMv2R=0)),
    ('mv1On(0)+mv3On(1.0)', dict(mv1On=True, mv1R=0.0, mv3On=True, mv3R=1.0), dict(InpMv1On=1, InpMv1R=0, InpMv3On=1, InpMv3R=1.0)),
    ('deepOn', dict(deepOn=True), dict(InpDeepOn=1)),
    ('halfStrict', dict(halfStrict=True), dict(InpHalfStrict=1)),
    ('lossBlock', dict(lossBlock=True), dict(InpLossBlock=1)),
    ('exitAt2', dict(exitAt=2), dict(InpExitAt=2)),
    ('entry pct30', dict(entryMode='pct', entryPct=30.0), dict(InpEntryMode=1, InpEntryPct=30)),
    ('entry market', dict(entryMode='market'), dict(InpEntryMode=2)),
    ('rearmKeep off', dict(rearmKeep=False), dict(InpRearm=1)),
    ('stopMode swing', dict(stopMode='swing'), dict(InpStopMode=1)),
    ('days Mon/Wed/Fri', dict(dayOn=True, days=(True, False, True, False, True, False, False)),
     dict(InpDayOn=1, InpMon=1, InpTue=0, InpWed=1, InpThu=0, InpFri=1, InpSat=0, InpSun=0)),
    ('hours 1000-2000', dict(hoursOn=True, hoursSess=(1000, 2000)), dict(InpHoursOn=1, InpStartH=10, InpStartM=0, InpEndH=20, InpEndM=0)),
    ('killzones all, shift 0', dict(kzOn=True), dict(InpKzOn=1)),
    ('killzones Asia+NY, +1', dict(kzOn=True, kz=(True, False, True, False), kzShift=1), dict(InpKzOn=1, InpKzLon=0, InpKzLc=0, InpKzShift=1)),
    ('killzones Lon+LC, -2', dict(kzOn=True, kz=(False, True, False, True), kzShift=-2), dict(InpKzOn=1, InpKzAsia=0, InpKzNy=0, InpKzShift=-2)),
    ('killzones all, +2', dict(kzOn=True, kzShift=2), dict(InpKzOn=1, InpKzShift=2)),
    ('min 1 ATR from VWAP', dict(minVwOn=True), dict(InpMinVwOn=1)),
    ('min 1 ATR + Don\'t Chase 2.0', dict(minVwOn=True, noChase=True, noChaseSig=2.0), dict(InpMinVwOn=1, InpNoChase=1, InpNoChaseSig=2.0)),
    ('min 0.5 ATR + chop + ema', dict(minVwOn=True, minVwAtr=0.5, chopOn=True, emaOn=True), dict(InpMinVwOn=1, InpMinVwAtr=0.5, InpChopOn=1, InpEmaOn=1)),
    ('dayStopR2', dict(dayStopR=2.0), dict(InpDayStopR=2)),
    ('maxFills2', dict(maxFills=2), dict(InpMaxFills=2)),
    ('chop+ema+halfCap', dict(chopOn=True, emaOn=True, halfCap=True), dict(InpChopOn=1, InpEmaOn=1, InpHalfCap=1)),
    ('max 3 ATR from VWAP', dict(maxVwOn=True, maxVwDist=3.0), dict(InpMaxVwOn=1, InpMaxVwDist=3.0)),
    ('max distance on, default value (both sides)', dict(maxVwOn=True), dict(InpMaxVwOn=1)),
    ('max 1.5 ATR + min 0.5 ATR', dict(maxVwOn=True, maxVwDist=1.5, minVwOn=True, minVwAtr=0.5), dict(InpMaxVwOn=1, InpMaxVwDist=1.5, InpMinVwOn=1, InpMinVwAtr=0.5)),
    ('max price 2.0', dict(maxVwOn=True, maxVwDist=2.0, maxVwUnit='price'), dict(InpMaxVwOn=1, InpMaxVwDist=2.0, InpMaxVwUnit=1)),
    ('max price 0.0015', dict(maxVwOn=True, maxVwDist=0.0015, maxVwUnit='price'), dict(InpMaxVwOn=1, InpMaxVwDist=0.0015, InpMaxVwUnit=1)),
    ('max price 40 + noChase', dict(maxVwOn=True, maxVwDist=40.0, maxVwUnit='price', noChase=True), dict(InpMaxVwOn=1, InpMaxVwDist=40.0, InpMaxVwUnit=1, InpNoChase=1)),
]


def tick_digits(t):
    return len(('%.10f' % t).rstrip('0').split('.')[1])


def prep_sym(sym):
    """Common inputs for both engines: returns (P', csv path, look, n)."""
    P = ORIG_EPREP(sym)
    rows = P['rows']; n = len(rows)
    ist = [datetime.datetime.strptime(r['t'], '%Y-%m-%d %H:%M') for r in rows]
    srv = [calendar.timegm(x.timetuple()) - 5 * 3600 - 1800 + 2 * 3600 for x in ist]   # IST -> UTC -> server (GMT+2)
    path = '%s/data/%s.csv' % (RUN, sym)
    with open(path, 'w') as f:
        for i, r in enumerate(rows):
            f.write('%d,%r,%r,%r,%r\n' % (srv[i], r['o'], r['h'], r['l'], r['c']))
    return P, path, srv


def build_slice(P, srv, look):
    rows = P['rows']; n = len(rows)
    sl = [dict(r) for r in rows[look:n - 1]]
    ssrv = srv[look:n - 1]
    days = [datetime.datetime.fromtimestamp(x, datetime.timezone.utc).date() for x in ssrv]
    ds = [True] + [days[i] != days[i - 1] for i in range(1, len(days))]
    cumPV = cumW = 0.0
    for i, r in enumerate(sl):
        if ds[i]: cumPV = 0.0; cumW = 0.0
        src = (r['h'] + r['l'] + r['c']) / 3.0
        cumPV += src * 1.0; cumW += 1.0
        r['vwap'] = cumPV / cumW
    tr = [sl[0]['h'] - sl[0]['l']]
    for a, b in zip(sl, sl[1:]):
        tr.append(max(b['h'] - b['l'], abs(b['h'] - a['c']), abs(b['l'] - a['c'])))
    return dict(sym=P['sym'], rows=sl, mt=P['mt'], tr=tr, daystart=ds)


def run_ea(path, tick, ea):
    cmd = [RUN + '/ea_harness', path, 'TICK=%r' % tick, 'DIGITS=%d' % tick_digits(tick)] + ['%s=%r' % kv for kv in ea.items()]
    out = subprocess.run(cmd, capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError('harness failed: %s' % out.stderr)
    trades, cur, stats = [], None, None
    for ln in out.stdout.splitlines():
        w = ln.split()
        if w[0] == 'FILL':
            cur = dict(dir=int(w[3]), arm=int(w[2]), fill=int(w[1]), entry=float(w[4]), stop=float(w[5]), exit=None, res=None); trades.append(cur)
        elif w[0] == 'EXIT':
            cur['exit'] = int(w[1]); cur['res'] = float(w[2])
        elif w[0] == 'STATS':
            stats = [float(x) for x in w[1:]]
    return trades, stats


def close(a, b):
    if a is None or b is None: return a is b
    return abs(a - b) <= TOL * max(1.0, abs(a), abs(b))


def same_trade(a, b):
    return (a['dir'] == b['dir'] and a['arm'] == b['arm'] and a['fill'] == b['fill'] and a['exit'] == b['exit']
            and close(a['entry'], b['entry']) and close(a['stop'], b['stop']) and close(a['res'], b['res']))


def pine_stats(trades, ghosts, Pn, p):
    """STATS block recomputed from the reference trades and bars (independent of the EA code)."""
    rows = Pn['rows']; mt = Pn['mt']; tol = mt * 0.001
    H = [r['h'] for r in rows]; L = [r['l'] for r in rows]
    exitK = p.get('exitAt', 4)
    R = [p.get('tp1R', 0.6), p.get('tp2R', 1.0), p.get('tp3R', 1.5), p.get('tp4R', 2.0)]
    exitR = R[exitK - 1]
    totW = totL = 0; totR = 0.0; tp = [0, 0, 0, 0]; be = lk = 0
    for x in trades:
        if x['exit'] is None: continue
        d = x['dir']; win = close(x['res'], exitR) and x['res'] > 0 and not (x['exit'] == x['fill'])
        risk = d * (x['entry'] - x['stop'])
        lv = [x['entry'] + d * R[k] * risk for k in range(4)]
        # walk the bars after the fill, tracking the (possibly moved) stop exactly as the engine does
        stp = x['stop']; best = x['entry']; tpHit = 0
        for j in range(x['fill'] + 1, x['exit'] + 1):
            sh = (L[j] <= stp + tol) if d == 1 else (H[j] >= stp - tol)
            th = (H[j] >= lv[exitK - 1] - tol) if d == 1 else (L[j] <= lv[exitK - 1] + tol)
            reached = 0
            for k in (2, 1, 0):
                if (H[j] >= lv[k] - 0 if d == 1 else L[j] <= lv[k]):
                    reached = k + 1; break
            prev = tpHit; tpHit = max(tpHit, reached)
            if not sh: best = max(best, H[j]) if d == 1 else min(best, L[j])
            if sh or th: break
            if tpHit > prev:
                ns = stp
                for kk, (on, mr) in enumerate(((p.get('mv1On'), p.get('mv1R', 0.0)), (p.get('mv2On'), p.get('mv2R', 0.6)), (p.get('mv3On'), p.get('mv3R', 1.0))), 1):
                    if on and tpHit >= kk: ns = max(ns, x['entry'] + mr * risk) if d == 1 else min(ns, x['entry'] - mr * risk)
                stp = ns
        moved = stp != x['stop']
        if win: totW += 1
        else: totL += 1
        totR += x['res']
        for k in range(1, 5):
            if win:
                if k <= exitK: tp[k - 1] += 1
            elif k < exitK and d * (best - lv[k - 1]) >= -tol: tp[k - 1] += 1
        if not win and moved:
            if x['res'] == 0.0: be += 1
            elif x['res'] > 0.0: lk += 1
    gW = gL = 0; gR = 0.0
    for x in ghosts:
        if x['exit'] is None: continue
        if close(x['res'], exitR) and x['res'] > 0 and x['exit'] != x['fill']: gW += 1
        else: gL += 1
        gR += x['res']
    return [totW, totL, totR] + tp + [be, lk, gW, gL, gR]


STAT_NAMES = ['totW', 'totL', 'totR', 'tp1', 'tp2', 'tp3', 'tp4', 'beN', 'lkN', 'ghW', 'ghL', 'ghR']


def work(sym):
    P, path, srv = prep_sym(sym)
    n = len(P['rows']); opts0 = dict(ref.IN)
    look = max(10, 6 + 1, 10 + 1, 6) + 2
    Pn = build_slice(P, srv, look)
    ref.eprep = lambda s: Pn
    ref.weights = lambda s: [1.0] * len(Pn['rows'])
    res = []
    for name, ro, ea in CONFIGS:
        p = dict(ref.IN); p.update(ro)
        eat, eas = run_ea(path, Pn['mt'], ea)
        allr = ref.run(sym, ro)
        shown = [x for x in allr if not x['ghost']]; ghosts = [x for x in allr if x['ghost']]
        rs = pine_stats(shown, ghosts, Pn, p)
        diffs = []
        for i in range(max(len(eat), len(shown))):
            a = eat[i] if i < len(eat) else None; b = shown[i] if i < len(shown) else None
            if a is None or b is None or not same_trade(a, b):
                diffs.append((i, a, b))
        ident = max(len(eat), len(shown)) - len(diffs)
        sd = [(STAT_NAMES[k], eas[k], rs[k]) for k in range(12) if not close(eas[k], rs[k])]
        res.append((name, len(shown), len(eat), ident, diffs[:3], sd))
    return sym, res


if __name__ == '__main__':
    syms = sys.argv[1:] or SYMS
    with Pool(min(len(syms), os.cpu_count() or 2)) as pool:
        out = dict(pool.map(work, syms))
    bad = 0
    print('%-22s %7s %7s %9s  %s' % ('config', 'ref', 'EA', 'identical', 'stats'))
    for ci, (name, _, _) in enumerate(CONFIGS):
        tr = ea = idn = 0; st_bad = []; d_syms = []
        for sym in syms:
            nm, nref, nea, ident, diffs, sd = out[sym][ci]
            tr += nref; ea += nea; idn += ident
            if sd: st_bad.append(sym)
            if diffs: d_syms.append(sym)
        ok = (tr == ea == idn) and not st_bad
        bad += not ok
        print('%-22s %7d %7d %9d  %s' % (name, tr, ea, idn, 'stats OK' if not st_bad else 'STATS DIFFER: ' + ','.join(st_bad)) + ('' if not d_syms else '  TRADES DIFFER: ' + ','.join(d_syms)))
    for ci, (name, _, _) in enumerate(CONFIGS):
        for sym in syms:
            nm, nref, nea, ident, diffs, sd = out[sym][ci]
            for (i, a, b) in diffs:
                print('DIFF %s / %s trade#%d\n   EA : %s\n   ref: %s' % (name, sym, i, a, b))
            for (k, ea_v, rf_v) in sd:
                print('STAT %s / %s %s: EA %r ref %r' % (name, sym, k, ea_v, rf_v))
    print('ALL IDENTICAL' if not bad else '%d configs differ' % bad)
