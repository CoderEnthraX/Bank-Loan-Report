"""Gold research harness: prepared bars per timeframe, engine runs, per-trade TP statistics, period tables and streaks."""
import sys, pickle, datetime, collections
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold'); sys.path.insert(0, S + '/build'); sys.path.insert(0, S + '/fit')
import ref_g
_P = {}
_RAW = {}
def prepare(tf, vw='session', src='hlc3'):
    key = (tf, vw, src)
    if key in _P: return _P[key]
    if tf not in _RAW: _RAW[tf] = pickle.load(open('%s/gold/data/%s.pkl' % (S, tf), 'rb'))
    d = _RAW[tf]
    srv, utc, O, H, L, C, TV, SP = (d[k] for k in ('srv', 'utc', 'O', 'H', 'L', 'C', 'TV', 'SP')); n = len(O)
    ds = [i == 0 or srv[i].date() != srv[i - 1].date() for i in range(n)]
    if vw == 'session': an = ds
    else:
        kf = (lambda t: t.isocalendar()[:2]) if vw == 'week' else (lambda t: (t.year, t.month))
        an = [i == 0 or (ds[i] and kf(srv[i]) != kf(srv[i - 1])) for i in range(n)]
    sf = {'hlc3': lambda i: (H[i] + L[i] + C[i]) / 3.0, 'close': lambda i: C[i], 'hl2': lambda i: (H[i] + L[i]) / 2.0, 'ohlc4': lambda i: (O[i] + H[i] + L[i] + C[i]) / 4.0}[src]
    V = [0.0] * n; cpv = cw = 0.0
    for i in range(n):
        if an[i]: cpv = cw = 0.0
        w = TV[i] if TV[i] > 0 else 1.0; sv = sf(i)
        cpv += sv * w; cw += w; V[i] = cpv / cw
    tr = [H[0] - L[0]] + [max(H[i] - L[i], abs(H[i] - C[i - 1]), abs(L[i] - C[i - 1])) for i in range(1, n)]
    P = dict(O=O, H=H, L=L, C=C, V=V, W=[float(x) if x > 0 else 1.0 for x in TV], T=[u + datetime.timedelta(hours=5, minutes=30) for u in utc],
             tr=tr, daystart=ds, anch=an, mt=0.01, SP=[x * 0.01 for x in SP], srv=srv)
    _P[key] = P; return P
_CUR = {'vw': 'session', 'src': 'hlc3'}
ref_g.eprep = lambda tf: prepare(tf, _CUR['vw'], _CUR['src'])
TPR = (0.6, 1.0, 1.5, 2.0)
def run(tf, opts=None, keep_ghost=False):
    o = dict(opts or {}); _CUR['vw'] = o.pop('vwAnchorG', 'session'); _CUR['src'] = o.pop('vwSrcG', 'hlc3')
    P = prepare(tf, _CUR['vw'], _CUR['src']); p = dict(ref_g.IN); p.update(o)
    xk = p['exitAt']; R = (p['tp1R'], p['tp2R'], p['tp3R'], p['tp4R']); exitR = R[xk - 1]; tol = P['mt'] * 0.001
    out = []
    for x in ref_g.run(tf, o):
        if x['exit'] is None or (x['ghost'] and not keep_ghost): continue
        d = x['dir']; risk = d * (x['entry'] - x['stop']); res = x['res']
        win = res is not None and abs(res - exitR) < 1e-9 and x['exit'] > x['fill']
        hits = [(k <= xk) if win else (k < xk and d * (x['best'] - (x['entry'] + d * R[k - 1] * risk)) >= -tol) for k in range(1, 5)]
        out.append(dict(t=P['T'][x['fill']], tx=P['T'][x['exit']], dir=d, res=res, win=win, risk=risk, hits=hits, ghost=x['ghost'],
                        be=(not win and x['stpX'] != x['stop'] and res == 0.0), sp=P['SP'][x['fill']], half=x['half']))
    return out
def streaks(seq):
    """max consecutive wins / losses (a 0R exit breaks both) and the list of loss-streak lengths"""
    mw = ml = cw = cl = 0; ls = []
    for r in seq:
        if r > 0: cw += 1; mw = max(mw, cw); (ls.append(cl) if cl else None); cl = 0
        elif r < 0: cl += 1; ml = max(ml, cl); cw = 0
        else: (ls.append(cl) if cl else None); cw = cl = 0
    if cl: ls.append(cl)
    return mw, ml, ls
def summarize(tr):
    n = len(tr)
    if not n: return dict(n=0)
    res = [x['res'] for x in tr]; mw, ml, _ = streaks(res)
    return dict(n=n, tp=[sum(x['hits'][k] for x in tr) / n for k in range(4)], win=sum(1 for x in tr if x['win']) / n,
                R=sum(res), E=sum(res) / n, Rc=sum(x['res'] - x['sp'] / x['risk'] for x in tr), maxW=mw, maxL=ml,
                be=sum(1 for x in tr if x['be']) / n)
def table(tr):
    """{year: {'year': summary, month: summary}} keyed on the IST fill time, plus 'all'"""
    by = collections.defaultdict(lambda: collections.defaultdict(list))
    for x in tr: by[x['t'].year][x['t'].month].append(x)
    out = {}
    for y in sorted(by):
        yt = [x for m in sorted(by[y]) for x in by[y][m]]
        out[y] = {'year': summarize(yt)}; out[y].update({m: summarize(by[y][m]) for m in sorted(by[y])})
    out['all'] = summarize(tr)
    return out
