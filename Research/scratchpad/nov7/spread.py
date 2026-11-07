"""Implied FxPro spread at order time: EA target = engine TP1 (entry +/- 0.6R) +/- (commission/100 + live spread) with earn-back on."""
import sys, statistics
from openpyxl import load_workbook
ws = load_workbook(sys.argv[1], read_only=True, data_only=True).worksheets[0]
sec = None; orders = {}; closes = []
for row in ws.iter_rows(values_only=True):
    v = [x for x in row if x not in (None, '')]
    if not v: continue
    if len(v) == 1 and v[0] in ('Orders', 'Deals'): sec = v[0]; continue
    if sec == 'Orders' and v[0] != 'Open Time':
        if 'limit' in str(v[3]): orders[v[1]] = dict(side=v[3], px=float(v[5]), sl=float(v[6]), state=v[8])
        elif str(v[-1]).startswith('tp '): closes.append((v[1], float(str(v[-1])[3:])))
sp = []
for oid, tp in closes:
    o = orders.get(oid - 1)
    if not o: continue
    d = 1 if o['side'].startswith('buy') else -1
    R = abs(o['px'] - o['sl']); lvl = o['px'] + d * 0.6 * R
    s = d * (tp - lvl) - 0.16 / 100
    sp.append(s)
print('trades closed at the target: %d | implied spread at order time: median %.3f, mean %.3f, min %.3f, max %.3f' % (len(sp), statistics.median(sp), statistics.mean(sp), min(sp), max(sp)))
print(sorted(round(x, 2) for x in sp))
