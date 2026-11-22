"""Simple combinations formed from the 2021-23 columns of the one-at-a-time sweeps and the concept table (few tests: little room for luck),
evaluated on 2021-22 / 2023 / 2024-26. Run: python3 -I simple.py -> simple.pkl"""
import sys, pickle, numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/snr')
import engine as E, evalx as V, search as S, features as F
H = dict(f1col=F.CI['hour_ist'], f1mode=2, f1a=11, f1b=16)
CANDS = {5: [('Default', {}), ('Zone confirmed by 2 absorption bars (minZoneN 2)', dict(minZoneN=2)),
             ('+ volume average 80', dict(minZoneN=2, volLen=80)), ('+ absorption sensitivity 1.0', dict(minZoneN=2, volLen=80, absSens=1.0)),
             ('London hours 11:00-16:00 IST', dict(H)), ('minZoneN 2 + London hours', dict(minZoneN=2, **H)), ('minZoneN 2 + volume 80 + London hours', dict(minZoneN=2, volLen=80, **H)),
             ('minZoneN 2 + volume 80 + stop buffer 0.3 ATR', dict(minZoneN=2, volLen=80, slBuf=0.3)),
             ('minZoneN 2 + volume 80 + London + stop buffer 0.3', dict(minZoneN=2, volLen=80, slBuf=0.3, **H))],
         15: [('Default', {}), ('minZoneN 2', dict(minZoneN=2)), ('VWAP slope against (20 bars)', dict(f1col=F.CI['vwap_slope20'], f1mode=5)),
              ('minZoneN 2 + VWAP slope against', dict(minZoneN=2, f1col=F.CI['vwap_slope20'], f1mode=5)), ('London hours 11:00-16:00 IST', dict(H)),
              ('minZoneN 2 + volume 80', dict(minZoneN=2, volLen=80))],
         60: [('Default, ratio 1.3', dict(aggRatio=1.3)), ('ratio 1.3 + minZoneN 2', dict(aggRatio=1.3, minZoneN=2)), ('ratio 1.5', dict(aggRatio=1.5)), ('ratio 1.1', dict(aggRatio=1.1))],
         120: [('Default, ratio 1.3', dict(aggRatio=1.3)), ('ratio 1.3 + Friday only', dict(aggRatio=1.3, f1col=F.CI['dow'], f1mode=2, f1a=4, f1b=4)),
               ('ratio 1.3 + session POC side 0..1 ATR', dict(aggRatio=1.3, f1col=F.CI['poc_dist'], f1mode=4, f1a=-1, f1b=1)), ('ratio 1.5', dict(aggRatio=1.5))],
         180: [('Default, ratio 1.3', dict(aggRatio=1.3)), ('ratio 1.3 + against the 20-bar delta', dict(aggRatio=1.3, f1col=F.CI['cvd_s20'], f1mode=5)),
               ('ratio 1.3 + against the H1 EMA50 slope', dict(aggRatio=1.3, f1col=F.CI['h1_slope'], f1mode=5)),
               ('ratio 1.3 + against the session VWAP slope', dict(aggRatio=1.3, f1col=F.CI['vwap_slope20'], f1mode=5)),
               ('ratio 1.3 + against the 20-bar delta + against the VWAP slope', dict(aggRatio=1.3, f1col=F.CI['cvd_s20'], f1mode=5, f2col=F.CI['vwap_slope20'], f2mode=5))]}
out = {}
for tf, cs in CANDS.items():
    Xf = V.feat(tf)
    for name, kw in cs:
        si, sd, se, ss, sf = E.run(tf, E.params(**kw), Xf)
        o = V.outc(tf, si, sd, se, ss, 0, False)
        m = S.mets(o, None); out[(tf, name)] = (kw, m)
        print('%4s %-58s n %4d/%4d/%4d | 0.5R %4.1f/%4.1f/%4.1f | 1R %4.1f/%4.1f/%4.1f | net1R T %+.3f' % (
            {5: 'M5', 15: 'M15', 60: 'H1', 120: 'H2', 180: 'H3'}[tf], name[:58], m['A_n_1'], m['B_n_1'], m['T_n_1'],
            100 * m['A_acc_0.5'], 100 * m['B_acc_0.5'], 100 * m['T_acc_0.5'], 100 * m['A_acc_1'], 100 * m['B_acc_1'], 100 * m['T_acc_1'], m['T_net_1']), flush=True)
pickle.dump(out, open('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/snr/simple.pkl', 'wb'))
