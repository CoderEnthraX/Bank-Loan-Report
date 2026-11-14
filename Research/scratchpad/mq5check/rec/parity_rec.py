"""EA money management (its own NextRisk / BookClosed, compiled) vs the Python simulator (gold/recovery.py), trade for trade:
every loss-recovery mode except % of equity, no cap / $500 clamp / start again / stop, Crooks B and Rule C split 1-5, on real gold sequences.
v4.5: Crooks E - J too (E / I with the 0.01-lot risk of each trade = 1 oz x (stop + cost); F / I limit 2 / 3 / 5 x base; G 6 / 10 x base;
H 1 / 2 % of a $10,000 start; J 10 / 20 / 40 x base), each also with Crooks C over 2 wins.
v4.6: the profit ladder on Crooks F - J (defaults) at every level, profit target $500 and $1,000, over 1 / 2 wins."""
import sys, os, subprocess, tempfile
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
import recovery as RC, crooks
H = S + '/mq5check/rec/rec_harness'
EA_REC = {m: i for i, m in enumerate(RC.MODES)}          # MODES order == ENUM_REC order (0..27)
CAPS = {'clamp': 0, 'stop': 1, 'reset': 2}
LADN = {'Low': 1, 'Medium': 2, 'High': 3, 'Extra high': 4, 'Max': 5}            # v4.6 ENUM_LADDER

NEW = {'Crooks E': [{}], 'Crooks F': [dict(fK=2.0), dict(fK=3.0), dict(fK=5.0)], 'Crooks G': [dict(gX=6.0), dict(gX=10.0)],
       'Crooks H': [dict(hPct=1.0), dict(hPct=2.0)], 'Crooks I': [dict(fK=2.0), dict(fK=3.0)], 'Crooks J': [dict(jX=10.0), dict(jX=20.0), dict(jX=40.0)]}
def ea(path, exitR, mode, cap, act, split, n, cn=1, kw=None, start=1e12):
    kw = kw or {}
    args = [H, path, repr(exitR), 'InpRec=%d' % EA_REC[mode], 'InpCapOn=%d' % (1 if cap > 0 else 0), 'InpHardCap=%r' % (cap if cap > 0 else 500.0),
            'InpCapAction=%d' % CAPS[act], 'InpCSplit=%d' % split, 'InpBaseRisk=50', 'InpRecN=3', 'InpRecPct=50', 'InpRecMult=2', 'InpRecStep=25', 'InpParN=3', 'InpDelayN=2', 'InpCrkCnOn=%d' % (1 if cn > 1 else 0), 'InpCrkCn=%d' % cn, 'InpCommLot=0', 'InpSpread=0', 'InpCrkT1=0',   # v4.0: the v3.9 cost defaults
            'InpCrkFK=%r' % kw.get('fK', 3.0), 'InpCrkGX=%r' % kw.get('gX', 10.0), 'InpCrkHPct=%r' % kw.get('hPct', 1.0), 'InpCrkJX=%r' % kw.get('jX', 20.0),
            'InpLadder=%d' % LADN.get(kw.get('lad'), 0), 'InpLadT=%r' % kw.get('ladT', 1000.0)]
    out = subprocess.run(args, capture_output=True, text=True, check=True, env=dict(os.environ, REC_MIN='1', REC_START=repr(start))).stdout.split('\n')
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
        sds = [x[5] for x in sorted(d['trades'], key=lambda x: x[0])]       # the stop distance of each trade (same order as the sequence)
        seq = seq[:3000]                                                   # enough for every rule to cycle many times
        rmin = [1.0 * sd * (1.0 + c) for (_, _, c, _), sd in zip(seq, sds)]  # v4.5: 0.01 lot = 1 oz of gold at the stop, cost included
        path = os.path.join(tmp, '%s_%s.txt' % (tf, d['name'].replace(' ', '_')))
        with open(path, 'w') as f:
            for (_, res, c, parts), rm in zip(seq, rmin):
                f.write('%r %r %r %d%s\n' % (res, c, rm, len(parts or []), ''.join(' %r %r' % x for x in (parts or []))))
        trs = [(res, c, parts, None, None, rm) for (_, res, c, parts), rm in zip(seq, rmin)]
        jobs = []
        for mode in RC.MODES:
            if mode == '% of equity': continue
            splits = (1, 2, 3, 4, 5) if mode in ('Crooks B', 'Rule C split', 'Rule C: carry the losses') else (3,)
            cns = (1, 2, 3) if mode == 'Crooks C' else (1, 2) if mode in NEW else (1,)    # Crooks C (and E - J) over N wins
            for kw in NEW.get(mode, [{}]):
                for split, cn in [(s_, c_) for s_ in splits for c_ in cns]:
                    jobs.append((mode, split, cn, kw, 1e4 if mode == 'Crooks H' else 1e12))
            if mode in RC.LADFAM:                                          # v4.6 profit ladder
                for lv in RC.LADDER:
                    for T in (500.0, 1000.0):
                        for cn in (1, 2): jobs.append((mode, 3, cn, dict(lad=lv, ladT=T), 1e4 if mode == 'Crooks H' else 1e12))
        for mode, split, cn, kw, start in jobs:
            for cap, act in ((0.0, 'clamp'), (500.0, 'clamp'), (500.0, 'reset'), (500.0, 'stop')):
                tr = []; r = RC.simulate(trs, mode, cap=cap, capAction=act, cSplit=split, exitR=xr, start=start, trace=tr, cN=cn, **kw)   # no ruin stop in the EA harness
                e, stop = ea(path, xr, mode, cap, act, split, len(trs), cn, kw, start); runs += 1
                n = min(len(tr), len(e)); diff = max([abs(a - b) / max(1.0, abs(a)) for a, b in zip(tr, e)] or [0.0])
                worst = max(worst, diff); nblown += 1 if len(tr) < len(e) and r['ruined'] else 0; ntr += n
                short = len(tr) < len(e) and r['ruined']                     # the simulator stops at a blown account, the EA harness has no account
                if (len(tr) != len(e) and not short) or diff > 1e-9 or stop != r['capStopped']:
                    bad += 1
                    k = next((i for i, (a, b) in enumerate(zip(tr, e)) if abs(a - b) / max(1.0, abs(a)) > 1e-9), n)
                    print('MISMATCH %s %s | %s %s split %d N %d cap %d %s | py %d trades, EA %d | first diff at trade %d: py %s EA %s | stop py %s EA %s' % (
                        tf, d['name'], mode, kw, split, cn, cap, act, len(tr), len(e), k, tr[k] if k < len(tr) else None, e[k] if k < len(e) else None, r['capStopped'], stop))
    print('runs %d, trades compared %d, mismatches %d, worst relative difference %.2e; runs where the account blew (compared up to that trade): %d' % (runs, ntr, bad, worst, nblown))
main()
