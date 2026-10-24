import sys, pickle, collections, datetime
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold'); import geng
D = pickle.load(open(S + '/gold/grid1.pkl', 'rb')); R = D['res']
def ml(seq): return geng.streaks(seq)[1]
print('1) Do losses cluster?  P(loss) vs P(loss | previous 1, 2, 3 trades were losses)')
for tf in ('M5', 'M15', 'H1'):
    r = [x[1] for x in R[(tf, 'base')]]; L = [v < 0 for v in r]; n = len(L)
    out = ['P(loss) %.3f' % (sum(L) / n)]
    for k in (1, 2, 3, 5):
        idx = [i for i in range(k, n) if all(L[i - j] for j in range(1, k + 1))]
        out.append('after %d losses %.3f (n %d)' % (k, sum(L[i] for i in idx) / len(idx), len(idx)))
    print('  %-4s %s' % (tf, ' | '.join(out)))
def summ(tf, name, res, kept=None):
    tr = R[(tf, name)]
    yrs = collections.defaultdict(list)
    for x, v in zip(tr, res):
        if v is not None: yrs[x[0].year].append((v, x[4] / x[5]))
    allv = [(v, c) for y in yrs for (v, c) in yrs[y]]; n = len(allv)
    E = sum(v for v, c in allv) / n; Ec = sum(v - c for v, c in allv) / n
    A = [v for x, v in zip(tr, res) if v is not None and x[0].year <= 2023]; B = [v for x, v in zip(tr, res) if v is not None and x[0].year >= 2024]
    return '%5d trades | win %4.1f%% | E %+.3f net %+.3f | A %+.3f B %+.3f | yrs+ %d/6 | longest losing streak %2d (worst year %2d)' % (
        n, 100 * sum(1 for v, c in allv if v > 0) / n, E, Ec, sum(A) / len(A), sum(B) / len(B), sum(1 for y in yrs if sum(v for v, c in yrs[y]) > 0),
        ml([v for v in res if v is not None]), max(ml([v for v, c in yrs[y]]) for y in yrs))
print('\n2) Partial profits (results per trade; win = closed above 0)')
for tf in ('M5', 'M15', 'H1'):
    print(' ', tf)
    b = R[(tf, 'base')]; print('    %-40s %s' % ('base (all out at TP4 or stop)', summ(tf, 'base', [x[1] for x in b])))
    t1 = R[(tf, 'BE at TP1')]
    print('    %-40s %s' % ('BE at TP1 (no partial)', summ(tf, 'BE at TP1', [x[1] for x in t1])))
    print('    %-40s %s' % ('50% at TP1 + BE, rest TP4', summ(tf, 'BE at TP1', [(0.5 * 0.6 + 0.5 * x[1]) if x[3][0] else -1.0 for x in t1])))
    print('    %-40s %s' % ('70% at TP1 + BE, rest TP4', summ(tf, 'BE at TP1', [(0.7 * 0.6 + 0.3 * x[1]) if x[3][0] else -1.0 for x in t1])))
    t2 = R[(tf, 'BE at TP2')]
    print('    %-40s %s' % ('50% at TP2 + BE, rest TP4', summ(tf, 'BE at TP2', [(0.5 * 1.0 + 0.5 * x[1]) if x[3][1] else x[1] for x in t2])))
    print('    %-40s %s' % ('exit all at TP1', summ(tf, 'exit TP1', [x[1] for x in R[(tf, 'exit TP1')]])))
print('\n3) Execution-level streak controls on the base signals (the engine keeps running; only which trades are taken changes)')
def control(tr, mode, k, days=0):
    res = []; cl = 0; paused = False; pauseUntil = None; lastDay = None
    for x in tr:
        v = x[1]; day = x[0].date()
        if mode == 'virtual':          # after k losses in a row: skip until a skipped trade wins, then trade again
            if paused:
                res.append(None)
                if v > 0: paused = False; cl = 0
                continue
            res.append(v); cl = cl + 1 if v < 0 else 0
            if cl >= k: paused = True
        elif mode == 'day':            # after k losses in a row: stop for the rest of the day
            if lastDay != day: paused = False; lastDay = day
            if paused: res.append(None); continue
            res.append(v); cl = cl + 1 if v < 0 else (0 if v > 0 else cl)
            if cl >= k: paused = True; cl = 0
        elif mode == 'pause':          # after k losses in a row: no trades for the next `days` calendar days
            if pauseUntil and day < pauseUntil: res.append(None); continue
            res.append(v); cl = cl + 1 if v < 0 else (0 if v > 0 else cl)
            if cl >= k: pauseUntil = day + datetime.timedelta(days=days + 1); cl = 0
    return res
for tf in ('M5', 'M15', 'H1'):
    print(' ', tf); b = R[(tf, 'base')]
    for mode, k, dd in (('virtual', 3, 0), ('virtual', 4, 0), ('virtual', 5, 0), ('day', 2, 0), ('day', 3, 0), ('pause', 4, 1), ('pause', 5, 2)):
        lab = {'virtual': 'after %d losses wait for a skipped win' % k, 'day': 'after %d losses stop for the day' % k, 'pause': 'after %d losses pause %d day(s)' % (k, dd)}[mode]
        print('    %-40s %s' % (lab, summ(tf, 'base', control(b, mode, k, dd))))
