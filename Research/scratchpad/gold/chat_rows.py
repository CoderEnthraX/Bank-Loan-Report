"""Markdown rows for the chat summary from final_<TF>.pkl."""
import sys, os, pickle
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'; sys.path.insert(0, S + '/gold')
import greedy, labels
pk = lambda t: greedy.pack([(x[0], x[1], x[3][0], x[4] / x[5]) for x in t])
for prof in ('default', 'profit', 'streak'):
    print('\n' + prof)
    print('| TF | Trades (per day) | Profitable % | TP1 / TP2 / TP3 / TP4 hit | R per trade after spread (2021-23 / 2024-26) | Years positive | Longest win / loss streak |')
    for tf in ('M1', 'M5', 'M15', 'H1'):
        fn = S + '/gold/final_%s.pkl' % tf
        if not os.path.exists(fn): continue
        F = pickle.load(open(fn, 'rb')); tr = F['trades'][prof]; m = greedy.metrics(pk(tr), {}); n = len(tr)
        tp = [sum(1 for x in tr if x[3][k]) / n for k in range(4)]
        print('| %s | %s (%.2f) | %.0f%% | %s | %+.3f (%+.3f / %+.3f) | %d of 6 | %d / %d |' % (tf, format(n, ','), n / 1485, 100 * m['all']['win'], ' / '.join('%.0f%%' % (100 * v) for v in tp),
              m['all']['E'], m['A']['E'], m['B']['E'], m['ypos'], m['all']['maxW'], m['all']['maxL']))
    if prof != 'default':
        for tf in ('M1', 'M5', 'M15', 'H1'):
            fn = S + '/gold/final_%s.pkl' % tf
            if os.path.exists(fn): F = pickle.load(open(fn, 'rb')); print('  %s: %s' % (tf, labels.short(F['cfg'][prof])))
