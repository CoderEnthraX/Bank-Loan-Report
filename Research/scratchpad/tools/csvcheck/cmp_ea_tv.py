"""Match a TradingView strategy trade list (CSV, chart time zone) with an MT5 Strategy Tester report (xlsx, server time) trade by trade.
Usage: cmp_ea_tv.py TV.csv REPORT.xlsx TV_TZ_HOURS SERVER_SUMMER SERVER_WINTER US_DST_END(YYYY-MM-DD)"""
import sys, datetime as dt
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/tools/csvcheck')
from load import load
from replay import group
from openpyxl import load_workbook
def ea_positions(path):
    wb = load_workbook(path, read_only=True, data_only=True); ws = wb.worksheets[0]
    rows = [[v for v in r] for r in ws.iter_rows(values_only=True)]
    sec = None; deals = []
    for row in rows:
        vals = [v for v in row if v is not None]
        if not vals: continue
        if len(vals) == 1 and vals[0] in ('Orders', 'Deals'): sec = vals[0]; continue
        if sec == 'Deals' and vals[0] != 'Time' and len(vals) >= 12 and vals[2] == 'GOLD':
            deals.append(dict(t=dt.datetime.strptime(str(vals[0]), '%Y.%m.%d %H:%M:%S'), side=vals[3], dirn=vals[4], vol=float(vals[5]), px=float(vals[6]),
                              comm=float(vals[8]), profit=float(vals[10]), comment=str(vals[12]) if len(vals) > 12 else ''))
    pos = []; cur = None
    for d in deals:
        if d['dirn'] == 'in':
            cur = dict(t=d['t'], dir=1 if d['side'] == 'buy' else -1, px=d['px'], lots=d['vol'], left=d['vol'], net=d['comm'], exits=[]); pos.append(cur)
        elif cur is not None:
            cur['exits'].append(d); cur['left'] = round(cur['left'] - d['vol'], 8); cur['net'] += d['profit'] + d['comm']
    return pos, deals
if __name__ == '__main__':
    tvp, rp, tvtz, ssum, swin, dstend = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), dt.datetime.strptime(sys.argv[6], '%Y-%m-%d')
    tv = [p for p in group(load(tvp))]
    ea, deals = ea_positions(rp)
    def ea_to_tv(t):                        # server time -> UTC -> TradingView chart time
        off = ssum if t < dstend else swin
        return t - dt.timedelta(hours=off) + dt.timedelta(hours=tvtz)
    for p in ea: p['tvt'] = ea_to_tv(p['t'])
    used = set(); pairs = []
    for i, p in enumerate(tv):
        t0 = dt.datetime.strptime(p[0]['entry_time'], '%Y-%m-%d %H:%M'); d = p[0]['dir']
        best = None
        for j, e in enumerate(ea):
            if j in used or e['dir'] != d: continue
            lag = (e['tvt'] - t0).total_seconds() / 60.0
            if -1 <= lag < 10 and abs(e['px'] - p[0]['entry_px']) < 3.0:
                if best is None or abs(lag) < abs(best[1]): best = (j, lag)
        if best: used.add(best[0]); pairs.append((i, best[0]))
        else: pairs.append((i, None))
    print('TradingView positions %d (rows %d) | EA positions %d (closing deals %d)' % (len(tv), sum(len(p) for p in tv), len(ea), sum(len(e['exits']) for e in ea)))
    print('TradingView: %s to %s | EA: %s to %s (chart time)' % (tv[0][0]['entry_time'], tv[-1][0]['entry_time'], ea[0]['tvt'], ea[-1]['tvt']))
    m = [(i, j) for i, j in pairs if j is not None]
    print('same trade (same direction, entry within one bar and $3): %d' % len(m))
    rows = []
    for i, j in pairs:
        p = tv[i]; t = p[0]; tvnet = sum(x['pnl'] for x in p); tvoz = sum(x['qty'] for x in p)
        if j is None:
            rows.append('  TV #%-3d %s %s %8.2f %4.0f oz  P&L %+8.2f | EA: no trade' % (t['n'], t['entry_time'], 'L' if t['dir'] > 0 else 'S', t['entry_px'], tvoz, tvnet)); continue
        e = ea[j]
        exs = ', '.join('%s %.2f' % (x['comment'].split(' ')[0] if x['comment'] else 'close', x['vol']) for x in e['exits'])
        same = (tvnet > 0) == (e['net'] > 0)
        rows.append('  TV #%-3d %s %s %8.2f %4.0f oz  P&L %+8.2f | EA %s %8.2f %.2f lot P&L %+8.2f exits [%s] %s' % (
            t['n'], t['entry_time'], 'L' if t['dir'] > 0 else 'S', t['entry_px'], tvoz, tvnet, e['tvt'].strftime('%m-%d %H:%M'), e['px'], e['lots'], e['net'], exs, '' if same else '<< result differs'))
    for j, e in enumerate(ea):
        if j not in used:
            rows.append('  EA only: %s %s %8.2f %.2f lot P&L %+8.2f exits %s' % (e['tvt'].strftime('%Y-%m-%d %H:%M'), 'L' if e['dir'] > 0 else 'S', e['px'], e['lots'], e['net'],
                        [(x['comment'], x['vol']) for x in e['exits']]))
    print('\n'.join(rows))
    sw = sum(1 for i, j in m if (sum(x['pnl'] for x in tv[i]) > 0) == (ea[j]['net'] > 0))
    print('matched trades with the same result (win / loss): %d of %d' % (sw, len(m)))
    print('net: TradingView %+.2f (all %d), EA %+.2f (all %d)' % (sum(x['pnl'] for p in tv for x in p), len(tv), sum(e['net'] for e in ea), len(ea)))
