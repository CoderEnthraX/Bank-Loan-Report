"""Order flow concepts one by one on top of the default Sniper (per timeframe; H1 - H3 with the ratio 1.3): each context filter of
search.FILT, the new zone contexts (band reversal, previous day / session / previous week levels), the VWAP side and the user's filters.
Run: python3 -I concepts.py TF -> concepts_<tf>.pkl"""
import sys, pickle, numpy as np
HERE = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/snr'
sys.path.insert(0, HERE)
import engine as E, evalx as V, search as S, features as F

NAMES = {1: 'with the trend of', 5: 'against', 2: 'in range', 3: 'at least', 4: 'direction-signed range'}
EXPLAIN = {'h1_ema50': 'H1 close vs its EMA50', 'h4_ema50': 'H4 close vs its EMA50', 'd1_ema20': 'D1 close vs its EMA20', 'h1_slope': 'H1 EMA50 slope',
           'ema50_tf': 'chart close vs EMA50', 'ema200_tf': 'chart close vs EMA200', 'wvwap_side': 'weekly VWAP side', 'vwap_slope20': 'session VWAP slope (20 bars)',
           'cvd_s20': 'cumulative delta of the last 20 bars', 'pdc_side': 'previous day close side', 'poc_dist': 'session POC side', 'ppoc_dist': 'previous session POC side',
           'atr_reg': 'volatility regime (ATR / its 200-bar mean)', 'hour_ist': 'IST hour of the signal', 'dow': 'day of week (0 = Mon)',
           'stack_up': 'consecutive intrabars in the trade direction', 'upfrac': 'intrabar volume share in the trade direction', 'sweep_lo': 'liquidity sweep of the 20-bar low / high in the last 10 bars',
           'va_pos': 'position vs the session value area (1 above, -1 below, signed by direction)', 'rn_dist': 'distance to a $10 round number (ATR)'}


def base_kw(tf):
    return dict(aggRatio=1.3) if tf >= 60 else {}


def run(tf):
    X = V.feat(tf); filt = E.load(tf)['filt']
    rows = []
    def ev(name, kw, lv='pd', post=None):
        P = E.params(**kw); si, sd, se, ss, sf = E.run(tf, P, X, lv=lv)
        if len(si) == 0:
            rows.append((name, kw, lv, post, None)); return
        o = V.outc(tf, si, sd, se, ss, int(kw.get('entry', 0)), False)
        rows.append((name, kw, lv, post, S.mets(o, filt[si] if post == 'filt' else None)))
    b = base_kw(tf)
    ev('Default Sniper', dict(b))
    ev('Default + the user\'s filters (kill zones, 06-23 IST, news)', dict(b), post='filt')
    for k, m, a, z in S.FILT:
        kw = dict(b); kw.update(f1col=F.CI[k], f1mode=m, f1a=a, f1b=z)
        lab = '%s: %s %s' % (EXPLAIN.get(k, k), NAMES[m], ('%g..%g' % (a, z)) if m in (2, 4) else ('>= %g' % a) if m == 3 else '')
        ev(lab.strip(), kw)
    for ctx, lv, vs, bm, lab in ((1, 'pd', 0, 2.0, 'Reversal at VWAP band 2 (no VWAP-side rule)'), (1, 'pd', 0, 3.0, 'Reversal at VWAP band 3'),
                                  (1, 'pd', -1, 2.0, 'Reversal at band 2, entry against the VWAP side'),
                                  (2, 'pd', 0, 1.0, 'Absorption at the previous day high / low'), (2, 'sx', 0, 1.0, 'Absorption at the session high / low so far'),
                                  (2, 'pw', 0, 1.0, 'Absorption at the previous week high / low'), (2, 'pd', 1, 1.0, 'Previous day high / low, VWAP side kept'),
                                  (0, 'pd', 0, 1.0, 'Original zones, no VWAP-side rule')):
        kw = dict(b); kw.update(ctx=ctx, vside=vs, bandMult=bm, maxDist=0 if ctx else 2.5)
        ev(lab, kw, lv=lv)
    pickle.dump(rows, open(HERE + '/concepts_%d.pkl' % tf, 'wb'))
    return rows


if __name__ == '__main__':
    tf = int(sys.argv[1])
    rows = run(tf)
    for name, kw, lv, post, m in rows:
        if m is None:
            print('%-70s no signals' % name[:70]); continue
        def ac(p, X):
            n = m['%s_n_%g' % (p, X)]
            return '%5.1f' % (100 * m['%s_acc_%g' % (p, X)]) if n else '  -  '
        print('%-70s n %4d/%4d/%4d | 1R A %s B %s T %s | 0.5R T %s' % (name[:70], m['A_n_1'], m['B_n_1'], m['T_n_1'], ac('A', 1), ac('B', 1), ac('T', 1), ac('T', 0.5)))
