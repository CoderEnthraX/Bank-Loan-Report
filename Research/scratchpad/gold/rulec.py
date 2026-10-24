"""Rule C and Rule C split with the loss split over 1-5 trades, with and without the $500 hard cap (clamp), on every timeframe and setting.
Whole 2021-2026 run, plus 2021-23 and 2024-26 each from a fresh $10,000, so a rule that only works in one half shows up.
Partial closes (Close % at TP1) update the carried losses after each part, like the strategy. Output: rulec.pkl + printed table."""
import sys, pickle
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
import recovery as RC, greedy
TFS = ('M1', 'M5', 'M15', 'H1'); PROFS = ('default', 'profit', 'streak')
SPLITS = (1, 2, 3, 4, 5); CAPS = (0.0, 500.0)
def sequence(F, prof):
    d = dict(greedy.defaults()); d.update(F['cfg'][prof]); p = d['p1'] if d['exitAt'] > 1 else 0.0; t1 = d['tp1R']
    out = []
    for x in sorted(F['trades'][prof], key=lambda x: x[0]):
        res, c = x[1], x[4] / x[5]
        if p and x[3][0]: out.append((x[0], res, c, [(p * t1, p), (res - p * t1, 1 - p)]))   # TP1 part, then the rest
        else: out.append((x[0], res, c, None))
    return out
def run(seq, mode, split, cap, base=50.0):
    r = RC.simulate([(res, c, parts) for _, res, c, parts in seq], mode, base=base, cap=cap, cSplit=split)
    r['ratio'] = r['net'] / r['maxDD'] if r['maxDD'] > 0 else 0.0
    return r
def study(base=50.0):
    out = {}
    for tf in TFS:
        F = pickle.load(open(S + '/gold/final_%s.pkl' % tf, 'rb'))
        for prof in PROFS:
            seq = sequence(F, prof); A = [x for x in seq if x[0].year <= 2023]; B = [x for x in seq if x[0].year >= 2024]
            rows = []
            for mode, split, cap in [('Off', 3, 0.0)] + [(m, s, c) for m in ('Rule C: carry the losses', 'Rule C split') for s in SPLITS for c in CAPS]:
                rows.append(dict(mode=mode, split=split, cap=cap, all=run(seq, mode, split, cap, base), A=run(A, mode, split, cap, base), B=run(B, mode, split, cap, base)))
            out[(tf, prof)] = rows
    return out
if __name__ == '__main__':
    base = float(sys.argv[1]) if len(sys.argv) > 1 else 50.0
    out = study(base)
    pickle.dump(dict(base=base, rows=out), open(S + '/gold/rulec%s.pkl' % ('' if base == 50 else '_%d' % base), 'wb'))
    for (tf, prof), rows in out.items():
        off = rows[0]['all']
        print('\n%s %s (base $%d) | Off: net %+.0f, max DD $%.0f (%.0f%%), ratio %.2f' % (tf, prof, base, off['net'], off['maxDD'], 100 * off['maxDDpct'], off['ratio']))
        for x in rows[1:]:
            a, ra, rb = x['all'], x['A'], x['B']
            print('   %-12s split %d %-5s | net %+9.0f  DD $%7.0f (%3.0f%%)  max risk $%6.0f  %s | ratio %5.2f (x%.2f Off) | 21-23 %+8.0f DD %3.0f%% | 24-26 %+8.0f DD %3.0f%%' % (
                'Rule C' if x['mode'].startswith('Rule C:') else 'Rule C split', x['split'], 'cap' if x['cap'] else '', a['net'], a['maxDD'], 100 * a['maxDDpct'], a['maxRisk'],
                'BLOWN' if a['ruined'] else 'ok   ', a['ratio'], a['ratio'] / off['ratio'] if off['ratio'] > 0 else 0, ra['net'], 100 * ra['maxDDpct'], rb['net'], 100 * rb['maxDDpct']))
