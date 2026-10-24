import json, glob
R = {m: [json.loads(l) for f in glob.glob(f'rnull_{m}_*.jsonl') for l in open(f)] for m in ('ghost', 'veto')}
for m in R:
    for kp in sorted(set(x['keepP'] for x in R[m])):
        r = [x for x in R[m] if x['keepP'] == kp]; de = sorted(x['de'] for x in r); dn = sorted(x['dn'] for x in r)
        print(f"null {m} keep{kp}: n={len(r)} TEST d mean {sum(de)/len(de):+.3f} p95 {de[int(.95*len(de))]:+.3f} | TRAIN d mean {sum(dn)/len(dn):+.3f} p95 {dn[int(.95*len(dn))]:+.3f} | tot mean {sum(x['tot'] for x in r)/len(r):+.0f}")
F = json.load(open('finals.json'))
print('finalist: null(keep nearest) TEST-pct TRAIN-pct both-beat-share instr-pct')
for name, f in F.items():
    m = name.split(' | ')[1]; ks = sorted(set(x['keepP'] for x in R[m])); kp = min(ks, key=lambda k: abs(k - f['keep'])); r = [x for x in R[m] if x['keepP'] == kp]
    pe = sum(x['de'] < f['de'] for x in r) / len(r); pn = sum(x['dn'] < f['dn'] for x in r) / len(r); both = sum(x['de'] >= f['de'] and x['dn'] >= f['dn'] for x in r) / len(r)
    pb = sum(x['better'] < f['better'] for x in r) / len(r)
    print(f"{name:60s} keep {f['keep']:.0%} vs null{kp}: TEST pct {pe:.1%} TRAIN pct {pn:.1%} P(null beats both) {both:.3f} instr-better pct {pb:.0%}")
