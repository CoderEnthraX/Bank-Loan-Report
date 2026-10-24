"""Stage D: all loss-recovery rules on a trade sequence (2021-2026, after spread): $50 base risk, $10,000 start, without and with a $500 hard cap."""
import sys, pickle
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold'); import recovery as RC
def evaluate(seq, exitR=2.0):
    """seq: list of compact trades (t, res, win, hits, sp, risk, be) in time order"""
    tr = [(x[1], x[4] / x[5]) for x in sorted(seq, key=lambda x: x[0])]
    out = []
    for mode in RC.MODES:
        for cap in (0.0, 500.0):
            r = RC.simulate(tr, mode, cap=cap, exitR=exitR)
            r['cap'] = cap; out.append(r)
    return out
def show(label, rows):
    print('\n%s' % label)
    print('   %-46s %-8s | %10s | %10s %6s | %9s | %s' % ('recovery rule', 'cap', 'net profit', 'max DD $', 'DD %', 'max risk', 'blown?'))
    for r in rows:
        print('   %-46s %-8s | %+10.0f | %10.0f %5.0f%% | %9.0f | %s' % (r['mode'][:46], 'none' if r['cap'] == 0 else '$500', r['net'], r['maxDD'], 100 * r['maxDDpct'], r['maxRisk'],
              ('YES after %d trades' % r['ruinAt']) if r['ruined'] else 'no'))
if __name__ == '__main__':
    print('ok')
