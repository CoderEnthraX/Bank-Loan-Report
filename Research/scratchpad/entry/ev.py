"""Entry research kit, part 6: accuracy metrics. hit_k = MFE before the stop >= TP_k (1-minute path). Edge at TP_k = hit% minus the
no-edge rate 1 / (1 + R_k) (62.5 / 50 / 40 / 33.3 %). E_k = R per trade if every trade exits at TP_k (or the stop), minus the spread."""
import numpy as np, pandas as pd, pickle
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
TPR = np.array([0.6, 1.0, 1.5, 2.0]); BASE = 1.0 / (1.0 + TPR)

def load(tf, filled=True):
    df = pickle.load(open('%s/entry/ds_%s.pkl' % (S, tf), 'rb'))
    return df[df.filled].copy() if filled else df

def hits(df, col='mfe_m'):
    m = df[col].to_numpy()[:, None]
    return m >= TPR[None, :] - 1e-9

def stats(df, col='mfe_m', cost='cost_fill'):
    n = len(df)
    if n == 0: return dict(n=0, hit=np.full(4, np.nan), edge=np.full(4, np.nan), avg_edge=np.nan, E=np.full(4, np.nan))
    h = hits(df, col); p = h.mean(0)
    c = df[cost].to_numpy().mean() if cost else 0.0
    E = p * TPR - (1 - p) - c
    return dict(n=n, hit=p * 100, edge=(p - BASE) * 100, avg_edge=((p - BASE) * 100).mean(), E=E, se=np.sqrt(p * (1 - p) / n) * 100)

def line(name, df, col='mfe_m', months=None):
    s = stats(df, col)
    if s['n'] == 0: return '%-34s n     0' % name
    pm = '' if not months else ' %5.1f/mo' % (s['n'] / months)
    return ('%-34s n %6d%s | hit ' % (name, s['n'], pm) + ' '.join('%5.1f' % x for x in s['hit']) +
            ' | edge ' + ' '.join('%+5.1f' % x for x in s['edge']) + ' (avg %+5.2f, se %.1f)' % (s['avg_edge'], s['se'][1]) +
            ' | E ' + ' '.join('%+.3f' % x for x in s['E']))

MONTHS = {'train': 36.0, 'valid': 18.0, 'test': 15.1}
