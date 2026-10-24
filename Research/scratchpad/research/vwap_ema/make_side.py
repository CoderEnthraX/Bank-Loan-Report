"""Build ref_side.py = build/ref.py + research options for the VWAP-vs-EMA study (defaults = ref.py exactly)."""
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
s = open(S + '/build/ref.py').read()
R = [
 # options
 ("    kzOn=False, kz=(True, True, True, True), kzShift=0)",
  "    kzOn=False, kz=(True, True, True, True), kzShift=0,\n"
  "    # VWAP-vs-EMA research: side reference and EMA conditions (defaults = the model)\n"
  "    useVwap=True, emaPos=(), emaSlope=(), stack=(), pull=None, emaGhost=False, warmStart=0,\n"
  "    sigMode='disp', bounceLen=50, crossFast=50, crossSlow=200)"),
 # EMAs (SMA seed), once per run
 ("    atr = rma(P['tr'], p['atrLen'])\n",
  "    atr = rma(P['tr'], p['atrLen'])\n"
  "    def _ema(x, n):\n"
  "        o = [None] * len(x); a = 2.0 / (n + 1); s_ = None\n"
  "        for j in range(len(x)):\n"
  "            if s_ is None:\n"
  "                if j >= n - 1: s_ = sum(x[j - n + 1:j + 1]) / n\n"
  "            else: s_ = a * x[j] + (1 - a) * s_\n"
  "            o[j] = s_\n"
  "        return o\n"
  "    EM = {n: _ema(C, n) for n in (20, 50, 100, 200)}\n"
  "    def emaSide(j, d, A_):\n"
  "        for n in p['emaPos']:\n"
  "            e = EM[n][j]\n"
  "            if e is None or not d * (C[j] - e) > 0: return False\n"
  "        for n in p['emaSlope']:\n"
  "            e, e3 = EM[n][j], EM[n][j - 3]\n"
  "            if e is None or e3 is None or not d * (e - e3) > 0: return False\n"
  "        for a_, b_ in p['stack']:\n"
  "            ea, eb = EM[a_][j], EM[b_][j]\n"
  "            if ea is None or eb is None or not d * (ea - eb) > 0: return False\n"
  "        if p['pull']:\n"
  "            n, nb, k = p['pull']; ok = False\n"
  "            for jj in range(j - nb + 1, j + 1):\n"
  "                e = EM[n][jj]\n"
  "                if e is None: continue\n"
  "                if (L[jj] <= e + k * A_) if d > 0 else (H[jj] >= e - k * A_): ok = True; break\n"
  "            if not ok: return False\n"
  "        return True\n"),
 # side conditions in the base signal
 ("        setupOk = vwBars >= p['minOpenBars'] and not (p['skipSunday'] and utc.weekday() == 6)\n"
  "        bullBase = p['allowLong'] and setupOk and C[i] > O[i] and bigCandle and closeHi and sigUp and (not p['vwapFilter'] or C[i] > V[i]) and (p['momAtr'] <= 0 or momMove >= p['momAtr'] * A) and erUp\n"
  "        bearBase = p['allowShort'] and setupOk and C[i] < O[i] and bigCandle and closeLo and sigDn and (not p['vwapFilter'] or C[i] < V[i]) and (p['momAtr'] <= 0 or -momMove >= p['momAtr'] * A) and erDn\n",
  "        setupOk = vwBars >= p['minOpenBars'] and not (p['skipSunday'] and utc.weekday() == 6) and i >= p['warmStart']\n"
  "        vwL = (sigUp and (not p['vwapFilter'] or C[i] > V[i])) if p['useVwap'] else True\n"
  "        vwS = (sigDn and (not p['vwapFilter'] or C[i] < V[i])) if p['useVwap'] else True\n"
  "        eL = emaSide(i, 1, A); eS = emaSide(i, -1, A)\n"
  "        gEL = p['emaGhost'] and not eL; gES = p['emaGhost'] and not eS\n"
  "        bullBase = p['allowLong'] and setupOk and C[i] > O[i] and bigCandle and closeHi and vwL and (eL or p['emaGhost']) and (p['momAtr'] <= 0 or momMove >= p['momAtr'] * A) and erUp\n"
  "        bearBase = p['allowShort'] and setupOk and C[i] < O[i] and bigCandle and closeLo and vwS and (eS or p['emaGhost']) and (p['momAtr'] <= 0 or -momMove >= p['momAtr'] * A) and erDn\n"),
 # standalone EMA strategies replace the displacement trigger
 ("        bullDisp = (bullBase and C[i] > brkHigh) or deepL\n"
  "        bearDisp = (bearBase and C[i] < brkLow) or deepS\n",
  "        bullDisp = (bullBase and C[i] > brkHigh) or deepL\n"
  "        bearDisp = (bearBase and C[i] < brkLow) or deepS\n"
  "        if p['sigMode'] == 'emaBounce':\n"
  "            eb = EM[p['bounceLen']][i]\n"
  "            bullDisp = p['allowLong'] and setupOk and eb is not None and eL and vwL and L[i] <= eb and C[i] > eb and C[i] > O[i]\n"
  "            bearDisp = p['allowShort'] and setupOk and eb is not None and eS and vwS and H[i] >= eb and C[i] < eb and C[i] < O[i]\n"
  "            gEL = gES = False\n"
  "        elif p['sigMode'] == 'emaCross':\n"
  "            f0, s0, f1, s1 = EM[p['crossFast']][i], EM[p['crossSlow']][i], EM[p['crossFast']][i - 1], EM[p['crossSlow']][i - 1]\n"
  "            okc = None not in (f0, s0, f1, s1)\n"
  "            bullDisp = p['allowLong'] and setupOk and okc and f0 > s0 and f1 <= s1 and vwL\n"
  "            bearDisp = p['allowShort'] and setupOk and okc and f0 < s0 and f1 >= s1 and vwS\n"
  "            gEL = gES = False\n"),
 # EMA ghost at the arm
 ("                ghost = ghost or chopNo or emaNo\n",
  "                ghost = ghost or chopNo or emaNo or (gEL if isL else gES)\n"),
]
for a, b in R:
    assert s.count(a) == 1, a[:80]
    s = s.replace(a, b)
s = s.replace('"""Python reference of the SHARED ENGINE', '"""RESEARCH COPY (VWAP vs EMA study) of the Python reference of the SHARED ENGINE', 1)
open(S + '/research/vwap_ema/ref_side.py', 'w').write(s)
open(S + '/research/vwap_ema/score_side.py', 'w').write(
    "import sys; sys.path.insert(0, '%s/research/vwap_ema'); sys.path.insert(0, '%s/build')\nimport ref_side\n"
    "def run(sym, inp=None): return ref_side.shown(sym, inp)\n" % (S, S))
print('written')
