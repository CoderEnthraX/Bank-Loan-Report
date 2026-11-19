"""v5.1 (Size By Profit with the costs: each trade's D = the EA's PDiv with the live spread, earn-back on / off, given as x['pd'])
Crooks TP1 rule: the EA's own NextRisk() / CrkT1Dist() / BookClosed() (REC_T1 mode; the EA computes the 0.01-lot and the Crooks K
careful-lot risks itself with LotRisk(): tick 0.01, tick value 1, no commission) vs gold/crooks_tp1.py, on the trades the simulator took
(exit at TP1, every catalogue source of crooks_tp1.pkl): Crooks K (lots / $ / %, ladder off / Max $1,000; the TP1 rule is off in its zone),
Crooks L (default / other steps), and Crooks C / E / J / K / L with Size By Profit; caps none / clamp / start again / stop, every stop choice
with a cap. Per trade: the $ risk and whether the TP1 rule is used. Run: python3 -I parity_tp1_v50.py"""
import math, sys, os, pickle, subprocess, tempfile
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
import crooks_tp1 as K
H = S + '/mq5check/rec/rec_harness'
REC = {'Crooks C': 20, 'Crooks E': 22, 'Crooks J': 27, 'Crooks K': 28, 'Crooks L': 29}; ACT = {'clamp': 0, 'stop': 1, 'reset': 2}
LADN = {'Medium': 2, 'Max': 5}; KM = {'lots': 0, 'usd': 1, 'pct': 2}
TS = 0.01


def rmin(x): return x['R1'] + max(0.0, (1000.0 + x['spx']) - 1000.0)


def pdiv(xr, x, eb):
    """the EA's PDiv(exitR) in REC_T1 mode: trRisk = R1, CostSpr() = the live spread ask - bid (InpSpread 0), no commission"""
    if xr <= 0: return 1.0
    if x['R1'] <= 0: return xr
    spr = max(max(0.0, (1000.0 + x['spx']) - 1000.0), 0.0); loss = (x['R1'] + spr) / TS * 1.0 + 0.0
    win = xr * x['R1'] / TS * 1.0
    if not eb: win -= spr / TS * 1.0 + 0.0
    return win / loss if (loss > 0 and win > 0) else xr


def mult(x, tp1R, k):
    spr = max(0.0, (1000.0 + x['spx']) - 1000.0); R1 = x['R1']
    d = math.floor((tp1R * R1 / 2.0 - 1.5 * (spr + 0.0)) / TS + 1e-9) * TS
    if d < TS: return 1.0
    s0 = d if k == 0 else math.floor(0.45 * R1 / TS + 1e-9) * TS if k == 1 else math.floor(0.6 * R1 / TS + 1e-9) * TS if k == 2 else R1
    per = (d + spr) / TS * 1.0 + 0.0; perL = (s0 + spr) / TS * 1.0 + 0.0
    return perL / per if per > 0 else 1.0


CASES = ([('risk', 'Crooks K', dict(kMode=m, lad=lv)) for m in ('lots', 'usd', 'pct') for lv in (None, 'Max')] +
         [('risk', 'Crooks L', {}), ('risk', 'Crooks L', dict(lZ1=1.0, lZ1N=10, lZ2=3.0, lZ2N=5, lGrow=20.0, lGrowX=6.0))] +
         [('profit', m, {}) for m in ('Crooks C', 'Crooks E', 'Crooks J', 'Crooks L')] + [('profit', 'Crooks K', dict(kMode=m)) for m in ('lots', 'usd', 'pct')])
D = pickle.load(open(S + '/gold/crooks_tp1.pkl', 'rb'))
tdir = tempfile.TemporaryDirectory(); runs = bad = ntr = nt1 = 0
for (tf, name), d in D.items():
    tr0 = d['trades']
    trm = {k: [dict(x, m=mult(x, d['tp1R'], k), rmin=rmin(x), krisk=2.0 * rmin(x)) for x in tr0] for k in range(7)}
    trp = {eb: {k: [dict(x, pd=pdiv(d['tp1R'], x, eb)) for x in v] for k, v in trm.items()} for eb in (1, 0)}
    for sb, mode, kw, eb in [c + (e,) for c in CASES for e in ((1, 0) if c[0] == 'profit' else (None,))]:
        for cn in (1, 2):
            for cap, act in ((0.0, 'clamp'), (500.0, 'clamp'), (500.0, 'reset'), (500.0, 'stop')):
                for k in (range(7) if cap else (0,)):
                    trace = []
                    r = K.simulate(trm[k] if eb is None else trp[eb][k], mode, cap=cap, capAction=act, cSplit=3, tp1rule=True, exitR=d['tp1R'], start=1e12, trace=trace, cN=cn,
                                   lad=kw.get('lad'), ladT=1000.0, sizeBy=sb, **{a: b for a, b in kw.items() if a != 'lad'})
                    path = os.path.join(tdir.name, 'seq.txt')
                    with open(path, 'w') as f:
                        for x, risk, pnl, sp in trace: f.write('%r %r %r\n' % (x['R1'], x['spx'], 0.0 if pnl is None else pnl / risk))
                    args = [H, path, repr(d['tp1R']), 'InpRec=%d' % REC[mode], 'InpSizeBy=%d' % (1 if sb == 'profit' else 0), 'InpExitAt=1', 'InpTp1R=%r' % d['tp1R'],
                            'InpCrkT1=1', 'InpCommLot=0', 'InpBaseRisk=50', 'InpCSplit=3', 'InpCapOn=%d' % (1 if cap else 0), 'InpHardCap=%r' % (cap or 500.0),
                            'InpCapAction=%d' % ACT[act], 'InpCrkT1Stop=%d' % k, 'InpCrkCnOn=%d' % (1 if cn > 1 else 0), 'InpCrkCn=%d' % cn, 'InpSpread=0',
                            'InpLadder=%d' % LADN.get(kw.get('lad'), 0), 'InpLadT=1000', 'InpCrkKMode=%d' % KM[kw.get('kMode', 'lots')], 'InpCrkKLots=0.02',
                            'InpCrkKUsd=25', 'InpCrkKPct=50', 'InpCrkLZ1=%r' % kw.get('lZ1', 2.0), 'InpCrkLZ1N=%d' % kw.get('lZ1N', 6),
                            'InpCrkLZ2=%r' % kw.get('lZ2', 5.0), 'InpCrkLZ2N=%d' % kw.get('lZ2N', 3), 'InpCrkLGrow=%r' % kw.get('lGrow', 10.0),
                            'InpCrkLGrowX=%r' % kw.get('lGrowX', 4.0), 'InpEarnBack=%d' % (1 if eb is None else eb)]
                    out = subprocess.run(args, capture_output=True, text=True, check=True, env=dict(os.environ, REC_T1='1', REC_START='1e12')).stdout.split('\n')
                    ea = [(float(l.split()[1]), int(l.split()[2])) for l in out if l.startswith('R ')]
                    if trace and trace[-1][2] is None: trace = trace[:-1]
                    runs += 1; n = min(len(ea), len(trace)); ntr += n; nt1 += sum(1 for _, _, _, sp in trace[:n] if sp)
                    diff = [i for i in range(n) if abs(ea[i][0] - trace[i][1]) > 1e-9 * max(1.0, trace[i][1]) or ea[i][1] != int(bool(trace[i][3]))]
                    stopped = any(l == 'STOP' for l in out)
                    if diff or (len(ea) != len(trace) and not r['ruined']) or stopped != r['capStopped']:
                        bad += 1
                        if bad <= 8:
                            i = diff[0] if diff else n
                            print('MISMATCH %s %s %s eb %s %s %s N %d stop %d cap %d %s: py %d trades, EA %d; first diff trade %d: py %s EA %s' % (
                                tf, name, sb, eb, mode, kw, cn, k, cap, act, len(trace), len(ea), i, (trace[i][1], bool(trace[i][3])) if i < len(trace) else None, ea[i] if i < len(ea) else None))
print('TP1 v5.1: runs %d, trades compared %d (TP1-rule trades %d), mismatches %d -> %s' % (runs, ntr, nt1, bad, 'ALL IDENTICAL' if not bad else 'DIFFERENCES'))
