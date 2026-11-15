"""Monthly Crooks E-J x profit ladder workbook (asked 2026-11-15), Fractal Breakout Grid part: the trades of the 12 strategies on a gold M5
chart (S12, an M1 strategy, is switched off there) and on an M15 chart (S10 and S12 off), as the indicator / strategy model computes them on
that chart's candles (engine.run on the chart TF = the Pine twin, checked here trade for trade). Times are IST (the grid's default time zone).
Also stores the twin's own money for the default setting (Crooks F + ladder Medium, $500 cap clamp) to cross-check the money runs.
Output: mcej/grid_trades.pkl  {(ctf, k): dict(prm, trades=[dict(t, tx, F, X, why, R, c, sd, levk, rmin)], twin=dict(risks, net, pnl))}"""
import sys, pickle, datetime as dt, multiprocessing as mp
from zoneinfo import ZoneInfo
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/fractal'); sys.path.insert(0, S + '/gold')
import engine as EN, pine_twin2 as TW
from final11 import ALL12

IST = ZoneInfo('Asia/Kolkata')
COST = 0.23; LEV = 100.0; E_UNITS = 1.0          # costs per unit (price units), 1:100, 0.01 lot = 1 oz
_B = None


def bars():
    global _B
    if _B is None: _B = EN.load()
    return _B


def job(arg):
    ctf, k = arg
    B = bars(); p = ALL12[k - 1]; sl, tp = p[4], p[5]
    tr = EN.run(B, ctf, *p)
    tw = TW.twin2(B, ctf, p, TW.P())                       # the Pine model with its default money (Crooks F + ladder Medium)
    utc = TW.chart_utc(B, ctf)
    a = [(int(x[0]), round(float(x[1]), 6), int(x[2]), round(float(x[3]), 6), int(x[4])) for x in tr]
    b = [(int(e), round(float(F), 6), int(xb), round(float(X), 6), int(r)) for e, F, xb, X, r in tw.trades]
    same = a == b
    out = []
    for e, F, xb, X, why in a:
        sd = F * sl / 100.0
        out.append(dict(t=dt.datetime.fromtimestamp(int(utc[e]), IST).replace(tzinfo=None), tx=dt.datetime.fromtimestamp(int(utc[xb]), IST).replace(tzinfo=None),
                        F=F, X=X, why=why, R=(X - F) / sd, c=COST / sd, sd=sd, levk=LEV * (sd + COST) / F, rmin=E_UNITS * (sd + COST)))
    pnl = [r_ * (x['R'] - x['c']) / (1.0 + x['c']) for r_, x in zip(tw.risks, out)]
    return (ctf, k), dict(prm=p, trades=out, same=same, n_engine=len(a), n_twin=len(b), twin=dict(risks=list(tw.risks), net=tw.net, pnl=pnl))


if __name__ == '__main__':
    jobs = [(ctf, k) for ctf in ('M5', 'M15') for k in range(1, 13) if EN.TF_SEC[ALL12[k - 1][0]] >= EN.TF_SEC[ctf]]
    with mp.Pool(4) as pool: R = pool.map(job, jobs, chunksize=1)
    D = dict(R)
    pickle.dump(D, open(S + '/mcej/grid_trades.pkl', 'wb'))
    for (ctf, k), v in sorted(D.items(), key=lambda kv: (kv[0][0] != 'M5', kv[0][1])):
        tr = v['trades']; cross = sum(1 for x in tr if (x['t'].year, x['t'].month) != (x['tx'].year, x['tx'].month))
        print('%-3s S%-2d %-36s | engine %4d twin %4d identical %s | twin net (F + Medium) %+9.2f, sum pnl %+9.2f | %s .. %s | crossing a month end %d' % (
            ctf, k, str(v['prm']), v['n_engine'], v['n_twin'], v['same'], v['twin']['net'], sum(v['twin']['pnl']),
            tr[0]['t'] if tr else '-', tr[-1]['tx'] if tr else '-', cross))
