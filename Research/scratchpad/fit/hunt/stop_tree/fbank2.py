"""Extra sequence features (event counts) appended to feat.pkl -> feat_all.pkl.  w_ = rolling-window net/same/opp event counts,
p_ = previous-session event structure, x_ = cross-session last-event features.  All d-normalised, raw VWAP sessions."""
import os, sys, pickle
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from fbase import base, sessions, sigs


def feats2(P, i, d):
    f = {}
    S, idx = sessions(P, False); k = idx[i]; a = S[k][0]
    for nm in ('core', 'vsl', 'full', 'arm'):
        sg = sigs(P, nm)
        for N in (12, 24, 48, 72, 96, 144, 200, 288, 400, 576):
            w = sg[max(0, i - N):i]
            f[f'w_{nm}Net{N}'] = d * sum(w)
            if N in (72, 144, 288): f[f'w_{nm}Opp{N}'] = sum(1 for x in w if x == -d)
        f[f'w_{nm}NetToday'] = d * sum(sg[a:i])
        if k >= 1:
            pa, pb = S[k - 1]; ps = [x for x in sg[pa:pb] if x]
            f[f'p_{nm}Same'] = sum(1 for x in ps if x == d); f[f'p_{nm}Opp'] = sum(1 for x in ps if x == -d)
            f[f'p_{nm}First'] = d * ps[0] if ps else 0; f[f'p_{nm}LastD'] = d * ps[-1] if ps else 0
            half = (pa + pb) // 2
            f[f'p_{nm}Net2H'] = d * sum(sg[half:pb])        # second half of previous session
            f[f'p_{nm}Frac'] = (d * sum(ps) / len(ps)) if ps else 0.0
        else:
            for x in ('Same', 'Opp', 'First', 'LastD', 'Net2H', 'Frac'): f[f'p_{nm}{x}'] = float('nan')
        if k >= 2:
            qa, qb = S[k - 2]; f[f'p_{nm}Net2'] = d * sum(sg[qa:S[k - 1][1]])
        else: f[f'p_{nm}Net2'] = float('nan')
        # last event before this session (any earlier session)
        j = a - 1
        while j >= 0 and sg[j] == 0: j -= 1
        f[f'x_{nm}LastBefore'] = d * sg[j] if j >= 0 else 0
        # opposite events since the last same-direction event
        j = i - 1; c = 0
        while j >= 0 and sg[j] != d:
            if sg[j] == -d: c += 1
            j -= 1
        f[f'x_{nm}OppSinceSame'] = c
        # run of identical-direction events immediately before i (signed: + same, - opp)
        evs = [x for x in sg[max(0, i - 2000):i] if x]
        r = 0
        if evs:
            last = evs[-1]
            for x in reversed(evs):
                if x == last: r += 1
                else: break
            r *= d * last
        f[f'x_{nm}Run'] = r
    return f


if __name__ == '__main__':
    B = pickle.load(open(os.path.join(HERE, 'feat.pkl'), 'rb'))
    out = []
    for t, f in B:
        P = base(t['sym']); g = dict(f); g.update(feats2(P, t['arm_i'], t['d'])); out.append((t, g))
    pickle.dump(out, open(os.path.join(HERE, 'feat_all.pkl'), 'wb'))
    print(len(out), 'trades', len(out[0][1]), 'features')
