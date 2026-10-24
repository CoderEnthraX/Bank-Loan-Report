"""VWAP settings study on the model: each config at a 1R exit (1:1) and a 2R exit (1:2)."""
import sys, json, random
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/research'); import lib
M = S + '/research/vwap_set/score_vw.py'
CV = dict(vwCompute=True)
C = [
 ('Source / weights', 'Session VWAP, hlc3, slope 3 bars (current)', {}),
 ('Source / weights', 'Session VWAP rebuilt from volume (check)', dict(CV)),
 ('Source / weights', 'Source = close', dict(CV, vwSrc='close')),
 ('Source / weights', 'Source = hl2', dict(CV, vwSrc='hl2')),
 ('Source / weights', 'Source = ohlc4', dict(CV, vwSrc='ohlc4')),
 ('Source / weights', 'Equal weights (time-weighted average)', dict(CV, vwEqual=True)),
 ('Anchor', 'Weekly VWAP', dict(CV, vwAnchor='week')),
 ('Anchor', 'Monthly VWAP', dict(CV, vwAnchor='month')),
 ('Slope', 'Slope off (position only)', dict(slopeBars=0)),
 ('Slope', 'Slope 1 bar', dict(slopeBars=1)),
 ('Slope', 'Slope 2 bars', dict(slopeBars=2)),
 ('Slope', 'Slope 5 bars', dict(slopeBars=5)),
 ('Slope', 'Slope 10 bars', dict(slopeBars=10)),
 ('Slope', 'Slope 3, not across the session start', dict(slopeCross=False)),
 ('Slope', 'Slope only (no above/below rule)', dict(vwapFilter=False)),
 ('Slope', 'No VWAP rule at all', dict(vwapFilter=False, slopeBars=0)),
]
for s_ in (1.5, 2.0, 2.4, 3.0):
    C.append(('Distance (skipped run invisibly)', 'Max %.1f sigma from VWAP (Don\'t Chase)' % s_, dict(noChase=True, noChaseSig=s_)))
for m in (0.25, 0.5, 1.0):
    C.append(('Distance (skipped run invisibly)', 'Min %.2f ATR from VWAP' % m, dict(minDistAtr=m)))
for m in (0.25, 0.5, 1.0):
    C.append(('Distance (skipped run invisibly)', 'Min %.2f sigma from VWAP' % m, dict(minDistSig=m)))
def summ(tr):
    n = len(tr)
    return dict(n=n, win=sum(1 for x in tr if x['res'] > 0) / n if n else 0, E=sum(x['res'] for x in tr) / n if n else 0, tot=sum(x['res'] for x in tr))
out = []
for fam, name, o in C:
    row = dict(fam=fam, name=name)
    for ex, key in ((2, 'r1'), (4, 'r2')):
        tr = lib.run_all(M, dict(o, exitAt=ex)); tn, te = lib.split(tr)
        dd = {}
        for x in tr: dd.setdefault('%s|%s' % (x['sym'], x['t'][:10]), []).append(x['res'])
        row[key] = dict(all=summ(tr), train=summ(tn), test=summ(te), sym={s: summ([x for x in tr if x['sym'] == s]) for s in lib.SYMS}, days=dd)
    out.append(row); a, b = row['r1']['all'], row['r2']['all']
    print('%-34s %-44s 1:1 win %4.1f%% E %+.3f | 1:2 n %4d win %4.1f%% E %+.3f tot %+4.0f' % (fam, name, 100 * a['win'], a['E'], b['n'], 100 * b['win'], b['E'], b['tot']), flush=True)
json.dump(out, open(S + '/research/vwap_set/grid.json', 'w'))
