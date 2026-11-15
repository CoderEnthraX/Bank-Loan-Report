"""Cost sensitivity of the user's settings at a fixed risk: the same engine events and strategy execution with round-trip costs per oz
0 (no costs, no earn-back extension), 0.16 (spread only) and 0.23 (spread + $7 / lot, the default). Output: mcej2/user_costs.pkl"""
import sys, pickle
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold'); sys.path.insert(0, S + '/mcej2')
import geng, ref_gse, stratemu as EM, collect_user as CU
out = {}
for tf in ('M5', 'M15'):
    P = geng.prepare(tf, 'session', 'hlc3'); geng._CUR['vw'] = 'session'; geng._CUR['src'] = 'hlc3'
    for setup in ('off', 'on'):
        fl = EM.time_flags(P['T'], fcOn=True, wkOn=True, newsOn=CU.SETUP[setup]['news'])
        for ex in (1, 2):
            ev = []; ref_gse.run(tf, dict(CU.ENG, exitAt=ex, **CU.SETUP[setup]['eng']), ev)
            for cost in (0.0, 0.16, 0.23):
                tr, _ = EM.run(P['O'], P['H'], P['L'], P['C'], P['T'], ev, P['mt'], earnBack=cost > 0, costPx=cost, flags=fl)
                tr = [x for x in tr if x['exit'] is not None]
                net = [(x['dir'] * (x['xpx'] - x['fpx']) / x['risk'] - cost / x['risk']) / (1 + cost / x['risk']) for x in tr]
                out[(tf, setup, ex, cost)] = dict(n=len(tr), netR=sum(net), win=sum(1 for v in net if v > 0) / len(net))
                print(tf, setup, 'TP%d' % ex, 'cost %.2f' % cost, '%5d trades, wins %.1f%%, net %+.1fR' % (len(tr), 100 * out[(tf, setup, ex, cost)]['win'], sum(net)))
pickle.dump(out, open(S + '/mcej2/user_costs.pkl', 'wb'))
