"""Pine twin v2 vs engine2 (trades), random settings and option combinations. The engine's filter masks are computed independently of the
twin (time-zone arithmetic / pandas instead of zoneinfo per bar). Usage: parity2_trades.py SEED N CHART"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fractal')
import engine as EN, engine2 as E2, pine_twin2 as TW
from final11 import ALL
B = EN.load(); ctf = sys.argv[3] if len(sys.argv) > 3 else 'M15'
t = EN.chart(B, ctf)[0]; utc = TW.chart_utc(B, ctf).astype(np.int64)


def local_parts(tz):
    if tz == 'America/New_York': x = t - 7 * 3600
    elif tz == 'Asia/Kolkata': x = utc + 19800
    elif tz == 'UTC': x = utc.copy()
    else:   # pandas
        loc = pd.to_datetime(utc, unit='s', utc=True).tz_convert(tz).tz_localize(None)
        x = np.asarray((loc - pd.Timestamp('1970-01-01')) // pd.Timedelta('1s'), dtype=np.int64)
    days = x // 86400
    return ((days + 3) % 7), ((x % 86400) // 60), days


def masks(p):
    n = len(t); allow = np.ones(n, bool)
    dow, mins, days = local_parts(p.tz)
    if p.dayOn: allow &= np.array(p.days)[dow]
    if p.hoursOn:
        a0, a1 = p.sess; allow &= ((mins >= a0) & (mins < a1)) if a0 < a1 else ((mins >= a0) | (mins < a1))
    if p.trnOn:
        k = np.searchsorted(B[p.trnTf + '_t'], t, side='right') - 1; Ct = B[p.trnTf + '_C']
        e = TW.ema_seed(Ct, p.trnLen); okk = np.r_[False, Ct[:-1] > e[:-1]]; allow &= okk[k]
    ndow, nmins, _ = local_parts('America/New_York')
    wk = p.wkOn & (ndow == 4) & (nmins >= p.wkH * 60)
    allow &= ~wk
    y = pd.to_datetime(days * 86400, unit='s')
    return allow, wk, (y.year * 10000 + y.month * 100 + y.day).to_numpy().astype(np.int64)


rng = np.random.default_rng(int(sys.argv[1])); bad = 0; tot = 0
for it in range(int(sys.argv[2])):
    prm = ALL[int(rng.integers(len(ALL)))]
    if EN.TF_SEC[prm[0]] < EN.TF_SEC[ctf]: prm = ALL[int(rng.integers(9))]
    kw = dict(mmOn=False, tz=str(rng.choice(['Asia/Kolkata', 'America/New_York', 'UTC', 'Europe/London'])))
    if rng.random() < 0.5: kw['entClose'] = True
    if rng.random() < 0.4: kw['expN'] = int(rng.choice([2, 5, 12, 30]))
    if rng.random() < 0.4: kw['maxDay'] = int(rng.choice([1, 2]))
    if rng.random() < 0.5: kw['trA'] = float(rng.choice([0.0, 0.2, 0.5])); kw['trD'] = float(rng.choice([0.1, 0.3, 1.0]))
    if rng.random() < 0.4: kw['tExitH'] = float(rng.choice([1.0, 4.0, 24.0, 72.0]))
    if rng.random() < 0.4: kw['wkOn'] = True; kw['wkH'] = int(rng.choice([10, 16]))
    if rng.random() < 0.4: kw['trnOn'] = True; kw['trnTf'] = str(rng.choice(['H1', 'H4', 'D1'])); kw['trnLen'] = int(rng.choice([20, 50, 200]))
    if rng.random() < 0.4: kw['dayOn'] = True; kw['days'] = tuple(bool(x) for x in rng.random(7) < 0.7)
    if rng.random() < 0.4: kw['hoursOn'] = True; kw['sess'] = tuple(int(x) for x in rng.choice([(360, 1380), (120, 1020), (1200, 300), (0, 600)]))
    p = TW.P(**kw)
    s = TW.twin2(B, ctf, prm, p); tw = s.trades
    allow, wk, day = masks(p)
    ref = E2.run2(B, ctf, *prm, allow=allow, wk=wk, dayid=day, kexp=p.expN, trA=p.trA, trD=p.trD, tExit=int(round(p.tExitH * 3600)), emode=1 if p.entClose else 0, maxDay=p.maxDay, T=utc)
    same = len(tw) == len(ref) and all(a[0] == int(b[0]) and a[1] == b[1] and a[2] == int(b[2]) and a[3] == b[3] and a[4] == int(b[4]) for a, b in zip(tw, ref))
    tot += len(ref); bad += 0 if same else 1
    if not same:
        print('DIFF', prm, kw, 'twin', len(tw), 'engine', len(ref))
        for q, (a, b) in enumerate(zip(tw, ref)):
            if not (a[0] == int(b[0]) and a[1] == b[1] and a[2] == int(b[2]) and a[3] == b[3] and a[4] == int(b[4])):
                print('   first diff at', q, 'twin', a, 'engine', tuple(b[:5])); break
print('chart %s: %d random settings, %d trades, %s' % (ctf, it + 1, tot, 'ALL IDENTICAL' if bad == 0 else '%d DIFFERENT' % bad))
