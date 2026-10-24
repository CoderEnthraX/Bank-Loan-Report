import sys, datetime, collections, statistics
p = sys.argv[1]
rows = []
with open(p, newline='') as f:
    next(f)
    for ln in f:
        a = ln.rstrip('\r\n').split('\t')
        t = datetime.datetime.strptime(a[0] + ' ' + a[1], '%Y.%m.%d %H:%M:%S')
        rows.append((t, float(a[2]), float(a[3]), float(a[4]), float(a[5]), int(a[6]), int(a[7]), int(a[8])))
print('bars', len(rows), rows[0][0], '->', rows[-1][0])
# decimals / tick
dec = collections.Counter(len(str(r[4]).split('.')[1]) if '.' in str(r[4]) else 0 for r in rows[:200000]); print('close decimals', dec.most_common(3))
# monotonic time, duplicates
bad = sum(1 for i in range(1, len(rows)) if rows[i][0] <= rows[i - 1][0]); print('non-increasing timestamps', bad)
# anomalies: range vs median range of the day
rng = [r[2] - r[3] for r in rows]; med = statistics.median(rng)
big = [(rows[i][0], round(rng[i], 2), rows[i][5]) for i in range(len(rows)) if rng[i] > 40 * med]
print('median 1m range', round(med, 3), 'bars with range > 40x median:', len(big), big[:12])
tv = [r[5] for r in rows]; mtv = statistics.median(tv)
bigtv = [(rows[i][0], rows[i][5]) for i in range(len(rows)) if rows[i][5] > 50 * mtv]; print('median tickvol', mtv, 'tickvol > 50x median:', len(bigtv), bigtv[:10])
# daily first/last bar time and intraday gaps > 5 minutes (server time)
byday = collections.defaultdict(list)
for r in rows: byday[r[0].date()].append(r[0])
firsts = collections.Counter(v[0].strftime('%H:%M') for v in byday.values()); lasts = collections.Counter(v[-1].strftime('%H:%M') for v in byday.values())
print('first bar of day', firsts.most_common(6)); print('last bar of day', lasts.most_common(6))
gaps = collections.Counter()
for i in range(1, len(rows)):
    dt = (rows[i][0] - rows[i - 1][0]).total_seconds() / 60
    if 5 < dt < 600 and rows[i][0].date() == rows[i - 1][0].date(): gaps[(rows[i - 1][0].strftime('%H:%M'), rows[i][0].strftime('%H:%M'))] += 1
print('intraday gaps > 5 min (from, to):', gaps.most_common(8))
# weekday of days
print('weekdays', collections.Counter(d.strftime('%a') for d in byday))
# per year bars and spread
for y in range(2021, 2027):
    ys = [r for r in rows if r[0].year == y]
    if ys: print(y, 'bars', len(ys), 'median spread pts', statistics.median(r[7] for r in ys), 'median 1m range', round(statistics.median(r[2] - r[3] for r in ys), 3))
# DST check: in mid-March and early November weeks, when does the daily session start (first bar after the longest gap)?
for d0 in ('2021-03-08', '2021-03-15', '2021-03-29', '2021-10-25', '2021-11-01', '2021-11-08', '2024-03-11', '2024-03-25', '2024-10-28', '2024-11-04'):
    d = datetime.date.fromisoformat(d0); v = byday.get(d)
    print(d0, d.strftime('%a'), 'first', v[0].strftime('%H:%M') if v else None, 'last', v[-1].strftime('%H:%M') if v else None, 'bars', len(v) if v else 0)
