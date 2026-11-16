"""v4.8 monthly restart: the EA's own NextRisk / BookClosed with its monthly restart (MonthTick + MonthRestart: loss recovery, profit ladder,
Crooks J peak, Rule C split steps, hard-cap stop) vs gold/recovery.py run FRESH on every calendar month (the $1,000-a-month study), trade for
trade, on real gold sequences (catalogue strategies, entry month). Every rule except % of equity and Crooks H (both use the account equity,
which a real account cannot restart); caps none / $500 Clamp / Start again / Stop; the profit ladder on Crooks F, G, I, J (Medium / Max,
target $100 / $300). Run: python3 -I parity_month.py"""
import sys, os, subprocess, tempfile
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
import recovery as RC, crooks
H = S + '/mq5check/rec/mrs_harness'
EA_REC = {m: i for i, m in enumerate(RC.MODES)}
CAPS = {'clamp': 0, 'stop': 1, 'reset': 2}
LADN = {'Low': 1, 'Medium': 2, 'High': 3, 'Extra high': 4, 'Max': 5}
KW = {'Crooks F': [dict(fK=3.0)], 'Crooks G': [dict(gX=10.0)], 'Crooks I': [dict(fK=3.0)], 'Crooks J': [dict(jX=20.0)]}


def ea(path, exitR, mode, cap, act, kw):
    args = [H, path, repr(exitR), 'InpRec=%d' % EA_REC[mode], 'InpCapOn=%d' % (1 if cap > 0 else 0), 'InpHardCap=%r' % (cap if cap > 0 else 500.0),
            'InpCapAction=%d' % CAPS[act], 'InpCSplit=3', 'InpBaseRisk=50', 'InpRecN=3', 'InpRecPct=50', 'InpRecMult=2', 'InpRecStep=25', 'InpParN=3',
            'InpDelayN=2', 'InpCrkCnOn=0', 'InpCrkCn=1', 'InpCommLot=0', 'InpSpread=0', 'InpCrkT1=0', 'InpMRestart=1',
            'InpCrkFK=%r' % kw.get('fK', 3.0), 'InpCrkGX=%r' % kw.get('gX', 10.0), 'InpCrkJX=%r' % kw.get('jX', 20.0),
            'InpLadder=%d' % LADN.get(kw.get('lad'), 0), 'InpLadT=%r' % kw.get('ladT', 1000.0)]
    out = subprocess.run(args, capture_output=True, text=True, check=True).stdout.split('\n')
    return [l for l in out if l]


def main():
    tdir = tempfile.TemporaryDirectory(); tmp = tdir.name
    runs = bad = ntr = nstop = 0; worst = 0.0
    srcs = [(tf, d) for tf in crooks.TFS for d in crooks.sources(tf) if d['name'] in ('Most profit', 'Shortest losing streak')]
    for tf, d in srcs:
        seq = crooks.sequence(d['trades'], d['cfg']); xr = crooks.exit_r(d['cfg'])
        sds = [x[5] for x in sorted(d['trades'], key=lambda x: x[0])]
        months = []; key = None
        for (t, res, c, parts), sd in zip(seq, sds):
            k = (t.year, t.month)
            if k != key: months.append([]); key = k
            months[-1].append((res, c, parts, None, None, 1.0 * sd * (1.0 + c)))
        path = os.path.join(tmp, '%s_%s.txt' % (tf, d['name'].replace(' ', '_')))
        with open(path, 'w') as f:
            for mi, mt in enumerate(months):
                if mi: f.write('M\n')
                for (res, c, parts, _, _, rm) in mt:
                    f.write('%r %r %r %d%s\n' % (res, c, rm, len(parts or []), ''.join(' %r %r' % x for x in (parts or []))))
        jobs = []
        for mode in RC.MODES:
            if mode in ('% of equity', 'Crooks H'): continue
            for kw in KW.get(mode, [{}]):
                jobs.append((mode, kw))
                if mode in RC.LADFAM:
                    for lv in ('Medium', 'Max'):
                        for T in (100.0, 300.0): jobs.append((mode, dict(kw, lad=lv, ladT=T)))
        for mode, kw in jobs:
            for cap, act in ((0.0, 'clamp'), (500.0, 'clamp'), (500.0, 'reset'), (500.0, 'stop')):
                e = ea(path, xr, mode, cap, act, kw); runs += 1; pos = 0; diff = 0.0; ok = True
                for mt in months:
                    tr = []
                    RC.simulate(mt, mode, base=50.0, cap=cap, capAction=act, cSplit=3, exitR=xr, start=1e12, trace=tr, **kw)
                    toks = e[pos:pos + len(mt)]; pos += len(mt)
                    rs = [float(x.split()[1]) for x in toks if x.startswith('R ')]
                    if len(tr) < len(mt):                          # the simulator stopped (hard cap Stop trading): the EA must stop at the same trade
                        ok &= len(toks) == len(mt) and toks[len(tr)] == 'STOP' and all(x == 'SKIP' for x in toks[len(tr) + 1:]); nstop += 1
                    ok &= len(rs) == len(tr)
                    for a, b in zip(rs, tr): diff = max(diff, abs(a - b) / max(1.0, abs(b)))
                    ntr += len(tr)
                ok &= pos == len(e) and diff < 1e-9
                worst = max(worst, diff)
                if not ok:
                    bad += 1
                    if bad <= 5: print('DIFF %s %s | %s %s %s cap %r %s | worst %.3g' % (tf, d['name'], mode, kw, act, cap, '', diff))
        print('%-4s %-24s %4d months, %5d trades: done' % (tf, d['name'], len(months), len(seq)), flush=True)
    print('runs %d, trades compared %d, months stopped by the cap %d, worst relative difference %.3g -> %s' % (runs, ntr, nstop, worst, 'ALL IDENTICAL' if not bad else '%d runs differ' % bad))


if __name__ == '__main__':
    main()
