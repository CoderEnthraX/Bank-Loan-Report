import sys, random, time, math
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold'); sys.path.insert(0, S + '/v50/indep')
import recovery as N, crooks, indep_sim as I
MODES = ['Off', 'Recover all losses on the next trade', 'Recover losses over N trades', 'Recover a % of losses per trade', 'Exact recovery at final TP',
         'Step-up (+$ per loss in a row)', 'Delayed recovery', "Oscar's Grind", 'Rule C: carry the losses', 'Crooks C', 'Crooks E', 'Crooks J', 'Crooks K', 'Crooks L']
CF = ('Crooks C', 'Crooks E', 'Crooks J', 'Crooks K')
LIM = 1500
seqs = []   # (name, trades, exitR)
for tf in crooks.TFS:
    for d in crooks.sources(tf):
        if d['name'] not in ('Default settings', 'Most profit', 'Shortest losing streak'): continue
        seq = crooks.sequence(d['trades'], d['cfg'])[:LIM]; xr = crooks.exit_r(d['cfg'])
        sds = [x[5] for x in sorted(d['trades'], key=lambda x: x[0])]
        trs = []
        for (_, res, c, parts), sd in zip(seq, sds):
            rm = sd * (1.0 + c); trs.append((res, c, None, None, None, rm, 0.6 * rm, 2.0 * rm))
        seqs.append(('%s/%s' % (tf, d['name']), trs, xr))
def synth(seed, xr, pw, rminmul):
    rnd = random.Random(seed); t = []
    def add(res):
        c = rnd.choice([0.0, 0.1, 0.2, 0.3]); rm = rminmul * (1 + c) * rnd.uniform(0.5, 1.5); t.append((res, c, None, None, None, rm, 0.6 * rm, 2 * rm))
    for _ in range(12): add(xr)
    for _ in range(40): add(-1.0)
    for _ in range(40): add(xr if _ % 2 == 0 else -1.0)
    for _ in range(80): add(xr if rnd.random() < 0.75 else -1.0)
    for _ in range(30): add(-1.0)
    for _ in range(300): add(xr if rnd.random() < pw else -1.0)
    for _ in range(25): add(xr)
    for _ in range(300): add(xr if rnd.random() < pw else -1.0)
    return t
si = 0
for xr in (0.1, 0.5, 2.0):
    for pw in (0.3, 0.5, 0.7):
        for rm in (10.0, 40.0, 150.0):
            si += 1; seqs.append(('synth%d xr%.1f pw%.1f rm%.0f' % (si, xr, pw, rm), synth(si, xr, pw, rm), xr))
runs = trades = bad = 0; seen = {}
t0 = time.time()
for name, trs, xr in seqs:
    for mode in MODES:
        for sz in ('risk', 'profit'):
            for lad in ((None, 'Max') if mode in ('Crooks J', 'Crooks K') else (None,)):
                for cn in ((1, 2) if mode in CF else (1,)):
                    for km in (('lots', 'usd', 'pct') if mode == 'Crooks K' else ('lots',)):
                        kw = dict(sizeBy=sz, exitR=xr, cN=cn, kMode=km)
                        if lad: kw.update(lad=lad, ladT=200.0)
                        a = I.sim(trs, mode, **kw); b = []
                        N.simulate(trs, mode, trace=b, **kw)
                        runs += 1; trades += len(a)
                        idx = next((i for i in range(min(len(a), len(b))) if abs(a[i] - b[i]) > 1e-9 * max(1.0, abs(a[i]), abs(b[i]))), None)
                        if idx is None and len(a) != len(b): idx = min(len(a), len(b))
                        if idx is not None:
                            bad += 1
                            key = (mode, sz, lad, cn, km)
                            if key not in seen:
                                seen[key] = 1
                                print('DIFF', name, key, 'first idx', idx, 'mine', a[idx] if idx < len(a) else None, 'ref', b[idx] if idx < len(b) else None, flush=True)
                            else: seen[key] += 1
print('runs %d trades %d mismatching runs %d distinct settings %d time %.0fs' % (runs, trades, bad, len(seen), time.time() - t0))
