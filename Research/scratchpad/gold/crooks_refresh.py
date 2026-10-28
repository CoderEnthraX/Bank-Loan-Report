"""After adding Crooks A / B: recompute every recovery rule on the final_<TF>.pkl sequences (now 19 rules + Off, the strategy's exitR) and add
Crooks money (backtest + 500 random orders) to every catalogue strategy (catalog_<TF>.pkl 'money'). Idempotent; backups *_before_crooks.pkl."""
import sys, os, pickle, shutil
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
import final, catalog, recovery as RC, crooks
MC = pickle.load(open(S + '/gold/crooks_mc.pkl', 'rb'))
def save(obj, fn):
    if not os.path.exists(fn.replace('.pkl', '_before_crooks.pkl')): shutil.copy2(fn, fn.replace('.pkl', '_before_crooks.pkl'))
    pickle.dump(obj, open(fn + '.tmp', 'wb')); os.replace(fn + '.tmp', fn)
for tf in crooks.TFS:
    fn = S + '/gold/final_%s.pkl' % tf; F = pickle.load(open(fn, 'rb'))
    F['recovery'] = {n: final.recov(F['trades'][n], final.exitR_strategy(F['cfg'][n]), F['cfg'][n]) for n in F['trades']}
    save(F, fn); print(tf, 'recovery', {n: len(v) for n, v in F['recovery'].items()})
    fc = S + '/gold/catalog_%s.pkl' % tf; C = pickle.load(open(fc, 'rb'))
    src = crooks.sources(tf)
    for s in C['strategies']:
        seq = crooks.sequence(s['trades'], s['cfg']); xr = crooks.exit_r(s['cfg']); trs = [(res, c, parts) for _, res, c, parts in seq]
        s['money']['crA_reset'] = RC.simulate(trs, 'Crooks A', cap=500.0, capAction='reset', exitR=xr)
        s['money']['crB3_reset'] = RC.simulate(trs, 'Crooks B', cap=500.0, capAction='reset', cSplit=3, exitR=xr)
        i = [k for k, d in enumerate(src) if d['cfg'] == s['cfg'] and d['name'] == s['scen'][0][0]][0]
        mc = MC.get((tf, i))
        s['money']['mc'] = {k: mc['rules'][k] for k in (('Crooks A', 3, 500.0, 'reset'), ('Crooks B', 3, 500.0, 'reset'), ('Off', 3, 0.0, 'clamp'))} if mc else None
    save(C, fc); print(tf, 'catalogue money', len(C['strategies']), 'strategies, random orders for', sum(1 for s in C['strategies'] if s['money']['mc']))
