"""Best monthly settings, final choice (choice period 2021-23 only, then the test period 2024-26 reported):
  pool      ARS: candidates with no blown month and the deepest drop inside a month <= $300 in 2021-23 (calendar), best 600 by fewest losing
            months then profit; GRID: the best 600 of choose.py's lists (subsets x money)
  versions  calendar months, mid-month windows (15th - 14th), calendar with costs 0.30 per oz (robust.py)
  rule      in 2021-23 in ALL three versions: no blown window and the deepest drop inside a window <= $300 (30 % of the $1,000);
            then the fewest losing windows in the worst version, then the most calendar profit
Also: the best setting without any recovery (fixed base) for each family, and the user's own settings' best.
Output: mcej3/final.pkl + final.txt"""
import sys, pickle
import numpy as np
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/mcej3')
import choose as CH, robust as RB, search as SE
DDMAX = float(sys.argv[1]) if len(sys.argv) > 1 else 300.0


def ok(c):
    return all(c['sc'][v]['IN']['blown'] == 0 and c['sc'][v]['IN']['dd'] <= DDMAX for v in ('cal', 'mid', 'cost'))


def key(c):
    return (max(c['sc'][v]['IN']['lose'] for v in ('cal', 'mid', 'cost')), -c['sc']['cal']['IN']['total'])


def line(c):
    sc = c['sc']; f = lambda v, p: '%d loss / %d profit %+.0f, worst %+.0f, drop %.0f' % (sc[v][p]['lose'], sc[v][p]['prof'], sc[v][p]['total'], sc[v][p]['worst'], sc[v][p]['dd'])
    return ('%s\n   2021-23  cal %s | mid %s | cost %s\n   2024-26  cal %s | mid %s | cost %s' % (
        c['name'], f('cal', 'IN'), f('mid', 'IN'), f('cost', 'IN'), f('cal', 'OUT'), f('mid', 'OUT'), f('cost', 'OUT')))


if __name__ == '__main__':
    import multiprocessing as mp
    A, _ = CH.ars(); G = CH.grid()
    Apool = sorted([c for c in A if c['IN']['blown'] == 0 and c['IN']['active'] >= 30 and c['IN']['dd'] <= DDMAX],
                   key=lambda c: (c['IN']['lose'], -c['IN']['total']))[:600]
    Gpool = CH.rank(G, 'steady')[:600] + CH.rank(G, 'profit')[:300]
    seen = set(); Gpool = [c for c in Gpool if not (c['name'] in seen or seen.add(c['name']))]
    noRecA = sorted([c for c in A if SE.RULES[SE.RUNS[c['run']][1]][1] == 'Off' and c['IN']['blown'] == 0 and c['IN']['active'] >= 30],
                    key=lambda c: (c['IN']['lose'], -c['IN']['total']))[:60]
    noRecG = sorted([c for c in G if SE.RULES[SE.RUNS[c['run']][1]][1] == 'Off'], key=lambda c: (c['IN']['lose'], -c['IN']['total']))[:60]
    youA = sorted([c for c in A if c['key'].split('-')[1] == 'you' and c['IN']['blown'] == 0 and c['IN']['active'] >= 30 and c['IN']['dd'] <= DDMAX],
                  key=lambda c: (c['IN']['lose'], -c['IN']['total']))[:200]
    out = {}; L = []
    with mp.Pool(4) as pool:
        for nm, P in (('ARS', Apool), ('GRID', Gpool), ('ARS no recovery', noRecA), ('GRID no recovery', noRecG), ('ARS your settings', youA)):
            R = pool.map(RB.evaluate, P, chunksize=6)
            good = sorted([c for c in R if ok(c)], key=key)
            out[nm] = dict(all=R, good=good)
            L.append('\n=== %s: %d candidates, %d pass the 2021-23 rule (no blown window, drop <= $%d in calendar / mid / cost) ===' % (nm, len(R), len(good), DDMAX))
            for c in good[:8]: L.append(line(c))
            if len(good) >= 10:
                top = good[:30]
                L.append('   top 30 in the TEST period (calendar): losing months median %d (min %d, max %d); total median %+.0f; %d of 30 positive; worst month median %+.0f; deepest drop median %.0f' % (
                    np.median([c['sc']['cal']['OUT']['lose'] for c in top]), min(c['sc']['cal']['OUT']['lose'] for c in top), max(c['sc']['cal']['OUT']['lose'] for c in top),
                    np.median([c['sc']['cal']['OUT']['total'] for c in top]), sum(1 for c in top if c['sc']['cal']['OUT']['total'] > 0),
                    np.median([c['sc']['cal']['OUT']['worst'] for c in top]), np.median([c['sc']['cal']['OUT']['dd'] for c in top])))
    tag = '' if DDMAX == 300.0 else '_%d' % DDMAX
    pickle.dump(out, open(S + '/mcej3/final%s.pkl' % tag, 'wb'))
    open(S + '/mcej3/final%s.txt' % tag, 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
