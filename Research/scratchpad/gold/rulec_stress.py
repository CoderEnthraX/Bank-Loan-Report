"""Stress test: the same Rule C / Rule C split runs with an extra cost of 0.05 R and 0.10 R on every trade (weaker live edge, slippage)."""
import sys, pickle
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
import recovery as RC, rulec
RULES = [('Off', 3, 0.0, 'clamp'), ('Rule C split', 2, 500.0, 'clamp'), ('Rule C split', 3, 500.0, 'clamp'), ('Rule C split', 3, 500.0, 'reset'),
         ('Rule C: carry the losses', 3, 500.0, 'clamp'), ('Rule C: carry the losses', 3, 500.0, 'reset')]
out = {}
for tf in rulec.TFS:
    F = pickle.load(open(S + '/gold/final_%s.pkl' % tf, 'rb')); seq = rulec.sequence(F, 'profit')
    for extra in (0.0, 0.05, 0.10):
        trs = [(res, c + extra, parts) for _, res, c, parts in seq]
        for mode, split, cap, act in RULES:
            r = RC.simulate(trs, mode, cap=cap, capAction=act, cSplit=split); out[(tf, extra, mode, split, cap, act)] = r
pickle.dump(out, open(S + '/gold/rulec_stress.pkl', 'wb'))
for tf in rulec.TFS:
    print('\n%s best settings' % tf)
    for mode, split, cap, act in RULES:
        cells = []
        for extra in (0.0, 0.05, 0.10):
            r = out[(tf, extra, mode, split, cap, act)]
            cells.append('BLOWN            ' if r['ruined'] else '%+8.0f DD %3.0f%%' % (r['net'], 100 * r['maxDDpct']))
        print('   %-24s split %d %-12s | %s' % ('Off' if mode == 'Off' else ('Rule C split' if mode == 'Rule C split' else 'Rule C'), split, ('cap $%d %s' % (cap, act)) if cap else '', ' | '.join(cells)))
