"""v5.3 recovery part size = Fixed when recovery starts (SPEC section 7): the EA (rec_harness) vs gold/recovery.py partFix=True, trade for
trade, on every Crooks C family rule (C, E - L, X): Risk and Profit (REC_SD, costs, earn-back on), N 1 / 3 / 5, caps none / clamp / start
again / stop; and the Crooks C rule after N losing recovery trades (REC_DAYS). REC_RESTART=1: a restart after every step.
Run: python3 -I parity_fix.py [rec|pr] [workers]"""
import sys, os, tempfile
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parity_v51 as P
RC = P.RC
FAM = [m for m in RC.CFAM]
FIX = ('InpCrkPart=1',)


def work_rec(src):
    name, seq, sds, xr = src
    tmp = tempfile.mkdtemp(prefix='pf_')
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
        for mode in FAM:
            for cn in ((1,) if mode == 'Crooks L' else (1, 3, 5)):
                kws = [{}, dict(lad='Max', ladT=200.0)] if mode in RC.LADFAM else [{}]
                if mode == 'Crooks X': kws = [dict(xStep=1000.0), dict(xStep=50.0, xLim=300.0)]
                for kw in kws:
                    for cap, act in ((0.0, 'clamp'), (cap1, 'clamp'), (cap1, 'reset'), (cap1, 'stop')):
                        extra = FIX + (P.costs(1) if sb == 'profit' else ())
                        if mode == 'Crooks X': extra += ('InpCrkXStep=%r' % kw['xStep'], 'InpCrkXLim=%d' % (1 if kw.get('xLim') else 0), 'InpCrkXLimUsd=%r' % kw.get('xLim', 500.0))
                        ek = {k: v for k, v in kw.items() if k not in ('xStep', 'xLim')}
                        out = P.ea_run(psd if sb == 'profit' else path, xr, mode, sb, cap, act, cn, ek, 1e12, dict(REC_SD='1') if sb == 'profit' else {}, extra)
                        ok, n, info, tie = P.sim_cmp(trs[sb], mode, out, cap=cap, capAction=act, cSplit=3, exitR=xr, start=1e12, cN=cn, sizeBy=sb, partFix=True, **kw)
                        runs += 1; ntr += n; ties += tie
                        if not ok:
                            bad += 1
                            if bad <= 6: msgs.append('MISMATCH fix %s | %s %s %s N %d cap %r %s | first diff %s' % (name, sb, mode, kw, cn, cap, act, info))
    return name, runs, bad, ntr, ties, msgs


def work_pr(src):
    name, seq, sds, xr = src
    if name.startswith('M5 user'): seq, sds = seq[:1500], sds[:1500]
    tmp = tempfile.mkdtemp(prefix='pfpr_')
    rmin = [1.0 * sd * (1.0 + c) for (_, _, c, _), sd in zip(seq, sds)]; krisk = [2.0 * r for r in rmin]
    ev = P.dayev(seq); path = os.path.join(tmp, 's.txt')
    with open(path, 'w') as f:
        for (t, res, c, parts), e, rm, kr in zip(seq, ev, rmin, krisk):
            f.write('%d%s %r %r %r %r %d%s\n' % (len(e), ''.join(' %d' % v for v in e), res, c, rm, kr, len(parts or []), ''.join(' %r %r' % x for x in (parts or []))))
    trs = [(res, c, parts, e, None, rm, None, kr) for (t, res, c, parts), e, rm, kr in zip(seq, ev, rmin, krisk)]
    cap1 = 500.0 if xr >= 0.5 else 2000.0
    runs = bad = ntr = ties = 0; msgs = []
    for mode in ('Crooks C', 'Crooks E', 'Crooks X'):
        for rl in P.rules_pr():
            for cn in (3, 5):
                for cap, act in ((0.0, 'clamp'), (cap1, 'reset')):
                    extra = FIX + ('InpCrkPr=%d' % P.PR[rl['crkPr']], 'InpCrkPrN=%d' % rl['crkPrN'], 'InpCrkPrPct=%r' % rl.get('crkPrPct', 50.0),
                                   'InpCrkPrM=%d' % rl.get('crkPrM', 2), 'InpCrkPrD=%d' % rl.get('crkPrD', 3), 'InpCrkPrForget=%d' % (1 if rl.get('crkPrForget') else 0), 'InpCrkPrAll=0')
                    out = P.ea_run(path, xr, mode, 'risk', cap, act, cn, {}, 1e12, dict(REC_DAYS='1'), extra)
                    ok, n, info, tie = P.sim_cmp(trs, mode, out, True, cap=cap, capAction=act, cSplit=3, exitR=xr, start=1e12, cN=cn, sizeBy='risk', partFix=True, **rl)
                    runs += 1; ntr += n; ties += tie
                    if not ok:
                        bad += 1
                        if bad <= 6: msgs.append('MISMATCH fixpr %s | %s %s N %d cap %r %s | first diff %s' % (name, mode, rl, cn, cap, act, info))
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
    print('FIXED PARTS %s: runs %d, trades compared %d, floating-point tie-breaks %d, mismatches %d -> %s' % (sec, R, N, T, B, 'ALL IDENTICAL' if not B else 'DIFFERENCES'))
