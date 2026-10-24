"""TRAIN-only selection from the grid: per feature the TRAIN-best (side, pc) with TRAIN keep >= 60%; then show TEST for it."""
import json, glob, sys
mode = sys.argv[1] if len(sys.argv) > 1 else 'ghost'
G = [json.loads(l) for f in glob.glob(f'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/research/chop/grid_{mode}_*.jsonl') for l in open(f)]
best = {}
for g in G:
    if g['nn'] < 0.6 * 733: continue
    if g['f'] not in best or g['En'] > best[g['f']]['En']: best[g['f']] = g
rows = sorted(best.values(), key=lambda g: -g['En'])
print('feature    side pc  thr      | TRAIN E2 (d)    | TEST E2 (d)     keep  tot  instr+')
for g in rows:
    print(f"{g['f']:10s} {g['side']:3s} {g['pc']:3d} {g['rules'][0][2]:8.3g} | {g['En']:+.3f} ({g['dn']:+.3f}) | {g['Ee']:+.3f} ({g['de']:+.3f})  {g['keep']:.0%} {g['tot']:+5.0f} {g['better']}/10")
# rank correlation TRAIN d vs TEST d across all grid configs
import statistics
def rk(v):
    o = sorted(range(len(v)), key=lambda i: v[i]); r = [0] * len(v)
    for j, i in enumerate(o): r[i] = j
    return r
a = rk([g['dn'] for g in G]); b = rk([g['de'] for g in G]); print('Spearman TRAIN-d vs TEST-d over', len(G), 'grid configs:', round(statistics.correlation(a, b), 3))
print('share of grid configs with TRAIN d>0:', sum(g['dn'] > 0 for g in G) / len(G), ' TEST d>0:', sum(g['de'] > 0 for g in G) / len(G), ' both:', sum(g['dn'] > 0 and g['de'] > 0 for g in G) / len(G))
