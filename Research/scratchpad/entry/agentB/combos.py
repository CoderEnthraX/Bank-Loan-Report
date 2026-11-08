"""step 4: combinations of the best single changes + fades by NY window + per-year of the leaders"""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/agentB')
import numpy as np, lib, data, signals, kit
from pb import pb_bars
F = 'combo'

def run(tf):
    if tf == 'M1': lib.m1_baseline()
    b = data.load(tf); c = lib.ctx(tf); C, A = b['C'], b['atr']
    out = {}
    for lab, kw in (('', {}), ('cmo40 ', dict(cmoMin=40.0))):
        s = signals.raw(tf, **kw); J = pb_bars(b, s, 5, 'lvl'); m = J >= 0; j = J[m]; d = s['d'][m].astype(np.int64)
        tr5 = d * c['trend_d5'][j] > 0; vw = d * c['vww'][j] > 0; vm = d * c['vwm'][j] > 0; e20 = d * c['ema20_d'][j] > 0
        hv = c['atr_vs_h1'][j] >= np.nanquantile(c['atr_vs_h1'][s['i']][b['year'][s['i']] <= 2023], 2 / 3) if 'atr_vs_h1' in c else None
        hi = c['atr_r100'][j] > 1.1
        sets = [(lab + 'pb + 5d trend', tr5), (lab + 'pb + 5d trend + week VWAP', tr5 & vw), (lab + 'pb + month VWAP + 5d trend', vm & tr5),
                (lab + 'pb + daily EMA20 + 5d trend', e20 & tr5), (lab + 'pb + atr/atr100>1.1', hi)]
        if lab == '': sets = [('pb (ref)', np.ones(len(j), bool))] + sets
        if hv is not None: sets += [(lab + 'pb + atr_vs_h1 high3', hv), (lab + 'pb + atr_vs_h1 high3 + 5d trend', hv & tr5)]
        for nm, mk in sets:
            r = lib.ev(tf, j[mk], d[mk], C[j[mk]], C[j[mk]] - d[mk] * 1.8 * A[j[mk]], mode=1, name=nm, family=F)
            out[nm] = (j[mk], d[mk])
    # fades
    s = signals.raw(tf); i, d = s['i'], s['d'].astype(np.int64); nyh = c['nyh'][i]
    for nm, mk in (('FADE all', np.ones(len(i), bool)), ('FADE NY 07-10', (nyh >= 7) & (nyh < 10)), ('FADE NY 14-17', (nyh >= 14) & (nyh < 17)),
                   ('FADE outside NY 07-17', (nyh < 7) | (nyh >= 17)), ('FADE longs-sig NY07-10 + shorts-sig NY14-17', np.where(d == 1, (nyh >= 7) & (nyh < 10), (nyh >= 14) & (nyh < 17)))):
        lib.ev(tf, i[mk], -d[mk], C[i[mk]], C[i[mk]] + d[mk] * 1.8 * A[i[mk]], mode=1, name=nm, family=F)
        if nm == 'FADE all': lib.per_year(tf, i[mk], -d[mk], C[i[mk]], C[i[mk]] + d[mk] * 1.8 * A[i[mk]], 1, 5, nm)
    for nm in ('pb + 5d trend', 'cmo40 pb + 5d trend'):
        jj, dd = out[nm]; lib.per_year(tf, jj, dd, C[jj], C[jj] - dd * 1.8 * A[jj], 1, 5, nm)

if __name__ == '__main__':
    for tf in sys.argv[1:]:
        print('=====', tf); run(tf)
