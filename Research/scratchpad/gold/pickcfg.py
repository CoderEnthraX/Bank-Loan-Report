"""Pick the recommended settings per timeframe from every configuration evaluated (stages A-E).
Profit pick : profitable after spread in 2021-23 AND 2024-26, >= 4 of 6 years positive, enough trades in both halves; best min(score A, score B).
Streak pick : the same, plus longest losing streak over 2021-2026 <= LMAX (relaxed one step at a time if nothing qualifies).
score = net R after spread / sqrt(trades) of that half."""
import sys, pickle, math
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
import anaA, labels
def load(tf):
    P = pickle.load(open(S + '/gold/greedy_pool_%s.pkl' % tf, 'rb'))
    d0 = anaA.sweep_metrics(tf)[1]['default']
    return P, max(60, int(0.2 * d0['nA'])), max(60, int(0.2 * d0['nB']))
def ok(m, minA, minB, ymin=4):
    return m['A']['n'] >= minA and m['B']['n'] >= minB and m['A']['E'] > 0 and m['B']['E'] > 0 and m['ypos'] >= ymin
def robust(m): return min(m['A']['t'], m['B']['t'])
def pick(tf, lmax=None, top=10, simple=True):
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
    return rows[:top], len(P)
def pick_streak(tf, top=10, keep=0.33):
    """shortest longest-losing-streak (2021-2026) among robust settings that keep >= keep x the profit pick's robust score;
    then the fewest changed settings within 10% of the best robust score at that streak length"""
    P, minA, minB = load(tf)
    rows = [(c, m) for c, m in P.values() if ok(m, minA, minB)]
    if not rows: return [], len(P)
    pr = pick(tf, None, 1)[0][0]; floor = min(1.0, keep * robust(pr[1])) if robust(pr[1]) > 0 else 0.0
    q = [r for r in rows if robust(r[1]) >= floor]
    L = min(r[1]['all']['maxL'] for r in q); q = [r for r in q if r[1]['all']['maxL'] == L]
    q.sort(key=lambda r: -robust(r[1])); b0 = robust(q[0][1])
    s = min([r for r in q if robust(r[1]) >= 0.9 * b0], key=lambda r: (len(labels.rows(r[0])), -robust(r[1])))
    return [s] + [r for r in q if r is not s][:top - 1], len(P)
def line(c, m):
    a, b, t = m['A'], m['B'], m['all']
    return ('%5d tr (%.2f/day) | win %5.1f%% TP1 %4.1f%% | net/tr A %+.3f B %+.3f all %+.3f | total %+6.1fR | yrs+ %d/6 | W/L %2d/%2d | %s' % (
        t['n'], t['n'] / 1490, 100 * t['win'], 100 * m['tp1'], a['E'], b['E'], t['E'], t['net'], m['ypos'], t['maxW'], t['maxL'], labels.short(c)))
if __name__ == '__main__':
    for tf in sys.argv[1].split(','):
        for lab, L in (('PROFIT', None), ('SHORTEST LOSING STREAK', 'S')):
            rows, n = pick(tf, None) if L is None else pick_streak(tf)
            print('\n==== %s  %s  (from %d evaluated configurations)' % (tf, lab, n))
            for c, m in rows: print('  ' + line(c, m))
def choose(tf):
    """{'profit': (cfg, metrics, passed), 'streak': (...)}; passed = False when no setting was profitable in both halves (then the least-bad by the weaker half)"""
    out = {}
    pr, _ = pick(tf, None, 1)
    if pr:
        out['profit'] = (pr[0][0], pr[0][1], True); st, _ = pick_streak(tf, 1); out['streak'] = (st[0][0], st[0][1], True)
        return out
    P, minA, minB = load(tf)
    rows = [(c, m) for c, m in P.values() if m['A']['n'] >= minA and m['B']['n'] >= minB]
    rows.sort(key=lambda r: -robust(r[1])); b0 = rows[0]
    out['profit'] = (b0[0], b0[1], False)
    near = rows[:50]; L = min(r[1]['all']['maxL'] for r in near); q = [r for r in near if r[1]['all']['maxL'] == L]
    out['streak'] = (q[0][0], q[0][1], False)
    return out
