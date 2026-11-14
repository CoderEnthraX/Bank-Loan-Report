"""Candidate settings on the 11 strategies (exact engine v2, M1, costs 0.23): each setting alone vs the plain strategy.
Hours / days in New York time; trend = the last completed candle of TF closed above its EMA (seeded with the first close)."""
import sys, pickle, numpy as np
from multiprocessing import Pool
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fractal')
import engine as EN, engine2 as E2
from final11 import ALL
G = {}


def ema(x, n):
    a = 2.0 / (n + 1.0); e = np.empty(len(x)); e[0] = x[0]
    for k in range(1, len(x)): e[k] = a * x[k] + (1 - a) * e[k - 1]
    return e


def init():
    B = EN.load(); t = B['t']; ny = t - 7 * 3600
    hr = (ny // 3600) % 24; dow = ((ny // 86400) + 3) % 7       # 0 = Monday
    G.update(B=B, t=t, hr=hr, dow=dow, day=(ny // 86400).astype(np.int64), yr=np.array([1970 + int(x // 31556952) for x in t]))
    tr = {}
    for tf in ('H1', 'H4', 'D1'):
        k = np.searchsorted(B[tf + '_t'], t, side='right') - 1
        for n in (20, 50, 200):
            e = ema(B[tf + '_C'], n); okk = np.r_[False, B[tf + '_C'][:-1] > e[:-1]]   # candle k: candle k-1 closed above its EMA
            tr['%s EMA%d' % (tf, n)] = okk[k]
    G['trend'] = tr


def variants():
    V = [('plain', {})]
    for nm, (h0, h1) in {'hours 02-17 NY': (2, 17), 'hours 02-12 NY': (2, 12), 'hours 07-17 NY': (7, 17), 'hours 02-08 NY': (2, 8), 'hours 18-02 NY (Asia)': (18, 2)}.items():
        V.append((nm, dict(hours=(h0, h1))))
    V += [('skip Monday', dict(days=(0,))), ('skip Friday', dict(days=(4,))), ('skip Mon + Fri', dict(days=(0, 4)))]
    for k in ('H1 EMA50', 'H1 EMA200', 'H4 EMA50', 'H4 EMA200', 'D1 EMA20', 'D1 EMA50', 'D1 EMA200'):
        V.append(('trend ' + k, dict(trend=k)))
    for k in (3, 6, 12, 24, 48): V.append(('expiry %d candles' % k, dict(kexp=k)))
    for a, d in ((0.0, 0.3), (0.3, 0.3), (0.5, 0.5), (0.5, 1.0), (1.0, 0.5), (1.0, 1.0), (0.2, 0.2), (2.0, 1.0)): V.append(('trail from +%.1f%% by %.1f%%' % (a, d), dict(trA=a, trD=d)))
    for h in (4, 8, 24, 72, 168): V.append(('time exit %dh' % h, dict(tExit=h * 3600)))
    for hh in (12, 15, 16): V.append(('weekend close Fri %02d NY' % hh, dict(wkh=hh)))
    V += [('entry on candle close', dict(emode=1)), ('max 1 trade a day', dict(maxDay=1)), ('max 2 trades a day', dict(maxDay=2))]
    return V


def job(arg):
    s, pm = arg; p = ALL[s]; B = G['B']; t = G['t']; n = len(t); out = {}
    for nm, kw in variants():
        allow = np.ones(n, np.bool_); wk = np.zeros(n, np.bool_)
        if 'hours' in kw:
            h0, h1 = kw['hours']; hr = G['hr']
            allow &= ((hr >= h0) & (hr < h1)) if h0 < h1 else ((hr >= h0) | (hr < h1))
        if 'days' in kw:
            for d in kw['days']: allow &= G['dow'] != d
        if 'trend' in kw: allow &= G['trend'][kw['trend']]
        if 'wkh' in kw:
            wk = (G['dow'] == 4) & (G['hr'] >= kw['wkh']); allow &= ~wk
        tr = E2.run2(B, 'M1', *p, allow=allow, wk=wk, dayid=G['day'], kexp=kw.get('kexp', 0), trA=kw.get('trA', 0.0), trD=kw.get('trD', 0.0),
                     tExit=kw.get('tExit', 0), emode=kw.get('emode', 0), maxDay=kw.get('maxDay', 0), pm=pm)
        st = EN.stats(tr, p[4]); ey = G['yr'][tr[:, 0].astype(int)] if len(tr) else np.array([])
        R = (tr[:, 3] - tr[:, 1] - 0.23) / (tr[:, 1] * p[4] / 100.0) if len(tr) else np.array([])
        out[nm] = dict(n=st['n'], R=st['R'], dd=st['ddR'], pf=st['pf'], trR=R[ey <= 2023].sum() if len(R) else 0.0, teR=R[ey >= 2024].sum() if len(R) else 0.0,
                       yrs=[R[ey == y].sum() for y in range(2021, 2027)] if len(R) else [0.0] * 6)
    return (s, pm), out


if __name__ == '__main__':
    with Pool(4, initializer=init) as pool: res = dict(pool.map(job, [(s, pm) for s in range(len(ALL)) for pm in (0, 2)]))
    pickle.dump(res, open('study2.pkl', 'wb'))
    names = [nm for nm, _ in variants()]
    print('%-30s | %s | sum R | +/- vs plain (strategies better R and not deeper DD) | high-first sum R' % ('setting', ' '.join('%6s' % ('S%d' % (s + 1)) for s in range(len(ALL)))))
    base = {s: res[(s, 0)]['plain'] for s in range(len(ALL))}; base2 = {s: res[(s, 2)]['plain'] for s in range(len(ALL))}
    for nm in names:
        r0 = [res[(s, 0)][nm] for s in range(len(ALL))]; r2 = [res[(s, 2)][nm] for s in range(len(ALL))]
        better = sum(1 for s in range(len(ALL)) if r0[s]['R'] > base[s]['R'] and r0[s]['dd'] <= base[s]['dd'] + 1e-9)
        worse = sum(1 for s in range(len(ALL)) if r0[s]['R'] < base[s]['R'])
        print('%-30s | %s | %+7.1f | better %2d, lower R %2d | %+7.1f (plain %+7.1f) | train %+7.1f test %+7.1f' % (nm, ' '.join('%+6.1f' % r['R'] for r in r0), sum(r['R'] for r in r0), better, worse,
              sum(r['R'] for r in r2), sum(b['R'] for b in base2.values()), sum(r['trR'] for r in r0), sum(r['teR'] for r in r0)))
