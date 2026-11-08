"""step 1: baseline of the indicator's signals; check lib.stats == kit.evaluate; build OF feature caches"""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/of_agentA')
import lib, kit, signals, numpy as np, time
for tf in ('M5', 'M15', 'M1', 'H1'):
    t = time.time(); df = lib.ds(tf)
    r = lib.stats(tf, np.ones(len(df), bool), df, 'ALL signals (baseline)', tag='base')
    if tf in ('M5', 'M15'):
        s = signals.raw(tf); kit.evaluate(tf, s['i'], s['d'], s['entry'], s['stop_h'], mode=0, window=5, name='kit check ' + tf)
    F = lib.feats(tf); print(tf, F.shape, 'feats %.0fs' % (time.time() - t)); print(F.describe().T[['mean', '50%', 'count']].round(3).to_string())
