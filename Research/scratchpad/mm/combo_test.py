"""5 combination money rules (zone-based: one rule above the start / at the best, another below it or in a drawdown), every one with a
safety brake (no trade risks more than 3% of the equity), vs baselines. A trade = its net R (win +R, loss -1, or the real trade's net R
with costs). $1,000 start, base $20 (2%). Synthetic: independent trades, p and R, 1,000 trades, 1,000 orders. Real: the user's M5 / M15
TP1 0.2R trades (nt4), 2021-01 .. 2026-09 in one run ($1,000 once) and every month fresh. Output mm/combo_results.txt"""
import sys, random, pickle, statistics as st
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
START, BASE, CAP = 1000.0, 20.0, 0.03
MINR = BASE / 8.0                                     # the smallest trade (about 0.01 lot of gold on M5)

def run(rule, rs):
    eq = START; peak = START; mdd = 0.0; hist = [START]; wins = 0; seq = 0; pool = 0.0; lastR = []
    for x in rs:
        dd = (peak - eq) / peak if peak > 0 else 1.0
        above = eq >= START
        if rule == 'Fixed $20': r = BASE
        elif rule == '% of equity 2%': r = 0.02 * eq
        elif rule == 'Over N = 3': r = BASE + pool / 3.0
        elif rule == 'Crooks E, N = 3 (approx)': r = BASE if pool <= 0 else (MINR if seq < 1 else BASE + pool / 3.0 / 0.2)
        # ---- the 5 combinations
        elif rule == 'C1 Paroli up / brake down':          # profit zone: Paroli (x2 after each win, 3 wins then reset); below the start or 10% off the best: 1/2, 20%: 1/4
            r = BASE * (2 ** wins) if above and dd < 0.10 else BASE * min(1.0, eq / START) * (0.5 if dd < 0.20 else 0.25)   # v2: the brake shrinks with the account
        elif rule == 'C2 1-3-2-6 up / small lot down':     # profit zone: 1-3-2-6; below the start: the small lot until back above
            r = BASE * (1, 3, 2, 6)[seq % 4] if above else MINR
        elif rule == 'C3 % equity + equity-curve filter':  # 1.5% of equity; a quarter of it while equity is under its 20-trade average
            ma = sum(hist[-20:]) / len(hist[-20:]); r = 0.015 * eq * (1.0 if eq >= ma else 0.25)
        elif rule == 'C4 1/4 Kelly (learned) + brake':     # Kelly from the last 100 trades' win rate and win size, a quarter; no edge -> the small lot
            if len(lastR) < 30: r = BASE
            else:
                w = [v for v in lastR[-100:] if v > 0]; l = [v for v in lastR[-100:] if v <= 0]
                p = len(w) / len(lastR[-100:]); R = st.mean(w) if w else 0.0; L = -st.mean(l) if l else 1.0
                f = max(0.0, (p * R - (1 - p) * L) / (R * L)) / 4.0 if R > 0 and L > 0 else 0.0
                r = f * eq * L if f > 0 else MINR
                if dd >= 0.10: r *= 0.5
        elif rule == 'C5 profit-paid recovery + brake':    # above the start: Over N = 3, but the extra never more than 30% of the profit above the start; below: 1/2, 1/4
            r = BASE + min(pool / 3.0, 0.3 * max(0.0, eq - START)) if above else BASE * min(1.0, eq / START) * (0.5 if dd < 0.20 else 0.25)   # v2: shrinks with the account
        if rule.startswith('C'): r = min(r, CAP * eq)      # the brake: never more than 3% of the equity on one trade
        r = max(0.0, min(r, eq))
        pnl = r * x
        eq += pnl; peak = max(peak, eq); mdd = max(mdd, (peak - eq) / peak if peak > 0 else 1.0); hist.append(eq); lastR.append(x)
        win = pnl > 0
        if win: pool = max(0.0, pool - pnl); wins = 0 if wins + 1 >= 3 else wins + 1; seq = seq + 1 if rule.startswith('C2') else 1
        else: pool += -pnl; wins = 0; seq = 0
        if rule.startswith('Crooks'): seq = 1 if win else 0
        if eq <= START * 0.05: return eq - START, 1.0, True     # blown: under 5% of the start
    return eq - START, mdd, False

RULES = ['Fixed $20', '% of equity 2%', 'Over N = 3', 'Crooks E, N = 3 (approx)', 'C1 Paroli up / brake down', 'C2 1-3-2-6 up / small lot down',
         'C3 % equity + equity-curve filter', 'C4 1/4 Kelly (learned) + brake', 'C5 profit-paid recovery + brake']
out = []
def table(title, seqs):
    out.append('\n' + title)
    out.append('  %-36s %11s %11s %10s %8s' % ('rule', 'median net', 'mean net', 'avg maxDD', 'blown'))
    for rule in RULES:
        res = [run(rule, s) for s in seqs]
        out.append('  %-36s %11.0f %11.0f %9.1f%% %7.1f%%' % (rule, st.median(v[0] for v in res), st.mean(v[0] for v in res), 100 * st.mean(v[1] for v in res), 100 * sum(v[2] for v in res) / len(res)))
for p in (0.7, 0.8, 0.9):
    for R in (0.2, 0.3, 0.5):
        rng = random.Random(int(p * 1000 + R * 10)); seqs = [[(R if rng.random() < p else -1.0) for _ in range(1000)] for _ in range(1000)]
        table('synthetic: win rate %.0f%%, target %.1fR (expectancy %+.2fR), 1,000 trades x 1,000 orders' % (p * 100, R, p * R - (1 - p)), seqs)
for tf in ('M5', 'M15'):
    D = pickle.load(open(S + '/nt4/results_%s.pkl' % tf, 'rb')); trs = D['trades']
    rs = [x['net'] for x in trs]
    wr = sum(v > 0 for v in rs) / len(rs)
    table('REAL %s trades (TP1 0.2R, your filters), %d trades, win rate %.1f%%, mean %+.3fR: one run Jan 2021 - Sep 2026 from $1,000' % (tf, len(rs), 100 * wr, st.mean(rs)), [rs])
    months = sorted({(x['t'].year, x['t'].month) for x in trs})
    bym = [[x['net'] for x in trs if (x['t'].year, x['t'].month) == k] for k in months]
    out.append('  every month fresh from $1,000 (%d months): rule | total | profitable months | worst month' % len(bym))
    for rule in RULES:
        nets = [run(rule, m)[0] for m in bym]
        out.append('  %-36s %9.0f %4d / %d %9.0f' % (rule, sum(nets), sum(v > 0 for v in nets), len(nets), min(nets)))
open(S + '/mm/combo_results.txt', 'w').write('\n'.join(out)); print('\n'.join(out))
