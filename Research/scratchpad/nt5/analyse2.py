"""Rank stage 1: 2024 total R (fixed risk), with 2023 / 2025 / all-years as the honesty check. Run: python3 -I analyse1.py TF [top]"""
import sys, pickle
TF = sys.argv[1]; TOP = int(sys.argv[2]) if len(sys.argv) > 2 else 15
D = [d for d in pickle.load(open('stage2_%s.pkl' % TF, 'rb')) if d[1]]
def key(c): return '%s ' % c.get('dirn', 'both') + 'tp %.1f stop %.1f %s %d chop %s hrs %s kz %s %s vw %s mom %.2f %s' % (c['tp'], c['stopAtr'], c['entryMode'], c['entryPct'], c['chop'], c['hours'], c['kz'], c['days'], c['vw'], c['momAtr'], c['mv'])
rows = []
for c, r, e in D:
    y = r['years']; n24 = y[2024]['n']
    if n24 < 20: continue
    pm = sum(v > 0 for v in r['m24'].values())
    rows.append((y[2024]['sumR'], y[2024]['exp'], n24, y[2024]['wr'], pm, len(r['m24']), y[2023]['sumR'], y[2025]['sumR'], sum(y[k]['sumR'] for k in y), c))
print('%s: %d settings run, %d with >= 20 trades in 2024; 2024 positive: %d; 2023 and 2024 and 2025 positive: %d; every year 2021-2026 positive: %d' % (
    TF, len(D), len(rows), sum(r[0] > 0 for r in rows), sum(r[0] > 0 and r[6] > 0 and r[7] > 0 for r in rows),
    sum(all(dict(D[0][1]['years'])) and all(v['sumR'] > 0 for v in x[1]['years'].values() if v['n']) for x in D if x[1]['years'][2024]['n'] >= 20 for _ in [0])))
print('rank by 2024 total R | 2024: R/trade, trades, win rate, profitable months | 2023 R | 2025 R | 2021-26 R | settings')
for r in sorted(rows, key=lambda r: -r[0])[:TOP]:
    print('%+7.1fR %+.3f %4d %4.0f%% %2d/%2d | %+6.1f | %+6.1f | %+7.1f | %s' % (r[0], r[1], r[2], 100 * r[3], r[4], r[5], r[6], r[7], r[8], key(r[9])))
print('-- robust (2023, 2024, 2025 all positive), by 2024:')
for r in sorted([r for r in rows if r[6] > 0 and r[7] > 0], key=lambda r: -r[0])[:TOP]:
    print('%+7.1fR %+.3f %4d %4.0f%% %2d/%2d | %+6.1f | %+6.1f | %+7.1f | %s' % (r[0], r[1], r[2], 100 * r[3], r[4], r[5], r[6], r[7], r[8], key(r[9])))
print('-- best 2024 result per target (R):')
for tp in sorted({r[9]['tp'] for r in rows}):
    b = max([r for r in rows if r[9]['tp'] == tp], key=lambda r: r[0])
    print('  tp %.1f: %+7.1fR (%+.3f/trade, %d trades, %d/%d months) | 2023 %+.1f 2025 %+.1f | %s' % (tp, b[0], b[1], b[2], b[4], b[5], b[6], b[7], key(b[9])))
