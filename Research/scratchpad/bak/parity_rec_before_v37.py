"""EA money management (its own NextRisk / BookClosed, compiled) vs the Python simulator (gold/recovery.py), trade for trade:
every loss-recovery mode except % of equity, no cap / $500 clamp / start again / stop, Crooks B and Rule C split 1-5, on real gold sequences."""
import sys, os, subprocess, tempfile
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
import recovery as RC, crooks
H = S + '/mq5check/rec/rec_harness'
EA_REC = {m: i for i, m in enumerate(RC.MODES)}          # MODES order == ENUM_REC order (0..19)
CAPS = {'clamp': 0, 'stop': 1, 'reset': 2}
def ea(path, exitR, mode, cap, act, split, n):
    args = [H, path, repr(exitR), 'InpRec=%d' % EA_REC[mode], 'InpCapOn=%d' % (1 if cap > 0 else 0), 'InpHardCap=%r' % (cap if cap > 0 else 500.0),
            'InpCapAction=%d' % CAPS[act], 'InpCSplit=%d' % split, 'InpBaseRisk=50', 'InpRecN=3', 'InpRecPct=50', 'InpRecMult=2', 'InpRecStep=25', 'InpParN=3', 'InpDelayN=2']
    out = subprocess.run(args, capture_output=True, text=True, check=True).stdout.split('\n')
    rs = [float(l.split()[1]) for l in out if l.startswith('R ')]
    return rs, any(l == 'STOP' for l in out)
def main():
    tdir = tempfile.TemporaryDirectory(); tmp = tdir.name; bad = 0; runs = 0; worst = 0.0; nblown = 0; ntr = 0      # removed when the run ends
    srcs = []
    for tf in crooks.TFS:
        for d in crooks.sources(tf):
            if d['name'] in ('Default settings', 'Most profit', 'Shortest losing streak'): srcs.append((tf, d))
    for tf, d in srcs:
        seq = crooks.sequence(d['trades'], d['cfg']); xr = crooks.exit_r(d['cfg'])
        seq = seq[:3000]                                                   # enough for every rule to cycle many times
        path = os.path.join(tmp, '%s_%s.txt' % (tf, d['name'].replace(' ', '_')))
        with open(path, 'w') as f:
            for _, res, c, parts in seq:
                f.write('%r %r %d%s\n' % (res, c, len(parts or []), ''.join(' %r %r' % x for x in (parts or []))))
        trs = [(res, c, parts) for _, res, c, parts in seq]
        for mode in RC.MODES:
            if mode == '% of equity': continue
            splits = (1, 2, 3, 4, 5) if mode in ('Crooks B', 'Rule C split', 'Rule C: carry the losses') else (3,)
            for split in splits:
                for cap, act in ((0.0, 'clamp'), (500.0, 'clamp'), (500.0, 'reset'), (500.0, 'stop')):
                    tr = []; r = RC.simulate(trs, mode, cap=cap, capAction=act, cSplit=split, exitR=xr, start=1e12, trace=tr)   # no ruin stop in the EA harness
                    e, stop = ea(path, xr, mode, cap, act, split, len(trs)); runs += 1
                    n = min(len(tr), len(e)); diff = max([abs(a - b) / max(1.0, abs(a)) for a, b in zip(tr, e)] or [0.0])
                    worst = max(worst, diff); nblown += 1 if len(tr) < len(e) and r['ruined'] else 0; ntr += n
                    short = len(tr) < len(e) and r['ruined']                     # the simulator stops at a blown account, the EA harness has no account
                    if (len(tr) != len(e) and not short) or diff > 1e-9 or stop != r['capStopped']:
                        bad += 1
                        k = next((i for i, (a, b) in enumerate(zip(tr, e)) if abs(a - b) / max(1.0, abs(a)) > 1e-9), n)
                        print('MISMATCH %s %s | %s split %d cap %d %s | py %d trades, EA %d | first diff at trade %d: py %s EA %s | stop py %s EA %s' % (
                            tf, d['name'], mode, split, cap, act, len(tr), len(e), k, tr[k] if k < len(tr) else None, e[k] if k < len(e) else None, r['capStopped'], stop))
    print('runs %d, trades compared %d, mismatches %d, worst relative difference %.2e; runs where the account blew (compared up to that trade): %d' % (runs, ntr, bad, worst, nblown))
main()
