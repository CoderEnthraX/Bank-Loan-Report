"""Full check of the two monthly workbooks against monthly.pkl (every month x strategy x rule cell, the totals, Summary and By-month sheets)."""
import pickle, json, sys
import openpyxl
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
R = pickle.load(open(S + '/gold/monthly.pkl', 'rb')); J = json.load(open(S + '/gold/monthly_readme.json'))
V = [v for v, _ in R['variants']]; M = R['months']; ST = R['strategies']
ERR = ('#REF!', '#NAME?', '#VALUE!', '#DIV/0!', '#N/A', '#NUM!', '#NULL!', 'Err:')
bad = 0; nchk = 0
def near(a, b): return a is not None and abs(float(a) - float(b)) < 0.01
for f in ('file1', 'file2'):
    path = S + '/' + J['files'][f]['filename']
    wb = openpyxl.load_workbook(path, data_only=True)
    names = wb.sheetnames
    errs = [(ws.title, c.coordinate, c.value) for ws in wb for row in ws.iter_rows() for c in row if isinstance(c.value, str) and c.value.startswith(ERR)]
    print('%s: %d sheets (%s ... %s), error cells %d' % (path.split('/')[-1], len(names), names[:3], names[-2:], len(errs)))
    if errs: print('   first errors', errs[:5]); bad += len(errs)
    for s in ST:
        ws = wb[J['names'][s['key']]]
        # locate the header row with the rule labels and the month rows by scanning (layout-independent)
        hdr = None
        for r in range(1, 8):
            vals = [ws.cell(r, c).value for c in range(1, ws.max_column + 1)]
            if J['labels'][V[0]] in vals: hdr = r; row = vals; break
        assert hdr, (f, s['key'], 'no header row')
        first = [i for i, x in enumerate(row) if x == J['labels'][V[0]]]      # the first occurrence = the Net block
        netc = {v: row.index(J['labels'][v], first[0]) + 1 for v in V}        # Net block columns
        mrows = {}
        for r in range(hdr + 1, hdr + 80):
            a = ws.cell(r, 1).value
            if isinstance(a, str) and len(a) == 8 and a[3] == ' ':
                import datetime
                d = datetime.datetime.strptime(a, '%b %Y'); mrows['%04d-%02d' % (d.year, d.month)] = r
        if len(mrows) != 70: print('   %s %s: %d month rows' % (f, s['key'], len(mrows))); bad += 1; continue
        for m in M:
            base, v = R['res'][f][s['key']][m]
            r = mrows[m]
            for vn in V:
                nchk += 1
                if not near(ws.cell(r, netc[vn]).value, v[vn]['net']):
                    bad += 1
                    if bad < 10: print('   DIFF %s %s %s %s: sheet %r pickle %r' % (f, s['key'], m, vn, ws.cell(r, netc[vn]).value, v[vn]['net']))
            trc = [c for c in range(1, ws.max_column + 1) if ws.cell(hdr, c).value == 'Trades']
            if trc and ws.cell(r, trc[0]).value != base['trades']: bad += 1; print('   trades', f, s['key'], m, ws.cell(r, trc[0]).value, base['trades'])
        # the Total row of the Net block
        tot = [r for r in range(hdr + 70, hdr + 90) if ws.cell(r, 1).value == 'Total']
        for vn in V:
            exp = sum(R['res'][f][s['key']][m][1][vn]['net'] for m in M)
            if not tot or not near(ws.cell(tot[0], netc[vn]).value, exp): bad += 1; print('   TOTAL', f, s['key'], vn, ws.cell(tot[0], netc[vn]).value if tot else None, exp)
    # Summary block (a): totals per strategy and rule
    ws = wb['Summary']; found = 0
    for row in ws.iter_rows(values_only=True):
        if row and row[0] in J['names'].values():
            key = [k for k, n in J['names'].items() if n == row[0]][0]
            nums = [x for x in row[2:] if isinstance(x, (int, float))]
            if len(nums) >= 17 and found < 19:
                for vn, x in zip(V, nums[:17]):
                    nchk += 1
                    if not near(x, sum(R['res'][f][key][m][1][vn]['net'] for m in M)): bad += 1; print('   SUMMARY', f, key, vn, x)
                found += 1
    if found != 19: bad += 1; print('   Summary rows found', found)
    # one By-month sheet
    bm = [n for n in names if n.startswith('By month')]
    print('   By-month sheets: %d' % len(bm))
    for n in bm:
        ws = wb[n]; lab = n[len('By month - '):]
        vn = [v for v in V if J['labels'][v].replace('/', '-')[:len(lab)] == lab]
        if len(vn) != 1: continue
        vn = vn[0]
        hdr = [r for r in range(1, 8) if ws.cell(r, 2).value in J['names'].values()][0]
        cols = {ws.cell(hdr, c).value: c for c in range(2, ws.max_column + 1)}
        for r in range(hdr + 1, hdr + 71):
            import datetime
            d = datetime.datetime.strptime(ws.cell(r, 1).value, '%b %Y'); m = '%04d-%02d' % (d.year, d.month)
            for s in ST:
                nchk += 1
                if not near(ws.cell(r, cols[J['names'][s['key']]]).value, R['res'][f][s['key']][m][1][vn]['net']): bad += 1
print('cells checked %d, problems %d' % (nchk, bad))
