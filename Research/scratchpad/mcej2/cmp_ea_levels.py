"""EA simulator trades priced at the EA's OWN ORDER levels (limit price incl. the bid-chart spread shift, SL / TP levels; the actual price for an
EA close) with the $7 per lot commission (0.07 per oz), against the TradingView model (mid prices, 0.23 per oz). Usage: cmp_ea_levels.py LOG SETUP EXIT"""
import sys, re, pickle, datetime as dt
log, setup, ex = sys.argv[1], sys.argv[2], int(sys.argv[3])
src = open('cmp_ea.py').read().split("U = pickle.load")[0]
sys.argv = ['x', log, setup, str(ex)]; exec(src)
orders = {}
for ln in open(log):
    if ln.startswith('SIM ORDER'):
        m = re.match(r'SIM ORDER \S+ \S+ tk=(\d+) type=\d+ vol=[\d.]+ px=([\d.]+)', ln); orders[int(m.group(1))] = float(m.group(2))
U = pickle.load(open(S + '/mcej2/user_trades.pkl', 'rb'))[('M5', setup, ex)]['trades']
B = {(x['dir'], x['t'] - dt.timedelta(minutes=330)): x for x in U}
def bar(t): return t.replace(minute=t.minute - t.minute % 5, second=0)
n = 0; s_lvl = s_tv = s_book = 0.0; spr = []
for pid in order:
    p = pos[pid]
    if 'tx' not in p or pid not in orders: continue
    x = B.get((p['d'], bar(p['t'])))
    if x is None: continue
    n += 1; rp = x['rp']; e = orders[pid]
    lvl = p['tp'] if p['why'] == 'target' else p['sl'] if p['why'] == 'stop' else p['xpx']
    s_lvl += (p['d'] * (lvl - e) - 0.07) / (rp + 0.23)
    s_tv += (x['R'] - x['c']) / (1 + x['c']); s_book += p['Rn']
    spr.append(p['d'] * (e - x['fpx']) if p['d'] > 0 else -(e - x['fpx']))
spr.sort()
print('%s TP%d: matched %d | net R: EA as booked (sim fills, no commission) %+.1f | EA at its order levels + $7/lot commission %+.1f | TradingView model %+.1f | EA limit minus TV limit: median %+.3f, mean %+.3f' % (
    setup, ex, n, s_book, s_lvl, s_tv, spr[len(spr) // 2], sum(spr) / len(spr)))
