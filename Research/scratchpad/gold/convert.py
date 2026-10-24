"""FxPro MT5 GOLD M1 export -> clean M1, M5, M15, H1 bars (server-clock aligned, like MT5 builds them).
Drops the fake 00:00 'daily summary' bars. Server clock = EET: UTC+3 from the last Sunday of March to the last Sunday of October."""
import sys, datetime, pickle, statistics
SRC, OUT = sys.argv[1], sys.argv[2]
def last_sunday(y, m):
    d = datetime.date(y, m + 1, 1) - datetime.timedelta(days=1) if m < 12 else datetime.date(y, 12, 31)
    while d.weekday() != 6: d -= datetime.timedelta(days=1)
    return d
def srv_offset(t):   # EU DST switches at 01:00 UTC = 03:00 / 04:00 server; at day resolution is enough here (markets are closed on Sundays)
    y = t.year; a, b = last_sunday(y, 3), last_sunday(y, 10)
    return 3 if a <= t.date() < b else 2
raw = []
with open(SRC, newline='') as f:
    next(f)
    for ln in f:
        a = ln.rstrip('\r\n').split('\t')
        raw.append((datetime.datetime.strptime(a[0] + ' ' + a[1], '%Y.%m.%d %H:%M:%S'), float(a[2]), float(a[3]), float(a[4]), float(a[5]), int(a[6]), int(a[8])))
# fake daily-summary bars: an isolated 00:00 bar (next bar >= 30 min later) or any bar with > 50x the median tick volume
mtv = statistics.median(r[5] for r in raw)
drop = set()
for i, r in enumerate(raw):
    if r[5] > 50 * mtv: drop.add(i)
    if r[0].hour == 0 and r[0].minute == 0 and i + 1 < len(raw) and (raw[i + 1][0] - r[0]).total_seconds() >= 1800: drop.add(i)
m1 = [r for i, r in enumerate(raw) if i not in drop]
print('raw', len(raw), 'dropped', len(drop), 'kept', len(m1))
def agg(bars, mins):
    out = []; cur = None
    for (t, o, h, l, c, v, sp) in bars:
        k = t.replace(minute=(t.minute // mins) * mins, second=0) if mins < 60 else t.replace(minute=0, second=0)
        if cur is None or k != cur[0]:
            if cur: out.append(tuple(cur[:6]) + (cur[6] / cur[7],))
            cur = [k, o, h, l, c, v, sp, 1]
        else:
            cur[2] = max(cur[2], h); cur[3] = min(cur[3], l); cur[4] = c; cur[5] += v; cur[6] += sp; cur[7] += 1
    if cur: out.append(tuple(cur[:6]) + (cur[6] / cur[7],))
    return out
for tf, mins in (('M1', 1), ('M5', 5), ('M15', 15), ('H1', 60)):
    b = m1 if mins == 1 else agg(m1, mins)
    utc = [t - datetime.timedelta(hours=srv_offset(t)) for (t, *_ ) in b]
    pickle.dump(dict(srv=[x[0] for x in b], utc=utc, O=[x[1] for x in b], H=[x[2] for x in b], L=[x[3] for x in b], C=[x[4] for x in b],
                     TV=[x[5] for x in b], SP=[x[6] for x in b]), open('%s/%s.pkl' % (OUT, tf), 'wb'), protocol=4)
    print(tf, 'bars', len(b), b[0][0], '->', b[-1][0])
