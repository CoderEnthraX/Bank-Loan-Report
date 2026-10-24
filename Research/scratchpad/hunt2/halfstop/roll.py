"""Among first-same-dir-impulse-of-session cases: does a rolling net impulse count over N bars (or last K impulses) separate tight/normal?"""
import sys, io, contextlib
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S+'/hunt2/halfstop'); sys.path.insert(0, S+'/fit')
with contextlib.redirect_stdout(io.StringIO()):
    import feat
import m
R = [r for r in feat.ROWS if r['withN'] == 0 and r['lab'] in 'TN']
imp = {}
for s in set(r['sym'] for r in R):
    F = m.FEAT[s]; n = max(F) + 1
    imp[s] = [(1 if F[i]['bullImp'] else 0) - (1 if F[i]['bearImp'] else 0) if i in F else 0 for i in range(n)]
res = []
for N in list(range(10, 400, 10)):
    for k in range(1, 12):
        err = []
        for r in R:
            x = imp[r['sym']]; j = r['j']
            net = sum(x[max(0, j - N):j]) * r['d']
            pred = net <= -k
            if pred != (r['lab'] == 'T'): err.append(f"{r['src']}:{r['sym']}{r['t'][5:]}")
        res.append((len(err), N, k, err))
res.sort(key=lambda z: z[0])
for e in res[:12]: print('rolling N', e[1], 'k', e[2], 'errors', e[0], e[3])
res = []
for K in range(1, 30):
    for k in range(1, K + 1):
        err = []
        for r in R:
            x = imp[r['sym']]; j = r['j']; ev = [v for v in x[:j] if v][-K:]
            pred = sum(ev) * r['d'] <= -k
            if pred != (r['lab'] == 'T'): err.append(f"{r['src']}:{r['sym']}{r['t'][5:]}")
        res.append((len(err), K, k, err))
res.sort(key=lambda z: z[0])
for e in res[:8]: print('lastK', e[1], 'k', e[2], 'errors', e[0], e[3])
