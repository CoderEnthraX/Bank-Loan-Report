"""Print a timeframe's final picks: settings, halves, years, streaks, the four pure exits and the best recovery rules."""
import sys, pickle
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'; sys.path.insert(0, S + '/gold')
import greedy, labels
tf = sys.argv[1]; F = pickle.load(open(S + '/gold/final_%s.pkl' % tf, 'rb'))
pk = lambda t: greedy.pack([(x[0], x[1], x[3][0], x[4] / x[5]) for x in t])
for prof in ('default', 'profit', 'streak'):
    tr = F['trades'][prof]; m = greedy.metrics(pk(tr), {})
    print('\n%s %s | passed %s\n   %s' % (tf, prof, F.get('passed', {}).get(prof), labels.short(F['cfg'][prof])))
    n = len(tr); tp = [sum(1 for x in tr if x[3][k]) / n for k in range(4)]
    print('   n %d (%.2f/day) win %.1f%% profitable %.1f%% TP1-4 %s | A %+.3f B %+.3f all %+.3f | W/L %d/%d | ypos %d %s' % (
        n, n / 1485, 100 * sum(1 for x in tr if x[2]) / n, 100 * m['all']['win'], '/'.join('%.0f' % (100 * v) for v in tp), m['A']['E'], m['B']['E'], m['all']['E'],
        m['all']['maxW'], m['all']['maxL'], m['ypos'], {y: round(v, 1) for y, v in m['years'].items()}))
    if 'exits' in F:
        for k in (1, 2, 3, 4):
            c, t = F['exits'][(prof, k)]; mm = greedy.metrics(pk(t), {})
            print('     exit TP%d: n %d win %.1f%% all %+.3f A %+.3f B %+.3f W/L %d/%d ypos %d' % (k, mm['all']['n'], 100 * mm['all']['win'], mm['all']['E'], mm['A']['E'], mm['B']['E'], mm['all']['maxW'], mm['all']['maxL'], mm['ypos']))
    if 'recovery' in F:
        rows = F['recovery'][prof]; alive = sorted([x for x in rows if not x['ruined'] and x['net'] > 0 and x['maxDD'] > 0 and x['maxRisk'] <= 500.01], key=lambda x: -x['net'] / x['maxDD'])
        off = [x for x in rows if x['mode'] == 'Off'][0]
        print('     recovery: Off net %+.0f DD %.0f | ruined %d of %d | best: %s' % (off['net'], off['maxDD'], sum(1 for x in rows if x['ruined']), len(rows),
              '; '.join('%s%s %+.0f/%.0f=%.1f' % (x['mode'][:22], '+cap' if x['cap'] else '', x['net'], x['maxDD'], x['net'] / x['maxDD']) for x in alive[:4])))
