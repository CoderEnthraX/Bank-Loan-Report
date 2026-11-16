"""The Auction Retest STRATEGY on TradingView (build/strategy_template.pine, the user's defaults) executed on the engine's per-bar events
(mcej2/ref_gse.py), bar by bar:
  TradingView's broker emulator: orders placed at a bar's close act from the next bar; intrabar path O-H-L-C if the high is closer to the
  open than the low, else O-L-H-C; a limit fills on touch (a gap past it: at the open); a stop triggers when crossed (a gap: at the open);
  exits attached to an entry are active from its fill; strategy.close_all at a close fills at the next open.
  The strategy at each bar close (Pine sections 1-5): book a closed trade; follow the engine (no-fill / cancel / missed fill / exits with
  the targets after the engine's fill / close at the engine's exit unless earn-back and a target win); force-close time, Saturday start,
  news start: close; a working entry is cancelled at those and inside the news block; take the engine's new setup unless busy / news
  block / flat time. Prices on the tick grid like f_entryPx / f_stopPx / f_tgtPx (targets pushed by the round-trip costs with earn-back).
Default settings only (no partials, no stop moves, no Crooks TP1 rule, no streak stops, no monthly lock, no hard cap)."""
import math, datetime as dt


def floorT(x, mt): return round(math.floor(x / mt + 1e-6) * mt, 10)
def ceilT(x, mt): return round(math.ceil(x / mt - 1e-6) * mt, 10)
def path(o, h, l, c): return [o, h, l, c] if abs(h - o) < abs(o - l) else [o, l, h, c]
def entry_px(d, lim, mt): return floorT(lim + mt * 0.001, mt) if d > 0 else ceilT(lim - mt * 0.001, mt)
def stop_px(d, stp, mt): return floorT(stp + mt * 0.001, mt) if d > 0 else ceilT(stp - mt * 0.001, mt)
def tgt_px(d, lvl, cpx, mt): return ceilT(lvl + cpx - mt * 0.001, mt) if d > 0 else floorT(lvl - cpx + mt * 0.001, mt)


def _nth_sunday(y, m, n):
    d = dt.date(y, m, 1); return 1 + (6 - d.weekday()) % 7 + 7 * (n - 1)


def ny_summer(u):
    """New York daylight time at UTC instant u"""
    return dt.datetime(u.year, 3, _nth_sunday(u.year, 3, 2), 7) <= u < dt.datetime(u.year, 11, _nth_sunday(u.year, 11, 1), 6)


def time_flags(T, fcOn=True, fcHM=(23, 55), wkOn=True, newsOn=False, news=(17 * 60 + 45, 18 * 60 + 15), newsPre=60, dnAuto=True):
    """per bar (T = IST bar-open times): fcNow, wkndStart, newsBlock, newsStart, as the Pine globals compute them"""
    n = len(T); fc = [False] * n; wk = [False] * n; blk = [False] * n; st = [False] * n; inN = [False] * n
    fcM = fcHM[0] * 60 + fcHM[1]
    for i in range(n):
        t = T[i]; cur = t.hour * 60 + t.minute
        if i > 0:
            p = T[i - 1]; prv = p.hour * 60 + p.minute
            fc[i] = fcOn and ((prv < fcM <= cur) if cur >= prv else (fcM > prv or fcM <= cur))
            wk[i] = wkOn and t.weekday() == 5 and p.weekday() != 5
        if newsOn:
            sh = 0 if (not dnAuto or ny_summer(t - dt.timedelta(minutes=330))) else 60      # the window keeps its New York time
            s = (news[0] + sh) % 1440; e = (news[1] + sh) % 1440
            inN[i] = (s <= cur < e) if s < e else (cur >= s or cur < e)
            diff = (s - cur + 1440) % 1440
            blk[i] = inN[i] or (newsPre > 0 and 0 < diff <= newsPre)
            st[i] = inN[i] and not (inN[i - 1] if i > 0 else False)
    return fc, wk, blk, st


def run(O, H, L, C, T, ev, mt, earnBack=True, costPx=0.23, flags=None, market=False):
    fc, wk, blk, nst = flags if flags is not None else time_flags(T)
    n = len(O)
    exState = 0; pos = 0; entry = None; stopPx = tgtPx = None; closePend = None; exArm = None; ex = None
    trades = []; cur = None
    cnt = dict(noFill=0, missed=0, skipBusy=0, skipNews=0, skipFlat=0, taken=0, cancelEng=0, cancelFlat=0)
    for i in range(n):
        o, h, l, c = O[i], H[i], L[i], C[i]
        pts = path(o, h, l, c)
        closedNow = False; filledNow = False; k0 = 0; fpx = None
        # ---- the broker emulator, bar i, with the orders placed at the close of bar i-1 ----
        if closePend is not None and pos != 0:                       # close_all from the previous close: at this open
            cur.update(exit=i, xpx=o, how=closePend); pos = 0; closedNow = True; stopPx = tgtPx = None
        closePend = None
        if entry is not None and pos == 0:
            d, lp = entry
            if lp is None: fpx = o; k0 = 0                              # market entry (Entry Price: Market): the next open
            elif (d > 0 and o <= lp) or (d < 0 and o >= lp): fpx = o; k0 = 0
            else:
                for k in range(1, 4):
                    b = pts[k]
                    if (d > 0 and b <= lp) or (d < 0 and b >= lp): fpx = lp; k0 = k - 1; break
            if fpx is not None:
                pos = d; filledNow = True; entry = None
                cur = dict(ex, fill=i, fpx=fpx, exit=None, xpx=None, how=None); trades.append(cur)
        if pos != 0:
            d = pos; hit = None
            seq = [fpx] + pts[k0 + 1:] if filledNow else pts
            if filledNow:
                if stopPx is not None and ((d > 0 and fpx <= stopPx) or (d < 0 and fpx >= stopPx)): hit = ('stop', fpx)
            else:
                if stopPx is not None and ((d > 0 and o <= stopPx) or (d < 0 and o >= stopPx)): hit = ('stop', o)
                elif tgtPx is not None and ((d > 0 and o >= tgtPx) or (d < 0 and o <= tgtPx)): hit = ('target', o)
            if hit is None:
                for k in range(1, len(seq)):
                    a, b = seq[k - 1], seq[k]; lo, hi = min(a, b), max(a, b); cands = []
                    if stopPx is not None and lo <= stopPx <= hi and ((d > 0 and b < a) or (d < 0 and b > a) or a == stopPx):
                        cands.append((abs(stopPx - a), 'stop', stopPx))
                    if tgtPx is not None and lo <= tgtPx <= hi and ((d > 0 and b > a) or (d < 0 and b < a) or a == tgtPx):
                        cands.append((abs(tgtPx - a), 'target', tgtPx))
                    if cands: cands.sort(); hit = (cands[0][1], cands[0][2]); break
            if hit is not None:
                cur.update(exit=i, xpx=hit[1], how=hit[0]); pos = 0; closedNow = True; stopPx = tgtPx = None
        # ---- the strategy at the close of bar i ----
        e = ev[i]
        exNewPos = exState == 1 and pos != 0
        if exNewPos: exState = 2
        exClosed = (exState == 1 and pos == 0 and closedNow) or (exState == 2 and pos == 0)
        if exClosed:
            exState = 0; exArm = None; entry = None; stopPx = tgtPx = None
        exMine = exArm is not None and e['armBar'] == exArm
        if exNewPos and not e['fill']:
            closePend = 'engine: no fill'; cnt['noFill'] += 1
        if exState == 1 and e['cancel']:
            entry = None; stopPx = None; exState = 0; exArm = None; cnt['cancelEng'] += 1
        if e['fill'] and exState == 1 and pos == 0 and not exClosed:
            entry = None; stopPx = None; exState = 0; exArm = None; cnt['missed'] += 1
        if exState == 2 and exMine and e['move']:
            ex['stp'] = e['stp']                                      # the engine moved its stop (TP1 / TP2 / TP3 stop moves)
        if exState == 2 and exMine and (e['fill'] or e['move']):
            stopPx = stop_px(pos, ex['stp'], mt); tgtPx = tgt_px(pos, ex['tF'], costPx if earnBack else 0.0, mt)
        if e['exit'] and exState == 2 and exMine and (not earnBack or not e['win']):
            closePend = 'engine exit'
        flat = fc[i] or wk[i] or nst[i]
        if flat and pos != 0:
            closePend = 'force close' if fc[i] else 'weekend' if wk[i] else 'news'
        if exState == 1 and (flat or blk[i]):
            entry = None; stopPx = None; exState = 0; exArm = None; cnt['cancelFlat'] += 1
        a = e['arm']
        if a is not None:
            if exState != 0 or pos != 0: cnt['skipBusy'] += 1
            elif blk[i]: cnt['skipNews'] += 1
            elif flat: cnt['skipFlat'] += 1
            else:
                d = a['dir']
                ex = dict(dir=d, arm=i, lim=a['lim'], stp=a['stp'], tF=a['tF'], risk=a['risk'])
                entry = (d, None if market else entry_px(d, a['lim'], mt)); stopPx = stop_px(d, a['stp'], mt); tgtPx = None
                exState = 1; exArm = i; cnt['taken'] += 1
    return trades, cnt
