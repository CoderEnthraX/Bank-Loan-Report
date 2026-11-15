"""Money runs for the user's-settings monthly workbooks: the 8 trade lists of collect_user.py (M5 / M15 x filters off / on x TP1 / TP2),
each with No recovery (fixed $50) + Crooks E + Crooks F - J x Off / Low / Medium / High / Extra high / Max, one account from January 2021
(booked by exit month) and each month on its own (fresh $10,000, trades by entry month). gold/recovery.py; the strategy defaults: $50,
$10,000, 1:100 (limit price), no hard cap, costs 0.23 per oz (TradingView commission 0.115 per side), E / I lot 0.01 = 1 oz, F x3, G x10,
H 1 %, J x20, ladder target $1,000; exitR = 0.6 (TP1) / 1.0 (TP2). Output: mcej2/user_money.pkl"""
import sys, pickle
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold'); sys.path.insert(0, S + '/mcej')
import recovery as RC, money as MO
CONFIGS = [('Off', 'Off')] + MO.CONFIGS
D = pickle.load(open(S + '/mcej2/user_trades.pkl', 'rb')); out = {}
for key, v in D.items():
    tf, setup, ex = key; trs = v['trades']
    P = dict(base=50.0, start=10000.0, cap=0.0, capAction='clamp', exitR=0.6 if ex == 1 else 1.0, ladT=1000.0)
    res = {}
    for rule, lvl in CONFIGS:
        per, r = MO.run(RC, trs, rule, lvl, P)
        cm, whole = MO.cont_months(per, trs, P['start'])
        res[(rule, lvl)] = dict(per=per, cont=cm, whole=whole, fresh=MO.fresh_months(RC, trs, rule, lvl, P), ruined=r['ruined'], maxRisk=r['maxRisk'])
    out[key] = dict(P=P, counts=MO.trade_counts(trs), res=res, n=len(trs), cnt=v['cnt'], hows=dict(v['hows']),
                    netR=sum((x['R'] - x['c']) / (1 + x['c']) for x in trs), wins=sum(1 for x in trs if x['R'] - x['c'] > 0))
    print('%-3s %-3s TP%d %5d trades | %s' % (tf, setup, ex, len(trs), ' '.join('%s/%s %+.0f%s' % (r_[-1] if r_ != 'Off' else 'none', l[:2], res[(r_, l)]['whole']['net'],
          '(blown %s)' % res[(r_, l)]['whole']['blown'] if res[(r_, l)]['ruined'] else '') for r_, l in CONFIGS if l in ('Off', 'Max'))))
pickle.dump(dict(months=MO.MONTHS, configs=CONFIGS, runs=out), open(S + '/mcej2/user_money.pkl', 'wb'))
