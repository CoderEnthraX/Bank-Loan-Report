"""Entry research kit: evaluate ANY entry rule on gold 2021-2026 the same way.
    import kit
    r = kit.evaluate('M15', i, d, entry, stop, mode=1, name='my rule')   # prints train / valid lines, returns a dict
i = signal bar indexes (decision at that bar's close), d = +1 long / -1 short, entry = price, stop = price;
mode 0 = limit (fills when price trades back to entry within `window` bars), 1 = market at the signal bar's close (entry should be
C[i]; filled on the next bar), 2 = stop entry (fills when price trades through entry within `window` bars).
Targets TP1-TP4 = 0.6 / 1 / 1.5 / 2 R (R = |entry - stop|). Outcomes on the 1-minute path, stop first. Test data (2025-07..) are
excluded unless allow_test=True: DO NOT use it while searching.
Excess edge = hit% minus the hit% of RANDOM entries of the same direction in the same period (stop 1.8 ATR, market): this removes
gold's trend (2024-25 strongly up), so only a real edge is left. Raw edge = hit% minus the no-edge rate 1/(1+R) (62.5/50/40/33.3)."""
import sys, pickle, os, numpy as np, pandas as pd
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
if S + '/entry' not in sys.path: sys.path.insert(0, S + '/entry')
import data, outcomes, dataset
from zoneinfo import ZoneInfo
TPR = np.array([0.6, 1.0, 1.5, 2.0]); BASE = 1.0 / (1.0 + TPR)
MONTHS = {'train': 36.0, 'valid': 18.0, 'test': 15.1}
NY = ZoneInfo('America/New_York'); LON = ZoneInfo('Europe/London')

def load(tf):
    """bars + engine series (O H L C TV SP atr V SD Vw Vm ds vb utc ...), see data.py"""
    return data.load(tf)

def local_min(tf, zone='ny'):
    """minutes after midnight in New York (DST aware) or London local time, for every bar of tf (bar open time)"""
    key = '_%s_min' % zone; b = data.load(tf)
    if key not in b:
        s = pd.to_datetime(b['utc'], unit='s', utc=True).tz_convert(NY if zone == 'ny' else LON)
        b[key] = (s.hour * 60 + s.minute).to_numpy(); b['_%s_wd' % zone] = s.dayofweek.to_numpy()
    return b[key]

_BL = {}
def baseline(tf):
    """random market entries per (split, direction): hit% at TP1-TP4 (cached)"""
    if tf in _BL: return _BL[tf]
    f = '%s/entry/bars_%s.pkl' % (S, tf)
    if not os.path.exists(f): raise SystemExit('run barscan.py %s first' % tf)
    g = pickle.load(open(f, 'rb')); out = {}
    for sp in ('train', 'valid', 'test'):
        m = g[g.split == sp]
        for d, col in ((1, 'mfeL'), (-1, 'mfeS')):
            x = m[col].to_numpy(); x = x[~np.isnan(x)]
            out[(sp, d)] = np.array([np.mean(x >= r - 1e-9) for r in TPR]) * 100
    _BL[tf] = out; return out

def outcomes_of(tf, i, d, entry, stop, mode=1, window=5):
    return outcomes.simulate(tf, np.asarray(i), np.asarray(d), np.asarray(entry, float), np.asarray(stop, float), mode=mode, window=window)

def evaluate(tf, i, d, entry, stop, mode=1, window=5, name='', allow_test=False, quiet=False, by_dir=True):
    b = data.load(tf); i = np.asarray(i, np.int64); d = np.asarray(d, np.int64)
    o = outcomes_of(tf, i, d, entry, stop, mode, window)
    sp = dataset.split_of(b['utc'][i]); bl = baseline(tf)
    filled = o['fill_m1'] >= 0; mfe = o['mfe_m']
    risk = d * (np.asarray(entry, float) - np.asarray(stop, float))
    cost = b['SP'][np.maximum(o['fill_bar'], 0)] / np.where(risk > 0, risk, np.nan)
    res = {}
    for s_ in (('train', 'valid', 'test') if allow_test else ('train', 'valid')):
        rows = [('both', None)] + ([('long', 1), ('short', -1)] if by_dir else [])
        for lab, dd in rows:
            m = (sp == s_) & filled & ((d == dd) if dd else True)
            n = int(m.sum())
            if n == 0: res[(s_, lab)] = dict(n=0); continue
            hit = np.array([np.mean(mfe[m] >= r - 1e-9) for r in TPR]) * 100
            # excess vs random entries of the same direction mix
            nl = int(((d == 1) & m).sum()); ns = n - nl
            ref = (bl[(s_, 1)] * nl + bl[(s_, -1)] * ns) / n
            E = hit / 100 * TPR - (1 - hit / 100) - np.nanmean(cost[m])
            res[(s_, lab)] = dict(n=n, per_month=n / MONTHS[s_], hit=hit, raw=hit - BASE * 100, excess=hit - ref,
                                  avg_raw=float(np.mean(hit - BASE * 100)), avg_excess=float(np.mean(hit - ref)), E=E,
                                  se=float(np.sqrt(0.25 / n) * 100), fill_rate=float(m.sum() / max(((sp == s_) & ((d == dd) if dd else True)).sum(), 1)))
            if not quiet:
                r = res[(s_, lab)]
                print('%-30s %-5s %-5s n %6d %6.1f/mo fill %3.0f%% | hit %s | excess %s avg %+5.2f (se %.1f) | E@TP1 %+.3f E@TP4 %+.3f' % (
                    name[:30], s_, lab, n, r['per_month'], 100 * r['fill_rate'], ' '.join('%5.1f' % x for x in hit),
                    ' '.join('%+5.1f' % x for x in r['excess']), r['avg_excess'], r['se'], E[0], E[3]))
    return res
