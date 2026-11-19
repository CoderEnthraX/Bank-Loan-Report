"""v5.1 (Size By Profit with the costs: REC_SD, InpSpread 0.16, InpCommLot 7, earn-back on / off, each trade's D given to the reference
as element [8], computed like the EA's PDiv) monthly restart: the EA's own NextRisk / BookClosed with its monthly restart (mrs_harness, REC_KMIN) vs gold/recovery.py run FRESH on
every calendar month, trade for trade: Size By Profit on every rule except % of equity and Crooks H (account equity), and Crooks K (lots / $ /
%, ladder off / Max $200) and Crooks L (default / other steps) with Risk and Profit; caps none / clamp / start again / stop.
Sources: the catalogue 'Most profit' / 'Shortest losing streak' sequences + the user's M5 settings with TP1 = 0.1R and 0.3R.
REC_RESTART=1: a restart after every step. Run: python3 -I parity_month_v50.py"""
import sys, os, subprocess, tempfile, pickle
from multiprocessing import Pool
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
import recovery as RC, crooks
H = S + '/mq5check/rec/mrs_harness'
EA_REC = {m: i for i, m in enumerate(RC.MODES)}
CAPS = {'clamp': 0, 'stop': 1, 'reset': 2}
LADN = {'Low': 1, 'Medium': 2, 'High': 3, 'Extra high': 4, 'Max': 5}
KM = {'lots': 0, 'usd': 1, 'pct': 2}
TS, TV, SPR, COMM = 0.01, 1.0, 0.16, 7.0


def pdiv(xr, sd, eb):
    """the EA's PDiv(exitR) with trRisk = sd, the same operations in the same order"""
    if xr <= 0: return 1.0
    if sd <= 0: return xr
    spr = max(SPR, 0.0); loss = (sd + spr) / TS * TV + COMM
    win = xr * sd / TS * TV
    if not eb: win -= spr / TS * TV + COMM
    return win / loss if (loss > 0 and win > 0) else xr


def ea(path, xr, mode, sb, cap, act, kw, eb):
    args = [H, path, repr(xr), 'InpRec=%d' % EA_REC[mode], 'InpSizeBy=%d' % (1 if sb == 'profit' else 0), 'InpExitAt=1', 'InpTp1R=%r' % xr,
            'InpCapOn=%d' % (1 if cap > 0 else 0), 'InpHardCap=%r' % (cap if cap > 0 else 500.0), 'InpCapAction=%d' % CAPS[act], 'InpCSplit=3',
            'InpBaseRisk=50', 'InpRecN=3', 'InpRecPct=50', 'InpRecMult=2', 'InpRecStep=25', 'InpParN=3', 'InpDelayN=2', 'InpCrkCnOn=0', 'InpCrkCn=1',
            'InpCommLot=0', 'InpSpread=0', 'InpCrkT1=0', 'InpMRestart=1', 'InpCrkFK=3', 'InpCrkGX=10', 'InpCrkJX=20',
            'InpLadder=%d' % LADN.get(kw.get('lad'), 0), 'InpLadT=%r' % kw.get('ladT', 1000.0),
            'InpCrkKMode=%d' % KM[kw.get('kMode', 'lots')], 'InpCrkKLots=0.02', 'InpCrkKUsd=25', 'InpCrkKPct=50',
            'InpCrkLZ1=%r' % kw.get('lZ1', 2.0), 'InpCrkLZ1N=%d' % kw.get('lZ1N', 6), 'InpCrkLZ2=%r' % kw.get('lZ2', 5.0), 'InpCrkLZ2N=%d' % kw.get('lZ2N', 3),
            'InpCrkLGrow=%r' % kw.get('lGrow', 10.0), 'InpCrkLGrowX=%r' % kw.get('lGrowX', 4.0)]
    env = dict(os.environ, REC_KMIN='1')
    if eb is not None: args += ['InpSpread=%r' % SPR, 'InpCommLot=%r' % COMM, 'InpEarnBack=%d' % eb]; env['REC_SD'] = '1'
    out = subprocess.run(args, capture_output=True, text=True, check=True, env=env).stdout.split('\n')
    return [l for l in out if l]


def jobs(xr):
    cap1 = 500.0 if xr >= 0.5 else 2000.0
    J = []
    for sb in ('risk', 'profit'):
        for mode in RC.MODES:
            if mode in ('% of equity', 'Crooks H'): continue
            if sb == 'risk' and mode not in ('Crooks K', 'Crooks L'): continue
            kws = [{}]
            if mode == 'Crooks K': kws = [dict(kMode=m, **lv) for m in ('lots', 'usd', 'pct') for lv in ({}, dict(lad='Max', ladT=200.0))]
            elif mode == 'Crooks L': kws = [{}, dict(lZ1=1.0, lZ1N=10, lZ2=3.0, lZ2N=5, lGrow=20.0, lGrowX=6.0)]
            elif mode in RC.LADFAM: kws = [{}, dict(lad='Max', ladT=200.0)]
            for eb in ((1, 0) if sb == 'profit' else (None,)):
                for kw in kws:
                    for cap, act in ((0.0, 'clamp'), (cap1, 'clamp'), (cap1, 'reset'), (cap1, 'stop')): J.append((sb, mode, kw, cap, act, eb))
    return J


def work(src):
    name, seq, sds, xr = src
    tmp = tempfile.mkdtemp(prefix='pm51_')
    months = []; key = None
    for (t, res, c, parts), sd in zip(seq, sds):
        k = (t.year, t.month)
        if k != key: months.append([]); key = k
        rm = 1.0 * sd * (1.0 + c)
        months[-1].append((res, c, parts, None, None, rm, None, 2.0 * rm, sd))
    runs = bad = ntr = nstop = nblown = 0; msgs = []
    for sb, mode, kw, cap, act, eb in jobs(xr):
        refs = []
        for mt in months:
            tr = []
            mt = [x[:8] + (None if eb is None else pdiv(xr, x[8], eb),) for x in mt]
            rr = RC.simulate(mt, mode, base=50.0, cap=cap, capAction=act, cSplit=3, exitR=xr, start=1e12, trace=tr, sizeBy=sb, **kw)
            refs.append((tr, rr))
        # a month in which the simulator's 1e12 account blew: the harness (no account) would go on with impossible amounts, so its totals lose
        # their precision for the later months; it is compared up to the blow-up and the EA starts again (a fresh harness) after that month
        segs = []; s0 = 0
        for i, (tr, rr) in enumerate(refs):
            if rr['ruined'] and len(tr) < len(months[i]): segs.append((s0, i)); s0 = i + 1
        if s0 < len(months): segs.append((s0, len(months) - 1))
        ok = True; worst = 0.0; runs += 1
        for a, b in segs:
            path = os.path.join(tmp, 'seq.txt')
            with open(path, 'w') as f:
                for mi in range(a, b + 1):
                    if mi > a: f.write('M\n')
                    for (res, c, parts, _, _, rm, _, kr, sd) in months[mi]:
                        f.write('%r %r %r %r %s%d%s\n' % (res, c, rm, kr, '' if eb is None else '%r ' % sd, len(parts or []), ''.join(' %r %r' % x for x in (parts or []))))
            e = ea(path, xr, mode, sb, cap, act, kw, eb); pos = 0
            for mi in range(a, b + 1):
                mt = months[mi]; tr, rr = refs[mi]
                toks = e[pos:pos + len(mt)]; pos += len(mt)
                rs = [float(x.split()[1]) for x in toks if x.startswith('R ')]
                if len(tr) < len(mt) and rr['ruined']:
                    nblown += 1; rs = rs[:len(tr)]; ok &= len(toks) == len(mt)
                elif len(tr) < len(mt):
                    ok &= len(toks) == len(mt) and toks[len(tr)] == 'STOP' and all(x == 'SKIP' for x in toks[len(tr) + 1:]); nstop += 1
                ok &= len(rs) == len(tr)
                for u, v in zip(rs, tr): worst = max(worst, abs(u - v) / max(1.0, abs(v)))
                ntr += len(tr)
            ok &= pos == len(e)
        ok &= worst < 1e-9
        if not ok:
            bad += 1
            if bad <= 6: msgs.append('MISMATCH month %s | %s eb %s %s %s cap %r %s | worst %.3g' % (name, sb, eb, mode, kw, cap, act, worst))
    return name, runs, bad, ntr, nstop, nblown, msgs


if __name__ == '__main__':
    srcs = []
    for tf in crooks.TFS:
        for d in crooks.sources(tf):
            if d['name'] in ('Most profit', 'Shortest losing streak'):
                srcs.append(('%s %s' % (tf, d['name']), crooks.sequence(d['trades'], d['cfg']), [x[5] for x in sorted(d['trades'], key=lambda x: x[0])], crooks.exit_r(d['cfg'])))
    U = pickle.load(open(S + '/v50/user_seq.pkl', 'rb'))
    for tp, u in sorted(U.items()): srcs.append(('M5 user TP1 %.1fR' % tp, u['seq'], u['sds'], u['xr']))
    R = B = N = NS = NB = 0
    with Pool(int(sys.argv[1]) if len(sys.argv) > 1 else 4) as pool:
        for name, runs, bad, ntr, nstop, nblown, msgs in pool.imap_unordered(work, srcs):
            R += runs; B += bad; N += ntr; NS += nstop; NB += nblown
            for m in msgs: print(m)
            print('%-30s runs %4d, trades %8d, mismatches %d' % (name, runs, ntr, bad), flush=True)
    print('MONTH v5.1: runs %d, trades compared %d, months stopped by the cap %d, months where the simulator account blew (compared up to it) %d, mismatches %d -> %s' % (R, N, NS, NB, B, 'ALL IDENTICAL' if not B else 'DIFFERENCES'))
