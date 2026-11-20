"""Every year 2021-2026 (one year from $1,000 and every month fresh) for chosen (settings, money rule) pairs. Output allyears.txt"""
import sys, os, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stage3 as S3
RC = S3.RC
C = {c[0][:5]: c for f in ('cands_m15.pkl', 'cands_m5.pkl') for c in pickle.load(open(f, 'rb'))}
PAIRS = [('M5 D:', 'Off', 'risk', 1), ('M5 D:', 'Labouchere', 'profit', 1), ('M5 D:', 'Labouchere', 'risk', 1), ('M5 D:', 'Step-up (+$ per loss in a row)', 'risk', 1),
         ('M5 D:', 'Fibonacci', 'risk', 1), ('M5 D:', 'Recover a % of losses per trade', 'risk', 1), ('M5 D:', 'Fibonacci', 'profit', 1), ('M5 D:', 'C3', 'risk', 1),
         ('M5 E:', 'Off', 'risk', 1), ('M5 E:', 'Step-up (+$ per loss in a row)', 'profit', 1), ('M5 E:', 'Labouchere', 'profit', 1), ('M5 F:', 'Off', 'risk', 1), ('M5 F:', 'Fibonacci', 'profit', 1)]
L = ['one year from $1,000 per year (max drawdown) | months fresh from $1,000: profitable / total']
cache = {}
for key, mode, sb, cn in PAIRS:
    name, tf, c = C[key]
    if key not in cache: cache[key] = S3.trades_of(tf, c)
    tr = cache[key]; parts = []; mp = mt = 0
    for y in range(2021, 2027):
        ty = [S3.tup(x, c['tp']) for x in tr if x['t'].year == y]
        r = RC.simulate(ty, mode, base=20.0, exitR=c['tp'], start=1000.0, cN=cn, sizeBy=sb)
        ms = sorted({x['t'].month for x in tr if x['t'].year == y}); pos = 0
        for m in ms:
            rm = RC.simulate([S3.tup(x, c['tp']) for x in tr if x['t'].year == y and x['t'].month == m], mode, base=20.0, exitR=c['tp'], start=1000.0, cN=cn, sizeBy=sb)
            pos += rm['net'] > 0
        mp += pos; mt += len(ms)
        parts.append('%d %+6.0f (%2.0f%%) %2d/%2d' % (y, r['net'], 100 * r['maxDDpct'], pos, len(ms)))
    L.append('%s | %-38s %-6s | %s | all months %d/%d' % (key, mode[:38], sb, ' | '.join(parts), mp, mt))
open('allyears_m5.txt', 'w').write('\n'.join(L)); print('\n'.join(L))
