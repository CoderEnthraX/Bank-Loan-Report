"""Stage 1 ranking: choose on 2021-2023 (train), check on 2024-2026 (test)."""
import numpy as np, sys
NY = 6
def load(tf):
    z = np.load('search%s_%s.npz' % (__import__('os').environ.get('STAGE', '1'), tf)); res = z['res']; prm = z['prm']
    yR = res[:, 7:7 + 3 * NY:3]; yN = res[:, 8:8 + 3 * NY:3]
    d = dict(prm=prm, n=res[:, 0], R=res[:, 1], dd=res[:, 2], pf=res[:, 3] / np.maximum(res[:, 4], 1e-9), mst=res[:, 5], win=res[:, 6] / np.maximum(res[:, 0], 1),
             trR=yR[:, :3].sum(1), teR=yR[:, 3:].sum(1), trN=yN[:, :3].sum(1), teN=yN[:, 3:].sum(1), trDD=res[:, 7 + 3 * NY], teDD=res[:, 8 + 3 * NY], yR=yR, yN=yN)
    return d
def show(d, idx, title):
    print(title)
    print('   R  L   off    TP    SL    BE    SV |  trades  win%   PF | train R   DD  R/DD | test R   DD  R/DD | all R  DD | years R')
    for i in idx:
        r, l, off, tp, sl, be, sv, ne = d['prm'][i]
        print('%4d %2d %5.2f %5.2f %5.2f %5.2f %5.2f | %6d %5.1f %4.2f | %7.1f %4.1f %5.1f | %6.1f %4.1f %5.1f | %6.1f %4.1f | %s' % (
            r, l, off, tp, sl, be, sv, d['n'][i], 100 * d['win'][i], d['pf'][i], d['trR'][i], d['trDD'][i], d['trR'][i] / max(d['trDD'][i], 1),
            d['teR'][i], d['teDD'][i], d['teR'][i] / max(d['teDD'][i], 1), d['R'][i], d['dd'][i], ' '.join('%+.0f' % x for x in d['yR'][i])))
if __name__ == '__main__':
  for tf in sys.argv[1:] or ['M5', 'M15']:
    d = load(tf); N = len(d['n'])
    ok = (d['trN'] >= 150) & (d['teN'] >= 100)
    print('=== %s: %d combinations, %d with >= 150 train and >= 100 test trades; train R > 0: %d; test R > 0: %d; both: %d' % (
        tf, N, ok.sum(), (ok & (d['trR'] > 0)).sum(), (ok & (d['teR'] > 0)).sum(), (ok & (d['trR'] > 0) & (d['teR'] > 0)).sum()))
    obj = np.where(ok, d['trR'] / np.maximum(d['trDD'], 2.0), -np.inf)
    show(d, np.argsort(-obj)[:25], '-- top 25 by train R / train DD')
    obj2 = np.where(ok & (d['trR'] > 0), d['trR'], -np.inf)
    show(d, np.argsort(-obj2)[:10], '-- top 10 by train R')
    allo = np.where(ok, d['R'] / np.maximum(d['dd'], 2.0), -np.inf)
    show(d, np.argsort(-allo)[:10], '-- (for reference, not for choosing) top 10 by whole-period R / DD')
