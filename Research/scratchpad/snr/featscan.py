"""Feature scan: accuracy and net R of the Sniper signals by quintile of each feature (direction-adjusted), train and test separately.
Run: python3 -I featscan.py TF [params as k=v ...] -> featscan_<tf>.txt"""
import sys, numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/snr')
import engine as E, outcome as O, features as F

DIRFEAT = ['ema50_tf', 'ema200_tf', 'h1_ema50', 'h4_ema50', 'd1_ema20', 'h1_slope', 'pdc_side', 'wvwap_side', 'vwap_slope20', 'cvd_s20', 'poc_dist', 'ppoc_dist', 'va_pos']


def sigfeat(tf, si, sd, sf):
    X = np.load('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/snr/feat_%d.npz' % tf)['X'][si]
    out = {}
    for k, i in F.CI.items():
        out[k] = X[:, i] * (sd if k in DIRFEAT else 1)
    out['pdhl_pos'] = np.where(sd == 1, X[:, F.CI['pdhl_pos']], 1 - X[:, F.CI['pdhl_pos']])
    out['sweep'] = np.where(sd == 1, X[:, F.CI['sweep_lo']], X[:, F.CI['sweep_hi']])
    out['stack'] = np.where(sd == 1, X[:, F.CI['stack_up']], X[:, F.CI['stack_dn']])
    out['frac'] = np.where(sd == 1, X[:, F.CI['upfrac']], X[:, F.CI['dnfrac']])
    for k in ('sweep_lo', 'sweep_hi', 'stack_up', 'stack_dn', 'upfrac', 'dnfrac'):
        out.pop(k)
    for j, k in enumerate(E.FEAT):
        out['s_' + k] = sf[:, j]
    out['dir'] = sd.astype(float)
    return out


def main():
    tf = int(sys.argv[1]); kw = {}
    for a in sys.argv[2:]:
        k, v = a.split('='); kw[k] = float(v)
    P = E.params(**kw); si, sd, se, ss, sf = E.run(tf, P)
    o = O.outcomes(tf, si, sd, se, ss)
    tr = o['t'] < O.TEST0
    fe = sigfeat(tf, si, sd, sf)
    lines = ['TF %d params %s: %d signals (train %d, test %d)' % (tf, kw, len(si), tr.sum(), (~tr).sum())]
    for X in (0.5, 1.0):
        net, hit = O.net_at(o, X)
        lines.append('all: X=%.1f train acc %.1f%% net %+.3f | test acc %.1f%% net %+.3f' % (X, 100 * hit[tr].mean(), np.nanmean(net[tr]), 100 * hit[~tr].mean(), np.nanmean(net[~tr])))
    net1, hit1 = O.net_at(o, 1.0); net5, hit5 = O.net_at(o, 0.5)
    for k, x in fe.items():
        ok = ~np.isnan(x)
        uq = np.unique(x[ok])
        if len(uq) <= 6:
            edges = None; groups = [(u, ok & (x == u)) for u in uq]
            lab = lambda g: '=%g' % g
        else:
            q = np.nanquantile(x[tr & ok], [0.2, 0.4, 0.6, 0.8])
            b = np.digitize(x, q)
            groups = [(g, ok & (b == g)) for g in range(5)]
            lab = lambda g, q=q: ('<%.3g' % q[0]) if g == 0 else ('>=%.3g' % q[3]) if g == 4 else '%.3g..%.3g' % (q[g - 1], q[g])
        lines.append('\n%s' % k)
        for g, m in groups:
            a, z = m & tr, m & ~tr
            if a.sum() < 15:
                continue
            lines.append('  %-16s n %4d/%4d | 0.5R acc %5.1f%% / %5.1f%% | 1R acc %5.1f%% / %5.1f%%  net1R %+.3f / %+.3f' % (
                lab(g), a.sum(), z.sum(), 100 * hit5[a].mean(), 100 * hit5[z].mean() if z.sum() else np.nan,
                100 * hit1[a].mean(), 100 * hit1[z].mean() if z.sum() else np.nan, np.nanmean(net1[a]), np.nanmean(net1[z]) if z.sum() else np.nan))
    txt = '\n'.join(lines)
    open('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/snr/featscan_%d%s.txt' % (tf, ('_' + '_'.join(sys.argv[2:])) if kw else ''), 'w').write(txt)
    print(txt)


if __name__ == '__main__':
    main()
