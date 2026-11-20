"""Best settings per timeframe, 2021 - Sep 2026 (asked 2026-11-20). Your EA rules (nt5/edge.trades_for). Every setting keeps its R per month and
per year, the trade count and the largest drawdown of its R curve. Score = total R - 0.5 x max drawdown (R), at least MINTR trades.
Random NRAND settings (plus seeds), then ROUNDS hill-climb rounds (every one-setting change of the best 8 by score and the best 4 picked on
2021-2023 only). Run: python3 -I search.py TF NRAND ROUNDS [seed] -> res_TF.pkl (resumes)."""
import sys, os, random, pickle, collections
HERE = os.path.dirname(os.path.abspath(__file__)); S = os.path.dirname(HERE)
sys.path.insert(0, S + '/nt5')
from multiprocessing import Pool
TF, NRAND, ROUNDS = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]); SEED = int(sys.argv[4]) if len(sys.argv) > 4 else 7
sys.argv = [sys.argv[0], TF, '0', '0']
import stage1 as S1
OUT = HERE + '/res_%s.pkl' % TF
MINTR = {'M1': 200, 'M5': 150, 'M15': 100, 'H1': 60, 'H4': 30, 'D1': 20}[TF]
SPACE = dict(S1.SPACE, dirn=['both', 'long', 'short'])
if TF in ('H4', 'D1'): SPACE = dict(SPACE, hours=[None, (600, 2300)], kz=[None, 'user'], stopAtr=[1.0, 1.8, 2.4, 3.0, 4.0])


def cfg_eng(c):
    on, eng = S1.cfg_of(c)
    if c.get('dirn') == 'long': eng.update(allowShort=False)
    if c.get('dirn') == 'short': eng.update(allowLong=False)
    return on, eng


def one(c):
    import edge
    on, eng = cfg_eng(c)
    try: tr = edge.trades_for(TF, c['tp'], on, eng)
    except Exception as e: return c, None
    mon = collections.defaultdict(float); yr = collections.defaultdict(float); eq = pk = dd = 0.0
    for x in tr:
        mon[(x['t'].year, x['t'].month)] += x['net']; yr[x['t'].year] += x['net']
        eq += x['net']; pk = max(pk, eq); dd = max(dd, pk - eq)
    tot = sum(x['net'] for x in tr)
    return c, dict(n=len(tr), tot=tot, dd=dd, mon=dict(mon), yr=dict(yr), wr=(sum(x['net'] > 0 for x in tr) / len(tr) if tr else 0.0))


def score(r, years=None):
    if r is None or r['n'] < MINTR: return -1e9
    if years is None: return r['tot'] - 0.5 * r['dd']
    return sum(v for y, v in r['yr'].items() if y in years)


def k(c): return tuple(sorted((a, str(b)) for a, b in c.items()))


if __name__ == '__main__':
    res = {}
    if os.path.exists(OUT): res = {k(c): (c, r) for c, r in pickle.load(open(OUT, 'rb'))}
    rng = random.Random(SEED); todo = []
    U = dict(stopAtr=1.8, entryMode='model', entryPct=25.0, chop=None, hours=(600, 2300), kz='user', days='TWT', vw='session', momAtr=0.85, mv=None, dirn='both')
    for tp in SPACE['tp']: todo.append(dict(U, tp=tp))
    for f in ('stage2_%s.pkl' % TF,):                       # seeds: the 2024 search's best settings by every year
        p = S + '/nt5/' + f
        if os.path.exists(p):
            prev = [d for d in pickle.load(open(p, 'rb')) if d[1]]
            for c, r, e in sorted(prev, key=lambda d: -sum(v['sumR'] for v in d[1]['years'].values()))[:25]: todo.append(dict(c))
    while len(todo) < NRAND + 40: todo.append({a: rng.choice(v) for a, v in SPACE.items()})
    def run(batch, tag):
        batch = [c for c in batch if k(c) not in res]; seen = set(); b2 = []
        for c in batch:
            if k(c) not in seen: seen.add(k(c)); b2.append(c)
        print(TF, tag, 'runs', len(b2), flush=True)
        with Pool(4) as pool:
            for i, (c, r) in enumerate(pool.imap_unordered(one, b2)):
                res[k(c)] = (c, r)
                if (i + 1) % 25 == 0: pickle.dump(list(res.values()), open(OUT + '.tmp', 'wb')); os.replace(OUT + '.tmp', OUT); print(TF, tag, i + 1, flush=True)
        pickle.dump(list(res.values()), open(OUT + '.tmp', 'wb')); os.replace(OUT + '.tmp', OUT)
    run(todo, 'random')
    for rnd in range(ROUNDS):
        allr = list(res.values())
        seeds = [c for c, r in sorted(allr, key=lambda x: -score(x[1]))[:8]] + [c for c, r in sorted(allr, key=lambda x: -score(x[1], (2021, 2022, 2023)))[:4]]
        nb = []
        for c in seeds:
            for p, vals in SPACE.items():
                for v in vals:
                    c2 = dict(c); c2[p] = v; nb.append(c2)
        run(nb, 'round %d' % (rnd + 1))
    best = max(res.values(), key=lambda x: score(x[1]))
    print(TF, 'DONE', len(res), 'best score %.1f' % score(best[1]), best[0], flush=True)
