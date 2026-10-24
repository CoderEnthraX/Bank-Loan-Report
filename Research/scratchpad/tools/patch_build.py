p='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/gold/build_final.py'; s=open(p).read()
R=[("""    import repC
    for tf in TFS:""","""    for tf in TFS:"""),
("""            for e in repC.EX:
                q = repC.m(D['res'][(cn, e)])""","""            for e in EXN:
                q = exm(D['res'][(cn, e)])"""),
("""# ---------------------------------------------------------------- exits (stage C)
""","""# ---------------------------------------------------------------- exits (stage C)
EXN = ['Exit at TP1 (0.6R)', 'Exit at TP2 (1R)', 'Exit at TP3 (1.5R)', 'Exit at TP4 (2R)', 'TP4 + breakeven at TP1', 'TP2 + breakeven at TP1', 'TP4 + breakeven at TP2', '50% at TP1 + breakeven, rest TP4']
def exm(tr):
    n = len(tr); res = [x[1] for x in tr]; mw, ml = streaks(res)
    A = [x for x in tr if x[0].year <= 2023]; B = [x for x in tr if x[0].year >= 2024]
    ec = lambda q: sum(x[1] - x[4] / x[5] for x in q) / len(q) if q else 0.0
    yrs = collections.defaultdict(list)
    for x in tr: yrs[x[0].year].append(x)
    return dict(n=n, win=sum(1 for v in res if v > 0) / n, EA=ec(A), EB=ec(B), Ec=ec(tr), Rc=sum(x[1] - x[4] / x[5] for x in tr),
                ypos=sum(1 for y in yrs if sum(x[1] - x[4] / x[5] for x in yrs[y]) > 0), mw=mw, ml=ml)
"""),
("""                put(ws, r, 1, tf); put(ws, r, 2, PNAME[prof]); put(ws, r, 3, 'TP%d (%sR)' % (k, labels.fmt((0.6, 1.0, 1.5, 2.0)[k - 1])))""",
 """                dd = dict(greedy.defaults()); dd.update(cfg)
                put(ws, r, 1, tf); put(ws, r, 2, PNAME[prof]); put(ws, r, 3, 'TP%d (%sR)' % (k, labels.fmt(float(dd['tp%dR' % k]))))"""),
("""            put(ws, r, 5, '=D%d/%d' % (r, DAYS_N if last else 248) if True else '', '0.00', last, None, fl)""",
 """            put(ws, r, 5, '=D%d/%d' % (r, DAYS_N if last else DAYS_Y[y]), '0.00', last, None, fl)"""),
("""    ws.cell(3, 5, 'Trades per day: year rows use 248 trading days (2026: Jan-Oct 2 only, so it reads low); 2021-2026 uses the %d trading days in the data.' % DAYS_N).font = font(italic=True, size=8)""",
 """    ws.cell(3, 1, 'Trades per day = trades / trading days in the data (2026 = 2 Jan - 2 Oct). Year rows: ' + ', '.join('%d: %d days' % (y, d) for y, d in sorted(DAYS_Y.items())) + '.').font = font(italic=True, size=8)"""),
("""F = 'Arial'; DAYS_N = 1485""","""F = 'Arial'
def _days():
    d = pickle.load(open(S + '/gold/data/H1.pkl', 'rb')); ds = set(t.date() for t in d['srv']); c = collections.Counter(x.year for x in ds)
    return len(ds), dict(c)
DAYS_N, DAYS_Y = _days()"""),
]
for a,b in R:
    assert s.count(a)==1, a[:70]
    s=s.replace(a,b)
open(p,'w').write(s); print('ok')
