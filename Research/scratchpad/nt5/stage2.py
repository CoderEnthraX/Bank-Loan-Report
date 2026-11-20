"""Stage 2: from stage 1's best (2024 total R; and robust: 2023-2025 positive), every one-parameter change plus the direction
(both / long only / short only); two rounds of hill-climbing on 2024 R with a 2023 + 2025 tie-break. Run: python3 -I stage2.py TF -> stage2_TF.pkl"""
import sys, os, pickle, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from multiprocessing import Pool
TF = sys.argv[1]
sys.argv = [sys.argv[0], TF, '0', '0']
import stage1 as S1
SPACE = dict(S1.SPACE, dirn=['both', 'long', 'short'])
OUT = os.path.dirname(os.path.abspath(__file__)) + '/stage2_%s.pkl' % TF


def one(c):
    import edge
    on, eng = S1.cfg_of(c)
    if c.get('dirn') == 'long': eng.update(allowShort=False)
    if c.get('dirn') == 'short': eng.update(allowLong=False)
    try: tr = edge.trades_for(TF, c['tp'], on, eng)
    except Exception as e: return c, None, repr(e)[:200]
    yr = {y: edge.stats(tr, y) for y in range(2021, 2027)}
    m24 = collections.defaultdict(float)
    for x in tr:
        if x['t'].year == 2024: m24[x['t'].month] += x['net']
    return c, dict(years=yr, m24=dict(m24), n=len(tr)), None


def k(c): return tuple(sorted(c.items()))
def score(r): y = r['years']; return y[2024]['sumR'] if y[2024]['n'] >= 20 else -1e9


if __name__ == '__main__':
    S1D = [d for d in pickle.load(open(os.path.dirname(os.path.abspath(__file__)) + '/stage1_%s.pkl' % TF, 'rb')) if d[1]]
    res = {k(c): (c, r) for c, r, e in (pickle.load(open(OUT, 'rb')) if os.path.exists(OUT) else [])}
    for c, r, e in S1D: res.setdefault(k(dict(c, dirn='both')), (dict(c, dirn='both'), r))
    good = sorted(S1D, key=lambda d: -score(d[1]))[:6]
    rob = sorted([d for d in S1D if d[1]['years'][2023]['sumR'] > 0 and d[1]['years'][2025]['sumR'] > 0], key=lambda d: -score(d[1]))[:4]
    seeds = [dict(d[0], dirn='both') for d in good + rob]
    with Pool(4) as pool:
        for rnd in range(2):
            todo = []
            for c in seeds:
                for p, vals in SPACE.items():
                    for v in vals:
                        c2 = dict(c); c2[p] = v
                        if k(c2) not in res and k(c2) not in {k(x) for x in todo}: todo.append(c2)
            print(TF, 'round', rnd + 1, 'runs', len(todo), flush=True)
            for i, (c, r, e) in enumerate(pool.imap_unordered(one, todo)):
                if r: res[k(c)] = (c, r)
                if (i + 1) % 40 == 0: pickle.dump([(c, r, None) for c, r in res.values()], open(OUT, 'wb'))
            pickle.dump([(c, r, None) for c, r in res.values()], open(OUT, 'wb'))
            allr = list(res.values())
            seeds = [c for c, r in sorted(allr, key=lambda x: -score(x[1]))[:6]] + \
                    [c for c, r in sorted([x for x in allr if x[1]['years'][2023]['sumR'] > 0 and x[1]['years'][2025]['sumR'] > 0], key=lambda x: -score(x[1]))[:4]]
    print(TF, 'stage 2 done', len(res), flush=True)
