"""Crooks TP1 rule: the EA's own NextRisk() / CrkT1Dist() / BookClosed() vs gold/crooks_tp1.py on the trades the simulator took
(exit at TP1, every source, Crooks A / B, caps). Per trade: the $ risk and whether the TP1 rule is used. The path P&L comes from the simulator."""
import sys, os, pickle, subprocess, tempfile
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
import crooks_tp1 as K
H = S + '/mq5check/rec/rec_harness'
REC = {'Crooks A': 18, 'Crooks B': 19}; ACT = {'clamp': 0, 'stop': 1, 'reset': 2}
D = pickle.load(open(S + '/gold/crooks_tp1.pkl', 'rb'))
tdir = tempfile.TemporaryDirectory(); runs = bad = ntr = nt1 = 0
for (tf, name), d in D.items():
    tr = d['trades']
    for mode, split in (('Crooks A', 3), ('Crooks B', 2), ('Crooks B', 3), ('Crooks B', 5)):
        for cap, act in ((0.0, 'clamp'), (500.0, 'clamp'), (500.0, 'reset'), (500.0, 'stop')):
            trace = []; r = K.simulate(tr, mode, cap=cap, capAction=act, cSplit=split, tp1rule=True, exitR=d['tp1R'], start=1e12, trace=trace)
            path = os.path.join(tdir.name, 'seq.txt')
            with open(path, 'w') as f:
                for x, risk, pnl, sp in trace: f.write('%r %r %r\n' % (x['R1'], x['spx'], 0.0 if pnl is None else pnl / risk))
            args = [H, path, repr(d['tp1R']), 'InpRec=%d' % REC[mode], 'InpExitAt=1', 'InpTp1R=%r' % d['tp1R'], 'InpCrkT1=1', 'InpCommLot=0', 'InpBaseRisk=50',
                    'InpCSplit=%d' % split, 'InpCapOn=%d' % (1 if cap else 0), 'InpHardCap=%r' % (cap or 500.0), 'InpCapAction=%d' % ACT[act]]
            out = subprocess.run(args, capture_output=True, text=True, check=True, env=dict(os.environ, REC_T1='1')).stdout.split('\n')
            ea = [(float(l.split()[1]), int(l.split()[2])) for l in out if l.startswith('R ')]
            if trace and trace[-1][2] is None: trace = trace[:-1]          # the stopping signal: the EA must print STOP there
            runs += 1; n = min(len(ea), len(trace)); ntr += n; nt1 += sum(1 for _, _, _, sp in trace[:n] if sp)
            diff = [i for i in range(n) if abs(ea[i][0] - trace[i][1]) > 1e-9 * max(1.0, trace[i][1]) or ea[i][1] != int(bool(trace[i][3]))]
            stopped = any(l == 'STOP' for l in out)
            if diff or (len(ea) != len(trace) and not r['ruined']) or stopped != r['capStopped']:
                bad += 1
                if bad <= 8:
                    i = diff[0] if diff else n
                    print('MISMATCH %s %s %s split %d cap %d %s: py %d trades, EA %d; first diff trade %d: py %s EA %s' % (
                        tf, name, mode, split, cap, act, len(trace), len(ea), i, (trace[i][1], bool(trace[i][3])) if i < len(trace) else None, ea[i] if i < len(ea) else None))
print('runs %d, trades compared %d (TP1-rule trades %d), mismatches %d' % (runs, ntr, nt1, bad))
