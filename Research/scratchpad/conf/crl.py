"""Crooks L test (asked 2026-11-18) with the user's EA settings: $1,000 start, $10 base, final exit TP1 = 0.1R, hours 06:00-23:00 IST, kill zones
Asia / London / New York (New York time: kzAuto), days Tue-Thu (the user's EA), daily news window 17:45 IST for 30 min (New York time all year)
with no new trades 30 min before (InpNewsPre 30, the user's EA), force-close 23:55 IST, weekend close, no locks, no monthly restart.
EXECUTION like the EA on top of the engine's setups (M5 candles): a setup armed while the news block is on, or cancelled by it before the fill, is
not taken; an open trade is closed at the candle open when a news window starts / at 23:55 / on Saturday; the broker target has the earn-back push
(entry + 0.1R + 0.23 per oz, so a win nets 0.1R); one position at a time (a setup while the EA is still in a trade is skipped). Sizes: whole
0.01-lot steps, rounded down, at least 0.01 lot (the EA's 'trade the minimum'), 1:100 leverage. Costs 0.23 per oz (spread 0.16 + $7 a lot)."""
import sys, math, pickle, datetime as dt
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/conf'); sys.path.insert(0, S + '/bese')
import confirm as Q
from ref_gbe import ny_summer
COST = 0.23; LEVG = 100.0


def ea_trades(tp=0.1, days=(False, True, True, True, False, False, False), pre=30):
    cfg = dict(Q.USER_ENG, exitAt=1, tp1R=tp, **dict(Q.USER_ON, days=days))
    P, p, tr = Q.engine(dict(key='user', tf='M5', cfg=cfg))
    O, H, L, C, T = P['O'], P['H'], P['L'], P['C'], P['T']; n = len(O)
    def mins(t): return t.hour * 60 + t.minute
    def nshift(t): return 0 if ny_summer(t - dt.timedelta(minutes=330)) else 60
    def block(i):
        t = T[i]; s0 = (17 * 60 + 45 + nshift(t)) % 1440; cur = mins(t)
        inw = s0 <= cur < s0 + 30; diff = (s0 - cur) % 1440
        return inw or (0 < diff <= pre)
    def flat(i):                                         # at the open of candle i: a news window starts, 23:55 passes, or Saturday starts
        if i == 0: return False
        t, u = T[i], T[i - 1]; s0 = (17 * 60 + 45 + nshift(t)) % 1440
        nS = (s0 <= mins(t) < s0 + 30) and not (s0 <= mins(u) < s0 + 30)
        fc = (mins(u) < 1435 <= mins(t)) or (t.date() != u.date() and mins(u) < 1435)
        return nS or fc or (t.weekday() == 5 and u.weekday() != 5)
    out = []; busy = -1; skipped = dict(news=0, busy=0, cancel=0)
    for x in tr:
        a, f, d, E = x['arm'], x['fill'], x['dir'], x['entry']; risk = d * (E - x['stop'])
        if a + 1 <= busy: skipped['busy'] += 1; continue
        if block(a + 1): skipped['news'] += 1; continue
        if any(block(j) or flat(j) for j in range(a + 1, f + 1)): skipped['cancel'] += 1; continue
        tgt = E + d * (tp * risk + COST); stp = x['stop']; ex = None
        if (L[f] <= stp if d == 1 else H[f] >= stp): ex = (f, -1.0, 'sl')
        i = f + 1
        while ex is None and i < n:
            if flat(i): ex = (i, d * (O[i] - E) / risk - COST / risk, 'flat')     # closed at the candle open (cost paid on top: R per oz / risk)
            elif (L[i] <= stp if d == 1 else H[i] >= stp): ex = (i, -1.0, 'sl')
            elif (H[i] >= tgt if d == 1 else L[i] <= tgt): ex = (i, tp, 'tp')
            i += 1
        if ex is None: break
        # R here is AFTER costs per unit of (risk + cost) sizing: a stop-out loses exactly the $ risk (dist + 0.23 per oz)
        ei, rr, kind = ex
        out.append(dict(t=T[f], dist=risk, px=E, kind=kind, net=-1.0 if kind == 'sl' else (rr * risk / (risk + COST) if kind == 'flat' else tp * risk / (risk + COST))))
        busy = ei
    return out, skipped


def run(trades, mode, base=10.0, start=1000.0, exitR=0.1, L=None):
    """mode Off / C / E / J / L. net of a trade per $ of stop-out loss: t['net'] (a stop-out = -1). L = dict(z1Step, z1Max, z2Step, z2Max, grow, growCap)"""
    eq = start; peak = start; maxDD = 0.0; crL = 0.0; crW = False; crP = 1; months = {}; ruined = None; maxRisk = 0.0; n = 0; jPk = 0.0; net = 0.0
    for x in trades:
        mk = x['t'].strftime('%Y-%m'); months.setdefault(mk, 0.0)
        rmin = x['dist'] + COST
        units_lev = math.floor(eq * LEVG / (x['px'] * 100) / 0.01 + 1e-9)          # 1:100: lots <= equity x 100 / (price x 100 oz)
        if units_lev < 1: ruined = x['t']; break
        B = base; Np = 1
        if mode == 'L':
            if eq < start: Np = min(L['z1Max'], max(1, math.ceil((start - eq) / (L['z1Step'] * base))))
            elif eq < peak: Np = min(L['z2Max'], max(1, math.ceil((peak - eq) / (L['z2Step'] * base))))
            else: B = base + min(L['growCap'] * base, L['grow'] * (eq - start))
            crP = min(crP, Np) if crL > 0 else Np
        rec = crW and crL > 0
        if mode == 'Off': r = B
        elif rec: r = max(B, crL / (crP if mode == 'L' else 1) / exitR)
        elif crL > 0 and mode in ('E', 'L'): r = rmin                                # 0.01 lot while a loss waits for a win
        else: r = B
        if mode == 'J' and rec: r = max(B, r * max(0.0, 1.0 - (jPk - net) / (20 * B)))
        units = max(1, min(math.floor(r / rmin + 1e-9), units_lev))
        risk = units * rmin; maxRisk = max(maxRisk, risk)
        pnl = risk * x['net']; n += 1
        eq += pnl; net += pnl; months[mk] += pnl; peak = max(peak, eq); maxDD = max(maxDD, peak - eq); jPk = max(jPk, net)
        win = pnl > 0; crL = max(0.0, crL - pnl)
        if crL < 0.01: crL = 0.0
        if mode == 'L':
            if not win: crP = Np
            elif rec: crP = max(1, crP - 1)
        crW = win
        if eq <= 0: ruined = x['t']; break
    return dict(end=eq, maxDD=maxDD, maxRisk=maxRisk, months=months, n=n, ruined=ruined)


if __name__ == '__main__':
    LD = dict(z1Step=2, z1Max=6, z2Step=5, z2Max=3, grow=0.10, growCap=3)
    res = {}
    for tp in (0.1, 0.6, 2.0):
        tr, sk = ea_trades(tp)
        w = sum(1 for x in tr if x['kind'] == 'tp'); fl = sum(1 for x in tr if x['kind'] == 'flat')
        totR = sum(x['net'] for x in tr)
        print('\n=== final TP %.1fR: %d trades (2021-01 .. 2026-10), win %.1f%%, closed by news / 23:55 / weekend %d, skipped %s, total %+.1fR (1R = one stop-out incl. costs)' % (
            tp, len(tr), 100.0 * w / len(tr), fl, sk, totR))
        print('%-44s %9s %8s %8s %8s %7s %6s  %s' % ('money rule ($1,000 start, $10 base)', 'end', 'maxDD', 'worstM', 'bestM', 'maxRisk', 'lossM', 'ruined'))
        rows = [('Off (fixed $10)', 'Off', None), ('Crooks C', 'C', None), ('Crooks E', 'E', None), ('Crooks J', 'J', None),
                ('Crooks L (default)', 'L', LD), ('Crooks L, base grows 5%', 'L', dict(LD, grow=0.05)), ('Crooks L, base grows 20%', 'L', dict(LD, grow=0.20)),
                ('Crooks L, more parts (z1 $10/part, max 10)', 'L', dict(LD, z1Step=1, z1Max=10))]
        for nm, m, ld in rows:
            r = run(tr, m, exitR=tp, L=ld); mv = list(r['months'].values())
            res[(tp, nm)] = r
            print('%-44s %9.0f %8.0f %8.0f %8.0f %7.0f %3d/%-3d %s' % (nm, r['end'], r['maxDD'], min(mv), max(mv), r['maxRisk'], sum(v < 0 for v in mv), len(mv),
                                                                 r['ruined'].strftime('%Y-%m-%d') + ' (after %d trades)' % r['n'] if r['ruined'] else '-'))
    pickle.dump(res, open(S + '/conf/crl_results.pkl', 'wb'))
