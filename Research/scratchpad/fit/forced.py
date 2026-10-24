"""Teacher-forced evaluation: my arm/fill logic runs, but position/day state follows the ORIGINAL's trades.
Each original fill is a positive; each fill of mine that the original did not make (while the original was flat) is a false positive."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine2 import prepare, BASE, hh, ll
from volrec import recover
from adxfit import dmi
from engine import rma, rtick
from gtscore import load_gt, covered
def eval_symbol(P, c, gts, windows, sym):
    O, H, L, C, V, T = P['O'], P['H'], P['L'], P['C'], P['V'], P['T']; n = len(O); mt = P['mt']
    if ('atr', c['atrLen']) not in P: P[('atr', c['atrLen'])] = rma(P['tr'], c['atrLen'])
    atr = P[('atr', c['atrLen'])]; idx = {t: i for i, t in enumerate(T)}
    G = []
    for g in gts:
        f = idx.get(g['fill'])
        if f is None: continue
        x = idx.get(g['exit']) if g.get('exit') else None
        G.append(dict(f=f, x=x, d=g['d'], e=g['entry'], s=g['stop'], out=g.get('out')))
    recover(sym)
    if 'dmi' not in P: P['dmi'] = dmi(P['rows'], 14, 14)
    dip, dim, _ = P['dmi']; vsd = P['vsd']
    G.sort(key=lambda g: g['f'])
    fills = {(g['f'], g['d']): g for g in G}
    busy = set()
    for k, g in enumerate(G):
        end = g['x'] if g['x'] is not None else (G[k + 1]['f'] - 1 if k + 1 < len(G) else g['f'])
        for i in range(g['f'], end + 1): busy.add(i)
    exits = {g['x']: g for g in G if g['x'] is not None}
    TP = FP = 0; FN = []; fp_list = []; tp_list = []; entry_err = 0.0
    st = 0; armBar = lim = None; arm_d = 0; lastExit = None; lastRes = 0
    mx = max(c['brkLen'], c['entryLen']) + 1
    matched = set()
    fillset = {g['f'] for g in G}
    dayFills = dayLoss = 0; dayR = 0.0; lastWinTP = None; sdl = 0; sdlDir = 0
    for i in range(mx, n):
        if P['daystart'][i]: dayFills = dayLoss = 0; dayR = 0.0; sdl = 0
        if not covered(windows, sym, T[i]):
            st = 0; continue
        if i in exits:
            gx = exits[i]; lastExit = i; lastRes = 1 if gx.get('out') == 'tp4' else -1
            dayR += 2 if lastRes > 0 else -1; dayLoss += lastRes < 0
            lastWinTP = None
            if lastRes > 0 and gx['e'] and gx['s']: lastWinTP = (gx['d'], gx['e'] + 2 * (gx['e'] - gx['s']))
            if lastRes < 0: sdl = sdl + 1 if gx['d'] == sdlDir else 1; sdlDir = gx['d']
            else: sdl = 0
        # pending limit (checked before the busy test: the fill bar itself is busy)
        if st != 0 and i > armBar:
            touched = L[i] <= lim if st > 0 else H[i] >= lim
            if touched:
                if (i, st) in fills:
                    TP += 1; matched.add(i); tp_list.append((T[i], st)); g = fills[(i, st)]
                    if g['e']: entry_err += abs(lim - g['e']) / atr[armBar]
                else:
                    FP += 1; fp_list.append((T[i], 'L' if st > 0 else 'S', T[armBar]))
                st = 0
            elif i - armBar >= c['retest']:
                st = 0
        if i in fillset: dayFills += 1
        if i in busy:
            st = 0; continue
        if dayFills >= c['maxFills']: continue
        if c['maxLossDay'] and dayLoss >= c['maxLossDay']: continue
        if c['maxDayR'] and dayR <= -c['maxDayR']: continue
        if c.get('sameDirLoss') and sdl >= c['sameDirLoss']: continue
        # arm
        if lastExit is not None:
            cd = c['cooldown']
            if lastRes > 0 and c['coolWin'] is not None: cd = c['coolWin']
            if lastRes < 0 and c['coolLoss'] is not None: cd = c['coolLoss']
            if i - lastExit < max(cd, 1): continue
        if P['sinceStart'][i] < c['minBars']: continue
        if st != 0 and c['rearm'] == 'ignore': continue
        A = atr[i]
        if A is None or A <= 0: continue
        o, h, l, cl = O[i], H[i], L[i], C[i]; rng = h - l
        if rng <= 0: continue
        body = abs(cl - o)
        if rng < c['dispAtr'] * A or body / rng * 100 < c['bodyPct'] or body < c['bodyAtr'] * A: continue
        vw = V[i]; bull = bear = False
        if cl > o and (h - cl) / rng * 100 <= c['closePct']: bull = cl > (hh(H, i, c['brkLen']) if c.get('brkSrc', 'wick') == 'wick' else (max(C[i - c['brkLen']:i]) if c['brkSrc'] == 'close' else max(max(O[x], C[x]) for x in range(i - c['brkLen'], i)))) + c['brkMin'] * A
        if cl < o and (cl - l) / rng * 100 <= c['closePct']: bear = cl < (ll(L, i, c['brkLen']) if c.get('brkSrc', 'wick') == 'wick' else (min(C[i - c['brkLen']:i]) if c['brkSrc'] == 'close' else min(min(O[x], C[x]) for x in range(i - c['brkLen'], i)))) - c['brkMin'] * A
        if c['vwap'] == 'close': bull = bull and cl > vw; bear = bear and cl < vw
        elif c['vwap'] == 'open': bull = bull and o > vw and cl > vw; bear = bear and o < vw and cl < vw
        elif c['vwap'] == 'mid': bull = bull and (o + cl) / 2 > vw; bear = bear and (o + cl) / 2 < vw
        if c.get('zMin'):
            z = (cl - vw) / vsd[i] if vsd[i] else 0
            bull = bull and z >= c['zMin']; bear = bear and -z >= c['zMin']
        if c.get('noSunUTC') and P['dowutc'][i] == 6: bull = bear = False
        if c.get('momMin'):
            mn = c.get('momN', 10); mv = cl - C[i - mn]
            bull = bull and mv >= c['momMin'] * A; bear = bear and -mv >= c['momMin'] * A
        if c.get('vsLag'):
            lg = c['vsLag']
            if P['sinceStart'][i] >= lg:
                sl = V[i] - V[i - lg]
                bull = bull and sl > c.get('vsMin', 0.0) * A; bear = bear and -sl > c.get('vsMin', 0.0) * A
        if c.get('diAlign'):
            bull = bull and dip[i] >= dim[i]; bear = bear and dim[i] >= dip[i]
        if c.get('pivA'):
            key = ('piv', c['pivA'], c['pivB'])
            if key not in P:
                a_, b_ = c['pivA'], c['pivB']; ph = [None] * n; pl = [None] * n; lh = ll_ = None
                for j in range(n):
                    p = j - b_
                    if p - a_ >= 0:
                        if all(H[q] < H[p] for q in range(p - a_, p)) and all(H[q] <= H[p] for q in range(p + 1, j + 1)): lh = H[p]
                        if all(L[q] > L[p] for q in range(p - a_, p)) and all(L[q] >= L[p] for q in range(p + 1, j + 1)): ll_ = L[p]
                    ph[j] = lh; pl[j] = ll_
                P[key] = (ph, pl)
            ph, pl = P[key]
            bull2 = cl > o and (h - cl) / rng * 100 <= c['closePct'] and ph[i - 1] is not None and cl > ph[i - 1]
            bear2 = cl < o and (cl - l) / rng * 100 <= c['closePct'] and pl[i - 1] is not None and cl < pl[i - 1]
            if c['vwap'] == 'close': bull2 = bull2 and cl > vw; bear2 = bear2 and cl < vw
            if c.get('vsLag') and P['sinceStart'][i] >= c['vsLag']:
                sl = V[i] - V[i - c['vsLag']]; bull2 = bull2 and sl > 0; bear2 = bear2 and sl < 0
            if c.get('momMin'):
                mv = cl - C[i - 10]; bull2 = bull2 and mv >= c['momMin'] * A; bear2 = bear2 and -mv >= c['momMin'] * A
            if c.get('noSunUTC') and P['dowutc'][i] == 6: bull2 = bear2 = False
            if c.get('pivOnly'): bull, bear = bull2, bear2
            else: bull, bear = bull or bull2, bear or bear2
        if not (bull or bear): continue
        d = 1 if bull else -1
        if st != 0 and c['rearm'] == 'samedir' and st == d: continue
        mid = (o + cl) / 2
        e = max(mid, hh(H, i, c['entryLen'])) if d > 0 else min(mid, ll(L, i, c['entryLen']))
        if st != 0 and c['rearmBetter'] and st == d and d * (e - lim) < 0: continue
        if c.get('reTP') and lastWinTP and lastWinTP[0] == d and d * (e - lastWinTP[1]) < 0: continue
        st = d; armBar = i; lim = e
    for g in G:
        if g['f'] not in matched and covered(windows, sym, T[g['f']]): FN.append((T[g['f']], 'L' if g['d'] > 0 else 'S'))
    return TP, FP, FN, fp_list, entry_err
def evaluate(cfg, tr, win, detail=False):
    c = dict(BASE); c.update(cfg)
    tot = dict(TP=0, FP=0, FN=0, eerr=0.0); det = []
    for sym in sorted({t['sym'] for t in tr}):
        P = prepare(sym)
        TP, FP, FN, fpl, ee = eval_symbol(P, c, [t for t in tr if t['sym'] == sym], [w for w in win if w['sym'] == sym], sym)
        tot['TP'] += TP; tot['FP'] += FP; tot['FN'] += len(FN); tot['eerr'] += ee
        if detail: det.append((sym, FN, fpl))
    tot['obj'] = tot['TP'] * 3 - tot['FP'] * 2 - tot['FN'] * 2 - tot['eerr']
    return (tot, det) if detail else tot
if __name__ == '__main__':
    tr, win = load_gt(os.path.join(os.path.dirname(__file__), '..', 'gt', 'final'))
    cfg = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    r, det = evaluate(cfg, tr, win, True); print(r)
    for sym, FN, fpl in det: print(sym, 'MISSED:', FN, '\n      FALSE+:', fpl)
