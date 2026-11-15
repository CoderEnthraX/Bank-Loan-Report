"""EA v4.7 position size: the EA's own NextRisk / BookClosed (compiled from the EA) vs gold/recovery.py simulate, trade for trade, with
Fixed lots (the base = the lots' stop-out loss of each trade: lots x ((stop + spread 0.16) / tick 0.01 x tick value 1 + commission 7)) and
% of equity at risk (the base = basePct % of the equity before the trade), on real gold sequences, every loss-recovery rule, no cap / $500
clamp / start again / stop, Crooks C (and E - J) over 1 / 2 wins, the profit ladder on Crooks F - J. Usage: parity_size_ea.py [N trades per source]"""
import sys, os, subprocess, tempfile
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
import recovery as RC, crooks
H = S + '/mq5check/rec/rec_harness'
EA_REC = {m: i for i, m in enumerate(RC.MODES)}
CAPS = {'clamp': 0, 'stop': 1, 'reset': 2}
LADN = {'Low': 1, 'Medium': 2, 'High': 3, 'Extra high': 4, 'Max': 5}
NT = int(sys.argv[1]) if len(sys.argv) > 1 else 1500
def ea(path, exitR, mode, cap, act, cn, kw, start, bm, bv):
    args = [H, path, repr(exitR), 'InpRec=%d' % EA_REC[mode], 'InpCapOn=%d' % (1 if cap > 0 else 0), 'InpHardCap=%r' % (cap if cap > 0 else 500.0),
            'InpCapAction=%d' % CAPS[act], 'InpCSplit=3', 'InpBaseRisk=50', 'InpRecN=3', 'InpRecPct=50', 'InpRecMult=2', 'InpRecStep=25', 'InpParN=3', 'InpDelayN=2',
            'InpCrkCnOn=%d' % (1 if cn > 1 else 0), 'InpCrkCn=%d' % cn, 'InpCrkFK=3', 'InpCrkGX=10', 'InpCrkHPct=1', 'InpCrkJX=20',
            'InpLadder=%d' % LADN.get(kw.get('lad'), 0), 'InpLadT=%r' % kw.get('ladT', 1000.0), 'InpSpread=0.16', 'InpCommLot=7',
            'InpSizeMode=%d' % (1 if bm == 'lot' else 2), 'InpBaseLots=%r' % (bv if bm == 'lot' else 0.01), 'InpEqPct=%r' % (bv if bm == 'pct' else 1.0)]
    out = subprocess.run(args, capture_output=True, text=True, check=True, env=dict(os.environ, REC_MIN='1', REC_SD='1', REC_START=repr(start))).stdout.split('\n')
    return [float(l.split()[1]) for l in out if l.startswith('R ')], any(l == 'STOP' for l in out)
def main():
    tdir = tempfile.TemporaryDirectory(); tmp = tdir.name; bad = runs = ntr = nblown = 0; worst = 0.0
    srcs = [(tf, d) for tf in crooks.TFS for d in crooks.sources(tf) if d['name'] in ('Default settings', 'Most profit', 'Shortest losing streak')]
    for tf, d in srcs:
        seq = crooks.sequence(d['trades'], d['cfg']); xr = crooks.exit_r(d['cfg'])
        sds = [x[5] for x in sorted(d['trades'], key=lambda x: x[0])]
        seq = seq[:NT]; sds = sds[:len(seq)]
        rmin = [1.0 * sd * (1.0 + c) for (_, _, c, _), sd in zip(seq, sds)]
        path = os.path.join(tmp, '%s_%s.txt' % (tf, d['name'].replace(' ', '_')))
        with open(path, 'w') as f:
            for (_, res, c, parts), rm, sd in zip(seq, rmin, sds):
                f.write('%r %r %r %r %d%s\n' % (res, c, rm, sd, len(parts or []), ''.join(' %r %r' % x for x in (parts or []))))
        for bm, vals in (('lot', (0.01, 0.05)), ('pct', (0.5, 1.0, 2.0))):
            for bv in vals:
                lotb = [bv * ((sd + 0.16) / 0.01 * 1.0 + 7.0) for sd in sds] if bm == 'lot' else [None] * len(sds)
                trs = [(res, c, parts, None, None, rm, lb) for (_, res, c, parts), rm, lb in zip(seq, rmin, lotb)]
                jobs = []
                for mode in RC.MODES:
                    for cn in ((1, 2) if mode in RC.CFAM else (1,)):
                        jobs.append((mode, cn, {}))
                    if mode in RC.LADFAM:
                        for lv in ('Low', 'Max'): jobs.append((mode, 1, dict(lad=lv, ladT=500.0)))
                for mode, cn, kw in jobs:
                    start = 1e4 if (bm == 'pct' or mode in ('Crooks H', '% of equity')) else 1e12
                    for cap, act in ((0.0, 'clamp'), (500.0, 'clamp'), (500.0, 'reset'), (500.0, 'stop')):
                        tr = []
                        r = RC.simulate(trs, mode, cap=cap, capAction=act, cSplit=3, exitR=xr, start=start, trace=tr, cN=cn, eqPct=bv if bm == 'pct' else 1.0,
                                        baseMode=bm, basePct=bv if bm == 'pct' else 1.0, **kw)
                        e, stop = ea(path, xr, mode, cap, act, cn, kw, start, bm, bv); runs += 1
                        n = min(len(tr), len(e)); diff = max([abs(a - b) / max(1.0, abs(a)) for a, b in zip(tr, e)] or [0.0])
                        worst = max(worst, diff); ntr += n
                        short = len(tr) < len(e) and r['ruined']; nblown += 1 if short else 0
                        if (len(tr) != len(e) and not short) or diff > 1e-9 or stop != r['capStopped']:
                            bad += 1
                            k = next((i for i, (a, b) in enumerate(zip(tr, e)) if abs(a - b) / max(1.0, abs(a)) > 1e-9), n)
                            if bad <= 25:
                                print('MISMATCH %s %s | %s %s=%s %s N %d cap %d %s | py %d trades, EA %d | first diff at %d: py %s EA %s | stop py %s EA %s' % (
                                    tf, d['name'], mode, bm, bv, kw, cn, cap, act, len(tr), len(e), k, tr[k] if k < len(tr) else None, e[k] if k < len(e) else None, r['capStopped'], stop))
    print('position size: runs %d, trades compared %d, mismatches %d, worst relative difference %.2e; runs where the account blew (compared up to it): %d' % (runs, ntr, bad, worst, nblown))
main()
