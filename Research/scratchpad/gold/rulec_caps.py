"""Rule C / Rule C split at split 2 and 3: how the hard cap size ($250 / $500 / $1,000) and the cap action (clamp / start again) change the result."""
import sys, pickle
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
import recovery as RC, rulec
out = {}
for tf in rulec.TFS:
    F = pickle.load(open(S + '/gold/final_%s.pkl' % tf, 'rb'))
    for prof in ('profit', 'streak'):
        seq = rulec.sequence(F, prof); trs = [(res, c, parts) for _, res, c, parts in seq]; rows = []
        for mode in ('Rule C: carry the losses', 'Rule C split'):
            for split in (2, 3):
                for cap in (250.0, 500.0, 1000.0):
                    for act in ('clamp', 'reset'):
                        r = RC.simulate(trs, mode, cap=cap, capAction=act, cSplit=split); r['ratio'] = r['net'] / r['maxDD'] if r['maxDD'] > 0 else 0.0
                        rows.append(dict(mode=mode, split=split, cap=cap, act=act, r=r))
        out[(tf, prof)] = rows
pickle.dump(out, open(S + '/gold/rulec_caps.pkl', 'wb'))
for (tf, prof), rows in out.items():
    print('\n%s %s' % (tf, prof))
    for x in rows:
        r = x['r']
        print('   %-12s split %d cap $%4d %-5s | net %+8.0f  DD $%6.0f (%3.0f%%)  ratio %5.2f  %s' % ('Rule C' if x['mode'].startswith('Rule C:') else 'Rule C split', x['split'], x['cap'], x['act'],
              r['net'], r['maxDD'], 100 * r['maxDDpct'], r['ratio'], 'BLOWN' if r['ruined'] else ''))
