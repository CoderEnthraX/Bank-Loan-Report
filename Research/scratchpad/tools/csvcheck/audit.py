"""Check every position of a trade list against Crooks C: is each big trade a recovery trade and each recovery trade big, and does its
size match the owed amount (or the leverage limit)? Usage: audit.py FILE exitR tp1rule(0/1)"""
import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/tools/csvcheck')
from load import load
from replay import group, replay
path, exitR, t1 = sys.argv[1], float(sys.argv[2]), sys.argv[3] == '1'
rows = replay(group(load(path)), exitR)
bad = []; nrec = ncap = 0; forgot = []; worst = 0.0
for i, r in enumerate(rows):
    p = r['parts']; gross = sum(t['qty'] * abs(t['exit_px'] - t['entry_px']) for t in p)
    worst = max(worst, r['owed'])
    if r['rec']:
        nrec += 1
        target = max(50.0, r['owed']) if t1 else max(50.0, r['owed'] / exitR)       # TP1 rule: a stop-out loses the owed amount
        capped = r['val'] >= 0.99 * r['levcap']
        ncap += capped
        if t1:
            got = p[0]['pnl'] if (len(p) == 2 and p[0]['pnl'] > 0) else -r['pnl'] if r['pnl'] < 0 else None    # banked at TP1, or the stop-out loss
            okSize = len(p) == 2 and (got is None or 0.8 * target <= got <= 1.2 * target)
        else:
            exp_gross = target if r['pnl'] < 0 else target * 1.0                       # a stop-out or a TP2 exit is 1R
            okSize = capped or 0.85 * target <= gross <= 1.15 * target
        if not okSize: bad.append((r['k'], 'recovery size', round(r['owed']), round(gross), len(p)))
        if r['pnl'] > 0 and r['owed'] - r['pnl'] > 0.01: forgot.append((r['k'], r['nums'][0], round(r['owed']), round(r['pnl']), round(r['owed'] - r['pnl']), capped))
    else:
        if len(p) > 1 or gross > 1.3 * 50: bad.append((r['k'], 'base trade too big', round(r['owed']), round(gross), len(p)))
print('%s: %d positions (%d rows), %d recovery trades, %d of them cut by the leverage limit; largest owed $%.0f; end P&L $%.0f' % (
    path.split('/')[-2], len(rows), sum(len(r['parts']) for r in rows), nrec, ncap, worst, sum(r['pnl'] for r in rows)))
print('positions that do not follow the rule:', bad[:15], '(total %d)' % len(bad))
print('winning recovery trades that left part of the loss (forgotten by the new cycle): %d, total $%.0f' % (len(forgot), sum(f[4] for f in forgot)))
for f in sorted(forgot, key=lambda f: -f[4])[:6]: print('   position %d (trade #%d): owed $%d, won $%d, forgotten $%d, leverage-capped %s' % f)
base = [r for r in rows if not r['rec'] and len(r['parts']) == 1]
L = [-r['pnl'] for r in base if r['pnl'] < -20]; W = [r['pnl'] for r in base if r['pnl'] > 10]
print('base trades: average loss $%.1f (%d), average win $%.1f (%d)' % (sum(L) / len(L), len(L), sum(W) / len(W), len(W)))
comm = [t['comm'] / t['qty'] for r in rows for t in r['parts'] if t['qty'] > 0]
print('commission per unit in the list: %.3f to %.3f' % (min(comm), max(comm)))
