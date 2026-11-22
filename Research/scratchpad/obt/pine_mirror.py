"""A line-by-line Python copy of the Pine OB_ENGINE (build_ob_pine.py), on the M5 bars of prep.py with UTC times and the Europe/Athens
clock: its signals must equal py_sig.txt (the EA = ob_stream)."""
import numpy as np, datetime as dt, math, sys
CM = int(sys.argv[1]) * 60 if len(sys.argv) > 1 else 300
TFS = [int(x) for x in sys.argv[2].split(',')] if len(sys.argv) > 2 else [15, 30, 60]
from zoneinfo import ZoneInfo
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
d = dict(np.load(S + '/entry/cache_M1.npz'))
a, b = 1780275600, 1790985600
m = (d['srv'] >= a) & (d['srv'] < b)
bars = []
for s, u, o, h, l, c, v in zip(d['srv'][m], d['utc'][m], d['O'][m], d['H'][m], d['L'][m], d['C'][m], d['TV'][m]):
    k = int(s) // CM * CM
    if bars and bars[-1][0] == k:
        x = bars[-1]; x[3] = max(x[3], h); x[4] = min(x[4], l); x[5] = c; x[6] += v
    else: bars.append([k, (int(u) - (int(s) - k)) * 1000, o, h, l, c, float(v)])   # [srv key, utc open, o h l c v]
ATH = ZoneInfo('Europe/Athens')
def hourz(t_ms, z): return dt.datetime.fromtimestamp(t_ms / 1000, z).hour
def f_obOff(t): return ((hourz(t, ATH) - hourz(t, dt.timezone.utc) + 24) % 24) * 60
def f_obKey(t, off, mm): return int(math.floor((t + off * 60000) / (mm * 60000.0)))
obTfA = TFS; obTfN = len(TFS); obFvgN = 3; obEpi = 30; obDays = 20; obVolN = 20; obVolMult = 1.0; obAbsBody = 40.0; obAbsWick = 50.0; obAggBody = 55.0; obBufTk = 1; mintick = 0.01
obTfMs = CM * 1000
obCurOn = [False] * 3; obCurK = [0] * 3; obCurO = [0.0] * 3; obCurH = [0.0] * 3; obCurL = [0.0] * 3; obCurC = [0.0] * 3; obDN = [0] * 3
obDO = [0.0] * 18; obDH = [0.0] * 18; obDL = [0.0] * 18; obDC = [0.0] * 18
Z = []   # [d, lo, hi, t0, st, tb, ab]
obPL = []; obPH = []
def f_obDel(k): del Z[k]
def f_obAdd(dr, lo, hi, t0):
    if len(Z) >= 100: f_obDel(0)
    Z.append([dr, lo, hi, t0, 0, -1, False])
def f_obFvg(q, dr, i, kk):
    bb = q * 6
    return (obDL[bb + kk] > obDH[bb + kk - 2] and obDC[bb + kk] > obDH[bb + i]) if dr == 1 else (obDH[bb + kk] < obDL[bb + kk - 2] and obDC[bb + kk] < obDL[bb + i])
def prange(x, y): return range(x, y + 1) if x <= y else range(x, y - 1, -1)   # Pine for x to y
def f_obClose(q, t0):
    bb = q * 6; n = obDN[q]
    if n == 6:
        for j in prange(0, 4):
            obDO[bb + j] = obDO[bb + j + 1]; obDH[bb + j] = obDH[bb + j + 1]; obDL[bb + j] = obDL[bb + j + 1]; obDC[bb + j] = obDC[bb + j + 1]
        n = 5
    obDO[bb + n] = obCurO[q]; obDH[bb + n] = obCurH[q]; obDL[bb + n] = obCurL[q]; obDC[bb + n] = obCurC[q]
    n += 1; obDN[q] = n; obCurOn[q] = False
    k = n - 1
    for dd in prange(0, 1):
        dr = 1 if dd == 0 else -1
        for i in prange(k - obFvgN, k - 2):
            if i >= 0:
                opp = obDC[bb + i] < obDO[bb + i] if dr == 1 else obDC[bb + i] > obDO[bb + i]
                if opp and f_obFvg(q, dr, i, k):
                    early = False
                    if i + 2 <= k - 1:
                        for kk in prange(i + 2, k - 1):
                            if f_obFvg(q, dr, i, kk): early = True
                    if not early: f_obAdd(dr, obDL[bb + i], obDH[bb + i], t0)
out = open(S + '/obt/pine_sig.txt', 'w')
V = [x[6] for x in bars]
for bi, x in enumerate(bars):
    key, time, op, hi_, lo_, cl, vol = x
    obV = vol if vol > 0 else 1.0
    obVa = sum(V[bi - obVolN:bi]) / obVolN if bi >= obVolN else None
    obHaveV = bi >= obVolN and obVa is not None
    obSig = 0; obStopC = None; obStopS = None
    obOffM = f_obOff(time)
    for q in prange(0, obTfN - 1):
        mm = obTfA[q]; kq = f_obKey(time, obOffM, mm)
        if obCurOn[q] and obCurK[q] != kq: f_obClose(q, time)
        if not obCurOn[q]:
            obCurOn[q] = True; obCurK[q] = kq; obCurO[q] = op; obCurH[q] = hi_; obCurL[q] = lo_; obCurC[q] = cl
        else:
            obCurH[q] = max(obCurH[q], hi_); obCurL[q] = min(obCurL[q], lo_); obCurC[q] = cl
    if bi >= 4:
        L = lambda k: bars[bi - k][4]; H = lambda k: bars[bi - k][3]
        if L(2) <= L(0) and L(2) <= L(1) and L(2) <= L(3) and L(2) <= L(4):
            if len(obPL) == 200: obPL.pop(0)
            obPL.append(L(2))
        if H(2) >= H(0) and H(2) >= H(1) and H(2) >= H(3) and H(2) >= H(4):
            if len(obPH) == 200: obPH.pop(0)
            obPH.append(H(2))
    obRng = hi_ - lo_; obBody = abs(cl - op); obS = 0; zk = 0
    while zk < len(Z):
        zt0 = Z[zk][3]
        if zt0 > time: zk += 1
        else:
            zd, zlo, zhi = Z[zk][0], Z[zk][1], Z[zk][2]
            zdead = cl < zlo if zd == 1 else cl > zhi
            zgone = False; zgo = True
            if Z[zk][4] == 0:
                if time - zt0 > obDays * 86400000 or zdead: zgone = True
                elif lo_ <= zhi and hi_ >= zlo: Z[zk][4] = 1; Z[zk][5] = bi
                else: zgo = False
            if not zgone and zgo:
                if bi - Z[zk][5] >= obEpi or zdead: zgone = True
                elif obRng > 0:
                    if Z[zk][6] and (cl > op if zd == 1 else cl < op) and obBody >= obAggBody / 100.0 * obRng:
                        obS = zd; zgone = True
                    elif obHaveV and lo_ <= zhi and hi_ >= zlo:
                        zwk = min(op, cl) - lo_ if zd == 1 else hi_ - max(op, cl)
                        if obV > obVolMult * obVa and obBody < obAbsBody / 100.0 * obRng and zwk >= obAbsWick / 100.0 * obRng: Z[zk][6] = True
            if zgone: f_obDel(zk)
            else: zk += 1
    obTc = time + obTfMs
    for q in prange(0, obTfN - 1):
        if obCurOn[q] and f_obKey(obTc, obOffM, obTfA[q]) != obCurK[q]: f_obClose(q, obTc)
    if obS != 0:
        obBuf = obBufTk * mintick; obSig = obS
        obStopC = lo_ - obBuf if obS == 1 else hi_ + obBuf
        if obS == 1 and len(obPL) > 0:
            for j in prange(len(obPL) - 1, 0):
                if obPL[j] < cl: obStopS = obPL[j] - obBuf; break
        if obS == -1 and len(obPH) > 0:
            for j in prange(len(obPH) - 1, 0):
                if obPH[j] > cl: obStopS = obPH[j] + obBuf; break
        out.write('%d %d %.2f %.2f %s\n' % (key, obSig, cl, obStopC, '%.2f' % obStopS if obStopS is not None else '0'))
out.close()
import importlib
src = open(S + '/ob/ob_stream.py').read().replace('import ob_test as T', 'T = None')
ns = {'__file__': S + '/ob/ob_stream.py', '__name__': 'obs'}; exec(compile(src, 'ob_stream', 'exec'), ns)
eng = ns['OB'](CM // 60, TFS); po = open(S + '/obt/py_sig2.txt', 'w')
for x in bars:
    r = eng.bar(dt.datetime(1970, 1, 1) + dt.timedelta(seconds=x[0]), x[2], x[3], x[4], x[5], x[6])
    if r: po.write('%d %d %.2f %.2f %s\n' % (x[0], r[0], r[1], r[2], '%.2f' % r[3] if r[3] is not None else '0'))
po.close()
A = set(open(S + '/obt/py_sig2.txt').read().split('\n')) - {''}; B = set(open(S + '/obt/pine_sig.txt').read().split('\n')) - {''}
print('python (= EA)', len(A), 'pine copy', len(B), 'only python', len(A - B), 'only pine', len(B - A))
