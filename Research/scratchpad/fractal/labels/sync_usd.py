"""$ of the next-open exits of S11 (TradingView emulation) against the rules' own exit of the same trade."""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fractal')
import sync_why as SW, pine_twin2 as TW
COMM = 0.115
for ctf in sys.argv[1:]:
    mt, tt, _ = SW.run_tag(ctf, 10, TW.P())
    byEntry = {(a[0], round(a[1], 9)): a for a in mt}
    tvU = mdU = 0.0; n = 0; worst = best = 0.0
    for a in tt:
        if a[5] != 'close' or a[7] in ('TIME', 'WKND'): continue
        m = byEntry.get((a[0], round(a[1], 9)))
        u = a[4] * (a[3] - a[1]) - 2 * COMM * a[4]; tvU += u; n += 1; worst = min(worst, u); best = max(best, u)
        if m is not None: mdU += a[4] * (m[3] - m[1]) - 2 * COMM * a[4]
    print('chart %-3s: %d next-open exits, TradingView $ %+.0f (worst %+.0f, best %+.0f) vs the rules $ %+.0f for the same trades' % (ctf, n, tvU, worst, best, mdU))
