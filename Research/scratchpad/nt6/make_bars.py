"""H4 and D1 gold bars from the H1 bars (server-time buckets: H4 = 4-hour blocks from server midnight, D1 = the server day):
O first, H max, L min, C last, TV sum, SP mean; srv / utc of the first H1 bar. -> gold/data/H4.pkl, gold/data/D1.pkl"""
import pickle, collections
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
d = pickle.load(open(S + '/gold/data/H1.pkl', 'rb'))
for tf, kf in (('H4', lambda t: (t.date(), t.hour // 4)), ('D1', lambda t: t.date())):
    out = collections.OrderedDict((k, []) for k in ('srv', 'utc', 'O', 'H', 'L', 'C', 'TV', 'SP'))
    cur = None; grp = []
    def flush():
        if not grp: return
        out['srv'].append(d['srv'][grp[0]]); out['utc'].append(d['utc'][grp[0]])
        out['O'].append(d['O'][grp[0]]); out['H'].append(max(d['H'][i] for i in grp)); out['L'].append(min(d['L'][i] for i in grp)); out['C'].append(d['C'][grp[-1]])
        out['TV'].append(sum(d['TV'][i] for i in grp)); out['SP'].append(sum(d['SP'][i] for i in grp) / len(grp))
    for i, t in enumerate(d['srv']):
        k = kf(t)
        if k != cur: flush(); grp = []; cur = k
        grp.append(i)
    flush()
    pickle.dump(dict(out), open(S + '/gold/data/%s.pkl' % tf, 'wb'))
    print(tf, len(out['O']), out['srv'][0], out['srv'][-1])
