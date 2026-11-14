"""Python twin of the Pine indicator v2 (pine2/build_fbg2.py): the same per-candle code and money code, method by method.
request.security is emulated (fractal: f_piv on every TF candle k handed to the chart candles inside k; trend: close[1] and EMA[1] of the
trend TF); time-zone values with zoneinfo from each chart bar's UTC open time, as Pine's dayofweek / time(tf, session, tz) / hour do."""
import sys, math, datetime as dt, numpy as np
from zoneinfo import ZoneInfo
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fractal')
import engine as EN
from pine_twin import f_piv_series
NA = float('nan')
MODES = ['Off', 'Recover all losses on the next trade', 'Recover losses over N trades', 'Recover a % of losses per trade', 'Martingale (multiply after each loss)',
         'Exact recovery at final TP', 'Step-up (+$ per loss in a row)', 'Fibonacci', "D'Alembert", 'Rule C: carry the losses', 'Rule C split', 'Labouchere',
         'Grand Martingale', 'Paroli', "Reverse D'Alembert", 'Delayed recovery', '% of equity', "Oscar's Grind", 'Crooks A', 'Crooks B', 'Crooks C', 'Crooks D',
         'Crooks E', 'Crooks F', 'Crooks G', 'Crooks H', 'Crooks I', 'Crooks J']
(L_OFF, L_ALL, L_SPLIT, L_PART, L_MART, L_EXACT, L_STEP, L_FIB, L_DALE, L_C, L_CS, L_LAB, L_GMART, L_PAR, L_RDALE, L_DELAY, L_EQPCT, L_OSC,
 L_CRA, L_CRB, L_CRC, L_CRD, L_CRE, L_CRF, L_CRG, L_CRH, L_CRI, L_CRJ) = range(28)
LAD = {'Off': None, 'Low': (0.8, 0.10, 2.0, 0.25), 'Medium': (0.7, 0.15, 3.0, 0.30), 'High': (0.6, 0.20, 5.0, 0.35), 'Extra high': (0.5, 0.25, 8.0, 0.40), 'Max': (0.4, 0.30, 12.0, 0.50)}


class P:   # the inputs (defaults = the Pine defaults)
    costIn = 0.23; statsFrom = 0
    entClose = False; expN = 0; maxDay = 0; trA = 0.0; trD = 0.0; tExitH = 0.0; wkOn = False; wkH = 16
    trnOn = False; trnTf = 'H4'; trnLen = 50
    tz = 'Asia/Kolkata'; dayOn = False; days = (True, True, True, True, True, False, False); hoursOn = False; sess = (6 * 60, 23 * 60)
    mmOn = True; startB = 10000.0; baseR = 50.0; lotSz = 100.0; lotStep = 0.01; levIn = 100.0; capOn = True; hardCap = 500.0; capAction = 'clamp'
    recMode = L_CRF; lad = 'Medium'; ladT = 1000.0; recN = 3; recPct = 50.0; recMult = 2.0; recStep = 25.0; cSplit = 3; parN = 3; delayN = 2; eqPct = 1.0
    crkCn = 1; crkPr = 'off'; crkPrN = 2; crkPrPct = 50.0; crkPrM = 2; crkELot = 0.01; crkFK = 3.0; crkGX = 10.0; crkHPct = 1.0; crkJX = 20.0

    def __init__(self, **kw):
        for k, v in kw.items(): setattr(self, k, v)
        m = self.recMode
        self.crkFam = m in (L_CRC, L_CRE, L_CRF, L_CRG, L_CRH, L_CRI, L_CRJ)
        self.ladFam = m in (L_CRF, L_CRG, L_CRH, L_CRI, L_CRJ)
        self.prOn = self.crkFam and self.crkPr != 'off'
        self.ladOff = self.lad == 'Off'
        self.ladLam, self.ladPhi, self.ladBmx, self.ladGam = LAD[self.lad] if not self.ladOff else LAD['Low']
        self.eUnits = math.ceil(max(self.crkELot, self.lotStep) / self.lotStep - 1e-9) * self.lotStep * self.lotSz


class Strat:
    def __init__(s, P_, sid, off, sl, tp, be, sv):
        s.P = P_; s.id = sid; s.off = off; s.sl = sl; s.tp = tp; s.be = be; s.sv = sv
        s.lab = [1.0, 2.0, 3.0]
        s.lvlOn = False; s.lvlH = NA; s.E = NA; s.lvlT = None; s.kAct = None; s.armed = False
        s.pos = False; s.F = NA; s.SLp = NA; s.TPp = NA; s.BEl = NA; s.SVl = NA; s.beOn = False; s.svOn = False; s.trOn = False; s.hi = NA
        s.eTime = None; s.cnt = False; s.dCnt = 0; s.dPrev = None; s.stopped = False
        s.eq = P_.startB; s.pkEq = P_.startB; s.ddU = 0.0; s.ddP = 0.0; s.net = 0.0; s.peakNet = 0.0
        s.recPool = 0.0; s.recLosses = 0; s.dUnits = 1; s.carried = 0.0; s.parWins = 0; s.rdUnits = 1; s.oscU = 1; s.oscP = 0.0
        s.crL = 0.0; s.crN = 0; s.crW = False; s.crP = P_.crkCn; s.crF = 0; s.crWait = False; s.crWW = 0; s.crNeedL = False; s.crRecT = False
        s.risk = NA; s.units = NA
        s.trades = []; s.risks = []

    # ---- money
    def f_lad(s):
        p = s.P
        on = (not p.ladOff) and p.ladFam and s.peakNet >= p.ladT
        C = max(0.0, s.net - p.ladLam * s.peakNet) if on else 0.0
        return on, on and s.net <= 0, (p.baseR + min((p.ladBmx - 1.0) * p.baseR, p.ladPhi * C)) if on else p.baseR, C

    def f_crk(s, B, rec, rmin, pf, xr):
        p = s.P
        x = max(B, s.crL / s.crP * pf / xr) if rec else B
        if rec:
            if p.recMode in (L_CRF, L_CRI): x = min(x, p.crkFK * B)
            elif p.recMode == L_CRH: x = min(x, max(B, s.eq * p.crkHPct / 100.0))
            elif p.recMode == L_CRJ: x = max(B, x * max(0.0, 1.0 - (s.peakNet - s.net) / (p.crkJX * B)))
        elif s.crL > 0 and p.recMode in (L_CRE, L_CRI):
            x = min(B, rmin)
        return x

    def f_raw(s, sd):
        p = s.P; m = p.recMode; base = p.baseR
        xr = s.tp / s.sl; rmin = p.eUnits * (sd + p.costIn)
        add = s.recPool if m == L_ALL else s.recPool / p.recN if m == L_SPLIT else s.recPool * p.recPct / 100.0 if m == L_PART else s.recPool / xr if m == L_EXACT else p.recStep * s.recLosses if m == L_STEP else 0.0
        fa = 1.0; fb = 1.0
        if s.recLosses >= 2:
            for _ in range(2, min(s.recLosses, 200) + 1):
                t2 = fa + fb; fa = fb; fb = t2
        stepBase = 0.0
        if s.net >= 1000:
            kk = int(math.floor((s.net - 1000.0) / 500.0)); stepBase = (1000.0 + 500.0 * kk) / (8.0 + kk)
        elif s.net >= 500: stepBase = 500.0 / 5.0
        elif s.net >= 200: stepBase = 200.0 / 3.0
        baseC = max(base, min(stepBase, p.hardCap) if p.capOn else stepBase) if m == L_CS else base
        labU = s.lab[0] + s.lab[-1] if len(s.lab) > 1 else s.lab[0]
        oscNd = int(max(1, math.ceil((base - s.oscP) / (base * xr) - 1e-9)))
        rec = ((m in (L_CRA, L_CRB)) and s.crN >= 2 and s.crN % 2 == 0) or (p.crkFam and s.crW and s.crL > 0) or (m == L_CRD and s.crN >= 2 and (s.crN - 2) % 3 == 0)
        if rec and p.prOn and p.crkPr == 'wait' and (s.crWait or s.crNeedL): rec = False
        pf = p.crkPrPct / 100.0 if (p.prOn and p.crkPr == 'pct') else 1.0
        if m == L_LAB: r = base * labU
        elif m == L_GMART: r = base * math.pow(p.recMult, min(s.recLosses, 200)) + base * s.recLosses
        elif m == L_PAR: r = base * math.pow(2.0, s.parWins)
        elif m == L_RDALE: r = base * s.rdUnits
        elif m == L_DELAY: r = base + s.recPool / p.recN if s.recLosses >= p.delayN else base
        elif m == L_EQPCT: r = s.eq * p.eqPct / 100.0
        elif m == L_OSC: r = base * min(s.oscU, oscNd)
        elif m == L_MART: r = base * math.pow(p.recMult, min(s.recLosses, 200))
        elif m == L_FIB: r = base * (1.0 if s.recLosses == 0 else fb)
        elif m == L_DALE: r = base * s.dUnits
        elif m in (L_C, L_CS): r = max(baseC, s.carried / p.cSplit)
        elif m == L_CRA: r = max(base, s.crL / xr) if rec else base
        elif m == L_CRB: r = max(base, s.crL / p.cSplit / xr) if rec else base
        elif m == L_CRC: r = max(base, s.crL / s.crP * pf / xr) if rec else base
        elif m == L_CRD: r = max(base, s.crL / xr) if rec else base
        else: r = base + add
        if p.crkFam:
            r = s.f_crk(base, rec, rmin, pf, xr)
            lOn, lGuard, lB, lC = s.f_lad()
            if lOn:
                r = min(s.f_crk(lB, rec, rmin, pf, xr), r + p.ladGam * lC)
                if lGuard: r = min(base, rmin)
        return r, rec, baseC

    def mmOpen(s, F):
        p = s.P; sd = F * s.sl / 100.0
        r0, rec0, baseC = s.f_raw(sd); r = r0; take = True; s.crRecT = rec0
        if p.capOn and r > p.hardCap:
            if p.capAction == 'stop':
                s.stopped = True; take = False
            elif p.capAction == 'reset':
                s.recPool = 0.0; s.recLosses = 0; s.dUnits = 1; s.carried = 0.0; s.lab = [1.0, 2.0, 3.0]; s.parWins = 0; s.rdUnits = 1; s.oscU = 1; s.oscP = 0.0
                s.crL = 0.0; s.crN = 0; s.crRecT = False; s.crW = False; s.crP = p.crkCn; s.crF = 0; s.crWait = False; s.crWW = 0; s.crNeedL = False
                r = min(baseC, p.hardCap)
            else:
                r = p.hardCap
        if take and s.eq > 0: r = min(r, s.eq * p.levIn * (sd + p.costIn) / F)
        s.risk = r if take else NA; s.units = r / (sd + p.costIn) if take else NA
        return take

    def mmBook(s, pnl):
        p = s.P
        s.eq += pnl; s.net += pnl; s.pkEq = max(s.pkEq, s.eq); s.ddU = max(s.ddU, s.pkEq - s.eq); s.ddP = max(s.ddP, (s.pkEq - s.eq) / s.pkEq)
        s.peakNet = max(s.peakNet, s.net)
        if s.eq <= 0: s.stopped = True
        win = pnl > 0
        s.carried = max(0.0, s.carried - pnl)
        if win:
            s.recPool = max(0.0, s.recPool - pnl); s.recLosses = s.recLosses if s.recPool > 0 else 0
            s.dUnits = max(1, s.dUnits - 1); s.rdUnits += 1; s.parWins = 0 if s.parWins + 1 >= p.parN else s.parWins + 1
            if s.lab: s.lab.pop(0)
            if s.lab: s.lab.pop()
            if not s.lab: s.lab = [1.0, 2.0, 3.0]
        else:
            s.recPool += -pnl; s.recLosses += 1; s.dUnits += 1; s.rdUnits = max(1, s.rdUnits - 1); s.parWins = 0
            s.lab.append(s.lab[0] + s.lab[-1] if len(s.lab) > 1 else s.lab[0])
        s.oscP += pnl
        if s.oscP >= p.baseR: s.oscU = 1; s.oscP = 0.0
        elif win: s.oscU += 1
        lastPart = s.crP == 1
        s.crL = max(0.0, s.crL - pnl)
        if p.recMode == L_CRG:
            s.crL = min(s.crL, p.crkGX * s.f_lad()[2])
        if s.crL < 0.01 or (p.recMode in (L_CRA, L_CRD) and win and s.crRecT):
            s.crL = 0.0; s.crN = 0; s.crP = p.crkCn; s.crF = 0; s.crWait = False; s.crWW = 0; s.crNeedL = False
        else:
            s.crN += 1
            s.crP = p.crkCn if not win else (max(1, s.crP - 1) if s.crRecT else s.crP)
            if p.prOn:
                if s.crWait:
                    s.crWW = s.crWW + 1 if win else 0
                    if s.crWW >= p.crkPrM: s.crWait = False; s.crWW = 0; s.crNeedL = True
                elif s.crNeedL and not win: s.crNeedL = False
                if s.crRecT and win:
                    s.crF = 0
                    if p.crkPr == 'pct' and lastPart: s.crL = 0.0; s.crN = 0; s.crP = p.crkCn
                elif s.crRecT:
                    s.crF += 1
                    if s.crF >= p.crkPrN:
                        s.crF = 0
                        if p.crkPr in ('forget', 'pct'): s.crL = 0.0; s.crN = 0; s.crP = p.crkCn
                        elif p.crkPr == 'wait': s.crWait = True; s.crWW = 0; s.crNeedL = False
        s.crW = win

    # ---- trades
    def openAt(s, px, gap, bar, T):
        p = s.P; counted = T >= p.statsFrom
        take = s.mmOpen(px) if (p.mmOn and counted) else True
        if take:
            s.pos = True; s.F = px; s.SLp = px * (1.0 - s.sl / 100.0); s.TPp = px * (1.0 + s.tp / 100.0)
            s.BEl = px * (1.0 + s.be / 100.0); s.SVl = px * (1.0 - s.sv / 100.0); s.beOn = False; s.svOn = False; s.trOn = False; s.hi = px
            s.eTime = T; s.cnt = p.mmOn and counted; s.dCnt += 1; s.eBar = bar
            if s.cnt: s.risks.append(s.risk)
        return take

    def closeAt(s, px, rsn, bar):
        p = s.P; pnl = px - s.F - p.costIn
        if s.cnt: s.mmBook(s.units * pnl)
        s.trades.append((s.eBar, s.F, bar, px, rsn)); s.pos = False; s.cnt = False

    def doBE(s):
        s.beOn = True
        if s.F > s.SLp: s.SLp = s.F

    def doSV(s):
        s.svOn = True; s.TPp = s.F

    def trail(s):
        p = s.P
        if p.trD > 0 and s.hi >= s.F * (1.0 + p.trA / 100.0):
            tl = s.hi * (1.0 - p.trD / 100.0)
            if tl > s.SLp: s.SLp = tl; s.trOn = True

    def useLvl(s):
        s.lvlOn = False

    def canEnter(s, okb):
        p = s.P
        return okb and not s.pos and not s.stopped and (p.maxDay <= 0 or s.dCnt < p.maxDay)

    def up(s, x, y, okb, bar, T):
        p = s.P
        for _ in range(8):
            best = NA; ev = 0
            if s.pos:
                if x < s.TPp and s.TPp <= y: best = s.TPp; ev = 1
                if s.be > 0 and not s.beOn and not s.svOn and x < s.BEl and s.BEl <= y and (math.isnan(best) or s.BEl < best): best = s.BEl; ev = 2
            if (not p.entClose) and s.lvlOn and x < s.E and s.E <= y and (math.isnan(best) or s.E < best): best = s.E; ev = 3
            if ev == 0: break
            if ev == 1: s.closeAt(s.TPp, 4 if s.svOn else 1, bar)
            elif ev == 2: s.doBE()
            else:
                if s.canEnter(okb): s.openAt(s.E, False, bar, T)
                s.useLvl()
        if s.pos and y > s.hi: s.hi = y

    def dn(s, x, y, bar):
        if s.pos: s.trail()
        for _ in range(8):
            best = NA; ev = 0
            if s.pos:
                if y <= s.SLp and s.SLp < x: best = s.SLp; ev = 1
                if s.sv > 0 and not s.svOn and not s.beOn and y <= s.SVl and s.SVl < x and (math.isnan(best) or s.SVl > best): best = s.SVl; ev = 2
            if ev == 0: break
            if ev == 1: s.closeAt(s.SLp, 5 if s.trOn else (3 if s.beOn else 2), bar)
            else: s.doSV()

    def seg(s, x, y, okb, bar, T):
        if y > x: s.up(x, y, okb, bar, T)
        elif y < x: s.dn(x, y, bar)

    def onBar(s, ph, pt, hb, pc, okb, wk, dno, o, h, l, c, bar, T):
        p = s.P
        if s.dPrev is None or dno != s.dPrev: s.dCnt = 0; s.dPrev = dno
        lvlNew = False
        if not math.isnan(ph) and pt is not None and (s.lvlT is None or pt != s.lvlT):
            s.lvlT = pt; s.lvlOn = True; s.lvlH = ph; s.E = ph * (1.0 + s.off / 100.0); s.kAct = hb; s.armed = False; lvlNew = True
        if s.lvlOn and p.expN > 0 and s.kAct is not None and hb - s.kAct >= p.expN: s.useLvl()
        if s.pos:
            s.trail(); xr = 0
            if o >= s.TPp: xr = 4 if s.svOn else 1
            elif o <= s.SLp: xr = 5 if s.trOn else (3 if s.beOn else 2)
            elif p.tExitH > 0 and T >= s.eTime + round(p.tExitH * 3600000): xr = 6
            elif wk: xr = 7
            if xr > 0: s.closeAt(o, xr, bar)
            else:
                if s.be > 0 and not s.beOn and not s.svOn and o >= s.BEl: s.doBE()
                elif s.sv > 0 and not s.svOn and not s.beOn and o <= s.SVl: s.doSV()
                if o > s.hi: s.hi = o
        if (not p.entClose) and s.lvlOn and not lvlNew and not math.isnan(pc) and pc < s.E and o >= s.E:
            if s.canEnter(okb): s.openAt(o, True, bar, T)
            s.useLvl()
        hf = (h - o) < (o - l); a = h if hf else l; b = l if hf else h
        s.seg(o, a, okb, bar, T); s.seg(a, b, okb, bar, T); s.seg(b, c, okb, bar, T)
        if p.entClose and s.lvlOn:
            if s.armed and c >= s.E:
                if s.canEnter(okb): s.openAt(c, False, bar, T)
                s.useLvl()
            elif c < s.E:
                s.armed = True


def chart_utc(B, ctf):
    """UTC open time (seconds) of every chart bar"""
    if ctf == 'M1': return B['ut']
    i0 = B[ctf + '_i0']; return B[ctf + '_t'] - (B['t'][i0] - B['ut'][i0])


def ema_seed(x, n):
    a = 2.0 / (n + 1.0); e = np.empty(len(x)); e[0] = x[0]
    for k in range(1, len(x)): e[k] = a * x[k] + (1.0 - a) * e[k - 1]
    return e


def globals_twin(B, ctf, p):
    """per chart bar: okBar, wkNow, dayNo, as the Pine globals compute them (zoneinfo)"""
    tch = EN.chart(B, ctf)[0]; utc = chart_utc(B, ctf); n = len(utc)
    tz = ZoneInfo(p.tz); ny = ZoneInfo('America/New_York')
    ok = np.ones(n, bool); wk = np.zeros(n, bool); dno = np.zeros(n, np.int64)
    if p.trnOn:
        k = np.searchsorted(B[p.trnTf + '_t'], tch, side='right') - 1; Ct = B[p.trnTf + '_C']; e = ema_seed(Ct, p.trnLen)
    for i in range(n):
        d = dt.datetime.fromtimestamp(int(utc[i]), dt.timezone.utc)
        lz = d.astimezone(tz); lny = d.astimezone(ny)
        dayOk = (not p.dayOn) or p.days[lz.weekday()]
        mins = lz.hour * 60 + lz.minute; a0, a1 = p.sess
        inS = (a0 <= mins < a1) if a0 < a1 else (mins >= a0 or mins < a1)
        hourOk = (not p.hoursOn) or inS
        trendOk = True
        if p.trnOn:
            kk = k[i]; trendOk = kk >= 1 and Ct[kk - 1] > e[kk - 1]
        wkNow = p.wkOn and lny.weekday() == 4 and lny.hour >= p.wkH
        ok[i] = dayOk and hourOk and trendOk and not wkNow; wk[i] = wkNow
        dno[i] = lz.year * 10000 + lz.month * 100 + lz.day
    return ok, wk, dno


def twin2(B, ctf, prm, p):
    """trades (entry bar, F, exit bar, exit price, reason) and the per-trade $ risks of one strategy"""
    ftf, r, l, off, sl, tp, be, sv = prm
    t, O, H, L, C = EN.chart(B, ctf); utc = chart_utc(B, ctf)
    kk = np.searchsorted(B[ftf + '_t'], t, side='right') - 1
    ph, pt = f_piv_series(B[ftf + '_H'], B[ftf + '_t'], l, r)
    ok, wk, dno = globals_twin(B, ctf, p)
    s = Strat(p, 0, off, sl, tp, be, sv)
    for i in range(len(O)):
        s.onBar(ph[kk[i]], pt[kk[i]], int(kk[i]), C[i - 1] if i > 0 else NA, bool(ok[i]), bool(wk[i]), int(dno[i]), O[i], H[i], L[i], C[i], i, int(utc[i]) * 1000)
    return s
