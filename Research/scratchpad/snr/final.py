"""Final picks per timeframe and target, by train-only rules (2021-2023; the test 2024-26 is only reported):
  robust = the highest lower bound of the pooled 2021-23 edge (edge - 1 standard error), with a positive edge in 2021-22 and in 2023 and
           enough trades; top = the highest selection score (min edge of 2021-22 and 2023).
Pool: all random-search configurations + the refined ones. Run: python3 -I final.py -> final.pkl"""
import sys, glob, pickle, numpy as np
HERE = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/snr'
sys.path.insert(0, HERE)
import analyze as A, search as S

TFS = (5, 15, 60, 120, 180)
NMIN = {5: 400, 15: 150, 60: 80, 120: 60, 180: 40}


def pool(tf):
    res = A.load(tf)
    for f in glob.glob(HERE + '/refine_%d_*.pkl' % tf):
        for d in pickle.load(open(f, 'rb')):
            s, kw, lv, fl, post, m = d['best']
            res.append((kw, lv, fl, post, m))
    return res


def lcb(m, X, tf):
    na, nb = m['A_n_%g' % X], m['B_n_%g' % X]
    if na + nb < NMIN[tf] or na == 0 or nb == 0:
        return -np.inf
    rnd = 1 / (1 + X)
    if not (m['A_acc_%g' % X] > rnd and m['B_acc_%g' % X] > rnd):
        return -np.inf
    acc = (m['A_acc_%g' % X] * na + m['B_acc_%g' % X] * nb) / (na + nb)
    return acc - rnd - np.sqrt(rnd * (1 - rnd) / (na + nb))


def main():
    out = {}
    for tf in TFS:
        res = pool(tf)
        for X in (0.5, 1.0):
            L = np.array([lcb(r[4], X, tf) for r in res]); Sc = np.array([A.score(r[4], X, tf) for r in res])
            qr = int(np.argmax(L)); qt = int(np.argmax(np.where(np.isfinite(Sc), Sc, -9)))
            out[(tf, X)] = dict(robust=res[qr], top=res[qt], lcb=L[qr], sel=Sc[qt], npool=len(res))
            for nm, q in (('robust', qr), ('top', qt)):
                m = res[q][4]
                print('TF %3d X %.1f %-6s | A %4.1f%% (%d) B %4.1f%% (%d) | TEST %4.1f%% (%d) edge %+5.1f net %+.3f | %s' % (
                    tf, X, nm, 100 * m['A_acc_%g' % X], m['A_n_%g' % X], 100 * m['B_acc_%g' % X], m['B_n_%g' % X], 100 * m['T_acc_%g' % X],
                    m['T_n_%g' % X], 100 * (m['T_acc_%g' % X] - 1 / (1 + X)), m['T_net_%g' % X], A.desc(*res[q][:4])[:150]), flush=True)
    pickle.dump(out, open(HERE + '/final.pkl', 'wb'))


if __name__ == '__main__':
    main()
