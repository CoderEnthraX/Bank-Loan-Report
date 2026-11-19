"""Independent v5.0 money-management simulator written from SPEC_v50.md (usd base, cap 0, no parts / day events / leverage)."""
import math
LADDER = {'Low': (0.8, 0.10, 2.0, 0.25), 'Medium': (0.7, 0.15, 3.0, 0.30), 'High': (0.6, 0.20, 5.0, 0.35),
          'Extra high': (0.5, 0.25, 8.0, 0.40), 'Max': (0.4, 0.30, 12.0, 0.50)}
CFAM = ('Crooks C', 'Crooks E', 'Crooks J', 'Crooks K', 'Crooks L')
LADFAM = ('Crooks J', 'Crooks K')

def ladder(lad, ladT, net, peak, B0):
    if lad is None or peak < ladT: return None
    lam, phi, bmax, gam = LADDER[lad]
    C = max(0.0, net - lam * peak)
    return B0 + min((bmax - 1.0) * B0, phi * C), C, gam

def sim(trades, mode, sizeBy='risk', base=50.0, exitR=2.0, start=10000.0, recN=3, recPct=50.0, step=25.0, cSplit=3, delayN=2,
        jX=20.0, cN=1, lad=None, ladT=200.0, kMode='lots', kUsd=25.0, kPct=50.0, lZ1=2.0, lZ1N=6, lZ2=5.0, lZ2N=3, lGrow=10.0, lGrowX=4.0,
        Lbase='B0', stats=None):
    pm = sizeBy == 'profit'
    D = exitR if pm else 1.0
    B0 = base / exitR if pm else base
    eq = start; net = 0.0; peak = 0.0
    pool = 0.0; losses = 0; carried = 0.0; oscU = 1; oscP = 0.0
    crL = 0.0; crW = False; crP = cN
    out = []
    for tr in trades:
        R, c = tr[0], tr[1]
        rmin = tr[5]; kRisk = tr[7]
        B = B0
        if mode == 'Crooks L':
            if net >= peak:
                if stats is not None: stats['L_grow_checks'] = stats.get('L_grow_checks', 0) + 1
                B = B0 + min((lGrowX - 1.0) * B0, max(0.0, lGrow / 100.0 * net / D))
        rec = crW and crL > 0
        def crk(Bx):
            if mode == 'Off': return Bx
            if rec:
                x = max(Bx, crL / crP / exitR)
                if mode == 'Crooks J' or mode == 'Crooks K':
                    x = max(Bx, x * max(0.0, 1.0 - max(0.0, peak - net) / (jX * Bx)))
                return x
            if crL > 0 and mode in ('Crooks E', 'Crooks L'): return min(Bx, rmin)
            return Bx
        if mode == 'Off': r = B
        elif mode == 'Recover all losses on the next trade': r = B + pool / D
        elif mode == 'Recover losses over N trades': r = B + pool / recN / D
        elif mode == 'Recover a % of losses per trade': r = B + pool * recPct / 100.0 / D
        elif mode == 'Exact recovery at final TP': r = B + pool / exitR
        elif mode == 'Step-up (+$ per loss in a row)': r = B + step * losses / D
        elif mode == 'Delayed recovery': r = B + pool / recN / D if losses >= delayN else B
        elif mode == "Oscar's Grind":
            G = B * exitR if pm else B
            need = max(1, math.ceil((G - oscP) / (B * exitR)))
            r = B * min(oscU, need)
        elif mode == 'Rule C: carry the losses': r = max(B, carried / cSplit / D)
        elif mode in CFAM:
            r = crk(B)
            if mode in LADFAM:
                L = ladder(lad, ladT, net, peak, B0)
                if L is not None:
                    lB, C, gam = L
                    r = min(B0, rmin) if (mode != 'Crooks K' and net <= 0) else min(crk(lB), r + gam * C)
            if stats is not None and mode == 'Crooks K': stats['K_below_w' if (net < 0 and crW) else 'K_below_l' if net < 0 else 'K_above_rec' if rec else 'K_above'] = stats.get('K_below_w' if (net < 0 and crW) else 'K_below_l' if net < 0 else 'K_above_rec' if rec else 'K_above', 0) + 1
            if mode == 'Crooks K' and net < 0:
                if crW:
                    r = kRisk if kMode == 'lots' else (kUsd / D if kMode == 'usd' else B0 * kPct / 100.0)
                else:
                    r = min(B0, rmin)
        else: raise ValueError(mode)
        out.append(r)
        pnl = r * (R - c) / (1.0 + c)
        eq += pnl; net += pnl; peak = max(peak, net)
        if eq <= 0: break      # v4.9 behaviour: ruined, the run stops
        win = pnl > 0
        carried = max(0.0, carried - pnl)
        if win:
            pool = max(0.0, pool - pnl)
            if pool <= 0: losses = 0
        else:
            pool += -pnl; losses += 1
        oscP += pnl
        if oscP >= (B * exitR if pm else B): oscU = 1; oscP = 0.0
        elif win: oscU += 1
        if mode in CFAM:
            crL = max(0.0, crL - pnl)
            if crL < 0.01:
                crL = 0.0; crP = cN if mode != 'Crooks L' else 1
            else:
                if mode == 'Crooks L':
                    if win: crP = max(1, crP - 1) if rec else crP
                    else:
                        b = B0 if Lbase == 'B0' else B
                        if net < 0: dd = -net; stp = lZ1 * b; most = lZ1N
                        elif net < peak: dd = peak - net; stp = lZ2 * b; most = lZ2N
                        else: dd = 0.0; stp = 1.0; most = 1
                        if stats is not None: stats[('Lz', 'below' if net < 0 else 'mid' if net < peak else 'best', 'parts%d' % max(1, min(most, math.ceil(dd / stp - 1e-9))) if dd else 'p1')] = stats.get(('Lz', 'below' if net < 0 else 'mid' if net < peak else 'best', 'parts%d' % max(1, min(most, math.ceil(dd / stp - 1e-9))) if dd else 'p1'), 0) + 1
                        crP = 1 if dd == 0.0 else max(1, min(most, math.ceil(dd / stp - 1e-9)))
                else:
                    crP = cN if not win else (max(1, crP - 1) if rec else crP)
        crW = win
    return out
