"""Exact engine trades (ref_g = the Pine engine's Python twin, one trade at a time) as a table, so a ghost-type filter (decided at
the signal bar, the skipped trade still occupies the slot, exactly like the indicator's accuracy filters) can be scored exactly:
trades(tf, opts) -> DataFrame (arm, fill, dir, entry, stop, res, hit1..4 chart convention, mfe_m 1-minute path, split, ny_min, ...)."""
import sys, numpy as np, pandas as pd
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold'); sys.path.insert(0, S + '/entry')
import geng, ref_g, data, kit, outcomes, dataset
TPR = (0.6, 1.0, 1.5, 2.0)
def trades(tf, opts=None):
    o = dict(opts or {}); o.setdefault('exitAt', 4)
    vw = o.pop('vwAnchorG', 'session'); src = o.pop('vwSrcG', 'hlc3'); geng._CUR['vw'] = vw; geng._CUR['src'] = src
    P = geng.prepare(tf, vw, src); p = dict(ref_g.IN); p.update(o)
    R = [p['tp%dR' % k] for k in range(1, 5)]
    rows = [x for x in ref_g.run(tf, o) if x['exit'] is not None]
    b = data.load(tf)
    df = pd.DataFrame(dict(arm=[x['arm'] for x in rows], fill=[x['fill'] for x in rows], exit=[x['exit'] for x in rows], dir=[x['dir'] for x in rows],
                           entry=[x['entry'] for x in rows], stop=[x['stop'] for x in rows], res=[x['res'] for x in rows],
                           best=[x['best'] for x in rows], ghost=[x['ghost'] for x in rows], half=[x['half'] for x in rows]))
    risk = df.dir * (df.entry - df.stop)
    mfe_c = df.dir * (df.best - df.entry) / risk
    win = df.res.notna() & (df.res > 0) & (np.abs(df.res - R[p['exitAt'] - 1]) < 1e-9)
    for k in range(4):
        df['hit%d' % (k + 1)] = np.where(win, k + 1 <= p['exitAt'], (k + 1 < p['exitAt']) & (mfe_c >= R[k] - 1e-9))
    # 1-minute path outcome of the same trade (entry, stop, fill bar known): limit at the engine's fill bar
    om = outcomes.simulate(tf, df.arm.to_numpy(), df.dir.to_numpy(), df.entry.to_numpy(), df.stop.to_numpy(), mode=0, window=10 ** 6)
    df['mfe_m'] = om['mfe_m']; df['fill_chk'] = om['fill_bar'] == df.fill.to_numpy()
    df['utc'] = b['utc'][df.arm.to_numpy()]; df['split'] = dataset.split_of(df.utc.to_numpy())
    df['ny_min'] = kit.local_min(tf, 'ny')[df.arm.to_numpy()]
    df['cost'] = b['SP'][df.fill.to_numpy()] / risk
    return df
def report(df, name, splits=('train', 'valid'), col='mfe_m'):
    for s_ in splits:
        m = df[(df.split == s_) & ~df.ghost]
        if not len(m): continue
        h = np.array([np.mean(m[col] >= r - 1e-9) if col == 'mfe_m' else m['hit%d' % (k + 1)].mean() for k, r in enumerate(TPR)]) * 100
        print('%-34s %-5s n %5d %6.1f/mo | TP1-TP4 hit %s | vs no-edge %s' % (name[:34], s_, len(m), len(m) / kit.MONTHS[s_],
              ' '.join('%5.1f' % x for x in h), ' '.join('%+5.1f' % x for x in h - kit.BASE * 100)))
