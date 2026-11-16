"""Grid presets on the Pine twin (pine_twin2, M1 chart = the grid EA) with the monthly restart: $ per IST calendar month (trades by entry month),
start balance $1,000 / k per strategy as in the $1,000-a-month study, compared with that study (mcej3/robust.run_grid on the same settings)."""
import sys, datetime as dt
from zoneinfo import ZoneInfo
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/fractal'); sys.path.insert(0, S + '/presets')
import engine as EN, pine_twin2 as TW, preset_data as PD
from final11 import ALL12
B = EN.load()
for k in ('t', 'O', 'H', 'L', 'C'): B['M1_' + k] = B[k]
IST = ZoneInfo('Asia/Kolkata')
REC = {'EXACT': TW.L_EXACT, 'OFF': TW.L_OFF}


def months_twin(g, start_total=1000.0):
    k = len(g['strats']); tot = {}
    for sid in g['strats']:
        prm = ALL12[sid - 1]
        p = TW.P(mRestart=True, baseR=g['base'], recMode=REC[g['rec']], capOn=g['cap'] is not None, hardCap=g['cap'] or 500.0, capAction=g['act'],
                 lad='Off', startB=start_total / k, costIn=0.23)
        s = TW.twin2(B, 'M1', prm, p)
        t = EN.chart(B, 'M1')[0]; utc = TW.chart_utc(B, 'M1')
        for (eb, F, xb, X, rsn), r in zip(s.trades, s.risks):
            sd = F * prm[4] / 100.0; pnl = r / (sd + 0.23) * (X - F - 0.23)
            m = dt.datetime.fromtimestamp(int(utc[eb]), IST).strftime('%Y-%m')
            tot[m] = tot.get(m, 0.0) + pnl
    return tot


if __name__ == '__main__':
    sys.path.insert(0, S + '/mcej3'); sys.path.insert(0, S + '/gold')
    import robust as RB, search as SE
    for g in PD.GRID_PRESETS:
        tw = months_twin(g)
        rule = PD.REC_RESEARCH[g['rec']]; ri = [r[0] for r in SE.RULES].index('Exact recovery at final TP' if g['rec'] == 'EXACT' else 'No recovery')
        cap = 0.0 if g['cap'] is None else g['cap']; act = g['act']
        ci = [i for i, c in enumerate(SE.CAPS) if c[1] == cap and (cap == 0 or c[2] == act)][0]
        run = SE.RUNS.index((g['base'], ri, ci))
        res = RB.run_grid([sid - 1 for sid in g['strats']], run, 'cal', None)
        W = RB.WIN['cal']; worst = 0.0; nl = [0, 0]; tt = [0.0, 0.0]; nl2 = [0, 0]; tt2 = [0.0, 0.0]
        for (a, b, per), r in zip(W, res):
            m = a.strftime('%Y-%m'); x = tw.get(m, 0.0); worst = max(worst, abs(x - r[0]))
            if per in ('IN', 'OUT'):
                j = 0 if per == 'IN' else 1
                nl[j] += x < -1e-9; tt[j] += x; nl2[j] += r[0] < -1e-9; tt2[j] += r[0]
        print('%s %-62s twin: 2021-23 %2d losing %+7.0f | 2024-26 %2d losing %+7.0f || study: %2d %+7.0f | %2d %+7.0f | max month diff $%.2f' % (
            g['key'], g['name'][:62], nl[0], tt[0], nl[1], tt[1], nl2[0], tt2[0], nl2[1], tt2[1], worst), flush=True)
