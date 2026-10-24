import sys, pickle, itertools
rows = pickle.load(open(sys.argv[1], 'rb'))
miss_ok = int(sys.argv[2]) if len(sys.argv) > 2 else 0
keys = sorted({k for _, f in rows for k in f})
N = len(rows)
tight = [i for i, (t, f) in enumerate(rows) if t['tight']]
atoms = []  # (name, set of normal indices passing, set of tight passing)
for k in keys:
    vals = [f.get(k) for t, f in rows]
    if sum(v is not None for v in vals) < 75: continue
    tv = sorted(vals[i] for i in tight if vals[i] is not None)
    if len(tv) < 8 - miss_ok: continue
    for m in range(miss_ok + 1):
        # >= threshold covering all but m lowest tight; <= covering all but m highest
        for side in ('>=', '<='):
            th = tv[m] if side == '>=' else tv[len(tv) - 1 - m]
            pas = {i for i, v in enumerate(vals) if v is not None and (v >= th if side == '>=' else v <= th)}
            tp = len(pas & set(tight)); fp = len(pas - set(tight))
            atoms.append((f'{k}{side}{th:.4g}', frozenset(pas), tp, fp))
print(len(atoms), 'atoms')
best = []
for a, b in itertools.combinations(atoms, 2):
    s = a[1] & b[1]; tp = len(s & set(tight)); fp = len(s) - tp
    err = (8 - tp) + fp
    best.append((err, fp, -tp, a[0], b[0]))
best.sort()
for r in best[:25]: print(r)
