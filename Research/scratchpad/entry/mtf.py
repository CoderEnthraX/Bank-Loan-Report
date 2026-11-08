"""(1) multi-timeframe stacking: an M5 signal with a same-direction M15 / H1 raw signal closed in the last N higher bars;
(2) first-Friday (US jobs report) days vs other days for the indicator's signals."""
import sys, numpy as np, pandas as pd
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'; sys.path.insert(0, S + '/entry')
import kit, data, signals
def recent_same(tf_lo, s_lo, tf_hi, nbars):
    lo = data.load(tf_lo); hi = data.load(tf_hi); sh = signals.raw(tf_hi)
    close_lo = lo['utc'][s_lo['i']] + 60 * lo['tfmin']
    out = np.zeros(len(s_lo['i']), bool)
    for d in (1, -1):
        hc = hi['utc'][sh['i'][sh['d'] == d]] + 60 * hi['tfmin']           # close times of the higher-TF signals
        k = np.searchsorted(hc, close_lo, 'right') - 1                    # last one closed by the low-TF signal's close
        ok = (k >= 0) & (s_lo['d'] == d)
        age = np.where(k >= 0, close_lo - hc[np.maximum(k, 0)], 10 ** 12)
        out |= ok & (age <= nbars * 60 * hi['tfmin'])
    return out
for tf_lo, tf_hi, nb in (('M5', 'M15', 3), ('M5', 'H1', 2), ('M15', 'H1', 3)):
    s = signals.raw(tf_lo); m = recent_same(tf_lo, s, tf_hi, nb)
    for lab, mask in (('stacked with %s (last %d)' % (tf_hi, nb), m), ('not stacked', ~m)):
        kit.evaluate(tf_lo, s['i'][mask], s['d'][mask], s['entry'][mask], s['stop_h'][mask], mode=0, name='%s %s' % (tf_lo, lab), by_dir=False)
# first Friday of the month (NY date) vs other days
for tf in ('M5', 'M15'):
    b = data.load(tf); s = signals.raw(tf)
    t = pd.to_datetime(b['utc'][s['i']], unit='s', utc=True).tz_convert('America/New_York')
    ff = (t.dayofweek == 4) & (t.day <= 7)
    for lab, mask in (('first Friday', np.asarray(ff)), ('other days', ~np.asarray(ff))):
        kit.evaluate(tf, s['i'][mask], s['d'][mask], s['entry'][mask], s['stop_h'][mask], mode=0, name='%s %s' % (tf, lab), by_dir=False)
