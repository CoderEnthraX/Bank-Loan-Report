"""evaluate a chop option set through lib.run_all (full engine). ev(opts) -> dict; paired-by-day bootstrap vs baseline."""
import sys, pickle, random, json
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/research'); import lib
MOD = S + '/research/chop/score_chop.py'
BASE = pickle.load(open(S + '/research/chop/base.pkl', 'rb'))
def key(x): return (x['sym'], x['arm'], x['fill'], x['dir'])
def run(opts): return lib.run_all(MOD, opts)
def E(tr): return sum(x['res'] for x in tr) / len(tr) if tr else 0.0
def daypaired(a, b, it=2000, seed=7):
    """paired-by-day bootstrap of E2(b) - E2(a) over TEST days (sym, date of fill)"""
    days = sorted(set((x['sym'], x['t'][:10]) for x in a) | set((x['sym'], x['t'][:10]) for x in b))
    ga = {d: [] for d in days}; gb = {d: [] for d in days}
    for x in a: ga[(x['sym'], x['t'][:10])].append(x['res'])
    for x in b: gb[(x['sym'], x['t'][:10])].append(x['res'])
    rnd = random.Random(seed); ds = []
    for _ in range(it):
        sa = na = sb = nb = 0
        for _ in days:
            d = days[rnd.randrange(len(days))]; sa += sum(ga[d]); na += len(ga[d]); sb += sum(gb[d]); nb += len(gb[d])
        ds.append(sb / max(nb, 1) - sa / max(na, 1))
    ds.sort(); return ds[int(.025 * it)], ds[int(.975 * it)]
def summary(tr, ci=True):
    tn, te = lib.split(tr); bn, be = lib.split(BASE)
    r = dict(n=len(tr), keep=len(tr) / len(BASE), E=E(tr), tot=sum(x['res'] for x in tr), En=E(tn), Ee=E(te), nn=len(tn), ne=len(te),
             dn=E(tn) - E(bn), de=E(te) - E(be), hit2e=sum(x['hit2'] for x in te) / max(len(te), 1), E1e=sum(1 if x['hit1'] else -1 for x in te) / max(len(te), 1))
    better = 0; ps = {}
    for s in lib.SYMS:
        a = [x for x in BASE if x['sym'] == s]; b = [x for x in tr if x['sym'] == s]; ps[s] = E(b) - E(a); better += E(b) > E(a) + 1e-12
    r['better'] = better; r['ps'] = ps
    if ci: r['ci_day'] = daypaired(be, te); r['ci_lib'] = lib.boot_diff(be, te)
    return r
def line(name, r):
    s = (f"{name:44s} keep {r['keep']:.0%} ALL E2 {r['E']:+.3f} tot {r['tot']:+.0f} | TRAIN n={r['nn']} {r['En']:+.3f} ({r['dn']:+.3f}) | TEST n={r['ne']} {r['Ee']:+.3f} ({r['de']:+.3f})"
         f" hit2 {r['hit2e']:.1%} E1 {r['E1e']:+.3f} | instr better {r['better']}/10")
    if 'ci_day' in r: s += f" | dayCI [{r['ci_day'][0]:+.3f},{r['ci_day'][1]:+.3f}] libCI [{r['ci_lib'][0]:+.3f},{r['ci_lib'][1]:+.3f}]"
    return s
if __name__ == '__main__':
    o = json.loads(sys.argv[1]); tr = run(o); print(line(sys.argv[1], summary(tr)))
