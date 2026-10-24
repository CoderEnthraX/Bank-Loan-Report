"""Stage C: exit choices (each TP as the real exit, breakeven moves, partials) for candidate settings per timeframe."""
import sys, pickle, collections, multiprocessing as mp
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
EXITS = [('Exit at TP1 (0.6R)', dict(exitAt=1)), ('Exit at TP2 (1R)', dict(exitAt=2)), ('Exit at TP3 (1.5R)', dict(exitAt=3)), ('Exit at TP4 (2R)', dict(exitAt=4)),
         ('TP4 + breakeven at TP1', dict(exitAt=4, mv1On=True, mv1R=0.0)), ('TP2 + breakeven at TP1', dict(exitAt=2, mv1On=True, mv1R=0.0)),
         ('TP4 + breakeven at TP2', dict(exitAt=4, mv2On=True, mv2R=0.0))]
def job(arg):
    tf, cname, ename, o = arg
    import geng, ref_gs
    ref_gs.eprep = geng.ref_g.eprep; geng.ref_g = ref_gs
    tr = geng.run(tf, o)
    return tf, cname, ename, [(x['t'], x['res'], x['win'], tuple(x['hits']), x['sp'], x['risk'], x['be']) for x in tr]
def run(tf, cands):
    tasks = [(tf, cn, en, dict(co, **eo)) for cn, co in cands for en, eo in EXITS]
    out = {}
    with mp.Pool(4) as pool:
        for t, cn, en, tr in pool.imap_unordered(job, tasks): out[(cn, en)] = tr
    # partial: 50% at TP1, stop to breakeven, rest at TP4 (from the 'TP4 + breakeven at TP1' run)
    for cn, _ in cands:
        b = out[(cn, 'TP4 + breakeven at TP1')]
        out[(cn, '50% at TP1 + breakeven, rest TP4')] = [(x[0], (0.5 * 0.6 + 0.5 * x[1]) if x[3][0] else -1.0, x[3][0], x[3], x[4], x[5], False) for x in b]
    return out
if __name__ == '__main__':
    tf = sys.argv[1]; cands = pickle.load(open(S + '/gold/cands_%s.pkl' % tf, 'rb'))
    out = run(tf, cands)
    pickle.dump(dict(cands=cands, res=out), open(S + '/gold/stageC_%s.pkl' % tf, 'wb')); print(tf, 'stage C done', len(out), flush=True)
