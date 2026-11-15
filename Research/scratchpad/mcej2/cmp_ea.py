"""EA broker simulator (the EA's own code, MT5 ticks from M1) vs mcej2's TradingView-strategy emulator on M5: trades matched by side and
entry M5 bar (UTC); exit bar, close reason and net R (BOOK pnl / risk vs (R - c) / (1 + c)) compared. Usage: cmp_ea.py LOG SETUP EXIT"""
import sys, re, pickle, datetime as dt, collections
import numpy as np
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
log, setup, ex = sys.argv[1], sys.argv[2], int(sys.argv[3])
csv = np.loadtxt(S + '/mcej2/m1_all.csv', delimiter=',', usecols=(0, 1), dtype=np.int64)
off = dict(zip(csv[:, 0].tolist(), csv[:, 1].tolist()))
def srv2utc(s):
    t = dt.datetime.strptime(s, '%Y.%m.%d %H:%M:%S'); m = int((t - dt.datetime(1970, 1, 1)).total_seconds()) // 60 * 60
    o = off.get(m)
    if o is None:
        o = off.get(m - 60, off.get(m + 60, 7200))
    return t - dt.timedelta(seconds=o)
pos = {}; order = []; books = []
for ln in open(log):
    if ln.startswith('SIM OPEN'):
        m = re.match(r'SIM OPEN (\S+ \S+) pos=(\d+) (\w+) vol=([\d.]+) px=([\d.]+) sl=([\d.]+) tp=([\d.]+)', ln)
        pid = int(m.group(2)); pos[pid] = dict(t=srv2utc(m.group(1)), d=1 if m.group(3) == 'buy' else -1, px=float(m.group(5)), sl=float(m.group(6)), tp=float(m.group(7)))
        order.append(pid)
    elif ln.startswith('SIM CLOSE'):
        m = re.match(r'SIM CLOSE (\S+ \S+) pos=(\d+) reason=(\d+) px=([\d.]+)', ln)
        p = pos[int(m.group(2))]; p['tx'] = srv2utc(m.group(1)); p['why'] = {4: 'stop', 5: 'target', 3: 'EA close'}.get(int(m.group(3)), m.group(3)); p['xpx'] = float(m.group(4))
    elif ln.startswith('BOOK'):
        m = re.match(r'BOOK (\S+ \S+) pnl=(-?[\d.]+) hedge=\d risk=([\d.]+)', ln); books.append((float(m.group(2)), float(m.group(3))))
ea = [pos[k] for k in order if 'tx' in pos[k]]
for p, (pnl, rk) in zip(ea, books): p['Rn'] = pnl / rk if rk > 0 else 0.0
U = pickle.load(open(S + '/mcej2/user_trades.pkl', 'rb'))[('M5', setup, ex)]['trades']
t0 = ea[0]['t'] - dt.timedelta(minutes=5)
mine = [x for x in U if x['t'] - dt.timedelta(minutes=330) >= t0]
def bar(t): return t.replace(minute=t.minute - t.minute % 5, second=0)
A = {(p['d'], bar(p['t'])): p for p in ea}
B = {(x['dir'], x['t'] - dt.timedelta(minutes=330)): x for x in mine}
both = set(A) & set(B)
sameExit = sum(1 for k in both if bar(A[k]['tx']) == B[k]['tx'] - dt.timedelta(minutes=330) or abs((bar(A[k]['tx']) - (B[k]['tx'] - dt.timedelta(minutes=330))).total_seconds()) <= 300)
sameRes = sum(1 for k in both if (A[k]['Rn'] > 0) == (B[k]['R'] - B[k]['c'] > 0))
dR = [abs(A[k]['Rn'] - (B[k]['R'] - B[k]['c']) / (1 + B[k]['c'])) for k in both]
print('setup %s TP%d | EA %d trades, emulator %d (same period) | matched %d (%.1f%% of EA, %.1f%% of emulator) | same exit bar (+-1) %d (%.1f%%) | same win/loss %d (%.1f%%) | |net R diff| median %.3f, mean %.3f' % (
    setup, ex, len(ea), len(mine), len(both), 100 * len(both) / len(ea), 100 * len(both) / len(mine), sameExit, 100 * sameExit / len(both),
    sameRes, 100 * sameRes / len(both), sorted(dR)[len(dR) // 2], sum(dR) / len(dR)))
print('  net R: EA %+.1f, emulator %+.1f (same period); matched trades only: EA %+.1f, emulator %+.1f' % (
    sum(p['Rn'] for p in ea), sum((x['R'] - x['c']) / (1 + x['c']) for x in mine), sum(A[k]['Rn'] for k in both), sum((B[k]['R'] - B[k]['c']) / (1 + B[k]['c']) for k in both)))
print('  win rate: EA %.1f%%, emulator %.1f%% | EA closes: %s | emulator closes: %s' % (100 * sum(1 for p in ea if p['Rn'] > 0) / len(ea),
      100 * sum(1 for x in mine if x['R'] - x['c'] > 0) / len(mine), dict(collections.Counter(p['why'] for p in ea)), dict(collections.Counter(x['how'] for x in mine))))
