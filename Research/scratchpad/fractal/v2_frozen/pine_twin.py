"""Python twin of the Pine indicator (pine/build_fbg.py): the same per-candle code, method by method, run on chart candles.
request.security(tf, f_piv(L, R), lookahead_on) is emulated: f_piv evaluated on every fractal-TF candle k
(high[R+1] > ta.highest(high, L)[R+2] and > ta.highest(high, R)[1]) and handed to every chart candle inside candle k.
Compares the twin's trades with engine.run on the same chart timeframe."""
import sys, math, numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fractal')
import engine as EN
NA = float('nan')


def ta_highest(h, n):
    out = np.full(len(h), NA)
    for k in range(n - 1, len(h)):
        out[k] = h[k - n + 1:k + 1].max()
    return out


def f_piv_series(Hf, Tf, lft, rgt):
    """[ph, pt] of f_piv on each fractal candle k (Pine series semantics: x[m] is na before the start)"""
    lh_s = ta_highest(Hf, lft); rh_s = ta_highest(Hf, rgt); n = len(Hf)
    ph = np.full(n, NA); pt = [None] * n
    for k in range(n):
        lh = lh_s[k - rgt - 2] if k - rgt - 2 >= 0 else NA
        rh = rh_s[k - 1] if k - 1 >= 0 else NA
        p = Hf[k - rgt - 1] if k - rgt - 1 >= 0 else NA
        ok = not math.isnan(lh) and not math.isnan(rh) and not math.isnan(p) and p > lh and p > rh
        if ok:
            ph[k] = p; pt[k] = int(Tf[k - rgt - 1])
    return ph, pt


class Strat:
    def __init__(s, sid, off, sl, tp, be, sv, cost):
        s.id = sid; s.off = off; s.sl = sl; s.tp = tp; s.be = be; s.sv = sv; s.cost = cost
        s.lvlOn = False; s.lvlH = NA; s.E = NA; s.lvlT = None
        s.pos = False; s.F = NA; s.SLp = NA; s.TPp = NA; s.BEl = NA; s.SVl = NA; s.beOn = False; s.svOn = False
        s.eBar = None; s.trades = []

    def openAt(s, px, gap, bar):
        s.pos = True; s.F = px
        s.SLp = px * (1.0 - s.sl / 100.0); s.TPp = px * (1.0 + s.tp / 100.0)
        s.BEl = px * (1.0 + s.be / 100.0); s.SVl = px * (1.0 - s.sv / 100.0)
        s.beOn = False; s.svOn = False; s.eBar = bar

    def closeAt(s, px, rsn, bar):
        s.trades.append((s.eBar, s.F, bar, px, rsn)); s.pos = False

    def doBE(s):
        s.beOn = True; s.SLp = s.F

    def doSV(s):
        s.svOn = True; s.TPp = s.F

    def useLvl(s):
        s.lvlOn = False

    def up(s, x, y, bar):
        for _ in range(8):
            best = NA; ev = 0
            if s.pos:
                if x < s.TPp and s.TPp <= y:
                    best = s.TPp; ev = 1
                if s.be > 0 and not s.beOn and not s.svOn and x < s.BEl and s.BEl <= y and (math.isnan(best) or s.BEl < best):
                    best = s.BEl; ev = 2
            if s.lvlOn and x < s.E and s.E <= y and (math.isnan(best) or s.E < best):
                best = s.E; ev = 3
            if ev == 0:
                break
            if ev == 1:
                s.closeAt(s.TPp, 4 if s.svOn else 1, bar)
            elif ev == 2:
                s.doBE()
            else:
                if not s.pos:
                    s.openAt(s.E, False, bar)
                s.useLvl()

    def dn(s, x, y, bar):
        for _ in range(8):
            best = NA; ev = 0
            if s.pos:
                if y <= s.SLp and s.SLp < x:
                    best = s.SLp; ev = 1
                if s.sv > 0 and not s.svOn and not s.beOn and y <= s.SVl and s.SVl < x and (math.isnan(best) or s.SVl > best):
                    best = s.SVl; ev = 2
            if ev == 0:
                break
            if ev == 1:
                s.closeAt(s.SLp, 3 if s.beOn else 2, bar)
            else:
                s.doSV()

    def seg(s, x, y, bar):
        if y > x:
            s.up(x, y, bar)
        elif y < x:
            s.dn(x, y, bar)

    def onBar(s, ph, pt, pc, o, h, l, c, bar):
        lvlNew = False
        if not math.isnan(ph) and pt is not None and (s.lvlT is None or pt != s.lvlT):
            s.lvlT = pt; s.lvlOn = True; s.lvlH = ph; s.E = ph * (1.0 + s.off / 100.0); lvlNew = True
        if s.pos:
            if o >= s.TPp:
                s.closeAt(o, 4 if s.svOn else 1, bar)
            elif o <= s.SLp:
                s.closeAt(o, 3 if s.beOn else 2, bar)
            elif s.be > 0 and not s.beOn and not s.svOn and o >= s.BEl:
                s.doBE()
            elif s.sv > 0 and not s.svOn and not s.beOn and o <= s.SVl:
                s.doSV()
        if s.lvlOn and not lvlNew and not math.isnan(pc) and pc < s.E and o >= s.E:
            if not s.pos:
                s.openAt(o, True, bar)
            s.useLvl()
        hf = (h - o) < (o - l)
        a = h if hf else l; b = l if hf else h
        s.seg(o, a, bar); s.seg(a, b, bar); s.seg(b, c, bar)


def twin(B, ctf, ftf, r, l, off, sl, tp, be, sv):
    t, O, H, L, C = EN.chart(B, ctf)
    kk = np.searchsorted(B[ftf + '_t'], t, side='right') - 1
    ph, pt = f_piv_series(B[ftf + '_H'], B[ftf + '_t'], l, r)
    s = Strat(0, off, sl, tp, be, sv, 0.23)
    for i in range(len(O)):
        s.onBar(ph[kk[i]], pt[kk[i]], C[i - 1] if i > 0 else NA, O[i], H[i], L[i], C[i], i)
    return s.trades


if __name__ == '__main__':
    from run9 import T9
    ctf = sys.argv[1] if len(sys.argv) > 1 else 'M5'
    extra = [tuple([a.split(',')[0]] + [int(a.split(',')[1]), int(a.split(',')[2])] + [float(x) for x in a.split(',')[3:]]) for a in sys.argv[2:]]
    B = EN.load(); tot = 0; bad = 0
    for k, p in enumerate(T9 + extra, 1):
        if EN.TF_SEC[p[0]] < EN.TF_SEC[ctf]: continue
        tw = twin(B, ctf, *p); ref = EN.run(B, ctf, *p)
        same = len(tw) == len(ref) and all(a[0] == int(b[0]) and a[1] == b[1] and a[2] == int(b[2]) and a[3] == b[3] and a[4] == int(b[4]) for a, b in zip(tw, ref))
        tot += len(ref); bad += 0 if same else 1
        print('S%-2d %-3s twin %4d engine %4d %s' % (k, p[0], len(tw), len(ref), 'IDENTICAL' if same else 'DIFFERENT'))
    print('chart %s: %d strategies, %d trades, %s' % (ctf, k, tot, 'ALL IDENTICAL' if bad == 0 else '%d DIFFERENT' % bad))
