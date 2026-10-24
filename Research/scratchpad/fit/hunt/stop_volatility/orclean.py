import sys, pickle, itertools
rows = pickle.load(open(sys.argv[1], 'rb'))
keys = sorted({k for _, f in rows for k in f})
tight = {i for i, (t, f) in enumerate(rows) if t['tight']}
atoms = []
for k in keys:
    vals = [f.get(k) for t, f in rows]
    if sum(v is not None for v in vals) < 65: continue
    xs = sorted(set(v for v in vals if v is not None))
    for th in xs:
        for side in ('>=', '<='):
            pas = {i for i, v in enumerate(vals) if v is not None and (v >= th if side == '>=' else v <= th)}
            if pas and not (pas - tight): atoms.append((f'{k}{side}{th:.4g}', frozenset(pas)))
# keep maximal atoms per feature/side
best = {}
for name, s in atoms:
    key = name.split('>=')[0].split('<=')[0] + ('>=' if '>=' in name else '<=')
    if key not in best or len(s) > len(best[key][1]): best[key] = (name, s)
A = list(best.values())
print(len(A), 'clean atoms; max single cover', max(len(s) for _, s in A))
res = []
for a, b in itertools.combinations(A, 2):
    res.append((len(a[1] | b[1]), a[0], b[0]))
res.sort(reverse=True)
print('best OR-pairs of clean atoms (tight covered of 8):')
for r in res[:10]: print('  ', r)
res3 = []
top = sorted(A, key=lambda x: -len(x[1]))[:120]
for a, b, c in itertools.combinations(top, 3):
    res3.append((len(a[1] | b[1] | c[1]), a[0], b[0], c[0]))
res3.sort(reverse=True)
print('best OR-triples:'); [print('  ', r) for r in res3[:5]]
