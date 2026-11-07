"""Classify every TV trade and EA order (6 Oct - 6 Nov 2026) by the time windows of each platform's settings.
Usage: classify.py TV.csv REPORT.xlsx"""
import sys, datetime as dt
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/tools/csvcheck')
from load import load
from openpyxl import load_workbook
H = dt.timedelta(hours=1); M5 = dt.timedelta(minutes=5)
EU_END = dt.datetime(2026, 10, 25, 1, 0)   # UTC: EU (UK, FxPro) summer time ends
US_END = dt.datetime(2026, 11, 1, 6, 0)    # UTC: New York summer time ends
def fx_utc(srv):                            # FxPro server (EET/EEST) -> UTC
    u = srv - 3 * H
    return u if u < EU_END else srv - 2 * H
def ea_utc(srv):                            # what the EA thinks with InpServerTz = 0 (US rule, by server date)
    return srv - (3 if srv.date() < dt.date(2026, 11, 1) else 2) * H
ist = lambda u: u + dt.timedelta(hours=5, minutes=30)
mins = lambda t: t.hour * 60 + t.minute
def kz(m, utc, auto, lc):
    lon = 60 if auto and utc >= EU_END else 0; ny = 60 if auto and utc >= US_END else 0
    z = []
    if 330 <= m < 570: z.append('Asia')
    if 690 + lon <= m < 870 + lon: z.append('London')
    if 990 + ny <= m < 1170 + ny: z.append('NY')
    if lc and 1170 + lon <= m < 1290 + lon: z.append('LondonClose')
    return z
def news(m, utc, start, dur, pre=60):       # daily window that keeps New York time (winter: 1 hour later)
    s = start + (60 if utc >= US_END else 0); e = s + dur
    return (s - pre) <= m < e
TV = dict(auto=True, lc=False, ns=17 * 60 + 45, nd=30, maxf=10)
EA = dict(auto=False, lc=True, ns=17 * 60 + 55, nd=75, maxf=5)
def flags(cfg, user_t, utc):
    m = mins(user_t); z = kz(m, utc, cfg['auto'], cfg['lc'])
    return ('KZ ' + '+'.join(z) if z else 'outside kill zones') + (' | NEWS-BLOCK' if news(m, utc, cfg['ns'], cfg['nd']) else '')
tv = load(sys.argv[1])
wb = load_workbook(sys.argv[2], read_only=True, data_only=True); ws = wb.worksheets[0]
orders = []; sec = None
for row in ws.iter_rows(values_only=True):
    v = [x for x in row if x not in (None, '')]
    if not v: continue
    if len(v) == 1 and v[0] in ('Orders', 'Deals'): sec = v[0]; continue
    if sec == 'Orders' and v[0] != 'Open Time' and 'limit' in str(v[3]):
        t = dt.datetime.strptime(str(v[0]), '%Y.%m.%d %H:%M:%S')
        orders.append(dict(t=t, side=v[3], vol=v[4], px=float(v[5]), sl=float(v[6]), done=dt.datetime.strptime(str(v[7]), '%Y.%m.%d %H:%M:%S'), state=v[8]))
print('EA ORDERS (armed setups). Signal bar = the bar before the order. Times in India time.')
fills = {}
for o in orders:
    u = fx_utc(o['t']); real = ist(u); eat = ist(ea_utc(o['t']))
    sig_u = u - M5
    d = real.date(); fills.setdefault(d, 0)
    if o['state'] == 'filled': fills[d] += 1
    k = (o['t'] - fx_utc(o['t'])).total_seconds() / 3600
    print('  %s IST (EA clock %s) %-10s %-9s %8.2f stop %8.2f dist %5.2f %-8s ends %s | TV rules: %s | EA rules: %s%s' % (
        real.strftime('%m-%d %H:%M'), eat.strftime('%H:%M'), o['side'], o['vol'], o['px'], o['sl'], abs(o['px'] - o['sl']), o['state'],
        ist(fx_utc(o['done'])).strftime('%H:%M'), flags(TV, ist(sig_u), sig_u), flags(EA, ist(ea_utc(o['t'] - M5)), ea_utc(o['t'] - M5)),
        '  [EA day fill #%d]' % fills[d] if o['state'] == 'filled' else ''))
print('\nTV TRADES. Signal bar = 1 to 5 bars before the fill; flags for the bar just before the fill and 5 bars before.')
day = {}
for t in tv:
    f = dt.datetime.strptime(t['entry_time'], '%Y-%m-%d %H:%M'); u = f - dt.timedelta(hours=5, minutes=30)
    day[f.date()] = day.get(f.date(), 0) + 1
    print('  #%-2d %s %s %8.2f qty %3.0f %+8.2f | TV day fill #%d | sig bar -1: TV %s / EA %s | -5: TV %s / EA %s' % (
        t['n'], f.strftime('%m-%d %H:%M'), 'L' if t['dir'] > 0 else 'S', t['entry_px'], t['qty'], t['pnl'], day[f.date()],
        flags(TV, f - M5, u - M5), flags(EA, f - M5 - (H if EU_END <= u < US_END else dt.timedelta(0)), u - M5),
        flags(TV, f - 5 * M5, u - 5 * M5), flags(EA, f - 5 * M5 - (H if EU_END <= u < US_END else dt.timedelta(0)), u - 5 * M5)))
