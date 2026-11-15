"""(sync_why: emsim3 with tags) TradingView broker emulation of the STRATEGY build (pine3/build_fbg3.py ORDERS): every candle the emulator fills the orders placed at
the previous close (market at the open; buy stop at the open on a gap, else where the path crosses it; the attached SL / TP from the fill
on; path open -> nearer of high / low -> other -> close), then the model (the Pine twin) runs the candle, then the next orders are placed
exactly as the Pine order layer does. Compares TradingView's trades with the model's. Usage: emsim3.py CHART S1 S2 ... (1-based)"""
import sys, math, numpy as np, datetime as dt
from zoneinfo import ZoneInfo
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fractal')
import engine as EN, pine_twin2 as TW
from pine_twin import f_piv_series
from final11 import ALL12
NA = float('nan')
B = EN.load()
for _k in ('t', 'O', 'H', 'L', 'C'): B['M1_' + _k] = B[_k]
COMM = 0.115   # Properties commission per contract per order


def f_next(s, F):
    p = s.P; sd = F * s.sl / 100.0
    r0, rec0, baseC = s.f_raw(sd); r = r0
    if p.capOn and r > p.hardCap:
        r = NA if p.capAction == 'stop' else (min(baseC, p.hardCap) if p.capAction == 'reset' else p.hardCap)
    if not math.isnan(r) and s.eq > 0: r = min(r, s.eq * p.levIn * (sd + p.costIn) / F)
    return r


def f_units(s, F):
    r = f_next(s, F)
    return NA if math.isnan(r) else r / (F * s.sl / 100.0 + s.P.costIn)


RS = {1: 'TP', 2: 'SL', 3: 'BE', 4: 'SALV', 5: 'TRAIL', 6: 'TIME', 7: 'WKND'}


def run_tag(ctf, k, p):
    prm = ALL12[k]; ftf, r, l, off, sl, tp, be, sv = prm
    t, O, H, L, C = EN.chart(B, ctf); utc = TW.chart_utc(B, ctf); csec = EN.TF_SEC[ctf]; fsec = EN.TF_SEC[ftf]
    kk = np.searchsorted(B[ftf + '_t'], t, side='right') - 1
    ph, pt = f_piv_series(B[ftf + '_H'], B[ftf + '_t'], l, r)
    nK = len(ph)
    ok, wk, dno = TW.globals_twin(B, ctf, p)
    TZ = ZoneInfo(p.tz); NYZ = ZoneInfo('America/New_York')
    if p.trnOn:
        kT = np.searchsorted(B[p.trnTf + '_t'], t, side='right') - 1; Ct = B[p.trnTf + '_C']; eT = TW.ema_seed(Ct, p.trnLen)
    s = TW.Strat(p, k + 1, off, sl, tp, be, sv)
    tv = None; order = None; tvTrades = []; units_at = {}
    for i in range(len(O)):
        o, h, lo, c = O[i], H[i], L[i], C[i]
        hf = (h - o) < (o - lo); path = [o, h, lo, c] if hf else [o, lo, h, c]
        # ---- TradingView fills bar i with the orders placed at bar i-1's close
        k0 = 0; fillPx = None
        if order is not None:
            if order[0] == 'close' and tv is not None:
                tvTrades.append((tv['bar'], tv['F'], i, o, tv['q'], 'close', tv['how'], order[1])); tv = None
            elif order[0] == 'mkt' and tv is None:
                tv = dict(bar=i, F=o, q=order[1], sl=order[2], tp=order[3], how='catch-up', why=order[4]); fillPx = o; k0 = 0
            elif order[0] == 'exit' and tv is not None:
                tv['sl'], tv['tp'], tv['cl'], tv['cp'] = order[1], order[2], order[3], order[4]
            elif order[0] == 'stop' and tv is None:
                q, E, dsl, dtp = order[1:]
                if o >= E:
                    tv = dict(bar=i, F=o, q=q, sl=o - dsl, tp=o + dtp, how='stop'); fillPx = o; k0 = 0
                else:
                    for g in range(1, 4):
                        x, y = path[g - 1], path[g]
                        if y > x and x < E <= y:
                            tv = dict(bar=i, F=E, q=q, sl=E - dsl, tp=E + dtp, how='stop'); fillPx = E; k0 = g; break
        if tv is not None:
            done = False
            if fillPx is None or k0 == 0:            # in the trade at the open (earlier fill, or a fill at this open)
                if o <= tv['sl']: tvTrades.append((tv['bar'], tv['F'], i, o, tv['q'], 'sl', tv['how'], tv.get('cl', 'SL'))); tv = None; done = True
                elif o >= tv['tp']: tvTrades.append((tv['bar'], tv['F'], i, o, tv['q'], 'tp', tv['how'], tv.get('cp', 'TP'))); tv = None; done = True
            if not done:
                segs = [(path[g - 1], path[g]) for g in range(1, 4)]
                if fillPx is not None and k0 >= 1:
                    segs = [(fillPx, path[k0])] + [(path[g - 1], path[g]) for g in range(k0 + 1, 4)]
                for x, y in segs:
                    if y > x and x < tv['tp'] <= y: tvTrades.append((tv['bar'], tv['F'], i, tv['tp'], tv['q'], 'tp', tv['how'], tv.get('cp', 'TP'))); tv = None; break
                    if y < x and y <= tv['sl'] < x: tvTrades.append((tv['bar'], tv['F'], i, tv['sl'], tv['q'], 'sl', tv['how'], tv.get('cl', 'SL'))); tv = None; break
        # ---- the model runs bar i
        npos = len(s.trades)
        s.onBar(ph[kk[i]], pt[kk[i]], int(kk[i]), C[i - 1] if i > 0 else NA, bool(ok[i]), bool(wk[i]), int(dno[i]), o, h, lo, c, i, int(utc[i]) * 1000)
        # ---- the orders for bar i+1 (the Pine order layer)
        inTv = tv is not None; order = None
        tN = (int(utc[i]) + csec) * 1000
        dN = dt.datetime.fromtimestamp(tN // 1000, dt.timezone.utc); lzN = dN.astimezone(TZ); nyN = dN.astimezone(NYZ)
        wkN = p.wkOn and nyN.weekday() == 4 and nyN.hour >= p.wkH
        mN = lzN.hour * 60 + lzN.minute; a0, a1 = p.sess
        inSesN = (a0 <= mN < a1) if a0 < a1 else ((mN >= a0 or mN < a1) if a0 > a1 else True)
        trendN = True
        if p.trnOn:
            kt = int(kT[i]); lastT = t[i] + csec >= B[p.trnTf + '_t'][kt] + EN.TF_SEC[p.trnTf]
            trendN = (Ct[kt] > eT[kt]) if lastT else (kt >= 1 and Ct[kt - 1] > eT[kt - 1])
        okN = ((not p.dayOn) or p.days[lzN.weekday()]) and ((not p.hoursOn) or inSesN) and trendN and not wkN
        dayN = lzN.year * 10000 + lzN.month * 100 + lzN.day
        if s.pos and inTv:
            if (p.tExitH > 0 and tN >= s.eTime + round(p.tExitH * 3600000)) or wkN: order = ('close', 'WKND' if wkN else 'TIME')
            else: order = ('exit', s.SLp, s.TPp, 'TRAIL' if s.trOn else ('BE' if s.beOn else 'SL'), 'SALV' if s.svOn else 'TP')
        elif s.pos:
            dueX = (p.tExitH > 0 and tN >= s.eTime + round(p.tExitH * 3600000)) or wkN
            q = s.units if s.cnt else f_units(s, s.F)
            if not dueX and not math.isnan(q) and q > 0: order = ('mkt', q, s.SLp, s.TPp, 'entry')
        elif inTv:
            lastX = s.trades[-1] if s.trades else None
            order = ('close', (RS[lastX[4]] if lastX is not None and lastX[2] == i else 'none'))
        else:
            kc = int(kk[i]); tc = B[ftf + '_t'][kc] + fsec; last = t[i] + csec >= tc
            q0 = ph[kc + 1] if kc + 1 < nK else NA; u0 = pt[kc + 1] if kc + 1 < nK else None
            newL = last and not math.isnan(q0) and u0 is not None and (s.lvlT is None or u0 != s.lvlT)
            nOn = newL or s.lvlOn; nE = q0 * (1.0 + off / 100.0) if newL else s.E
            hbN = kc + (1 if last else 0)
            if nOn and not newL and p.expN > 0 and s.kAct is not None and hbN - s.kAct >= p.expN: nOn = False
            cntOk = p.maxDay <= 0 or s.dPrev is None or dayN != s.dPrev or s.dCnt < p.maxDay
            q = NA
            if (not p.entClose) and nOn and not math.isnan(nE) and c < nE and okN and cntOk and not s.stopped:
                q = f_units(s, nE)
            if not math.isnan(q) and q > 0: order = ('stop', q, nE, nE * sl / 100.0, nE * tp / 100.0)
    return s.trades, tvTrades, (t, utc)
    model = [(a[0], a[1], a[2], a[3]) for a in s.trades]
    mUsd = sum(s.risks[j] / (a[1] * sl / 100.0 + p.costIn) * (a[3] - a[1] - p.costIn) for j, a in enumerate(s.trades))   # risks: one per opened trade, in order
    tvUsd = sum(q * (x - f) - 2 * COMM * q for (_, f, _, x, q, _) in tvTrades)
    ms = set((a[0], round(a[1], 6), a[2], round(a[3], 6)) for a in model); ts = set((a[0], round(a[1], 6), a[2], round(a[3], 6)) for a in tvTrades)
    return len(model), len(tvTrades), len(ms & ts), mUsd, tvUsd, s.net




if __name__ == '__main__':
    import collections
    k = int(sys.argv[1]) - 1
    for ctf in sys.argv[2:]:
        mt, tt, _ = run_tag(ctf, k, TW.P())
        ms = set((a[0], round(a[1], 6), a[2], round(a[3], 6)) for a in mt)
        same = sum(1 for a in tt if (a[0], round(a[1], 6), a[2], round(a[3], 6)) in ms)
        mr = collections.Counter(RS[a[4]] for a in mt)
        lab = collections.Counter((a[6] == 'catch-up' and 'entry next open / ' or '') + (a[7] + ' next open' if a[5] == 'close' else a[7]) for a in tt)
        print('chart %-3s S%d: model %d trades %s | TradingView %d trades, identical %d (%.1f%%)' % (ctf, k + 1, len(mt), dict(mr), len(tt), same, 100.0 * same / max(1, len(mt))))
        print('    TradingView exit labels:', dict(sorted(lab.items(), key=lambda x: -x[1])))
        nx = [a for a in tt if a[5] == 'close' and a[7] not in ('TIME', 'WKND')]
        print('    next-open exits %d = %.1f%% of TradingView trades' % (len(nx), 100.0 * len(nx) / max(1, len(tt))))
