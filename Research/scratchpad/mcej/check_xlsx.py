"""Checks the recalculated workbooks against the simulation pickles: every formula total / count / year / balance / summary link and the grid's
by-strategy Check row. Usage: check_xlsx.py OUTDIR"""
import sys, pickle
from openpyxl import load_workbook
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/mcej')
import build_xlsx as BX
OUT = sys.argv[1]
CF = BX.CONFIGS; C0 = BX.C0
bad = []; nchk = [0]


def eq(a, b, tol=0.011, what=''):
    nchk[0] += 1
    if isinstance(b, str) or isinstance(a, str):
        if a != b: bad.append((what, a, b))
        return
    if a is None or abs(a - b) > tol: bad.append((what, a, b))


def find_row(ws, label, start=1, col=1):
    for r in range(start, ws.max_row + 1):
        if ws.cell(r, col).value == label: return r
    raise KeyError(label)


def check_monthly(ws, data, M, start, cnt, tag):
    """block 1 values, stats, years, balance, block 5 stats vs data (cont / fresh)"""
    first = 8
    for i, m in enumerate(M):
        eq(ws.cell(first + i, 2).value, cnt[m]['n'], 0, tag + ' trades ' + m)
    r_tot = find_row(ws, 'Total 2021-2026')
    for j, cfg in enumerate(CF):
        col = C0 + j; d = data[cfg]
        nets = [d['cont'][m]['net'] for m in M]
        eq(ws.cell(r_tot, col).value, sum(x for x in nets), 0.005, '%s total %s' % (tag, cfg))
        eq(ws.cell(r_tot + 1, col).value, sum(1 for x in nets if x > 0), 0, '%s prof %s' % (tag, cfg))
        eq(ws.cell(r_tot + 2, col).value, sum(1 for x in nets if x < 0), 0, '%s loss %s' % (tag, cfg))
        eq(ws.cell(r_tot + 3, col).value, min(x for x in nets), 0.005, '%s min %s' % (tag, cfg))
        eq(ws.cell(r_tot + 4, col).value, max(x for x in nets), 0.005, '%s max %s' % (tag, cfg))
        # years
        ry = find_row(ws, '2021', r_tot)
        for k, y in enumerate(('2021', '2022', '2023', '2024', '2025', '2026')):
            eq(ws.cell(ry + k, col).value, sum(d['cont'][m]['net'] for m in M if m[:4] == y), 0.005, '%s year %s %s' % (tag, y, cfg))
        # balance at the end = start + total, and = the simulation's balance
        rb = find_row(ws, 'Lowest month-end balance', ry) - 1
        eq(ws.cell(rb, col).value, start + sum(nets), 0.005, '%s end balance %s' % (tag, cfg))
        eq(ws.cell(rb, col).value, d['cont'][M[-1]]['end'], 0.005, '%s end balance vs sim %s' % (tag, cfg))
        # deepest drop (values) max
        rd = find_row(ws, 'Deepest month', rb)
        eq(ws.cell(rd, col).value, max(d['cont'][m]['drop'] for m in M), 0.005, '%s drop %s' % (tag, cfg))
        # block 5
        rf = find_row(ws, 'Total 2021-2026', rd)
        fn = [d['fresh'][m]['net'] for m in M]
        eq(ws.cell(rf, col).value, sum(x for x in fn), 0.005, '%s fresh total %s' % (tag, cfg))
        eq(ws.cell(rf + 2, col).value, sum(1 for x in fn if x < 0), 0, '%s fresh loss %s' % (tag, cfg))
    return r_tot


def main():
    G = pickle.load(open(S + '/mcej/grid_money.pkl', 'rb')); M = G['months']
    wb = load_workbook(OUT + '/Gold_Monthly_Crooks_EJ_Fractal_Grid.xlsx', data_only=True)
    print('grid sheets:', wb.sheetnames)
    for ctf in ('M5', 'M15'):
        C = G['charts'][ctf]
        data = {cfg: dict(cont=C['combined'][cfg]['cont'], fresh=C['combined'][cfg]['fresh']) for cfg in CF}
        check_monthly(wb['%s chart' % ctf], data, M, 10000.0 * len(C['ks']), C['counts'], 'grid ' + ctf)
        ws = wb['%s by strategy' % ctf]
        rc = find_row(ws, 'Check')
        for j in range(len(CF)): eq(ws.cell(rc, C0 + j).value, 0.0, 0.0, 'grid %s check row %s' % (ctf, CF[j]))
        ra = find_row(ws, 'All')
        for j, cfg in enumerate(CF): eq(ws.cell(ra, C0 + j).value, C['combined'][cfg]['whole']['net'], 0.005, 'grid %s All %s' % (ctf, cfg))
    sm = wb['Summary']
    r = find_row(sm, 'M5 chart', 4)
    for j, cfg in enumerate(CF):
        eq(sm.cell(r, C0 + j).value, G['charts']['M5']['combined'][cfg]['whole']['net'], 0.005, 'grid summary M5 total %s' % (cfg,))
        eq(sm.cell(r + 1, C0 + j).value, G['charts']['M15']['combined'][cfg]['whole']['net'], 0.005, 'grid summary M15 total %s' % (cfg,))
    # ARS
    A = pickle.load(open(S + '/mcej/ars_money.pkl', 'rb')); ST = A['strategies']
    wb = load_workbook(OUT + '/Gold_Monthly_Crooks_EJ_Auction_Retest.xlsx', data_only=True)
    print('ARS sheets:', wb.sheetnames)
    for key, st in ST.items():
        data = {cfg: dict(cont=st['res'][cfg]['cont'], fresh=st['res'][cfg]['fresh']) for cfg in CF}
        check_monthly(wb[key], data, M, 10000.0, st['counts'], 'ars ' + key)
    for tf in ('M5', 'M15'):
        sm = wb['Summary %s' % tf]; keys = [k for k in ST if ST[k]['tf'] == tf]
        r1 = find_row(sm, keys[0], 4)
        for i, k in enumerate(keys):
            w = ST[k]['res']
            for j, cfg in enumerate(CF):
                eq(sm.cell(r1 + i, C0 + j).value, w[cfg]['whole']['net'], 0.005, 'ars summary %s total %s' % (k, cfg))
            best = max(CF, key=lambda c: w[c]['whole']['net'])
            eq(sm.cell(r1 + i, BX.CL + 2).value, BX.cfgname(best), None, 'ars best %s' % k)
        # months in loss block + its best (min) column
        rl = find_row(sm, 'Months in loss (of 70)', r1)
        r2 = find_row(sm, keys[0], rl)
        for i, k in enumerate(keys):
            w = ST[k]['res']
            for j, cfg in enumerate(CF):
                eq(sm.cell(r2 + i, C0 + j).value, sum(1 for m in M if w[cfg]['cont'][m]['net'] < 0), 0, 'ars summary %s loss %s' % (k, cfg))
            mn = min(sum(1 for m in M if w[c]['cont'][m]['net'] < 0) for c in CF)
            eq(sm.cell(r2 + i, BX.CL + 3).value, mn, 0, 'ars fewest losing %s' % k)
    print('checks: %d, problems: %d' % (nchk[0], len(bad)))
    for b in bad[:30]: print('  ', b)


if __name__ == '__main__':
    main()
