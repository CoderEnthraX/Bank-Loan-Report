"""v3.9 Crooks C rule after N losing recovery trades in a row: the EA's own NextRisk() / CrkRecNext() / BookClosed() / CrkDayCount() / CrkPause()
(compiled, REC_DAYS mode of rec_driver) vs gold/recovery.py, trade for trade, on real gold sequences with their day changes.
Every rule (forget; % 50 / 75; wait M 1-3; skip D 1-3 with forget on / off and counted days Mon-Fri / every day) x N 1-3 x cap none / $500 Clamp /
Start again / Stop x Crooks C over 1 / 2 wins. Per signal: SKIP (paused) or the $ risk; STOP where the hard cap stops trading."""
import sys, os, subprocess, tempfile, datetime
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
import recovery as RC, crooks
H = S + '/mq5check/rec/rec_harness'
CAPS = {'clamp': 0, 'stop': 1, 'reset': 2}; PR = {'forget': 1, 'pct': 2, 'wait': 3, 'skip': 4}
def dayev(seq, all_days):
    """the new days before each signal, as the EA counts them in your time zone: every calendar day after the previous signal's day up to this one"""
    out = []; prev = None
    for t, *_ in seq:
        d = t.date(); ev = []
        if prev is not None:
            x = prev
            while x < d:
                x += datetime.timedelta(days=1); ev.append(all_days or x.weekday() < 5)
        prev = d; out.append(ev)
    return out
def rules():
    for N in (1, 2, 3):
        yield dict(crkPr='forget', crkPrN=N)
        for p in (50.0, 75.0): yield dict(crkPr='pct', crkPrN=N, crkPrPct=p)
        for M in (1, 2, 3): yield dict(crkPr='wait', crkPrN=N, crkPrM=M)
        for D in (1, 2, 3):
            for fg in (False, True):
                for al in (False, True): yield dict(crkPr='skip', crkPrN=N, crkPrD=D, crkPrForget=fg, _all=al)
def main():
    tdir = tempfile.TemporaryDirectory(); runs = bad = ntr = nskip = 0
    srcs = [(tf, d) for tf in crooks.TFS for d in crooks.sources(tf) if d['name'] in ('Default settings', 'Most profit', 'Shortest losing streak')]
    for tf, d in srcs:
        seq = crooks.sequence(d['trades'], d['cfg'])[:3000]; xr = crooks.exit_r(d['cfg'])
        for al in (False, True):
            ev = dayev(seq, al)
            path = os.path.join(tmp := tdir.name, '%s_%s_%d.txt' % (tf, d['name'].replace(' ', '_'), al))
            with open(path, 'w') as f:
                for (t, res, c, parts), e in zip(seq, ev):
                    f.write('%d%s %r %r %d%s\n' % (len(e), ''.join(' %d' % v for v in e), res, c, len(parts or []), ''.join(' %r %r' % x for x in (parts or []))))
            trs = [(res, c, parts, e) for (t, res, c, parts), e in zip(seq, ev)]
            for rl in rules():
                if rl.get('_all', False) != al: continue
                kw = {k: v for k, v in rl.items() if not k.startswith('_')}
                for cn in (1, 2):
                    for cap, act in ((0.0, 'clamp'), (500.0, 'clamp'), (500.0, 'reset'), (500.0, 'stop')):
                        tr = []; r = RC.simulate(trs, 'Crooks C', cap=cap, capAction=act, exitR=xr, start=1e12, trace=tr, cN=cn, **kw)
                        args = [H, path, repr(xr), 'InpRec=20', 'InpCapOn=%d' % (1 if cap > 0 else 0), 'InpHardCap=%r' % (cap if cap > 0 else 500.0), 'InpCapAction=%d' % CAPS[act],
                                'InpBaseRisk=50', 'InpCrkCnOn=%d' % (1 if cn > 1 else 0), 'InpCrkCn=%d' % cn, 'InpCrkPr=%d' % PR[kw['crkPr']], 'InpCrkPrN=%d' % kw['crkPrN'],
                                'InpCrkPrPct=%r' % kw.get('crkPrPct', 50.0), 'InpCrkPrM=%d' % kw.get('crkPrM', 2), 'InpCrkPrD=%d' % kw.get('crkPrD', 3),
                                'InpCrkPrForget=%d' % (1 if kw.get('crkPrForget') else 0), 'InpCrkPrAll=%d' % (1 if al else 0)]
                        out = subprocess.run(args, capture_output=True, text=True, check=True, env=dict(os.environ, REC_DAYS='1')).stdout.split('\n')
                        ea = [('SKIP' if l == 'SKIP' else float(l.split()[1])) for l in out if l.startswith('R ') or l == 'SKIP']
                        stop = any(l == 'STOP' for l in out); runs += 1
                        n = min(len(tr), len(ea)); ntr += n; nskip += sum(1 for x in tr[:n] if x == 'SKIP')
                        diff = [i for i in range(n) if (tr[i] == 'SKIP') != (ea[i] == 'SKIP') or (tr[i] != 'SKIP' and abs(tr[i] - ea[i]) > 1e-9 * max(1.0, abs(tr[i])))]
                        short = len(tr) < len(ea) and r['ruined']
                        if diff or (len(tr) != len(ea) and not short) or stop != r['capStopped']:
                            bad += 1
                            if bad <= 8:
                                i = diff[0] if diff else n
                                print('MISMATCH %s %s %s N/2 %d cap %d %s: py %d, EA %d; first diff %d: py %s EA %s; stop py %s EA %s' % (
                                    tf, d['name'], kw, cn, cap, act, len(tr), len(ea), i, tr[i] if i < len(tr) else None, ea[i] if i < len(ea) else None, r['capStopped'], stop))
    print('runs %d, signals compared %d (skipped by the pause %d), mismatches %d' % (runs, ntr, nskip, bad))
main()
