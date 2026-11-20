"""Stage 3: every money rule of the EA (gold/recovery.py MODES, Risk and Profit; C-family with N 1 / 3 / 5) on chosen settings' real trades:
2024 as one year from START and every 2024 month fresh from START; the same for 2023 and 2025 (honesty check). Leverage 1:100, costs
included (the trade's net R). Input: cands.pkl [(name, TF, config)]; output stage3.pkl + stage3.txt"""
import sys, os, pickle, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/gold')
from multiprocessing import Pool
import recovery as RC
START = float(os.environ.get('START', '1000')); BASE = float(os.environ.get('BASE', '20'))


def trades_of(tf, c):
    sys.argv = [sys.argv[0], tf, '0', '0']
    import stage2 as S2
    S2.TF = tf
    return S2_trades(S2, c)


def S2_trades(S2, c):
    import edge, stage1 as S1
    on, eng = S1.cfg_of(c)
    if c.get('dirn') == 'long': eng.update(allowShort=False)
    if c.get('dirn') == 'short': eng.update(allowLong=False)
    return edge.trades_for(S2.TF, c['tp'], on, eng)


def tup(x, tp):
    d = x['dist']; rmin = d + 0.23; D = tp * d / (d + 0.23)
    return (x['net'], 0.0, None, None, 100.0 * (d + 0.23) / x['px'], rmin, None, 2 * rmin, D)


def jobs():
    for sb in ('risk', 'profit'):
        for mode in RC.MODES:
            for cn in ((1, 3, 5) if mode in RC.CFAM else (1,)):
                yield sb, mode, cn


def work(arg):
    name, tf, c = arg
    tr = trades_of(tf, c); out = []
    for sb, mode, cn in jobs():
        row = dict(name=name, tf=tf, sb=sb, mode=mode, cn=cn)
        for y in (2023, 2024, 2025):
            ty = [tup(x, c['tp']) for x in tr if x['t'].year == y]
            r = RC.simulate(ty, mode, base=BASE, exitR=c['tp'], start=START, cN=cn, sizeBy=sb)
            months = sorted({x['t'].month for x in tr if x['t'].year == y}); nets = []
            for m in months:
                tm = [tup(x, c['tp']) for x in tr if x['t'].year == y and x['t'].month == m]
                rm = RC.simulate(tm, mode, base=BASE, exitR=c['tp'], start=START, cN=cn, sizeBy=sb); nets.append(rm['net'])
            row[y] = dict(net=r['net'], dd=r['maxDDpct'], ruined=r['ruined'], mnet=sum(nets), mpos=sum(v > 0 for v in nets), mn=len(nets), mworst=min(nets) if nets else 0.0)
        out.append(row)
    return out


if __name__ == '__main__':
    C = pickle.load(open(os.environ.get('CANDS', 'cands.pkl'), 'rb')); OUTN = os.environ.get('OUTN', 'stage3')
    rows = []
    with Pool(4) as pool:
        for o in pool.imap_unordered(work, C): rows += o; print('done', o[0]['name'], flush=True)
    pickle.dump(rows, open(OUTN + '.pkl', 'wb'))
    L = []
    for name in [c[0] for c in C]:
        rs = [r for r in rows if r['name'] == name]
        L.append('\n%s (%s): 2024 one year from $%d | 2024 months fresh: total, profitable months, worst | 2023 / 2025 one year' % (name, rs[0]['tf'], START))
        for r in sorted(rs, key=lambda r: -r[2024]['net'])[:12]:
            a, b, c3 = r[2024], r[2023], r[2025]
            L.append('  %-40s %-6s N%d  %+9.0f dd %3.0f%%%s | %+8.0f %2d/%2d %+6.0f | %+8.0f / %+8.0f' % (r['mode'][:40], r['sb'], r['cn'], a['net'], 100 * a['dd'], ' BLOWN' if a['ruined'] else '', a['mnet'], a['mpos'], a['mn'], a['mworst'], b['net'], c3['net']))
    open(OUTN + '.txt', 'w').write('\n'.join(L)); print('\n'.join(L))
