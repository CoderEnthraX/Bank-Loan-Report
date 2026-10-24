"""helpers: day-paired bootstrap, per-symbol counts, random-subset null (exact for ghost mode)."""
import random
SYMS = ['GC', 'EURUSD', 'NASDAQ', 'US30', 'CRUDE', 'NIFTY', 'SENSEX', 'ETH', 'NSE_NIFTY1', 'MCX_NATURALGAS']
def E(tr): return sum(x['res'] for x in tr) / len(tr) if tr else float('nan')
def day(x): return x['t'][:10]
def paired_ci(base, filt, it=2000, seed=7):
    """resample calendar days (all instruments of that day together); diff of mean res filtered - base on the same days."""
    days = sorted(set(map(day, base)) | set(map(day, filt))); B = {}; Fd = {}
    for x in base: B.setdefault(day(x), []).append(x['res'])
    for x in filt: Fd.setdefault(day(x), []).append(x['res'])
    rnd = random.Random(seed); ds = []
    for _ in range(it):
        sb = sf = 0.0; nb = nf = 0
        for _ in days:
            dd = days[rnd.randrange(len(days))]; b = B.get(dd, []); f = Fd.get(dd, [])
            sb += sum(b); nb += len(b); sf += sum(f); nf += len(f)
        if nb and nf: ds.append(sf / nf - sb / nb)
    ds.sort(); return ds[int(0.025 * len(ds))], ds[int(0.975 * len(ds))]
def syms_better(base, filt, syms=SYMS):
    k = m = 0
    for s in syms:
        b = [x for x in base if x['sym'] == s]; f = [x for x in filt if x['sym'] == s]
        if not b: continue
        m += 1; k += (E(f) if f else -9) > E(b) + 1e-12
    return k, m
def rnd_subset_null(base, share, it=500, seed=11):
    """E of random subsets keeping `share` of trades (ghost mode with a random veto == random subset)."""
    rnd = random.Random(seed); out = []
    for _ in range(it):
        s = [x for x in base if rnd.random() < share]; out.append(E(s))
    out.sort(); return out
def pct(null, v): return sum(1 for z in null if z < v) / len(null)
