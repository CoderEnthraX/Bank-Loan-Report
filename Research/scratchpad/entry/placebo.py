"""Placebo for time-of-day rules: a rule that keeps signal k when ok(ny_min[k], d[k]) is re-scored with the New York clock shifted by
random offsets (whole hours 2..22, both directions); the real rule's excess should beat most shifted copies in train AND valid.
Usage from code: placebo.run(tf, i, d, entry, stop, mode, window, keep_fn) with keep_fn(ny_min_array, d_array) -> bool mask."""
import sys, numpy as np
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'; sys.path.insert(0, S + '/entry')
import kit, data, dataset

def run(tf, i, d, entry, stop, mode, window, keep_fn, shifts=range(2, 23), quiet=False):
    b = data.load(tf); ny = kit.local_min(tf, 'ny')[i]
    o = kit.outcomes_of(tf, i, d, entry, stop, mode, window)
    sp = dataset.split_of(b['utc'][i]); bl = kit.baseline(tf); f = o['fill_m1'] >= 0; mfe = o['mfe_m']
    def excess(mask, s_):
        m = mask & f & (sp == s_)
        if m.sum() == 0: return np.nan, 0
        hit = np.array([np.mean(mfe[m] >= r - 1e-9) for r in kit.TPR]) * 100
        nl = ((d == 1) & m).sum(); ref = (bl[(s_, 1)] * nl + bl[(s_, -1)] * (m.sum() - nl)) / m.sum()
        return float(np.mean(hit - ref)), int(m.sum())
    real = {s_: excess(keep_fn(ny, d), s_) for s_ in ('train', 'valid')}
    plac = {s_: [excess(keep_fn((ny + 60 * h) % 1440, d), s_)[0] for h in shifts] for s_ in ('train', 'valid')}
    out = {s_: (real[s_][0], real[s_][1], float(np.mean(np.array(plac[s_]) < real[s_][0]))) for s_ in real}
    if not quiet:
        for s_, (x, n, pct) in out.items():
            print('  %-5s real excess %+5.2f (n %5d) beats %3.0f%% of %d clock-shifted copies (their mean %+5.2f)' % (s_, x, n, 100 * pct, len(plac[s_]), np.nanmean(plac[s_])))
    return out
