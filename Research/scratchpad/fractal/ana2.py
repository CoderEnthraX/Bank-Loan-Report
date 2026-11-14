"""Stage 2 ranking with the robustness filters: every year 2021-2026 positive, >= 150 train / 100 test trades; objective train R / DD."""
import numpy as np, sys, os
os.environ['STAGE'] = '2'
from ana1 import load, show
for tf in sys.argv[1:] or ['M15', 'M5']:
    d = load(tf)
    ok = (d['trN'] >= 150) & (d['teN'] >= 100)
    allpos = (d['yR'] > 0).all(1)
    print('=== %s stage 2: %d combos, %d enough trades, %d every year positive' % (tf, len(d['n']), ok.sum(), (ok & allpos).sum()))
    obj = np.where(ok & allpos, d['trR'] / np.maximum(d['trDD'], 2.0), -np.inf)
    show(d, np.argsort(-obj)[:30], '-- every year positive, top 30 by train R / DD')
    obj3 = np.where(ok & allpos & (d['win'] >= 0.15), d['trR'] / np.maximum(d['trDD'], 2.0), -np.inf)
    show(d, np.argsort(-obj3)[:12], '-- same, win rate >= 15%')
