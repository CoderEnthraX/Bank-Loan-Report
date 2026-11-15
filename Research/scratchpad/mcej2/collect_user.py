"""The user's Auction Retest strategy settings (= the strategy defaults, v4.x) on gold M5 and M15, 2021-01 .. 2026-10-02:
  setups  off = days / hours / kill zones / news all off;  on = Tue-Thu, 06:00-23:00 IST, kill zones Asia + London + New York (follow
          summer time), daily news 17:45-18:15 IST (follows New York time) with no new trades from 60 minutes before, close at its start
  both:   force-close 23:55 IST, close when Saturday starts, earn-back targets (costs 0.16 spread + $7 per lot = 0.23 per oz)
  exits   TP1 (0.6R) and TP2 (1.0R)
Engine events (ref_gse) -> TradingView strategy execution (stratemu). Check mode (python3 collect_user.py check): earn-back and the time
closes off -> the executed trades vs the engine's own trades. Output: mcej2/user_trades.pkl"""
import sys, pickle, time, collections
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold'); sys.path.insert(0, S + '/mcej2')
import geng, ref_gse, stratemu as EM
ref_gse.eprep = geng.ref_g.eprep
ENG = dict(halfCap=True, maxFills=10, entryPct=25.0, mv3R=0.0, noChaseSig=2.0, chopMax=13.5, kzShift=0, kzAuto=True)
SETUP = {'off': dict(eng=dict(dayOn=False, hoursOn=False, kzOn=False), news=False),
         'on': dict(eng=dict(dayOn=True, days=(False, True, True, True, False, False, False), hoursOn=True, hoursSess=(600, 2300), kzOn=True,
                             kz=(True, True, True, False)), news=True)}
COST = 0.23


def one(tf, setup, exitAt, check=False):
    P = geng.prepare(tf, 'session', 'hlc3'); geng._CUR['vw'] = 'session'; geng._CUR['src'] = 'hlc3'
    O, H, L, C, T, mt = P['O'], P['H'], P['L'], P['C'], P['T'], P['mt']
    o = dict(ENG, exitAt=exitAt, **SETUP[setup]['eng']); ev = []
    eng = [x for x in ref_gse.run(tf, o, ev) if not x['ghost']]
    if check:
        fl = EM.time_flags(T, fcOn=False, wkOn=False, newsOn=False)
        tr, cnt = EM.run(O, H, L, C, T, ev, mt, earnBack=False, flags=fl)
        A = {(x['dir'], x['fill'], x['exit']) for x in eng if x['exit'] is not None}
        B = {(x['dir'], x['fill'], x['exit']) for x in tr if x['exit'] is not None}
        # with earn-back off the strategy closes at the engine's exit: the same exit bar, or the next open after it
        Bn = {(x['dir'], x['fill'], x['exit'] - 1 if x['how'] == 'engine exit' else x['exit']) for x in tr if x['exit'] is not None}
        sameWin = sum(1 for x in tr if x['exit'] is not None and (x['dir'], x['fill'], x['exit']) in A)
        return dict(engine=len(A), executed=len(B), same=len(A & B), same_or_next_open=len(A & Bn), cnt=cnt,
                    hows=collections.Counter(x['how'] for x in tr))
    fl = EM.time_flags(T, fcOn=True, wkOn=True, newsOn=SETUP[setup]['news'])
    tr, cnt = EM.run(O, H, L, C, T, ev, mt, earnBack=True, costPx=COST, flags=fl)
    out = []
    for x in tr:
        if x['exit'] is None: continue                                   # still open at the end of the data
        d = x['dir']; rp = x['risk']
        out.append(dict(t=T[x['fill']], tx=T[x['exit']], arm=x['arm'], fill=x['fill'], exit=x['exit'], dir=d, lim=x['lim'], fpx=x['fpx'], xpx=x['xpx'],
                        how=x['how'], rp=rp, R=d * (x['xpx'] - x['fpx']) / rp, c=COST / rp, levk=100.0 * (rp + COST) / x['lim'], rmin=1.0 * (rp + COST)))
    return dict(trades=out, cnt=cnt, engine=len(eng), hows=collections.Counter(x['how'] for x in out))


if __name__ == '__main__':
    check = len(sys.argv) > 1 and sys.argv[1] == 'check'
    res = {}
    for tf in ('M5', 'M15'):
        for setup in ('off', 'on'):
            for ex in (1, 2):
                t0 = time.time(); r = one(tf, setup, ex, check); res[(tf, setup, ex)] = r
                if check:
                    print('%-3s %-3s TP%d engine %5d executed %5d same %5d (%.2f%%), same or closed at the next open %5d (%.2f%%) | %s | %s | %.0fs' % (
                        tf, setup, ex, r['engine'], r['executed'], r['same'], 100.0 * r['same'] / r['engine'], r['same_or_next_open'],
                        100.0 * r['same_or_next_open'] / r['engine'], dict(r['hows']), r['cnt'], time.time() - t0))
                else:
                    tr = r['trades']; w = sum(1 for x in tr if x['R'] - x['c'] > 0)
                    print('%-3s %-3s TP%d trades %5d (engine %5d) wins %.1f%% net %+.1fR | %s | %s | %.0fs' % (
                        tf, setup, ex, len(tr), r['engine'], 100.0 * w / len(tr), sum((x['R'] - x['c']) / (1 + x['c']) for x in tr), dict(r['hows']), r['cnt'], time.time() - t0))
    if not check:
        pickle.dump(res, open(S + '/mcej2/user_trades.pkl', 'wb'))
