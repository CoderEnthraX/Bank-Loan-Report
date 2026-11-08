"""check: every trade of the real engine (ref_g via geng, default settings) is a raw signal with the same direction, entry and stop,
and the engine's fill bar / TP hits equal the kit's (chart convention)"""
import sys, numpy as np
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold'); sys.path.insert(0, S + '/entry')
import geng, ref_g, signals, outcomes, data
for tf in sys.argv[1:]:
    s = signals.raw(tf); idx = {(int(a), int(b)): k for k, (a, b) in enumerate(zip(s['i'], s['d']))}
    o = outcomes.simulate(tf, s['i'], s['d'], s['entry'], s['stop_h'])
    tr = [x for x in ref_g.run(tf, {}) if x['exit'] is not None]
    bad = 0; hitbad = 0
    for x in tr:
        k = idx.get((x['arm'], x['dir']))
        if k is None or abs(s['entry'][k] - x['entry']) > 1e-9 or abs(s['stop_h'][k] - x['stop']) > 1e-9 or o['fill_bar'][k] != x['fill']:
            bad += 1
            if bad <= 3: print('  mismatch', x['arm'], x['dir'], x['entry'], x['stop'], x['fill'], None if k is None else (s['entry'][k], s['stop_h'][k], o['fill_bar'][k]))
            continue
        risk = x['dir'] * (x['entry'] - x['stop'])
        eng_mfe = x['dir'] * (x['best'] - x['entry']) / risk
        kit = o['mfe_c'][k]
        for r in (0.6, 1.0, 1.5, 2.0):
            ek = eng_mfe >= r - 1e-9 or (x['res'] is not None and x['res'] > 0 and r <= 2.0)
            if ek != (kit >= r - 1e-9): hitbad += 1
    print(tf, 'engine trades', len(tr), 'not matching a raw signal', bad, 'TP-hit disagreements', hitbad)
