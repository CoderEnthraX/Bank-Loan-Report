"""fast.py against engine.sim, trade for trade, on random settings (M1 execution, every fractal TF)."""
import sys, numpy as np, time
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fractal')
import engine as EN, fast as FA
B = EN.load(); t, O, H, L, C = EN.chart(B, 'M1')
BH1, BL1, BH2, BL2 = FA.blocks(H, L)
UPS = np.array([0.03, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5, 0.75, 1.0, 1.5, 2.0, 3.1]); DNS = np.array([0.05, 0.1, 0.15, 0.2, 0.3, 0.5, 0.7, 1.0, 2.0, 4.2])
rng = np.random.default_rng(int(sys.argv[1]) if len(sys.argv) > 1 else 1); bad = 0; ntr = 0; t0 = time.time()
for it in range(int(sys.argv[2]) if len(sys.argv) > 2 else 40):
    ftf = rng.choice(['M5', 'M15', 'H1', 'H4', 'D1']); r = int(rng.integers(1, 12)); l = int(rng.integers(1, 30)); off = float(rng.choice([-0.2, -0.1, -0.05, -0.02, 0.0, 0.03]))
    pm = int(rng.integers(0, 3))
    iT = int(rng.integers(len(UPS))); iS = int(rng.integers(len(DNS)))
    iB = int(rng.integers(-1, len(UPS))); iV = int(rng.integers(-1, len(DNS)))
    tp = UPS[iT]; sl = DNS[iS]; be = UPS[iB] if iB >= 0 else 0.0; sv = DNS[iV] if iV >= 0 else 0.0
    ref = EN.run(B, 'M1', ftf, r, l, off, sl, tp, be, sv, pm)
    kk = (np.searchsorted(B[ftf + '_t'], t, side='right') - 1).astype(np.int64); ph = EN.pivots(B[ftf + '_H'], l, r)
    ej, es, eF, eH = FA.events(O, H, L, C, kk, ph, off, pm)
    bes = np.arange(len(UPS)); svs = np.arange(len(DNS))
    KU, XU, KD, XD, KB, XB, KS, XS = FA.passages(O, H, L, C, BH1, BL1, BH2, BL2, ej, es, eF, UPS, DNS, bes, svs, pm)
    out = np.zeros((len(ej) + 1, 4))
    nt = FA.trades_one(ej, es, eF, iT, iS, iB, iV, KU, XU, KD, XD, KB, XB, KS, XS, bes, svs, out); f = out[:nt]
    ok = len(f) == len(ref)
    if ok and nt:
        ok = (np.array_equal(ej[f[:, 0].astype(int)], ref[:, 0].astype(int)) and np.array_equal(eF[f[:, 0].astype(int)], ref[:, 1]) and
              np.array_equal((f[:, 1].astype(np.int64) >> 2), ref[:, 2].astype(np.int64)) and np.array_equal(f[:, 2], ref[:, 3]) and np.array_equal(f[:, 3], ref[:, 4]))
    ntr += len(ref)
    if not ok:
        bad += 1
        print('MISMATCH', ftf, r, l, off, 'sl', sl, 'tp', tp, 'be', be, 'sv', sv, '| ref', len(ref), 'fast', len(f))
        n = min(len(f), len(ref))
        for q in range(n):
            a = (ej[int(f[q, 0])], eF[int(f[q, 0])], int(f[q, 1]) >> 2, f[q, 2], f[q, 3]); b_ = tuple(ref[q, [0, 1, 2, 3, 4]])
            if not (a[0] == b_[0] and a[1] == b_[1] and a[2] == b_[2] and a[3] == b_[3] and a[4] == b_[4]):
                print('  first diff at trade', q, 'fast', a, 'ref', b_); break
print('checked', it + 1, 'settings,', ntr, 'trades, mismatches', bad, '| %.0fs' % (time.time() - t0))
