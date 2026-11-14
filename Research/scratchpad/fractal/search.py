"""Stage 1 search for strategies 10 (M5 fractals) and 11 (M15 fractals): every right / left / offset x a coarse exit grid, M1 execution,
costs $0.23 per ounce. Results: search1_<TF>.npz (one row per combination; columns from fast.grid) + the settings of each row.
Progress per (right, left) pair is kept in search1_<TF>_parts/ so a stopped run resumes where it was."""
import sys, os, time, datetime as dt, numpy as np
from multiprocessing import Pool
D = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fractal'
sys.path.insert(0, D)
import engine as EN, fast as FA
import os as _os
STAGE = _os.environ.get('STAGE', '1')
PM = int(_os.environ.get('PM', '0'))
STAGE_TAG = STAGE + ('h' if PM == 2 else 'l' if PM == 1 else '')
if STAGE == '1':
    RS = [1, 2, 3, 5, 8, 12, 20]; LS = [2, 3, 5, 8, 12, 20, 30, 50]
else:   # stage 2: around the stage-1 best (right 20 / left 50 sat on the grid's edge), practical exits only
    RS = [12, 16, 20, 25, 30, 40, 60]; LS = [20, 30, 40, 50, 65, 80, 100, 150]
if STAGE == '1':
    OFFS = [-0.20, -0.15, -0.10, -0.07, -0.05, -0.03, -0.01, 0.0, 0.02, 0.05]
    UPS = np.array([0.05, 0.1, 0.15, 0.2, 0.3, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0])          # TP (and BE) grid, %
    DNS = np.array([0.05, 0.1, 0.15, 0.2, 0.3, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0])          # SL (and salvage) grid, %
    BE_I = np.array([-1, 0, 1, 3, 4]); SV_I = np.array([-1, 1, 3, 5])                     # BE off / 0.05 / 0.1 / 0.2 / 0.3; salvage off / 0.1 / 0.2 / 0.5
    TP_I = np.arange(len(UPS)); SL_I = np.arange(len(DNS))
else:
    OFFS = [-0.05, -0.03, -0.02, -0.01, 0.0, 0.01, 0.02]
    UPS = np.array([0.03, 0.05, 0.07, 0.1, 0.15, 0.2, 0.3, 0.5, 0.75, 1.0, 1.5, 2.0, 2.5, 3.0])
    DNS = np.array([0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.75, 1.0])
    TP_I = np.array([5, 6, 7, 8, 9, 10, 11, 12, 13]); SL_I = np.arange(len(DNS))            # TP 0.2 .. 3.0, SL 0.1 .. 1.0 (>= 0.10 %: costs <= ~0.1 R)
    BE_I = np.array([-1, 0, 1, 2, 3, 4, 5]); SV_I = np.array([-1, 0, 2, 4])                 # BE off / 0.03 / 0.05 / 0.07 / 0.1 / 0.15 / 0.2; salvage off / 0.1 / 0.2 / 0.3
COST = 0.23; YEARS = list(range(2021, 2027))
G = {}


def init():
    B = EN.load(); t, O, H, L, C = EN.chart(B, 'M1')
    G.update(B=B, t=t, O=O, H=H, L=L, C=C, blk=FA.blocks(H, L),
             yr=np.array([dt.datetime.fromtimestamp(int(x), dt.timezone.utc).year for x in t[::1440]]))


def job(arg):
    tf, r, l = arg
    fn = '%s/search%s_%s_parts/r%d_l%d.npz' % (D, STAGE_TAG, tf, r, l)
    if os.path.exists(fn): return fn
    B = G['B']; t, O, H, L, C = G['t'], G['O'], G['H'], G['L'], G['C']; BH1, BL1, BH2, BL2 = G['blk']
    kk = (np.searchsorted(B[tf + '_t'], t, side='right') - 1).astype(np.int64); ph = EN.pivots(B[tf + '_H'], l, r)
    rows = []; prm = []
    for off in OFFS:
        ej, es, eF, eH = FA.events(O, H, L, C, kk, ph, off, PM)
        eyr = (G['yr'][ej // 1440] - 2021).astype(np.int64)
        bes = np.arange(len(UPS)); svs = np.arange(len(DNS))
        KU, XU, KD, XD, KB, XB, KS, XS = FA.passages(O, H, L, C, BH1, BL1, BH2, BL2, ej, es, eF, UPS, DNS, bes, svs, PM)
        res = FA.grid(ej, es, eF, eyr, KU, XU, KD, XD, KB, XB, KS, XS, UPS, DNS, bes, svs, TP_I, SL_I, BE_I, SV_I, COST, len(YEARS), 3)
        rows.append(res)
        for a in TP_I:
            for b in SL_I:
                for g in BE_I:
                    for h in SV_I:
                        prm.append((r, l, off, UPS[a], DNS[b], UPS[g] if g >= 0 else 0.0, DNS[h] if h >= 0 else 0.0, len(ej)))
    np.savez(fn, res=np.vstack(rows), prm=np.array(prm))
    return fn


if __name__ == '__main__':
    tfs = sys.argv[1].split(',') if len(sys.argv) > 1 else ['M5', 'M15']
    jobs = [(tf, r, l) for tf in tfs for r in RS for l in LS]
    for tf in tfs: os.makedirs('%s/search%s_%s_parts' % (D, STAGE_TAG, tf), exist_ok=True)
    t0 = time.time(); done = 0
    with Pool(4, initializer=init) as pool:
        for fn in pool.imap_unordered(job, jobs):
            done += 1
            print('%d/%d %s %.0fs' % (done, len(jobs), os.path.basename(fn), time.time() - t0), flush=True)
    for tf in tfs:
        parts = [np.load('%s/search%s_%s_parts/r%d_l%d.npz' % (D, STAGE_TAG, tf, r, l)) for r in RS for l in LS]
        np.savez('%s/search%s_%s.npz' % (D, STAGE_TAG, tf), res=np.vstack([p['res'] for p in parts]), prm=np.vstack([p['prm'] for p in parts]))
    print('done stage', STAGE, time.time() - t0, flush=True)
