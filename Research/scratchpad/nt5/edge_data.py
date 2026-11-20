"""Data for the 2024 edge workbook: chosen (settings, money rule) picks -> 2024 monthly (one-year path and each month fresh), every year."""
import sys, os, pickle, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stage3 as S3
RC = S3.RC
C = {c[0][:5]: c for f in ('cands_m15.pkl', 'cands_m5.pkl') for c in pickle.load(open(f, 'rb'))}
PICKS = [('M5 D:', 'Off', 'risk', 'Fixed $20 (no recovery)'), ('M5 D:', 'Fibonacci', 'risk', 'Fibonacci (Risk)'),
         ('M5 D:', 'Recover a % of losses per trade', 'risk', 'Recover 50% of losses (Risk)'), ('M5 D:', 'Labouchere', 'profit', 'Labouchere (Profit)'),
         ('M15 B', 'Off', 'risk', 'Fixed $20 (no recovery)'), ('M15 B', 'Martingale (multiply after each loss)', 'risk', 'Martingale (Risk)'),
         ('M5 yo', 'Off', 'risk', 'Fixed $20 (no recovery)'), ('M15 y', 'Off', 'risk', 'Fixed $20 (no recovery)')]
out = []; cache = {}
for key, mode, sb, label in PICKS:
    name, tf, c = C[key]
    if key not in cache: cache[key] = S3.trades_of(tf, c)
    tr = cache[key]
    row = dict(name=name, tf=tf, cfg=c, rule=label, years={}, m24=[], m24fresh=[], n24=0, wr24=0.0)
    for y in range(2021, 2027):
        ty = [x for x in tr if x['t'].year == y]
        r = RC.simulate([S3.tup(x, c['tp']) for x in ty], mode, base=20.0, exitR=c['tp'], start=1000.0, sizeBy=sb)
        ms = sorted({x['t'].month for x in ty}); pos = 0
        for m in ms:
            rm = RC.simulate([S3.tup(x, c['tp']) for x in ty if x['t'].month == m], mode, base=20.0, exitR=c['tp'], start=1000.0, sizeBy=sb)
            pos += rm['net'] > 0
            if y == 2024: row['m24fresh'].append((m, rm['net'], rm['maxDDpct']))
        row['years'][y] = dict(net=r['net'], dd=r['maxDDpct'], ruined=r['ruined'], pos=pos, months=len(ms), n=len(ty))
        if y == 2024:
            trc = []; RC.simulate([S3.tup(x, c['tp']) for x in ty], mode, base=20.0, exitR=c['tp'], start=1000.0, sizeBy=sb, trace=trc)
            mn = collections.OrderedDict((m, 0.0) for m in range(1, 13)); eq = 1000.0
            for x, rk in zip(ty, trc):
                if rk == 'SKIP': continue
                p = rk * x['net']; mn[x['t'].month] += p
            row['m24'] = list(mn.items()); row['n24'] = len(ty); row['wr24'] = sum(x['net'] > 0 for x in ty) / len(ty) if ty else 0
    out.append(row); print(key, label, round(row['years'][2024]['net']), flush=True)
pickle.dump(out, open('edge_data.pkl', 'wb'))
