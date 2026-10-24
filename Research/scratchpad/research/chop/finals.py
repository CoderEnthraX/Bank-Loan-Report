"""full-engine evaluation of the finalists, ghost and veto, with CIs and per-instrument diffs -> finals.json"""
import sys, json
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/research/chop'); import ev
FIN = {
 'F1 near1S<=0.525 (hyp-family TRAIN-best)': [['near1S', 'le', 0.525]],
 'F2 rngS>=6.97 (same-session chop TRAIN-best)': [['rngS', 'ge', 6.97]],
 'F3 pEff<=0.561 (overall TRAIN-best, prev day)': [['pEff', 'le', 0.561]],
 'F4 xR2<=15.79 & rngS>=5.99 (composite TRAIN-best)': [['xR2', 'le', 15.789473684210526], ['rngS', 'ge', 5.993296264492603]],
 'F5 xR2<=9.73 (crossing-family TRAIN-best)': [['xR2', 'le', 9.73]],
 'F5b xR2<=11.8 (pre-look, 20% veto)': [['xR2', 'le', 11.8]],
}
import glob
G = [json.loads(l) for f in glob.glob(S + '/research/chop/grid3_*.jsonl') for l in open(f)]
g6 = [g for g in G if g['f'] == 'xR2+rngRel' and g['pc'] == [10, 20]][0]
FIN['F6 xR2+rngRel 10/20 (post-hoc, not TRAIN-best)'] = g6['rules']
res = {}
for name, rules in FIN.items():
    for mode in ('ghost', 'veto'):
        r = ev.summary(ev.run({'chopRules': rules, 'chopMode': mode})); r['rules'] = rules; res[name + ' | ' + mode] = r
        print(ev.line(name + ' ' + mode, r)); print('    per-instr dE2:', ' '.join(f"{s}:{v:+.2f}" for s, v in r['ps'].items()))
json.dump(res, open(S + '/research/chop/finals.json', 'w'), indent=1)
