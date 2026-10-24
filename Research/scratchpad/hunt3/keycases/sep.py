import sys, csv
rows = list(csv.DictReader(open(sys.argv[1]), delimiter='\t'))
ok = [r for r in rows if r['lab'].startswith('ok')]; X = [r for r in rows if r['lab'].startswith('X')]
print('ok', len(ok), 'X', len(X))
for c in rows[0]:
    if c in ('sym', 'arm', 'lab'): continue
    try: ov = sorted(float(r[c]) for r in ok); xv = [(float(r[c]), r['sym'][:3] + r['arm'][5:]) for r in X]
    except ValueError: continue
    lo, hi = ov[0], ov[-1]
    below = [n for v, n in xv if v < lo]; above = [n for v, n in xv if v > hi]
    # with 1 ok loss
    lo2, hi2 = ov[1], ov[-2]
    b2 = sum(v < lo2 for v, n in xv); a2 = sum(v > hi2 for v, n in xv)
    print(f"{c:8s} ok[{lo:.3f},{hi:.3f}] X: {' '.join(f'{v:.2f}' for v,n in xv)} | below {below} above {above} | 1-loss below {b2} above {a2}")
