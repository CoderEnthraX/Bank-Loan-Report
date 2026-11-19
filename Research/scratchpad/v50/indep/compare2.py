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

rnd = random.Random(7)
for i in range(150):
    pw = rnd.choice([0.2,0.35,0.5,0.65]); xr = rnd.choice([0.1,0.3,0.5,1.0,2.0,3.0]); rm = rnd.choice([3.0,15.0,60.0,200.0])
    seqs.append(('v%d'%i, synth(100+i, xr, pw, rm), xr))
runs = trades = bad = 0; seen = {}; cov = dict(kz_w=0, kz_l=0, Lparts={}, Lgrow=0, Lrec=0)
for name, trs, xr in seqs[-150:]:
    for mode in MODES:
        for sz in ('risk','profit'):
            for lad in ((None,'Max','Low') if mode in ('Crooks J','Crooks K') else (None,)):
                for cn in ((1,2) if mode in CF else (1,)):
                    for km in (('lots','usd','pct') if mode=='Crooks K' else ('lots',)):
                        kw = dict(sizeBy=sz, exitR=xr, cN=cn, kMode=km, start=rnd.choice([10000.0, 1e9]), base=rnd.choice([50.0, 7.0, 120.0]), recN=rnd.choice([2,3,5]), recPct=rnd.choice([30.0,50.0,100.0]),
                                  step=rnd.choice([10.0,25.0]), cSplit=rnd.choice([2,3,4]), delayN=rnd.choice([1,2,3]), jX=rnd.choice([5.0,20.0]), kUsd=rnd.choice([10.0,25.0,60.0]), kPct=rnd.choice([25.0,50.0,150.0]),
                                  lZ1=rnd.choice([1.0,2.0,3.0]), lZ1N=rnd.choice([2,6]), lZ2=rnd.choice([2.0,5.0]), lZ2N=rnd.choice([2,3,5]), lGrow=rnd.choice([0.0,10.0,50.0]), lGrowX=rnd.choice([1.0,4.0,10.0]))
                        if lad: kw.update(lad=lad, ladT=rnd.choice([0.0, 100.0, 200.0, 1000.0]))
                        a = I.sim(trs, mode, **kw); b = []
                        N.simulate(trs, mode, trace=b, **kw)
                        runs += 1; trades += len(a)
                        idx = next((i for i in range(min(len(a), len(b))) if abs(a[i]-b[i]) > 1e-9*max(1.0,abs(a[i]),abs(b[i]))), None)
                        if idx is None and len(a) != len(b): idx = min(len(a), len(b))
                        if idx is not None:
                            bad += 1; key=(mode,sz,lad,cn,km)
                            if key not in seen: print('DIFF', name, key, kw, 'idx', idx, a[idx] if idx<len(a) else None, b[idx] if idx<len(b) else None, flush=True)
                            seen[key]=seen.get(key,0)+1
print('extra pass: runs %d trades %d mismatching %d' % (runs, trades, bad))
# coverage on one sequence set (Crooks K / L, defaults): zones
import collections
cnt = collections.Counter()
for name, trs, xr in seqs[-150:]:
    a = I.sim(trs, 'Crooks K', exitR=xr, start=1e9)
    off = I.sim(trs, 'Crooks C', exitR=xr, start=1e9)
    net=0.0; peak=0.0; w=False
    # replay K to classify zones
    r_k = a
    for t, r in zip(trs, r_k):
        pass
print('done')
