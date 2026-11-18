"""Variable split (asked 2026-11-18): Crooks C whose recovery is split over N winning recovery trades, N = nUp while the month is at or above its
starting balance, nDn below it (Crooks C 'over N wins' logic of gold/recovery.py: recovery risk = max(base, loss owed / parts left / exitR); a
winning recovery trade -> one part fewer; a loss -> parts start again). Monthly restart = the EA's (zero line and the loss owed cleared), 1:100.
Check: nUp = nDn = N must equal recovery.py Crooks C with cN = N (restart off)."""
import sys, pickle
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/conf'); sys.path.insert(0, S + '/gold')
from krule import COST, LEV, summ, sim as ksim

def sim(trades, nUp, nDn, base=50.0, exitR=0.6, start=10000.0, restart=True, lev=True):
    eq = start; peak = start; maxDD = 0.0; net = 0.0; netB = 0.0; mk = None; crL = 0.0; crW = False; crP = nUp; maxRisk = 0.0; months = {}; ruined = None
    for x in trades:
        if eq <= 0: ruined = x['t']; break
        k = '%04d-%02d' % (x['t'].year, x['t'].month)
        if k != mk:
            mk = k
            if restart: netB = net; crL = 0.0; crW = False; crP = nUp
        N = nUp if net - netB >= 0 else nDn
        if net - netB >= 0: crP = min(crP, nUp)
        c = COST / x['dist']; crRec = crW and crL > 0
        r = max(base, crL / crP / exitR) if crRec else base
        if lev and eq > 0: r = min(r, eq * LEV * (x['dist'] + COST) / x['px'])
        maxRisk = max(maxRisk, r)
        pnl = r * (x['res'] - c) / (1.0 + c); eq += pnl; net += pnl; peak = max(peak, eq); maxDD = max(maxDD, peak - eq)
        months[mk] = months.get(mk, 0.0) + pnl
        win = pnl > 0; crL = max(0.0, crL - pnl)
        if crL < 0.01: crL = 0.0; crP = nUp if net - netB >= 0 else nDn
        else: crP = (nUp if net - netB >= 0 else nDn) if not win else (max(1, crP - 1) if crRec else crP)
        crW = win
    return dict(net=net, maxDD=maxDD, maxRisk=maxRisk, months=months, n=len(trades), nLot=0, nCare=0, ruined=ruined)

if __name__ == '__main__':
    import recovery as RC
    T = pickle.load(open(S + '/conf/ktrades.pkl', 'rb'))
    bad = 0
    for key, (tr, xr) in T.items():
        for N in (1, 2, 3, 4):
            a = sim(tr, N, N, exitR=xr, restart=False, lev=False)['net']
            b = RC.simulate([(x['res'], COST / x['dist']) for x in tr], 'Crooks C', exitR=xr, cN=N)['net']
            bad += abs(a - b) > 1e-6 * max(1, abs(b))
    print('PARITY with recovery.py Crooks C over N wins:', 'ALL OK' if not bad else '%d differ' % bad)
    SPL = [(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (2, 3), (2, 4), (3, 3)]
    for key, (tr, xr) in T.items():
        print('\n=== %s (final target %.1fR)' % (key, xr))
        print('%-34s %8s %8s %8s %7s %7s %6s %7s %5s' % ('rule', 'net', '2021-23', '2024-26', 'maxDD', 'worstM', 'lossM', 'maxRisk', 'n/DD'))
        rows = [('Off (fixed $50)', summ(ksim(tr, 'Off', exitR=xr))), ('Crooks J', summ(ksim(tr, 'J', exitR=xr)))]
        rows += [('C split: %d above start / %d below' % sp, summ(sim(tr, sp[0], sp[1], exitR=xr))) for sp in SPL]
        for nm, s in rows:
            print('%-34s %8.0f %8.0f %8.0f %7.0f %7.0f %3d/%-2d %7.0f %5.1f%s' % (nm, s['net'], s['A'], s['B'], s['dd'], s['worst'], s['lossM'], s['nM'], s['maxRisk'], s['ratio'], '  RUINED ' + str(s['ruined'].date()) if s['ruined'] else ''))
