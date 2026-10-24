"""Alternative VWAP series from the CSV VWAP: back out each bar's relative volume, then recompute with another source/anchor/weighting."""
import sys, datetime as dt
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S+'/fit')
from engine import prepare as eprep
_c = {}
def weights(sym):
    if sym in _c: return _c[sym]
    P = eprep(sym); R = P['rows']; D = P['daystart']; n = len(R); w = [1.0]*n; W = 0.0; bad = 0
    for i, r in enumerate(R):
        hl = (r['h']+r['l']+r['c'])/3
        if D[i] or r['vwap'] is None or R[i-1]['vwap'] is None: w[i] = 1.0; W = 1.0; continue
        den = hl - R[i-1]['vwap']; num = r['vwap'] - R[i-1]['vwap']
        rr = num/den if abs(den) > 1e-7*abs(hl) else None
        if rr is None or not (0 < rr < 1): bad += 1; wi = W*0.01   # unidentifiable -> small nominal weight
        else: wi = W*rr/(1-rr)
        w[i] = wi; W += wi
    # check: recompute
    err = 0.0; sp = sw = 0.0
    for i, r in enumerate(R):
        if D[i]: sp = sw = 0.0
        sp += w[i]*(r['h']+r['l']+r['c'])/3; sw += w[i]
        if r['vwap'] is not None: err = max(err, abs(sp/sw - r['vwap']))
    _c[sym] = (P, w, bad, err); return _c[sym]
def series(sym, mode):
    """mode: csv | twap (hlc3, equal weights) | close | hl2 | ohlc4 | twapclose | ny (hlc3 volume, anchor = New-York midnight) | utc"""
    P, w, bad, err = weights(sym); R = P['rows']; D = P['daystart']
    if mode == 'csv': return [r['vwap'] for r in R]
    src = {'close': lambda r: r['c'], 'twapclose': lambda r: r['c'], 'hl2': lambda r: (r['h']+r['l'])/2,
           'ohlc4': lambda r: (r['o']+r['h']+r['l']+r['c'])/4}.get(mode, lambda r: (r['h']+r['l']+r['c'])/3)
    eq = mode in ('twap', 'twapclose')
    def anchor(i):
        if mode in ('ny', 'utc'):
            t = dt.datetime.strptime(R[i]['t'], '%Y-%m-%d %H:%M') - dt.timedelta(hours=5, minutes=30)  # UTC
            if mode == 'ny': t -= dt.timedelta(hours=4)  # EDT in Oct
            if i == 0: return True
            tp = dt.datetime.strptime(R[i-1]['t'], '%Y-%m-%d %H:%M') - dt.timedelta(hours=5, minutes=30)
            if mode == 'ny': tp -= dt.timedelta(hours=4)
            return t.date() != tp.date()
        return D[i]
    out = []; sp = sw = 0.0
    for i, r in enumerate(R):
        if anchor(i): sp = sw = 0.0
        wi = 1.0 if eq else w[i]
        sp += wi*src(r); sw += wi; out.append(sp/sw)
    return out
if __name__ == '__main__':
    for s in ('SENSEX', 'CRUDE'):
        P, w, bad, err = weights(s); print(s, 'unidentifiable bars', bad, 'of', len(w), 'max recompute err', err)
        for m in ('twap', 'close', 'hl2', 'ohlc4', 'ny'):
            a = series(s, m); b = series(s, 'csv'); d = sorted(abs(x-y) for x, y in zip(a, b) if y is not None)
            print('   ', m, 'median |diff| %.3f p90 %.3f' % (d[len(d)//2], d[int(len(d)*.9)]))
