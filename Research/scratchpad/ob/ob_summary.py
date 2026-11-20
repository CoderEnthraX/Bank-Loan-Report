import pickle, collections
L = (0.1, 0.2, 0.3, 0.5, 0.6, 1.0, 1.5, 2.0, 3.0); COST = 0.23
R = pickle.load(open('ob_results.pkl', 'rb'))
def netR(x, lv):
    r = x['risk']
    return (lv * r - COST) / (r + COST) if x['mfe'] >= lv else -1.0
def rows():
    for (ltf, htf) in [('M1', 'M3'), ('M1', 'M5'), ('M5', 'M15'), ('M5', 'M30'), ('M5', 'H1'), ('M15', 'H1'), ('M15', 'H4')]:
        for st in ('candle', 'swing'):
            for fl in (False, True):
                xs = [x for x in R if x['ltf'] == ltf and x['htf'] == htf and x['stop'] == st and (x['filt'] or not fl)]
                if not xs: continue
                hit = [sum(x['mfe'] >= lv for x in xs) / len(xs) for lv in L]
                net = [sum(netR(x, lv) for x in xs) / len(xs) for lv in L]
                yield ltf, htf, st, fl, xs, hit, net
if __name__ == '__main__':
    print('entry TF / OB TF / stop / filters | trades | avg risk | reached %: ' + ' '.join('%4sR' % lv for lv in L))
    for ltf, htf, st, fl, xs, hit, net in rows():
        print('%-3s %-3s %-6s %-8s | %5d | %5.2f | %s' % (ltf, htf, st, 'filters' if fl else 'none', len(xs), sum(x['risk'] for x in xs) / len(xs), ' '.join('%4.0f%%' % (100 * h) for h in hit)))
        print('%35s net R/trade: %s | best %+.3f at %sR' % ('', ' '.join('%+.2f' % v for v in net), max(net), L[net.index(max(net))]))
