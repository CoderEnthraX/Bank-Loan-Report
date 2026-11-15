"""Trades per strategy and year, and in the last 365 days of the data, on a given chart timeframe (the indicator's rules)."""
import sys, numpy as np, datetime as dt
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fractal')
import engine as EN
from final11 import ALL12
B = EN.load()
for ctf in sys.argv[1:]:
    t = EN.chart(B, ctf)[0]; tEnd = int(t[-1]); t365 = tEnd - 365 * 86400
    print('chart %s (data to %s): trades per year 2021 ... 2026 (to Oct) | last 365 days: trades, TP / SL / BE / SALV' % (ctf, dt.datetime.fromtimestamp(tEnd, dt.timezone.utc).date()))
    for k, p in enumerate(ALL12, 1):
        if EN.TF_SEC[p[0]] < EN.TF_SEC[ctf]:
            print('  S%-2d %-3s needs a chart of %s or lower' % (k, p[0], p[0])); continue
        tr = EN.run(B, ctf, *p)
        yr = np.array([dt.datetime.fromtimestamp(int(t[int(i)]), dt.timezone.utc).year for i in tr[:, 0]])
        last = tr[np.array([int(t[int(i)]) >= t365 for i in tr[:, 0]])] if len(tr) else tr
        rs = np.bincount(last[:, 4].astype(int), minlength=5) if len(last) else [0] * 5
        print('  S%-2d %-3s R%-2d L%-3d | %s | last 365 d: %3d trades  TP %d SL %d BE %d SALV %d' % (k, p[0], p[1], p[2], ' '.join('%4d' % (yr == y).sum() for y in range(2021, 2027)), len(last), rs[1], rs[2], rs[3], rs[4]))
