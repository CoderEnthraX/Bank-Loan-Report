"""How flat was the VWAP at each signal candle, and do flat-VWAP signals fail more? (research only, no indicator change)
Slope = VWAP change over the last N bars, in ATR(14) units, signed in the trade direction (+ = VWAP moving the trade's way).
Measured on the signal (displacement) candle; bars within N bars of the VWAP reset are put in their own group.
Failed = stopped out before reaching TP1. Default settings and the best (S1) settings, every timeframe."""
import sys, pickle, collections, math, multiprocessing as mp
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
NS = (3, 10, 20)
def job(arg):
    tf, name, cfg = arg
    import geng, ref_gs
    ref_gs.eprep = geng.ref_g.eprep; geng.ref_g = ref_gs
    o = dict(cfg); p1 = o.pop('p1', 0.0)
    vw = o.get('vwAnchorG', 'session'); src = o.get('vwSrcG', 'hlc3')
    P = geng.prepare(tf, vw, src); geng._CUR['vw'] = vw; geng._CUR['src'] = src
    o2 = {k: v for k, v in o.items() if k not in ('vwAnchorG', 'vwSrcG')}
    p = dict(ref_gs.IN); p.update(o2)
    raw = ref_gs.run(tf, o2)
    V, C, tr, an = P['V'], P['C'], P['tr'], P['anch']; n = len(V)
    atr = [0.0] * n; a = tr[0]
    for i in range(n): a = tr[i] if i == 0 else a + (tr[i] - a) / p['atrLen']; atr[i] = a
    since = [0] * n; c = 0
    for i in range(n):
        c = 0 if an[i] else c + 1; since[i] = c
    R = (p['tp1R'], p['tp2R'], p['tp3R'], p['tp4R']); xk = p['exitAt']; exitR = R[xk - 1]; tol = P['mt'] * 0.001
    out = []
    for x in raw:
        if x['exit'] is None or x['ghost']: continue
        i = x['arm']; d = x['dir']; risk = d * (x['entry'] - x['stop']); res = x['res']
        win = res is not None and abs(res - exitR) < 1e-9 and x['exit'] > x['fill']
        tp1 = win or (xk > 1 and d * (x['best'] - (x['entry'] + d * R[0] * risk)) >= -tol)
        sl = {N: (d * (V[i] - V[i - N]) / atr[i] if since[i] >= N and atr[i] > 0 else None) for N in NS}
        dist = d * (C[i] - V[i]) / atr[i] if atr[i] > 0 else 0.0
        out.append(dict(t=P['T'][x['fill']], res=res, c=P['SP'][x['fill']] / risk, win=win, tp1=tp1, slope=sl, dist=dist, since=since[i],
                        pct10=(d * (V[i] - V[i - 10]) / V[i] * 100.0 if since[i] >= 10 else None), atrpct=atr[i] / C[i] * 100.0))
    return tf, name, out
if __name__ == '__main__':
    C = {}
    for tf in ('M1', 'M5', 'M15', 'H1'):
        Cat = pickle.load(open(S + '/gold/catalog_%s.pkl' % tf, 'rb'))
        C[(tf, 'default')] = {}
        C[(tf, 'best')] = [s['cfg'] for s in Cat['strategies'] if 'Most profit' in [n for n, _ in s['scen']]][0]
    with mp.Pool(4) as pool:
        res = pool.map(job, [(tf, nm, cfg) for (tf, nm), cfg in C.items()])
    pickle.dump({(tf, nm): out for tf, nm, out in res}, open(S + '/gold/flat_vwap.pkl', 'wb'))
    print('saved', [(tf, nm, len(out)) for tf, nm, out in res])
