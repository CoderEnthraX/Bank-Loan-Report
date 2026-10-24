p='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/gold/pickcfg.py'; s=open(p).read()
a='''def line(c, m):'''
b='''def pick_streak(tf, top=10, keep=0.5):
    """shortest longest-losing-streak (2021-2026) among robust settings that keep >= keep x the profit pick's robust score;
    then the fewest changed settings within 10% of the best robust score at that streak length"""
    P, minA, minB = load(tf)
    rows = [(c, m) for c, m in P.values() if ok(m, minA, minB)]
    if not rows: return [], len(P)
    pr = pick(tf, None, 1)[0][0]; floor = keep * robust(pr[1])
    q = [r for r in rows if robust(r[1]) >= floor]
    L = min(r[1]['all']['maxL'] for r in q); q = [r for r in q if r[1]['all']['maxL'] == L]
    q.sort(key=lambda r: -robust(r[1])); b0 = robust(q[0][1])
    s = min([r for r in q if robust(r[1]) >= 0.9 * b0], key=lambda r: (len(labels.rows(r[0])), -robust(r[1])))
    return [s] + [r for r in q if r is not s][:top - 1], len(P)
def line(c, m):'''
assert s.count(a)==1; s=s.replace(a,b,1)
s=s.replace("""        for lab, L in (('PROFIT', None), ('LOSING STREAK <= 6', 6)):
            rows, n = pick(tf, L)""","""        for lab, L in (('PROFIT', None), ('SHORTEST LOSING STREAK', 'S')):
            rows, n = pick(tf, None) if L is None else pick_streak(tf)""")
open(p,'w').write(s); print('ok')
