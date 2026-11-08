"""rows.jsonl -> table.md (every variant: name, TF, n/month (train), excess train L/S, valid L/S, verdict)"""
import json, sys
A = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/of_agentA'; sys.path.insert(0, A)
import lib
R = [json.loads(l) for l in open(A + '/rows.jsonl')]
GROUP = {'base': '0 baseline (all signals)', 'terc': '2a signal-bar / profile features, tercile screen (train thresholds)',
         'cat': '2b categorical order-flow / profile rules', 'diag': '3a pullback state at fill (diagnostic only, NOT a rule)',
         'cxl': '3b pullback CANCEL rules', 'lgbm': '4 LightGBM selections', 'combo': '5 composites and combinations',
         'ctrl': '5 controls (momentum / ATR regime)', 'pva': '5b prior value-area width', 'ctrl6': '6b prior range vs value area',
         'cand': '7 candidates (repeat of rows above, detailed)'}
out = []; npass = {}; ntot = {}
for tag in GROUP:
    rr = [r for r in R if r['tag'] == tag]
    if not rr: continue
    out.append('\n**%s** (%d rows)\n' % (GROUP[tag], len(rr)))
    out.append('| variant | TF | n/mo | train L | train S | valid L | valid S | verdict |'); out.append('|---|---|---:|---:|---:|---:|---:|---|')
    for r in rr:
        v = lib.verdict(r, r['tf'])
        if tag not in ('base', 'cand', 'diag'):
            ntot[r['tf']] = ntot.get(r['tf'], 0) + 1; npass[r['tf']] = npass.get(r['tf'], 0) + (v == 'PASS4')
        c = [r[k]['ex'] for k in ('train_long', 'train_short', 'valid_long', 'valid_short')]
        out.append('| %s | %s | %.1f | %s | %s | %s | %s | %s |' % (r['name'].replace('|', '/'), r['tf'], r['train_both'].get('n', 0) / 36.0,
                   *['%+.2f' % x for x in c], ('**PASS4**' if v == 'PASS4' else v)))
head = 'Variants counted (excluding baseline / diagnostics / candidate repeats): ' + ', '.join('%s %d (PASS4 %d)' % (k, ntot[k], npass[k]) for k in ntot)
open(A + '/table.md', 'w').write(head + '\n' + '\n'.join(out) + '\n')
print(head)
for r in R:
    if r['tag'] not in ('base', 'cand', 'diag') and lib.verdict(r, r['tf']) == 'PASS4':
        print('PASS4', r['tf'], r['tag'], r['name'], [r[k]['ex'] for k in ('train_long', 'train_short', 'valid_long', 'valid_short')], round(r['train_both']['n'] / 36, 1))
