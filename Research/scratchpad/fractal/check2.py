"""engine2.sim2 with every setting off == engine.sim, trade for trade (random settings, M1 and M5, all path modes)."""
import sys, numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fractal')
import engine as EN, engine2 as E2
B = EN.load(); rng = np.random.default_rng(int(sys.argv[1])); bad = 0; ntr = 0
for it in range(int(sys.argv[2])):
    ctf = str(rng.choice(['M1', 'M5'])); ftf = str(rng.choice(['M5', 'M15', 'H1', 'H4', 'D1'])); pm = int(rng.integers(0, 3))
    p = (ftf, int(rng.integers(1, 30)), int(rng.integers(1, 40)), float(rng.choice([-0.2, -0.05, 0.0, 0.02])), float(rng.choice([0.1, 0.3, 1.0, 3.0])),
         float(rng.choice([0.1, 0.3, 1.0, 3.0])), float(rng.choice([0.0, 0.05, 0.2, 0.5])), float(rng.choice([0.0, 0.1, 0.5, 1.0])))
    a = EN.run(B, ctf, *p, pm=pm); b = E2.run2(B, ctf, *p, pm=pm); ntr += len(a)
    if a.shape != b.shape or not np.array_equal(a, b):
        bad += 1; print('DIFF', ctf, p, pm, len(a), len(b))
print('checked', it + 1, 'settings,', ntr, 'trades, differences', bad)
