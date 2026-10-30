"""Crooks A and Crooks B loss recovery on gold 2021-2026, every timeframe, every catalogue strategy plus the default settings.
Crooks A: trades 1 and 2 of a cycle risk the base; from trade 3 every other trade is a recovery trade risking max(base, loss / final TP R);
          a winning recovery trade (or a fully won-back loss) starts a new cycle.
Crooks B: recovery trade risks max(base, loss / split / final TP R); a new cycle only when the whole loss is won back.
Compared with Off (fixed $50) and the earlier pick Rule C split (split 3, $500 cap, start again). Split 1-5 for Crooks B,
no cap / $500 clamp / $500 start again / $500 stop trading. Whole run, plus 2021-23 and 2024-26 each from a fresh $10,000.
The final TP R is the strategy's exitR (the R of the final target, partial closes not counted), like the strategy and the EA.
Output: crooks.pkl + crooks.txt (printed table)."""
import sys, pickle, multiprocessing as mp
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
import recovery as RC, greedy
TFS = ('M1', 'M5', 'M15', 'H1')
CAPV = ((0.0, 'clamp'), (500.0, 'clamp'), (500.0, 'reset'), (500.0, 'stop'))
VARIANTS = ([('Off', 3, 0.0, 'clamp'), ('Rule C split', 3, 500.0, 'reset')] + [('Crooks A', 3, c, a) for c, a in CAPV] +
            [('Crooks B', s, c, a) for s in (1, 2, 3, 4, 5) for c, a in CAPV])
def exit_r(cfg):
    d = dict(greedy.defaults()); d.update(cfg)
    return (d['tp1R'], d['tp2R'], d['tp3R'], d['tp4R'])[d['exitAt'] - 1]
def sequence(tr, cfg):
    """(time, R, spread cost in R, parts) in time order; a partial close at TP1 is passed in its two parts"""
    d = dict(greedy.defaults()); d.update(cfg); p = d['p1'] if d['exitAt'] > 1 else 0.0; t1 = d['tp1R']
    out = []
    for x in sorted(tr, key=lambda x: x[0]):
        res, c = x[1], x[4] / x[5]
        out.append((x[0], res, c, [(p * t1, p), (res - p * t1, 1 - p)] if (p and x[3][0]) else None))
    return out
def run(seq, mode, split, cap, act, exitR, extra=0.0, base=50.0):
    r = RC.simulate([(res, c + extra, parts) for _, res, c, parts in seq], mode, base=base, cap=cap, capAction=act, cSplit=split, exitR=exitR)
    r['ratio'] = r['net'] / r['maxDD'] if r['maxDD'] > 0 else 0.0
    return r
def sources(tf):
    """the default settings and every catalogue strategy (each with the scenarios it answers)"""
    F = pickle.load(open(S + '/gold/final_%s.pkl' % tf, 'rb')); Cat = pickle.load(open(S + '/gold/catalog_%s.pkl' % tf, 'rb'))
    out = [dict(name='Default settings', scen=['Default settings'], cfg=F['cfg']['default'], trades=F['trades']['default'])]
    for s in Cat['strategies']:
        out.append(dict(name=s['scen'][0][0], scen=[n for n, _ in s['scen']], cfg=s['cfg'], trades=s['trades']))
    return out
def job(arg):
    tf, i = arg
    src = sources(tf)[i]; seq = sequence(src['trades'], src['cfg']); xr = exit_r(src['cfg'])
    A = [x for x in seq if x[0].year <= 2023]; B = [x for x in seq if x[0].year >= 2024]
    rows = [dict(mode=m, split=s, cap=c, act=a, all=run(seq, m, s, c, a, xr), A=run(A, m, s, c, a, xr), B=run(B, m, s, c, a, xr)) for m, s, c, a in VARIANTS]
    stress = {(m, s, c, a, e): run(seq, m, s, c, a, xr, extra=e) for m, s, c, a in VARIANTS if c == 0 or a != 'stop' for e in (0.05, 0.10)}
    caps = {(m, s, c, a): run(seq, m, s, c, a, xr) for m in ('Crooks A', 'Crooks B') for s in ((3,) if m == 'Crooks A' else (1, 2, 3))
            for c in (250.0, 1000.0) for a in ('clamp', 'reset')}
    return tf, i, dict(name=src['name'], scen=src['scen'], cfg=src['cfg'], exitR=xr, n=len(seq), rows=rows, stress=stress, caps=caps)
def ok(r): return (not r['ruined']) and r['net'] > 0 and r['maxRisk'] <= 500.0 + 1e-9 and r['maxDDpct'] <= 0.40
def label(x): return ('%s%s%s' % (x['mode'], ' split %d' % x['split'] if x['mode'] in ('Crooks B', 'Rule C split') else '',
                                  (' cap $%d %s' % (x['cap'], {'clamp': 'clamp', 'reset': 'start again', 'stop': 'stop'}[x['act']])) if x['cap'] else ''))
if __name__ == '__main__':
    jobs = [(tf, i) for tf in TFS for i in range(len(sources(tf)))]
    with mp.Pool(4) as pool: res = pool.map(job, jobs)
    out = {}
    for tf, i, d in res: out[(tf, i)] = d
    pickle.dump(out, open(S + '/gold/crooks.pkl', 'wb'))
    lines = []
    for (tf, i), d in sorted(out.items(), key=lambda kv: (TFS.index(kv[0][0]), kv[0][1])):
        off = d['rows'][0]['all']
        lines.append('\n%s | %s (%s) | exit R %.2f | %d trades | Off: net %+.0f, DD $%.0f (%.0f%%), ratio %.2f' % (
            tf, d['name'], ', '.join(d['scen']), d['exitR'], d['n'], off['net'], off['maxDD'], 100 * off['maxDDpct'], off['ratio']))
        for x in d['rows'][1:]:
            a, ra, rb = x['all'], x['A'], x['B']
            lines.append('   %-36s | net %+9.0f  DD $%7.0f (%3.0f%%)  max risk $%7.0f  avg $%5.0f  worst run $%7.0f  %s | ratio %5.2f | 21-23 %+8.0f DD %3.0f%% %s | 24-26 %+8.0f DD %3.0f%% %s | %s' % (
                label(x), a['net'], a['maxDD'], 100 * a['maxDDpct'], a['maxRisk'], a['avgRisk'], a['worstRun'], 'BLOWN' if a['ruined'] else ('stop ' if a['capStopped'] else 'ok   '),
                a['ratio'], ra['net'], 100 * ra['maxDDpct'], 'X' if ra['ruined'] else ' ', rb['net'], 100 * rb['maxDDpct'], 'X' if rb['ruined'] else ' ', 'ELIGIBLE' if ok(a) and ok(ra) and ok(rb) else ''))
    open(S + '/gold/crooks.txt', 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))
