"""Appendix of the Auction Retest workbook: the profit ladder with other profit targets ($1,000 = the default, $2,000, $3,000, $5,000), one
account 2021-2026, Crooks F - J x Low .. Max, every other setting as in money.py. Output: mcej/ars_targets.pkl"""
import sys, pickle
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold'); sys.path.insert(0, S + '/mcej')
import recovery as RC, money as MO
TARGETS = (1000.0, 2000.0, 3000.0, 5000.0)
D = pickle.load(open(S + '/mcej/ars_trades.pkl', 'rb')); out = {}
for key, v in D.items():
    trs = [dict(x, R=x['res'], levk=100.0 * x['sd'] * (1.0 + x['c']) / x['px'], rmin=1.0 * x['sd'] * (1.0 + x['c'])) for x in v['trades']]
    for rule in MO.RULES[1:]:
        P = dict(base=50.0, start=10000.0, cap=0.0, capAction='clamp', exitR=v['exitR'], ladT=1000.0)
        per, r = MO.run(RC, trs, rule, 'Off', P); out[(key, rule, 'Off', None)] = dict(net=r['net'], maxDDpct=r['maxDDpct'], guard=0)
        for T in TARGETS:
            P['ladT'] = T
            for lvl in MO.LEVELS[1:]:
                per, r = MO.run(RC, trs, rule, lvl, P)
                out[(key, rule, lvl, T)] = dict(net=r['net'], maxDDpct=r['maxDDpct'], guard=sum(1 for z in per if z and z[3]))
pickle.dump(dict(targets=TARGETS, res=out), open(S + '/mcej/ars_targets.pkl', 'wb'))
print(len(out), 'runs; guard runs by target:', {T: sum(1 for k, v in out.items() if k[3] == T and v['guard']) for T in TARGETS})
