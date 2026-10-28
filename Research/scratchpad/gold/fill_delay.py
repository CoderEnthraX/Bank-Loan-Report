"""Trades grouped by how many candles after the signal candle the limit filled (1 = the very next candle). Research only."""
import sys, pickle, multiprocessing as mp
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
def job(arg):
    tf, name, cfg = arg
    import geng, ref_gs
    ref_gs.eprep = geng.ref_g.eprep; geng.ref_g = ref_gs
    o = dict(cfg); o.pop('p1', None); geng._CUR['vw'] = o.pop('vwAnchorG', 'session'); geng._CUR['src'] = o.pop('vwSrcG', 'hlc3')
    P = geng.prepare(tf, geng._CUR['vw'], geng._CUR['src']); p = dict(ref_gs.IN); p.update(o)
    R = (p['tp1R'], p['tp2R'], p['tp3R'], p['tp4R']); xk = p['exitAt']; tol = P['mt'] * 0.001; out = []
    for x in ref_gs.run(tf, o):
        if x['exit'] is None or x['ghost']: continue
        d = x['dir']; risk = d * (x['entry'] - x['stop']); res = x['res']
        win = res is not None and abs(res - R[xk - 1]) < 1e-9 and x['exit'] > x['fill']
        tp1 = win or (xk > 1 and d * (x['best'] - (x['entry'] + d * R[0] * risk)) >= -tol)
        out.append(dict(delay=x['fill'] - x['arm'], res=res, c=P['SP'][x['fill']] / risk, win=win, tp1=tp1, y=P['T'][x['fill']].year))
    return tf, name, out
if __name__ == '__main__':
    jobs = []
    for tf in ('M1', 'M5', 'M15', 'H1'):
        cat = pickle.load(open(S + '/gold/catalog_%s.pkl' % tf, 'rb'))
        best = [s['cfg'] for s in cat['strategies'] if 'Most profit' in [n for n, _ in s['scen']]][0]
        jobs += [(tf, 'default', {}), (tf, 'best (S1)', best)]
    with mp.Pool(4) as pool: res = pool.map(job, jobs)
    import anaA
    for tf, name, out in res:
        print('\n%s %s: %d trades' % (tf, name, len(out)))
        for k in range(1, 13):
            q = [x for x in out if x['delay'] == k]
            if not q: continue
            n = len(q); A = [x for x in q if x['y'] <= 2023]; B = [x for x in q if x['y'] >= 2024]
            e = lambda z: sum(x['res'] - x['c'] for x in z) / len(z) if z else float('nan')
            print('   filled on candle %2d after the signal: %5d trades (%4.1f%%)  failed before TP1 %4.1f%%  win %4.1f%%  R/trade %+.3f  (2021-23 %+.3f, 2024-26 %+.3f)' % (
                k, n, 100 * n / len(out), 100 * sum(1 for x in q if not x['tp1']) / n, 100 * sum(1 for x in q if x['win']) / n, e(q), e(A), e(B)))
    print('\nRetest Window setting tested alone (default 5), all other settings default:')
    for tf in ('M1', 'M5', 'M15', 'H1'):
        C, M = anaA.sweep_metrics(tf)
        for nm in ('retestBars = 2', 'retestBars = 3', 'default', 'retestBars = 8', 'retestBars = 12'):
            m = M.get(nm)
            if m: print('   %-4s %-16s trades %5d  R/trade 2021-23 %+.3f  2024-26 %+.3f  win %4.1f%%  longest W/L %d/%d' % (tf, 'retestBars = 5' if nm == 'default' else nm, m['n'], m['EcA'], m['EcB'], 100 * m['win'], m['maxW'], m['maxL']))
