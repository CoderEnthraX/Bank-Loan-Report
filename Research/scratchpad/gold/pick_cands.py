"""Candidates for stage C: default + the 3 best stage-B combinations by 2021-23 after spread (min trades) + a stage-2 combination of indicator settings."""
import sys, pickle
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold'); import anaA
EXTRA = {'H1': [('stopAtr = 2.2 + Don\'t Chase = 2.0 sigma', dict(stopAtr=2.2, noChase=True, noChaseSig=2.0))],
         'M15': [('stopAtr = 2.2 + Don\'t Chase = 1.5 sigma', dict(stopAtr=2.2, noChase=True, noChaseSig=1.5))],
         'M5': [('stopAtr = 2.5 + Kill zones: Asia + Don\'t Chase = 2.0 sigma', dict(stopAtr=2.5, kzOn=True, kz=(True, False, False, False), noChase=True, noChaseSig=2.0))],
         'M1': []}
tf = sys.argv[1]
B = pickle.load(open(S + '/gold/stageB_%s.pkl' % tf, 'rb')); opts = dict(B['combos'])
d0 = anaA.metrics(pickle.load(open(S + '/gold/sweep_%s.pkl' % tf, 'rb'))['res']['default'])
rows = [(n, anaA.metrics(tr)) for n, tr in B['res'].items() if tr]
rows = [r for r in rows if r[1] and r[1]['nA'] >= 0.25 * d0['nA']]
rows.sort(key=lambda r: -r[1]['EcA'])
cands = [('default', {})] + [(n, opts[n]) for n, _ in rows[:3]]
steady = sorted([r for r in rows if r[1]['EcA'] > 0 and r[1]['nA'] >= 0.3 * d0['nA']], key=lambda r: (-r[1]['ypos'], -r[1]['EcA']))
for n, _ in steady[:2]:
    if n not in dict(cands): cands.append((n, opts[n]))
cands += [c for c in EXTRA[tf] if c[0] not in dict(cands)]
pickle.dump(cands, open(S + '/gold/cands_%s.pkl' % tf, 'wb'))
for n, o in cands: print(tf, 'candidate:', n)
