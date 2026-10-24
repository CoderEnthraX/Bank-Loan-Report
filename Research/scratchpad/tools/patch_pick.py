p='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/gold/pickcfg.py'; s=open(p).read()
a='''def pick(tf, lmax=None, top=10):
    P, minA, minB = load(tf)
    rows = [(c, m) for c, m in P.values() if ok(m, minA, minB)]
    if lmax is not None:
        for L in range(lmax, 30):
            q = [(c, m) for c, m in rows if m['all']['maxL'] <= L]
            if q: rows = q; break
    rows.sort(key=lambda r: -robust(r[1]))
    return rows[:top], len(P)'''
b='''def pick(tf, lmax=None, top=10, simple=True):
    """top rows by robust score; with simple=True the first row is replaced by the configuration with the fewest changed settings
    whose robust score is within 10% of the best (fewer knobs = less fitted)"""
    P, minA, minB = load(tf)
    rows = [(c, m) for c, m in P.values() if ok(m, minA, minB)]
    if lmax is not None:
        for L in range(lmax, 30):
            q = [(c, m) for c, m in rows if m['all']['maxL'] <= L]
            if q: rows = q; break
    rows.sort(key=lambda r: -robust(r[1]))
    if simple and rows:
        b0 = robust(rows[0][1]); near = [r for r in rows if robust(r[1]) >= 0.9 * b0]
        s = min(near, key=lambda r: (len(labels.rows(r[0])), -robust(r[1])))
        rows = [s] + [r for r in rows if r is not s]
    return rows[:top], len(P)'''
assert s.count(a)==1; s=s.replace(a,b)
s=s.replace("""        for lab, L in (('PROFIT', None), ('LOSING STREAK <= 7', 7), ('LOSING STREAK <= 6', 6)):""","""        for lab, L in (('PROFIT', None), ('LOSING STREAK <= 6', 6)):""")
open(p,'w').write(s); print('ok')
