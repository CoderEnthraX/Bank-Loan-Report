import sys, pickle, os, tempfile
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold'); sys.path.insert(0, S + '/mq5check/rec')
import recovery as RC, parity_month_v50 as PM
U = pickle.load(open(S + '/v50/user_seq.pkl', 'rb'))[0.1]
seq, sds, xr = U['seq'], U['sds'], U['xr']
months = []; key = None
for (t, res, c, parts), sd in zip(seq, sds):
    k = (t.year, t.month)
    if k != key: months.append([]); key = k
    rm = sd * (1.0 + c); months[-1].append((res, c, parts, None, None, rm, None, 2.0 * rm))
tmp = tempfile.mkdtemp(); path = os.path.join(tmp, 'seq.txt')
with open(path, 'w') as f:
    for mi, mt in enumerate(months):
        if mi: f.write('M\n')
        for (res, c, parts, _, _, rm, _, kr) in mt: f.write('%r %r %r %r %d\n' % (res, c, rm, kr, 0))
e = PM.ea(path, xr, 'Rule C split', 'profit', 0.0, 'clamp', {})
pos = 0
for mi, mt in enumerate(months):
    tr = []; rr = RC.simulate(mt, 'Rule C split', base=50.0, cap=0.0, capAction='clamp', cSplit=3, exitR=xr, start=1e12, trace=tr, sizeBy='profit')
    toks = e[pos:pos + len(mt)]; pos += len(mt)
    rs = [float(x.split()[1]) for x in toks if x.startswith('R ')]
    for i, (a, b) in enumerate(zip(rs, tr)):
        if abs(a - b) > 1e-9 * max(1.0, abs(b)):
            print('month', mi, 'trade', i, 'EA', a, 'py', b, 'ruined', rr['ruined'], 'len', len(tr), len(mt))
            net = 0.0
            for j in range(max(0, i - 6), i + 1):
                res, c = mt[j][0], mt[j][1]
                print('   ', j, 'res %.3f c %.4f' % (res, c), 'py risk %.4f EA risk %.4f' % (tr[j], rs[j]))
            # net before trade i (py)
            net = sum(tr[j] * (mt[j][0] - mt[j][1]) / (1 + mt[j][1]) for j in range(i))
            print('   py net before trade', i, '= %.6f' % net)
            sys.exit(0)
print('no difference found')
