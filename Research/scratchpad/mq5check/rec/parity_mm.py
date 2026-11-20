"""v5.4 money rules parity (SPEC section 8): the EA (rec_harness) vs gold/recovery.py, trade for trade (a Cooling-off skip compared as SKIP),
on the 10 rules: Risk and Profit (REC_SD, costs, earn-back on), starts $1,000 / $10,000, default settings and a second set, caps none /
clamp / start again / stop (the second set has a 4% cap: with a cap equal to the first drawdown step, a capped loss at the best makes the drawdown exactly that step, a floating-point tie). REC_RESTART=1: a restart after every step. Run: python3 -I parity_mm.py [workers]"""
import sys, os, tempfile
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parity_v51 as P
RC = P.RC
SETS = [{}, dict(mmKFrac=0.5, mmKWin=50, mmKMin=10, mmEqN=10, mmEqLow=0.5, mmDd1=5.0, mmDd2=15.0, mmCoolL=3, mmCoolN=2, mmCap=4.0, mmC3Pct=2.0, mmC5Share=50.0)]
EAN = dict(mmKFrac='InpMmKFrac', mmKWin='InpMmKWin', mmKMin='InpMmKMin', mmEqN='InpMmEqN', mmEqLow='InpMmEqLow', mmDd1='InpMmDd1', mmDd2='InpMmDd2',
           mmCoolL='InpMmCoolL', mmCoolN='InpMmCoolN', mmCap='InpMmCap', mmC3Pct='InpMmC3Pct', mmC5Share='InpMmC5Share')


def work(src):
    name, seq, sds, xr = src
    tmp = tempfile.mkdtemp(prefix='pmm_')
    rmin = [1.0 * sd * (1.0 + c) for (_, _, c, _), sd in zip(seq, sds)]; krisk = [2.0 * r for r in rmin]
    path = os.path.join(tmp, 's.txt'); psd = os.path.join(tmp, 'sd.txt')
    with open(path, 'w') as f, open(psd, 'w') as g:
        for (_, res, c, parts), rm, kr, sd in zip(seq, rmin, krisk, sds):
            pp = '%d%s\n' % (len(parts or []), ''.join(' %r %r' % x for x in (parts or [])))
            f.write('%r %r %r %r %s' % (res, c, rm, kr, pp)); g.write('%r %r %r %r %r %s' % (res, c, rm, kr, sd, pp))
    trs = {sb: [(res, c, parts, None, None, rm, None, kr, P.pdiv(xr, sd, 1) if sb == 'profit' else None)
                for (_, res, c, parts), rm, kr, sd in zip(seq, rmin, krisk, sds)] for sb in ('risk', 'profit')}
    runs = bad = ntr = ties = 0; msgs = []
    for sb in ('risk', 'profit'):
        for mode in RC.MM:
            for st in (1000.0, 10000.0):
                for kw in SETS:
                    for cap, act in ((0.0, 'clamp'), (300.0, 'clamp'), (300.0, 'reset'), (300.0, 'stop')):
                        extra = tuple('%s=%r' % (EAN[k], v) for k, v in kw.items()) + (P.costs(1) if sb == 'profit' else ())
                        out = P.ea_run(psd if sb == 'profit' else path, xr, mode, sb, cap, act, 1, {}, st, dict(REC_SD='1') if sb == 'profit' else {}, extra)
                        ok, n, info, tie = P.sim_cmp(trs[sb], mode, out, True, cap=cap, capAction=act, cSplit=3, exitR=xr, start=st, cN=1, sizeBy=sb, **kw)
                        runs += 1; ntr += n; ties += tie
                        if not ok:
                            bad += 1
                            if bad <= 6: msgs.append('MISMATCH mm %s | %s %s start %r %s cap %r %s | first diff %s' % (name, sb, mode, st, kw, cap, act, info))
    return name, runs, bad, ntr, ties, msgs


if __name__ == '__main__':
    W = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    R = B = N = T = 0
    with Pool(W) as pool:
        for name, runs, bad, ntr, ties, msgs in pool.imap_unordered(work, P.sources()):
            R += runs; B += bad; N += ntr; T += ties
            for m in msgs: print(m)
            print('%-30s runs %5d, trades %8d, tie-breaks %d, mismatches %d' % (name, runs, ntr, ties, bad), flush=True)
    print('MONEY RULES: runs %d, trades compared %d, floating-point tie-breaks %d, mismatches %d -> %s' % (R, N, T, B, 'ALL IDENTICAL' if not B else 'DIFFERENCES'))
