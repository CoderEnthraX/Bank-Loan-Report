"""v5.1 money parity: Size By Profit with the costs (v50/SPEC_v50.md section 5). The EA's own NextRisk / BookClosed (compiled, rec_harness,
REC_SD: every trade's stop distance is set as the setup's stop, tick 0.01, tick value 1; InpSpread 0.16, InpCommLot 7, earn-back on and off)
vs gold/recovery.py given each trade's D (element [8]) computed exactly like the EA's PDiv(), trade for trade.
Sections (argv[1], default all):
  rec   Size By Profit on every rule, earn-back on / off: no cap / clamp / start again / stop, over 1 / 2 wins, Crooks K careful size lots /
        $ / % with the ladder off / Max $200 / Medium $500, Crooks L default / other steps / no growth, the ladder on F - J; Risk for Crooks K
        and L (no stop distance, as v5.0). Sources: the 12 catalogue sequences (first 1500 trades) + the user's M5 settings with TP1 = 0.1R and
        0.3R (first 2500 trades).
  pr    the Crooks C rule after N losing recovery trades (forget / % / wait / skip) on Crooks K and L, Risk and Profit (REC_DAYS mode).
  size  Fixed lots and % of equity with Size By Profit, every rule, earn-back on / off.
REC_RESTART=1 (environment): a restart (save, fresh load, reload) after every step. Run: python3 -I parity_v51.py [rec|pr|size] [workers]"""
import sys, os, subprocess, tempfile, pickle, datetime
from multiprocessing import Pool
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
import recovery as RC, crooks
H = S + '/mq5check/rec/rec_harness'
EA_REC = {m: i for i, m in enumerate(RC.MODES)}
CAPS = {'clamp': 0, 'stop': 1, 'reset': 2}; PR = {'forget': 1, 'pct': 2, 'wait': 3, 'skip': 4}
LADN = {'Low': 1, 'Medium': 2, 'High': 3, 'Extra high': 4, 'Max': 5}
KM = {'lots': 0, 'usd': 1, 'pct': 2}
LSETS = [dict(), dict(lZ1=1.0, lZ1N=10, lZ2=3.0, lZ2N=5, lGrow=20.0, lGrowX=6.0), dict(lGrow=0.0)]
TS, TV, SPR, COMM = 0.01, 1.0, 0.16, 7.0                          # the harness: tick size, tick value; the inputs InpSpread, InpCommLot


def pdiv(xr, sd, eb):
    """the EA's PDiv(exitR) with trRisk = sd, the same operations in the same order"""
    if xr <= 0: return 1.0
    if sd <= 0: return xr
    spr = max(SPR, 0.0); loss = (sd + spr) / TS * TV + COMM
    win = xr * sd / TS * TV
    if not eb: win -= spr / TS * TV + COMM
    return win / loss if (loss > 0 and win > 0) else xr


def sources():
    out = []
    for tf in crooks.TFS:
        for d in crooks.sources(tf):
            if d['name'] in ('Default settings', 'Most profit', 'Shortest losing streak'):
                seq = crooks.sequence(d['trades'], d['cfg']); sds = [x[5] for x in sorted(d['trades'], key=lambda x: x[0])]
                out.append(('%s %s' % (tf, d['name']), seq[:1500], sds[:1500], crooks.exit_r(d['cfg'])))
    U = pickle.load(open(S + '/v50/user_seq.pkl', 'rb'))
    for tp, u in sorted(U.items()):
        out.append(('M5 user TP1 %.1fR' % tp, u['seq'][:2500], u['sds'][:2500], u['xr']))
    return out


def ea_run(path, xr, mode, sb, cap, act, cn, kw, start, env_extra, extra=()):
    args = [H, path, repr(xr), 'InpRec=%d' % EA_REC[mode], 'InpSizeBy=%d' % (1 if sb == 'profit' else 0), 'InpExitAt=1', 'InpTp1R=%r' % xr,
            'InpCapOn=%d' % (1 if cap > 0 else 0), 'InpHardCap=%r' % (cap if cap > 0 else 500.0), 'InpCapAction=%d' % CAPS[act], 'InpCSplit=3',
            'InpBaseRisk=50', 'InpRecN=3', 'InpRecPct=50', 'InpRecMult=2', 'InpRecStep=25', 'InpParN=3', 'InpDelayN=2',
            'InpCrkCnOn=%d' % (1 if cn > 1 else 0), 'InpCrkCn=%d' % cn, 'InpCommLot=0', 'InpSpread=0', 'InpCrkT1=0',
            'InpCrkFK=%r' % kw.get('fK', 3.0), 'InpCrkGX=%r' % kw.get('gX', 10.0), 'InpCrkHPct=%r' % kw.get('hPct', 1.0), 'InpCrkJX=%r' % kw.get('jX', 20.0),
            'InpLadder=%d' % LADN.get(kw.get('lad'), 0), 'InpLadT=%r' % kw.get('ladT', 1000.0), 'InpEqPct=%r' % kw.get('eqPct', 1.0),
            'InpCrkKMode=%d' % KM[kw.get('kMode', 'lots')], 'InpCrkKLots=0.02', 'InpCrkKUsd=%r' % kw.get('kUsd', 25.0), 'InpCrkKPct=%r' % kw.get('kPct', 50.0),
            'InpCrkLZ1=%r' % kw.get('lZ1', 2.0), 'InpCrkLZ1N=%d' % kw.get('lZ1N', 6), 'InpCrkLZ2=%r' % kw.get('lZ2', 5.0), 'InpCrkLZ2N=%d' % kw.get('lZ2N', 3),
            'InpCrkLGrow=%r' % kw.get('lGrow', 10.0), 'InpCrkLGrowX=%r' % kw.get('lGrowX', 4.0)] + list(extra)
    env = dict(os.environ, REC_MIN='1', REC_KMIN='1', REC_START=repr(start), **env_extra)
    return subprocess.run(args, capture_output=True, text=True, check=True, env=env).stdout.split('\n')


def costs(eb):
    """the EA inputs of a Profit run with the costs (they come after the base list, so they override its 0s)"""
    return ('InpSpread=%r' % SPR, 'InpCommLot=%r' % COMM, 'InpEarnBack=%d' % eb)


def compare(tr, r, out, days=False):
    """tr: the simulator's trace (risks, 'SKIP' with days); out: the harness lines -> (ok, n compared, first diff)"""
    ea = [('SKIP' if l == 'SKIP' else float(l.split()[1])) for l in out if l.startswith('R ') or (days and l == 'SKIP')]
    stop = any(l == 'STOP' for l in out)
    n = min(len(tr), len(ea))
    diff = [i for i in range(n) if (tr[i] == 'SKIP') != (ea[i] == 'SKIP') or (tr[i] != 'SKIP' and abs(tr[i] - ea[i]) > 1e-9 * max(1.0, abs(tr[i])))]
    short = len(tr) < len(ea) and r['ruined']                     # the simulator stops at a blown account, the harness has no account
    ok = not diff and (len(tr) == len(ea) or short) and stop == r['capStopped']
    i = diff[0] if diff else n
    return ok, n, (i, tr[i] if i < len(tr) else None, ea[i] if i < len(ea) else None, len(tr), len(ea), r['capStopped'], stop)


def jobs_rec(xr):
    J = []
    cap1 = 500.0 if xr >= 0.5 else 2000.0                         # small targets: the base risk itself is $500+ with Profit at 0.1R
    caps = ((0.0, 'clamp'), (cap1, 'clamp'), (cap1, 'reset'), (cap1, 'stop'))
    for sb in ('risk', 'profit'):
        for mode in RC.MODES:
            if sb == 'risk' and mode not in ('Crooks K', 'Crooks L'): continue        # the old rules in Risk: the v4.9 suites
            cns = (1, 2) if mode in RC.CFAM else (1,)
            kws = [{}]
            if mode == 'Crooks K': kws = [dict(kMode=m, **lv) for m in ('lots', 'usd', 'pct') for lv in ({}, dict(lad='Max', ladT=200.0), dict(lad='Medium', ladT=500.0))]
            elif mode == 'Crooks L': kws = LSETS
            elif mode in RC.LADFAM: kws = [{}, dict(lad='Max', ladT=200.0)]
            for eb in ((1, 0) if sb == 'profit' else (None,)):
                for kw in kws:
                    for cn in cns:
                        for cap, act in caps: J.append((sb, mode, cn, kw, cap, act, eb))
    return J


def work_rec(src):
    name, seq, sds, xr = src
    tmp = tempfile.mkdtemp(prefix='p51_')
    rmin = [1.0 * sd * (1.0 + c) for (_, _, c, _), sd in zip(seq, sds)]
    krisk = [2.0 * rm for rm in rmin]                            # the Crooks K careful lots (0.02 lot = 2 oz of gold)
    path = os.path.join(tmp, 'seq.txt'); psd = os.path.join(tmp, 'seq_sd.txt')
    with open(path, 'w') as f, open(psd, 'w') as g:
        for (_, res, c, parts), rm, kr, sd in zip(seq, rmin, krisk, sds):
            pp = '%d%s\n' % (len(parts or []), ''.join(' %r %r' % x for x in (parts or [])))
            f.write('%r %r %r %r %s' % (res, c, rm, kr, pp)); g.write('%r %r %r %r %r %s' % (res, c, rm, kr, sd, pp))
    trs = {eb: [(res, c, parts, None, None, rm, None, kr, None if eb is None else pdiv(xr, sd, eb))
                for (_, res, c, parts), rm, kr, sd in zip(seq, rmin, krisk, sds)] for eb in (None, 1, 0)}
    runs = bad = ntr = 0; msgs = []
    for sb, mode, cn, kw, cap, act, eb in jobs_rec(xr):
        start = 1e4 if mode in ('Crooks H', '% of equity') else 1e12
        tr = []; r = RC.simulate(trs[eb], mode, cap=cap, capAction=act, cSplit=3, exitR=xr, start=start, trace=tr, cN=cn, sizeBy=sb, **kw)
        if eb is None: out = ea_run(path, xr, mode, sb, cap, act, cn, kw, start, {})
        else: out = ea_run(psd, xr, mode, sb, cap, act, cn, kw, start, dict(REC_SD='1'), costs(eb))
        ok, n, info = compare(tr, r, out); runs += 1; ntr += n
        if not ok:
            bad += 1
            if bad <= 6: msgs.append('MISMATCH rec %s | %s eb %s %s %s N %d cap %r %s | first diff %s' % (name, sb, eb, mode, kw, cn, cap, act, info))
    return name, runs, bad, ntr, msgs


def dayev(seq):
    out = []; prev = None
    for t, *_ in seq:
        d = t.date(); ev = []
        if prev is not None:
            x = prev
            while x < d:
                x += datetime.timedelta(days=1); ev.append(x.weekday() < 5)
        prev = d; out.append(ev)
    return out


def rules_pr():
    for N in (1, 2):
        yield dict(crkPr='forget', crkPrN=N)
        yield dict(crkPr='pct', crkPrN=N, crkPrPct=50.0)
        yield dict(crkPr='wait', crkPrN=N, crkPrM=2)
        for fg in (False, True): yield dict(crkPr='skip', crkPrN=N, crkPrD=2, crkPrForget=fg)


def work_pr(src):
    name, seq, sds, xr = src
    if name.startswith('M5 user'): seq, sds = seq[:1500], sds[:1500]
    tmp = tempfile.mkdtemp(prefix='p51pr_')
    rmin = [1.0 * sd * (1.0 + c) for (_, _, c, _), sd in zip(seq, sds)]; krisk = [2.0 * rm for rm in rmin]
    ev = dayev(seq); path = os.path.join(tmp, 'seq.txt'); psd = os.path.join(tmp, 'seq_sd.txt')
    with open(path, 'w') as f, open(psd, 'w') as g:
        for (t, res, c, parts), e, rm, kr, sd in zip(seq, ev, rmin, krisk, sds):
            dd = '%d%s' % (len(e), ''.join(' %d' % v for v in e)); pp = '%d%s\n' % (len(parts or []), ''.join(' %r %r' % x for x in (parts or [])))
            f.write('%s %r %r %r %r %s' % (dd, res, c, rm, kr, pp)); g.write('%s %r %r %r %r %r %s' % (dd, res, c, rm, kr, sd, pp))
    trs = {eb: [(res, c, parts, e, None, rm, None, kr, None if eb is None else pdiv(xr, sd, eb))
                for (t, res, c, parts), e, rm, kr, sd in zip(seq, ev, rmin, krisk, sds)] for eb in (None, 1, 0)}
    cap1 = 500.0 if xr >= 0.5 else 2000.0
    runs = bad = ntr = 0; msgs = []
    for sb in ('risk', 'profit'):
        for eb in ((1, 0) if sb == 'profit' else (None,)):
            for mode, mk in (('Crooks K', dict(kMode='lots')), ('Crooks K', dict(kMode='usd', lad='Max', ladT=200.0)), ('Crooks L', {}), ('Crooks L', LSETS[1])):
                for rl in rules_pr():
                    for cn in (1, 2):
                        for cap, act in ((0.0, 'clamp'), (cap1, 'clamp'), (cap1, 'reset'), (cap1, 'stop')):
                            tr = []; r = RC.simulate(trs[eb], mode, cap=cap, capAction=act, cSplit=3, exitR=xr, start=1e12, trace=tr, cN=cn, sizeBy=sb, **rl, **mk)
                            extra = ('InpCrkPr=%d' % PR[rl['crkPr']], 'InpCrkPrN=%d' % rl['crkPrN'], 'InpCrkPrPct=%r' % rl.get('crkPrPct', 50.0),
                                     'InpCrkPrM=%d' % rl.get('crkPrM', 2), 'InpCrkPrD=%d' % rl.get('crkPrD', 3), 'InpCrkPrForget=%d' % (1 if rl.get('crkPrForget') else 0), 'InpCrkPrAll=0')
                            if eb is None: out = ea_run(path, xr, mode, sb, cap, act, cn, mk, 1e12, dict(REC_DAYS='1'), extra)
                            else: out = ea_run(psd, xr, mode, sb, cap, act, cn, mk, 1e12, dict(REC_DAYS='1', REC_SD='1'), extra + costs(eb))
                            ok, n, info = compare(tr, r, out, days=True); runs += 1; ntr += n
                            if not ok:
                                bad += 1
                                if bad <= 6: msgs.append('MISMATCH pr %s | %s eb %s %s %s %s N %d cap %r %s | first diff %s' % (name, sb, eb, mode, mk, rl, cn, cap, act, info))
    return name, runs, bad, ntr, msgs


def work_size(src):
    name, seq, sds, xr = src
    seq, sds = seq[:800], sds[:800]
    tmp = tempfile.mkdtemp(prefix='p51sz_')
    rmin = [1.0 * sd * (1.0 + c) for (_, _, c, _), sd in zip(seq, sds)]; krisk = [2.0 * rm for rm in rmin]
    path = os.path.join(tmp, 'seq.txt')
    with open(path, 'w') as f:
        for (_, res, c, parts), rm, kr, sd in zip(seq, rmin, krisk, sds):
            f.write('%r %r %r %r %r %d%s\n' % (res, c, rm, kr, sd, len(parts or []), ''.join(' %r %r' % x for x in (parts or []))))
    runs = bad = ntr = 0; msgs = []
    cap1 = 500.0 if xr >= 0.5 else 2000.0
    for eb in (1, 0):
        for bm, vals in (('lot', (0.01, 0.05)), ('pct', (0.5, 1.0))):
            for bv in vals:
                lotb = [bv * ((sd + SPR) / TS * TV + COMM) for sd in sds] if bm == 'lot' else [None] * len(sds)
                trs = [(res, c, parts, None, None, rm, lb, kr, pdiv(xr, sd, eb)) for (_, res, c, parts), rm, lb, kr, sd in zip(seq, rmin, lotb, krisk, sds)]
                for mode in RC.MODES:
                    for cn in ((1, 2) if mode in RC.CFAM else (1,)):
                        kws = [dict(kMode='pct')] if mode == 'Crooks K' else [{}]
                        for kw in kws:
                            start = 1e4 if (bm == 'pct' or mode in ('Crooks H', '% of equity')) else 1e12
                            for cap, act in ((0.0, 'clamp'), (cap1, 'clamp'), (cap1, 'reset'), (cap1, 'stop')):
                                tr = []
                                r = RC.simulate(trs, mode, cap=cap, capAction=act, cSplit=3, exitR=xr, start=start, trace=tr, cN=cn, sizeBy='profit',
                                                eqPct=bv if bm == 'pct' else 1.0, baseMode=bm, basePct=bv if bm == 'pct' else 1.0, **kw)
                                extra = costs(eb) + ('InpSizeMode=%d' % (1 if bm == 'lot' else 2), 'InpBaseLots=%r' % (bv if bm == 'lot' else 0.01))
                                kw2 = dict(kw, eqPct=bv if bm == 'pct' else 1.0)
                                out = ea_run(path, xr, mode, 'profit', cap, act, cn, kw2, start, dict(REC_SD='1'), extra)
                                ok, n, info = compare(tr, r, out); runs += 1; ntr += n
                                if not ok:
                                    bad += 1
                                    if bad <= 6: msgs.append('MISMATCH size %s | eb %d %s=%s %s %s N %d cap %r %s | first diff %s' % (name, eb, bm, bv, mode, kw, cn, cap, act, info))
    return name, runs, bad, ntr, msgs


if __name__ == '__main__':
    secs = [sys.argv[1]] if len(sys.argv) > 1 and sys.argv[1] in ('rec', 'pr', 'size') else ['rec', 'pr', 'size']
    W = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    srcs = sources()
    for sec in secs:
        fn = {'rec': work_rec, 'pr': work_pr, 'size': work_size}[sec]
        R = B = N = 0
        with Pool(W) as pool:
            for name, runs, bad, ntr, msgs in pool.imap_unordered(fn, srcs):
                R += runs; B += bad; N += ntr
                for m in msgs: print(m)
                print('%-5s %-30s runs %5d, trades %8d, mismatches %d' % (sec, name, runs, ntr, bad), flush=True)
        print('SECTION %s: runs %d, trades compared %d, mismatches %d -> %s' % (sec, R, N, B, 'ALL IDENTICAL' if not B else 'DIFFERENCES'), flush=True)
