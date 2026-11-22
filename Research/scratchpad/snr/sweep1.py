"""One-at-a-time sweeps of the Sniper settings (and the research extensions) around the defaults, per timeframe.
Run: python3 -I sweep1.py TF -> sweep1_<tf>.pkl + .txt"""
import sys, pickle, numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/snr')
import engine as E, evalx as V

GRID = dict(aggRatio=[1.1, 1.3, 1.5, 1.8, 2.2, 2.6, 3.0, 4.0, 6.0], absSens=[0.6, 0.8, 1.0, 1.2, 1.5, 2.0, 2.5], deltaSrc=[0, 1], volLen=[10, 20, 40, 80],
            absLen=[3, 5, 8, 12, 20], divMin=[5, 10, 15, 25, 40], wickPct=[20, 30, 40, 50, 60, 70], aggRelV=[0, 0.5, 0.8, 1.0, 1.3, 1.6, 2.0, 3.0],
            aggBody=[0, 30, 40, 50, 60, 70, 80], mode=[0, 1, 2], expiry=[2, 3, 5, 10, 20, 40], zone=[0, 1, 2], bandMult=[0.5, 1.0, 1.5, 2.0, 3.0],
            zoneAtr=[0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.5], maxDist=[0, 0.5, 1.0, 1.5, 2.5, 4.0, 6.0], cvd=[0, 1, 2], cvdLen=[1, 2, 3, 5, 10, 20],
            slopeOn=[0, 1], slopeLen=[3, 5, 10, 20, 40], cool=[0, 1, 3, 6, 12, 24], entry=[0, 1, 2], slMode=[0, 1], slAtr=[0.5, 1.0, 1.5, 2.0, 3.0],
            slBuf=[0, 0.1, 0.15, 0.3, 0.5, 1.0], swingLen=[2, 3, 5, 10, 20], minRisk=[0, 0.3, 0.5, 1.0, 1.5], maxRisk=[1.0, 2.0, 4.0, 6.0, 10.0],
            absMask=[1, 2, 4, 8, 3, 5, 9, 6, 10, 12, 14, 15], minAbsN=[1, 2, 3], aggDeltaPct=[0, 20, 40, 60, 80], confirm=[0, 1], maxRelVAgg=[0, 1.5, 2.0, 3.0, 5.0],
            minZoneN=[1, 2, 3, 4], minBarsArm=[0, 1, 2, 4], maxAggRatio=[0, 3, 5, 10, 20], sideReq=[0, 1, -1])


def main():
    tf = int(sys.argv[1]); base = dict(aggRatio=float(sys.argv[2])) if len(sys.argv) > 2 else {}
    out = []
    lines = []
    m0, _ = V.evaluate(tf, E.params(**base))
    out.append(('base', None, m0))
    def row(k, v, m):
        return '%-12s %-6s n %5d (%4d/%4d) | 0.5R %4.1f/%4.1f | 1R %4.1f/%4.1f edge %+5.1f/%+5.1f | 1.5R %4.1f/%4.1f | net1R %+.3f/%+.3f' % (
            k, v, m['n'], m['n_tr'], m['n_te'], 100 * m['tr_acc_0.5'], 100 * m['te_acc_0.5'], 100 * m['tr_acc_1'], 100 * m['te_acc_1'],
            100 * m['tr_edge_1'], 100 * m['te_edge_1'], 100 * m['tr_acc_1.5'], 100 * m['te_acc_1.5'], m['tr_net_1'], m['te_net_1'])
    lines.append(row('BASE', '', m0))
    for k, vals in GRID.items():
        for v in vals:
            kw = dict(base); kw[k] = v
            if k == 'slAtr':
                kw['slMode'] = 1
            if k == 'slopeLen':
                kw['slopeOn'] = 1
            if k == 'cvdLen':
                kw['cvd'] = 1
            try:
                m, _ = V.evaluate(tf, E.params(**kw))
            except Exception as e:
                lines.append('%s %s ERROR %s' % (k, v, e)); continue
            out.append((k, v, m))
            lines.append(row(k, v, m) if m['n_tr'] > 0 and m['n_te'] > 0 else '%-12s %-6s n %d' % (k, v, m['n']))
        lines.append('')
        print('\n'.join(lines[-len(vals) - 1:]), flush=True)
    pickle.dump(out, open('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/snr/sweep1_%d%s.pkl' % (tf, '_' + sys.argv[2] if base else ''), 'wb'))
    open('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/snr/sweep1_%d%s.txt' % (tf, '_' + sys.argv[2] if base else ''), 'w').write('\n'.join(lines))


if __name__ == '__main__':
    main()
