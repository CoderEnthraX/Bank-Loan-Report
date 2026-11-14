"""The 11 strategies on gold (M1 execution unless a chart TF is given): the numbers for the README / the user."""
import sys, json, numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fractal')
import engine as EN
from run9 import T9
P11 = [('M5', 30, 65, -0.05, 1.0, 1.0, 0.2, 0.0), ('M15', 20, 40, -0.01, 1.0, 3.0, 0.2, 0.1)]
ALL = T9 + P11
json.dump([list(p) for p in P11], open('pick_10_11.json', 'w'))


def slrun(tr):
    st = mx = 0
    for x in tr[:, 4]:
        if x == 2: st += 1; mx = max(mx, st)
        elif x == 1: st = 0
    return mx


if __name__ == '__main__':
    ctf = sys.argv[1] if len(sys.argv) > 1 else 'M1'
    B = EN.load(); t = EN.chart(B, ctf)[0]
    print('| # | TF | R / L | offset | SL | TP | BE | salvage | trades | win % | TP hits | net % | net R | PF | max DD R | SL in a row | high-first R | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |')
    print('|' + '---|' * 23)
    for s, p in enumerate(ALL, 1):
        if EN.TF_SEC[p[0]] < EN.TF_SEC[ctf]: continue
        tr = EN.run(B, ctf, *p); st = EN.stats(tr, p[4]); hf = EN.stats(EN.run(B, ctf, *p, pm=2), p[4])
        yr = [EN.stats(tr, p[4], t=t, y0=y, y1=y)['R'] for y in range(2021, 2027)]
        print('| %d | %s | %d / %d | %+.3f%% | %.2f%% | %.2f%% | %.2f%% | %.2f%% | %d | %.1f | %d | %+.1f%% | %+.1f | %.2f | %.1f | %d | %+.1f | %s |' % (
            s, p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], st['n'], st['win'], int((tr[:, 4] == 1).sum()), st['pct'], st['R'], st['pf'], st['ddR'], slrun(tr), hf['R'],
            ' | '.join('%+.1f' % x for x in yr)))
