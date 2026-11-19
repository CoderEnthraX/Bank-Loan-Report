"""v5.2 Crooks X parity (SPEC section 6): the EA's own NextRisk / BookClosed (rec_harness) vs gold/recovery.py, trade for trade.
Risk and Profit (Profit with REC_SD, spread 0.16, commission $7, earn-back on), N 1 / 3 / 5 (over N wins), steps $1,000 / $200 / $50,
limit: hard cap only / per-trade $300; caps none / clamp / start again / stop; plus the Crooks C rule after N losing recovery trades
(forget / % / wait / skip) in REC_DAYS mode. Sources as parity_v51.py. REC_RESTART=1: a restart after every step.
Run: python3 -I parity_x.py [rec|pr] [workers]"""
import sys, os, tempfile
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parity_v51 as P
RC = P.RC
STEPS = (1000.0, 200.0, 50.0)


def xin(step, lim):
    return ('InpCrkXStep=%r' % step, 'InpCrkXLim=%d' % (1 if lim > 0 else 0), 'InpCrkXLimUsd=%r' % (lim if lim > 0 else 500.0))


def work_rec(src):
    name, seq, sds, xr = src
    tmp = tempfile.mkdtemp(prefix='px_')
    rmin = [1.0 * sd * (1.0 + c) for (_, _, c, _), sd in zip(seq, sds)]; krisk = [2.0 * r for r in rmin]
    path = os.path.join(tmp, 's.txt'); psd = os.path.join(tmp, 'sd.txt')
    with open(path, 'w') as f, open(psd, 'w') as g:
        for (_, res, c, parts), rm, kr, sd in zip(seq, rmin, krisk, sds):
            pp = '%d%s\n' % (len(parts or []), ''.join(' %r %r' % x for x in (parts or [])))
            f.write('%r %r %r %r %s' % (res, c, rm, kr, pp)); g.write('%r %r %r %r %r %s' % (res, c, rm, kr, sd, pp))
    trs = {sb: [(res, c, parts, None, None, rm, None, kr, P.pdiv(xr, sd, 1) if sb == 'profit' else None)
                for (_, res, c, parts), rm, kr, sd in zip(seq, rmin, krisk, sds)] for sb in ('risk', 'profit')}
    cap1 = 500.0 if xr >= 0.5 else 2000.0
    runs = bad = ntr = ties = 0; msgs = []
    for sb in ('risk', 'profit'):
        for cn in (1, 3, 5):
            for step in STEPS:
                for lim in (0.0, 300.0):
                    for cap, act in ((0.0, 'clamp'), (cap1, 'clamp'), (cap1, 'reset'), (cap1, 'stop')):
                        extra = xin(step, lim) + (P.costs(1) if sb == 'profit' else ())
                        out = P.ea_run(psd if sb == 'profit' else path, xr, 'Crooks X', sb, cap, act, cn, {}, 1e12, dict(REC_SD='1') if sb == 'profit' else {}, extra)
                        ok, n, info, tie = P.sim_cmp(trs[sb], 'Crooks X', out, cap=cap, capAction=act, cSplit=3, exitR=xr, start=1e12, cN=cn, sizeBy=sb, xStep=step, xLim=lim)
                        runs += 1; ntr += n; ties += tie
                        if not ok:
                            bad += 1
                            if bad <= 6: msgs.append('MISMATCH x %s | %s N %d step %r lim %r cap %r %s | first diff %s' % (name, sb, cn, step, lim, cap, act, info))
    return name, runs, bad, ntr, ties, msgs


def work_pr(src):
    name, seq, sds, xr = src
    if name.startswith('M5 user'): seq, sds = seq[:1500], sds[:1500]
    tmp = tempfile.mkdtemp(prefix='pxpr_')
    rmin = [1.0 * sd * (1.0 + c) for (_, _, c, _), sd in zip(seq, sds)]; krisk = [2.0 * r for r in rmin]
    ev = P.dayev(seq); path = os.path.join(tmp, 's.txt')
    with open(path, 'w') as f:
        for (t, res, c, parts), e, rm, kr in zip(seq, ev, rmin, krisk):
            f.write('%d%s %r %r %r %r %d%s\n' % (len(e), ''.join(' %d' % v for v in e), res, c, rm, kr, len(parts or []), ''.join(' %r %r' % x for x in (parts or []))))
    trs = [(res, c, parts, e, None, rm, None, kr) for (t, res, c, parts), e, rm, kr in zip(seq, ev, rmin, krisk)]
    cap1 = 500.0 if xr >= 0.5 else 2000.0
    runs = bad = ntr = ties = 0; msgs = []
    for rl in P.rules_pr():
        for cn in (1, 3):
            for step in (1000.0, 50.0):
                for cap, act in ((0.0, 'clamp'), (cap1, 'reset')):
                    extra = ('InpCrkPr=%d' % P.PR[rl['crkPr']], 'InpCrkPrN=%d' % rl['crkPrN'], 'InpCrkPrPct=%r' % rl.get('crkPrPct', 50.0),
                             'InpCrkPrM=%d' % rl.get('crkPrM', 2), 'InpCrkPrD=%d' % rl.get('crkPrD', 3), 'InpCrkPrForget=%d' % (1 if rl.get('crkPrForget') else 0), 'InpCrkPrAll=0') + xin(step, 0.0)
                    out = P.ea_run(path, xr, 'Crooks X', 'risk', cap, act, cn, {}, 1e12, dict(REC_DAYS='1'), extra)
                    ok, n, info, tie = P.sim_cmp(trs, 'Crooks X', out, True, cap=cap, capAction=act, cSplit=3, exitR=xr, start=1e12, cN=cn, sizeBy='risk', xStep=step, **rl)
                    runs += 1; ntr += n; ties += tie
                    if not ok:
                        bad += 1
                        if bad <= 6: msgs.append('MISMATCH xpr %s | %s N %d step %r cap %r %s | first diff %s' % (name, rl, cn, step, cap, act, info))
    return name, runs, bad, ntr, ties, msgs


if __name__ == '__main__':
    sec = sys.argv[1] if len(sys.argv) > 1 else 'rec'
    W = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    R = B = N = T = 0
    with Pool(W) as pool:
        for name, runs, bad, ntr, ties, msgs in pool.imap_unordered(work_rec if sec == 'rec' else work_pr, P.sources()):
            R += runs; B += bad; N += ntr; T += ties
            for m in msgs: print(m)
            print('%-30s runs %5d, trades %8d, tie-breaks %d, mismatches %d' % (name, runs, ntr, ties, bad), flush=True)
    print('CROOKS X %s: runs %d, trades compared %d, floating-point tie-breaks %d, mismatches %d -> %s' % (sec, R, N, T, B, 'ALL IDENTICAL' if not B else 'DIFFERENCES'))
