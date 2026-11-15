"""The trades where TradingView (broker model) has the same entry as the rules but another exit: show both, and the entry candle."""
import sys, datetime as dt
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fractal')
import sync_why as SW, pine_twin2 as TW, engine as EN
from final11 import ALL12
for arg in sys.argv[1:]:
    ctf, k = arg.split(':'); k = int(k) - 1
    mt, tt, (t, utc) = SW.run_tag(ctf, k, TW.P())
    O, H, L, C = EN.chart(SW.B, ctf)[1:]
    byE = {(x[0], round(x[1], 6)): x for x in mt}; key = lambda x: (x[0], round(x[1], 6), x[2], round(x[3], 6)); ms = set(key(x) for x in mt)
    for x in tt:
        if key(x) in ms or x[6] == 'catch-up' or x[5] == 'close': continue
        m = byE.get((x[0], round(x[1], 6)))
        if m is None: continue
        e = x[0]; E = ALL12[k]
        print('%s S%d entry bar %d %s F %.3f | rules exit bar %d at %.3f (%s) | TradingView exit bar %d at %.3f (%s, %s) | entry candle O %.3f H %.3f L %.3f C %.3f, prev C %.3f' % (
            ctf, k + 1, e, dt.datetime.fromtimestamp(int(utc[e]), dt.timezone.utc), x[1], m[2], m[3], SW.RS[m[4]], x[2], x[3], x[5], x[7], O[e], H[e], L[e], C[e], C[e - 1]))
