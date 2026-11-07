"""Crooks C ledger of both platforms from their own trade results: owed before each trade, base / recovery, size, P&L; and P&L per day.
Usage: ledger.py TV.csv REPORT.xlsx"""
import sys, datetime as dt, collections
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/tools/csvcheck')
from load import load
from cmp_ea_tv import ea_positions
EU_END = dt.datetime(2026, 10, 25, 4, 0)
ist = lambda t: t - dt.timedelta(hours=3 if t < EU_END else 2) + dt.timedelta(hours=5, minutes=30)
tv = [(dt.datetime.strptime(t['entry_time'], '%Y-%m-%d %H:%M'), t['dir'], t['entry_px'], t['qty'] / 100.0, t['pnl']) for t in load(sys.argv[1])]
ea = [(ist(p['t']).replace(second=0), p['dir'], p['px'], p['lots'], p['net']) for p in ea_positions(sys.argv[2])[0]]
def crooks(trs):
    owed, won, out = 0.0, False, []
    for t, d, px, lots, pnl in trs:
        rec = won and owed > 0.005
        out.append((t, d, px, lots, pnl, owed, rec))
        owed = max(0.0, owed - pnl)
        if rec and pnl > 0 and owed < 0.01: owed = 0.0
        won = pnl > 0
    return out
A, B = crooks(tv), crooks(ea)
days = sorted({x[0].date() for x in A} | {x[0].date() for x in B})
print('%-6s %10s %10s %10s   biggest trades that day (R = Crooks C recovery trade)' % ('day', 'TV P&L', 'EA P&L', 'EA - TV'))
ct = ce = 0
for d in days:
    a = [x for x in A if x[0].date() == d]; b = [x for x in B if x[0].date() == d]
    pa = sum(x[4] for x in a); pb = sum(x[4] for x in b); ct += pa; ce += pb
    big = lambda xs, tag: ['%s %s%s %.2f %+.0f' % (tag, x[0].strftime('%H:%M'), ' R' if x[6] else '', x[3], x[4]) for x in xs if abs(x[4]) > 60 or x[6]]
    print('%-6s %+10.2f %+10.2f %+10.2f   %s' % (d.strftime('%m-%d'), pa, pb, pb - pa, '; '.join(big(a, 'TV') + big(b, 'EA'))))
print('total  %+10.2f %+10.2f %+10.2f' % (ct, ce, ce - ct))
rt = [x for x in A if x[6]]; re_ = [x for x in B if x[6]]
print('recovery trades: TV %d (won %d, net %+.2f) | EA %d (won %d, net %+.2f)' % (len(rt), sum(x[4] > 0 for x in rt), sum(x[4] for x in rt), len(re_), sum(x[4] > 0 for x in re_), sum(x[4] for x in re_)))
print('base trades:     TV %d (net %+.2f) | EA %d (net %+.2f)' % (len(A) - len(rt), sum(x[4] for x in A if not x[6]), len(B) - len(re_), sum(x[4] for x in B if not x[6])))
