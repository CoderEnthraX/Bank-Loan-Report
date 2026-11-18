"""Crooks K study (asked 2026-11-18). Money simulator for Off / Crooks C / E / J (+ profit ladder) and the new Crooks K, with the monthly restart
(zero line = the month's starting balance; the ladder's best profit and Crooks J's drawdown restart each month, the loss owed is cleared, like the EA's MonthRestart)
and the 1:100 leverage limit. Crooks K = Crooks J (+ ladder) while the month is at or above its start; below the start (this month's closed profit
< 0): after a loss the 0.01 lot, after a win the CAREFUL size (fixed $, % of base, or lots), repeated while it wins; the ladder's 0.01-lot guard is
replaced by this. Checked against gold/recovery.py (restart off): see parity()."""
import sys, os, pickle, datetime as dt, multiprocessing as mp
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/conf'); sys.path.insert(0, S + '/gold')
COST = 0.23; LEV = 100.0
LADDER = {'Max': (0.4, 0.30, 12.0, 0.50)}


def sim(trades, mode, base=50.0, exitR=0.6, start=10000.0, lad=None, ladT=1000.0, jX=20.0, careful=None, restart=True, lev=True):
    """trades: dicts t (fill time), res (R), dist (stop distance), px (entry). careful: ('usd', x) / ('pct', x) / ('lot', x).
    -> dict(net, maxDD, maxRisk, months={YYYY-MM: pnl}, n)"""
    eq = start; peak = start; maxDD = 0.0; net = 0.0; peakNet = 0.0; netB = 0.0; mk = None
    crL = 0.0; crW = False; maxRisk = 0.0; months = {}; nLot = nCare = 0; ruined = None
    for x in trades:
        if eq <= 0: ruined = x['t']; break
        k = '%04d-%02d' % (x['t'].year, x['t'].month)
        if k != mk:
            mk = k
            if restart: netB = net; peakNet = net; crL = 0.0; crW = False   # = the EA's MonthRestart (RecoveryRestart, gNet0, crkPk = 0)
        c = COST / x['dist']; rmin = x['dist'] + COST            # 0.01 lot = 1 oz: loses dist + cost
        nR = net - netB; pR = peakNet - netB; B = base
        crRec = crW and crL > 0
        def crk(Bx):
            r_ = max(Bx, crL / exitR) if crRec else Bx
            if crRec and mode in ('J', 'K'): r_ = max(Bx, r_ * max(0.0, 1.0 - (pR - nR) / (jX * Bx)))
            elif (not crRec) and crL > 0 and mode == 'E': r_ = min(Bx, rmin)
            return r_
        r = B if mode == 'Off' else crk(B)
        if lad and mode in ('J', 'K') and pR >= ladT:
            lam, phi, bmax, gam = LADDER[lad]; C = max(0.0, nR - lam * pR); lB = B + min((bmax - 1.0) * B, phi * C)
            r = min(crk(lB), r + gam * C)
            if mode == 'J' and nR <= 0: r = min(B, rmin)
        if mode == 'K' and nR < 0:                                 # below the month's start: careful zone
            if crW:
                kind, v = careful; r = v if kind == 'usd' else B * v / 100.0 if kind == 'pct' else rmin * v / 0.01
                nCare += 1
            else: r = min(B, rmin); nLot += 1
        if lev and eq > 0: r = min(r, eq * LEV * (x['dist'] + COST) / x['px'])
        maxRisk = max(maxRisk, r)
        pnl = r * (x['res'] - c) / (1.0 + c)
        eq += pnl; net += pnl; peak = max(peak, eq); maxDD = max(maxDD, peak - eq); peakNet = max(peakNet, net)
        months[mk] = months.get(mk, 0.0) + pnl
        crL = max(0.0, crL - pnl)
        if crL < 0.01: crL = 0.0
        crW = pnl > 0
    return dict(net=net, maxDD=maxDD, maxRisk=maxRisk, months=months, n=len(trades), nLot=nLot, nCare=nCare, ruined=ruined)


def parity():
    """restart off, no leverage: Off / C / E / J / J + ladder Max must equal gold/recovery.py"""
    import recovery as RC
    T = pickle.load(open(S + '/conf/ktrades.pkl', 'rb'))
    bad = 0
    for key, (tr, xr) in T.items():
        seq = [(x['res'], COST / x['dist'], None, None, None, x['dist'] + COST) for x in tr]
        for m, rc, lad, lt in (('Off', 'Off', None, 1000), ('C', 'Crooks C', None, 1000), ('E', 'Crooks E', None, 1000), ('J', 'Crooks J', None, 1000),
                               ('J', 'Crooks J', 'Max', 1000), ('J', 'Crooks J', 'Max', 50)):
            a = sim(tr, m, exitR=xr, lad=lad, ladT=lt, restart=False, lev=False)['net']
            b = RC.simulate(seq, rc, exitR=xr, lad=lad, ladT=lt, cN=1)['net']
            ok = abs(a - b) < 1e-6 * max(1, abs(b)); bad += not ok
            print('%-26s %-9s lad %-4s T%-5d mine %12.2f recovery.py %12.2f %s' % (key, rc, lad, lt, a, b, 'OK' if ok else 'DIFF'))
    print('PARITY', 'ALL OK' if not bad else '%d differ' % bad)


def trades_all():
    import confirm as Q
    out = {}
    for b in Q.bases():
        if b['key'] not in ('M5-your settings (TP1)', 'M5-S1', 'M5-S3', 'M15-S1', 'M15-S7', 'M15-S8'): continue
        P, p, tr = Q.engine(b); T = P['T']
        xr = (p['tp1R'], p['tp2R'], p['tp3R'], p['tp4R'])[p['exitAt'] - 1]
        out[b['key']] = ([dict(t=T[x['fill']], res=x['res'], dist=x['dir'] * (x['entry'] - x['stop']), px=x['entry']) for x in tr], xr)
    pickle.dump(out, open(S + '/conf/ktrades.pkl', 'wb'))


CAREFUL = [('usd', 15), ('usd', 25), ('usd', 35), ('pct', 25), ('pct', 50), ('pct', 75), ('lot', 0.02), ('lot', 0.03), ('lot', 0.05)]
def configs():
    C = [('Off (fixed $50)', 'Off', None, 0, None), ('Crooks C', 'C', None, 0, None), ('Crooks E', 'E', None, 0, None), ('Crooks J', 'J', None, 0, None),
         ('Crooks J + ladder Max $50 (yours)', 'J', 'Max', 50, None), ('Crooks J + ladder Max $1000', 'J', 'Max', 1000, None)]
    for cf in CAREFUL:
        nm = '%s %s' % ({'usd': '$', 'pct': '', 'lot': ''}[cf[0]], cf[1]) if cf[0] == 'usd' else ('%d%% of base' % cf[1] if cf[0] == 'pct' else '%.2f lot' % cf[1])
        nm = nm.replace('$ ', '$')
        for lad, lt in ((None, 0), ('Max', 50), ('Max', 1000)):
            C.append(('Crooks K, careful %s%s' % (nm, '' if not lad else ', ladder Max $%d' % lt), 'K', lad, lt, cf))
    return C


def summ(r):
    m = r['months']; ks = sorted(m)
    a = sum(v for k, v in m.items() if k < '2024'); b = sum(v for k, v in m.items() if k >= '2024')
    return dict(net=r['net'], A=a, B=b, dd=r['maxDD'], worst=min(m.values()), lossM=sum(1 for v in m.values() if v < 0), nM=len(m),
                maxRisk=r['maxRisk'], ruined=r['ruined'], ratio=r['net'] / r['maxDD'] if r['maxDD'] > 0 else 0, nLot=r['nLot'], nCare=r['nCare'])


def run_all():
    T = pickle.load(open(S + '/conf/ktrades.pkl', 'rb'))
    out = {}
    for key, (tr, xr) in T.items():
        out[key] = [(nm, summ(sim(tr, m, exitR=xr, lad=lad, ladT=lt or 1000, careful=cf))) for nm, m, lad, lt, cf in configs()]
    pickle.dump(out, open(S + '/conf/kresults.pkl', 'wb'))
    return out


if __name__ == '__main__':
    if sys.argv[1] == 'trades': trades_all()
    elif sys.argv[1] == 'parity': parity()
    else: run_all(); print('done')
