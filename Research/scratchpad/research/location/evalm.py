"""Run option sets through the shared evaluator; compact summary + progress.md line.  usage: evalm.py name '<json opts>' [name2 '<json2>' ...]"""
import sys, json, os
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(D))
import lib
MOD = D + '/combo_loc.py'
base = lib.run_all(MOD, {}); bn, be = lib.split(base)
def m(v): return sum(v) / len(v) if v else float('nan')
args = sys.argv[1:]
for k in range(0, len(args), 2):
    name, opts = args[k], json.loads(args[k + 1])
    tr = lib.run_all(MOD, opts); tn, te = lib.split(tr); sa, sn, se = lib.stats(tr), lib.stats(tn), lib.stats(te)
    lo, hi = lib.boot_diff(be, te); lo1, hi1 = lib.boot_diff([dict(res=1 if x['hit1'] else -1) for x in be], [dict(res=1 if x['hit1'] else -1) for x in te])
    symE = symT = 0; ps = []
    for s in lib.SYMS:
        a = [x['res'] for x in base if x['sym'] == s]; b = [x['res'] for x in tr if x['sym'] == s]
        symE += m(b) > m(a); symT += sum(b) > sum(a); ps.append('%s %+.2f>%+.2f' % (s[:4], m(a), m(b)))
    print('== %s %s' % (name, json.dumps(opts)))
    for lab, s in (('ALL', sa), ('TRAIN', sn), ('TEST', se)): print('  %-5s' % lab, lib.fmt(s))
    print('  keep ALL %.0f%%  TEST dE2 %+.3f CI[%+.3f,%+.3f]  dE1 %+.3f CI[%+.3f,%+.3f] dE15 %+.3f  syms better E/trade %d/10, totalR %d/10'
          % (100 * sa['n'] / len(base), se['E2'] - lib.stats(be)['E2'], lo, hi, se['E1'] - lib.stats(be)['E1'], lo1, hi1, se['E15'] - lib.stats(be)['E15'], symE, symT))
    print('   ', ' | '.join(ps))
    with open(D + '/progress.md', 'a') as f:
        f.write('- %s %s | TRAIN n=%d E1 %+.3f E15 %+.3f E2 %+.3f | TEST n=%d E1 %+.3f E15 %+.3f E2 %+.3f CI[%+.3f,%+.3f] | ALL keep %.0f%% tot %+.0f syms %d/10\n'
                % (name, json.dumps(opts), sn['n'], sn['E1'], sn['E15'], sn['E2'], se['n'], se['E1'], se['E15'], se['E2'], lo, hi, 100 * sa['n'] / len(base), sa['totR2'], symE))
