"""Crooks TP1 rule: the EA's own NextRisk() / CrkT1Dist() / BookClosed() vs gold/crooks_tp1.py on the trades the simulator took
(exit at TP1, every source, Crooks A / B / C / D, caps, Crooks C over 1-3 wins, every stop before TP1). Per trade: the $ risk and whether the TP1 rule
is used. The path P&L comes from the simulator (the tight-stop paths for every stop choice: only the sizing and the hard cap are compared here).
The hard cap covers the stop-out loss at the first stop: multiple m computed as the EA does (harness tick 0.01, tick value 1, no commission)."""
import math
import sys, os, pickle, subprocess, tempfile
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
import crooks_tp1 as K
H = S + '/mq5check/rec/rec_harness'
REC = {'Crooks A': 18, 'Crooks B': 19, 'Crooks C': 20, 'Crooks D': 21, 'Crooks E': 22, 'Crooks F': 23, 'Crooks G': 24, 'Crooks H': 25, 'Crooks I': 26,
       'Crooks J': 27}; ACT = {'clamp': 0, 'stop': 1, 'reset': 2}
NEW = (('Crooks E', 3, 1), ('Crooks F', 3, 1), ('Crooks F', 3, 2), ('Crooks G', 3, 1), ('Crooks H', 3, 1), ('Crooks I', 3, 1), ('Crooks J', 3, 1))   # v4.5 (defaults)
LADN = {'Low': 1, 'Medium': 2, 'High': 3, 'Extra high': 4, 'Max': 5}            # v4.6 ENUM_LADDER
NEWL = tuple((m, 3, 1, lv) for m in ('Crooks F', 'Crooks G', 'Crooks H', 'Crooks I', 'Crooks J') for lv in ('Medium', 'Max'))   # v4.6 ladder, target $1,000
def rmin(x):
    """v4.5 Crooks E / I: the EA's MinLotRisk() of this setup in the harness (0.01 lot, tick 0.01, tick value 1, no commission) = 1 x (stop + spread)"""
    return x['R1'] + max(0.0, (1000.0 + x['spx']) - 1000.0)
D = pickle.load(open(S + '/gold/crooks_tp1.pkl', 'rb'))
tdir = tempfile.TemporaryDirectory(); runs = bad = ntr = nt1 = 0
TS = 0.01
def mult(x, tp1R, k):
    """the EA's CrkT1Mult() for this trade with stop choice k (0 tight, 1 0.45R, 2 0.6R, 3-6 the normal stop)"""
    spr = max(0.0, (1000.0 + x['spx']) - 1000.0); R1 = x['R1']
    d = math.floor((tp1R * R1 / 2.0 - 1.5 * (spr + 0.0)) / TS + 1e-9) * TS
    if d < TS: return 1.0
    s0 = d if k == 0 else math.floor(0.45 * R1 / TS + 1e-9) * TS if k == 1 else math.floor(0.6 * R1 / TS + 1e-9) * TS if k == 2 else R1
    per = (d + spr) / TS * 1.0 + 0.0; perL = (s0 + spr) / TS * 1.0 + 0.0
    return perL / per if per > 0 else 1.0
for (tf, name), d in D.items():
    tr = d['trades']
    trm = {k: [dict(x, m=mult(x, d['tp1R'], k), rmin=rmin(x)) for x in tr] for k in range(7)}
    for mode, split, cn, lad in tuple(x + (None,) for x in (('Crooks A', 3, 1), ('Crooks B', 2, 1), ('Crooks B', 3, 1), ('Crooks B', 5, 1), ('Crooks C', 3, 1), ('Crooks C', 3, 2), ('Crooks C', 3, 3), ('Crooks D', 3, 1)) + NEW) + NEWL:
      for cap, act in ((0.0, 'clamp'), (500.0, 'clamp'), (500.0, 'reset'), (500.0, 'stop')):
        for k in (range(7) if cap else (0,)):                           # the stop choice matters only through the hard cap
            st0 = 1e4 if mode == 'Crooks H' else 1e12
            trace = []; r = K.simulate(trm[k], mode, cap=cap, capAction=act, cSplit=split, tp1rule=True, exitR=d['tp1R'], start=st0, trace=trace, cN=cn, lad=lad, ladT=1000.0)
            path = os.path.join(tdir.name, 'seq.txt')
            with open(path, 'w') as f:
                for x, risk, pnl, sp in trace: f.write('%r %r %r\n' % (x['R1'], x['spx'], 0.0 if pnl is None else pnl / risk))
            args = [H, path, repr(d['tp1R']), 'InpRec=%d' % REC[mode], 'InpExitAt=1', 'InpTp1R=%r' % d['tp1R'], 'InpCrkT1=1', 'InpCommLot=0', 'InpBaseRisk=50',
                    'InpCSplit=%d' % split, 'InpCapOn=%d' % (1 if cap else 0), 'InpHardCap=%r' % (cap or 500.0), 'InpCapAction=%d' % ACT[act],
                    'InpCrkT1Stop=%d' % k, 'InpCrkCnOn=%d' % (1 if cn > 1 else 0), 'InpCrkCn=%d' % cn, 'InpSpread=0',   # v4.0: the live spread, as the harness sets it
                    'InpLadder=%d' % LADN.get(lad, 0), 'InpLadT=1000']
            out = subprocess.run(args, capture_output=True, text=True, check=True, env=dict(os.environ, REC_T1='1', REC_START=repr(st0))).stdout.split('\n')
            ea = [(float(l.split()[1]), int(l.split()[2])) for l in out if l.startswith('R ')]
            if trace and trace[-1][2] is None: trace = trace[:-1]          # the stopping signal: the EA must print STOP there
            runs += 1; n = min(len(ea), len(trace)); ntr += n; nt1 += sum(1 for _, _, _, sp in trace[:n] if sp)
            diff = [i for i in range(n) if abs(ea[i][0] - trace[i][1]) > 1e-9 * max(1.0, trace[i][1]) or ea[i][1] != int(bool(trace[i][3]))]
            stopped = any(l == 'STOP' for l in out)
            if diff or (len(ea) != len(trace) and not r['ruined']) or stopped != r['capStopped']:
                bad += 1
                if bad <= 8:
                    i = diff[0] if diff else n
                    print('MISMATCH %s %s %s split %d N %d stop %d cap %d %s: py %d trades, EA %d; first diff trade %d: py %s EA %s' % (
                        tf, name, mode, split, cn, k, cap, act, len(trace), len(ea), i, (trace[i][1], bool(trace[i][3])) if i < len(trace) else None, ea[i] if i < len(ea) else None))
print('p = 50%%, exit TP1: runs %d, trades compared %d (TP1-rule trades %d), mismatches %d' % (runs, ntr, nt1, bad))
# v3.8: the part p closed at TP1 (InpCrkT1Pct 30 / 50 / 70) and any final exit (exit TP2 with InpCrkT1Any), tight and normal stop,
# on gold/crooks_t1p.pkl (the TP1-rule paths replayed for each p); the first 2500 trades of each setting
P2 = pickle.load(open(S + '/gold/crooks_t1p.pkl', 'rb'))
def mult_p(x, tp1R, pt, var):
    """the EA's CrkT1Mult() with InpCrkT1Pct = 100 p (harness tick 0.01, tick value 1, no commission)"""
    spr = max(0.0, (1000.0 + x['spx']) - 1000.0); R1 = x['R1']
    d = math.floor((pt * tp1R * R1 - (1.0 + pt) * (spr + 0.0)) / TS + 1e-9) * TS
    if d < TS: return 1.0
    s0 = d if var == 'tight' else R1
    return (s0 + spr) / (d + spr)
runs2 = bad2 = ntr2 = nt12 = 0
for (tf, name, ex), d in sorted(P2.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2])):
    for pt in (0.3, 0.5, 0.7):
        for var, k in (('tight', 0), ('wide', 3)):
            trs = [dict(x, sp=x['v'][(pt, var)], m=mult_p(x, d['tp1R'], pt, var), rmin=rmin(x)) for x in d['trades'][:2500]]
            for mode, split, cn, lad in tuple(x + (None,) for x in (('Crooks A', 3, 1), ('Crooks B', 3, 1), ('Crooks C', 3, 1), ('Crooks C', 3, 2), ('Crooks D', 3, 1)) + NEW) + NEWL:
                for cap, act in ((0.0, 'clamp'), (500.0, 'clamp'), (500.0, 'reset'), (500.0, 'stop')):
                    st0 = 1e4 if mode == 'Crooks H' else 1e12
                    trace = []; r = K.simulate(trs, mode, cap=cap, capAction=act, cSplit=split, tp1rule=True, exitR=d['exitR'], start=st0, trace=trace, cN=cn, lad=lad, ladT=1000.0)
                    path = os.path.join(tdir.name, 'seq.txt')
                    with open(path, 'w') as f:
                        for x, risk, pnl, sp in trace: f.write('%r %r %r\n' % (x['R1'], x['spx'], 0.0 if pnl is None else pnl / risk))
                    args = [H, path, repr(d['exitR']), 'InpRec=%d' % REC[mode], 'InpExitAt=%d' % ex, 'InpCrkT1Any=%d' % (1 if ex != 1 else 0), 'InpCrkT1Pct=%r' % (100.0 * pt),
                            'InpTp1R=%r' % d['tp1R'], 'InpTp2R=%r' % d['tp2R'], 'InpCrkT1=1', 'InpCommLot=0', 'InpBaseRisk=50', 'InpCSplit=%d' % split,
                            'InpCapOn=%d' % (1 if cap else 0), 'InpHardCap=%r' % (cap or 500.0), 'InpCapAction=%d' % ACT[act], 'InpCrkT1Stop=%d' % k,
                            'InpCrkCnOn=%d' % (1 if cn > 1 else 0), 'InpCrkCn=%d' % cn, 'InpSpread=0', 'InpLadder=%d' % LADN.get(lad, 0), 'InpLadT=1000']
                    out = subprocess.run(args, capture_output=True, text=True, check=True, env=dict(os.environ, REC_T1='1', REC_START=repr(st0))).stdout.split('\n')
                    ea = [(float(l.split()[1]), int(l.split()[2])) for l in out if l.startswith('R ')]
                    if trace and trace[-1][2] is None: trace = trace[:-1]
                    runs2 += 1; n = min(len(ea), len(trace)); ntr2 += n; nt12 += sum(1 for _, _, _, sp in trace[:n] if sp)
                    diff = [i for i in range(n) if abs(ea[i][0] - trace[i][1]) > 1e-9 * max(1.0, trace[i][1]) or ea[i][1] != int(bool(trace[i][3]))]
                    stopped = any(l == 'STOP' for l in out)
                    if diff or (len(ea) != len(trace) and not r['ruined']) or stopped != r['capStopped']:
                        bad2 += 1
                        if bad2 <= 8:
                            i = diff[0] if diff else n
                            print('MISMATCH v3.8 %s %s exit TP%d p %.1f %s %s N %d cap %d %s: py %d trades, EA %d; first diff trade %d: py %s EA %s' % (
                                tf, name, ex, pt, var, mode, cn, cap, act, len(trace), len(ea), i, (trace[i][1], bool(trace[i][3])) if i < len(trace) else None, ea[i] if i < len(ea) else None))
print('p = 30 / 50 / 70%%, exit TP1 and TP2 (any final exit), tight and normal stop: runs %d, trades compared %d (TP1-rule trades %d), mismatches %d' % (runs2, ntr2, nt12, bad2))
