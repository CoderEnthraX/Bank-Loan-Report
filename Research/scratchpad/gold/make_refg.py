"""ref_g.py = build/ref.py (the shared-engine twin) reading prepared gold arrays, plus per-trade best price / final stop for the TP statistics."""
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
s = open(S + '/build/ref.py').read()
R = [
 ("    P = eprep(sym); R = P['rows']; n = len(R); mt = P['mt']\n"
  "    O = [r['o'] for r in R]; H = [r['h'] for r in R]; L = [r['l'] for r in R]; C = [r['c'] for r in R]; V = [r['vwap'] for r in R]\n"
  "    T = [datetime.datetime.strptime(r['t'], '%Y-%m-%d %H:%M') for r in R]\n",
  "    P = eprep(sym); mt = P['mt']\n"
  "    O, H, L, C, V = P['O'], P['H'], P['L'], P['C'], P['V']; n = len(O)\n"
  "    T = P['T']   # IST datetimes of the bar opens\n"),
 ("    w = weights(sym) if p['noChase'] else None\n", "    w = P['W'] if (p['noChase'] or p.get('needW')) else None\n"),
 ("            prevHit = tpHit; tpHit = max(tpHit, reached)\n",
  "            prevHit = tpHit; tpHit = max(tpHit, reached)\n"
  "            if not stopHit: bestPx = max(bestPx, H[i]) if isL else min(bestPx, L[i])\n"),
 ("                lastExit = i; st = 0; cur.update(exit=i, res=res)\n",
  "                lastExit = i; st = 0; cur.update(exit=i, res=res, best=bestPx, stpX=stp)\n"),
 ("                cur = dict(dir=d, arm=armBar, fill=i, entry=lim, stop=stp, exit=None, res=None, half=trHalf, ghost=trGhost, vwd=trVwd, vwdA=trVwdA); trades.append(cur)\n",
  "                cur = dict(dir=d, arm=armBar, fill=i, entry=lim, stop=stp, exit=None, res=None, half=trHalf, ghost=trGhost, vwd=trVwd, vwdA=trVwdA); trades.append(cur)\n"
  "                bestPx = lim\n"),
 ("                    lastExit = i; st = 0; cur.update(exit=i, res=-1.0)\n",
  "                    lastExit = i; st = 0; cur.update(exit=i, res=-1.0, best=lim, stpX=stp)\n"),
]
for a, b in R:
    assert s.count(a) == 1, a[:70]
    s = s.replace(a, b)
s = s.replace("    trades = []; cur = None\n", "    trades = []; cur = None; bestPx = None\n", 1)
s = s[:s.index("if __name__ == '__main__':")]
open(S + '/gold/ref_g.py', 'w').write(s); print('ref_g.py written')
