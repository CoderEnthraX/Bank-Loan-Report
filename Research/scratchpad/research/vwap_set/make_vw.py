"""ref_vw.py = build/ref.py + VWAP-setting research options (defaults = ref.py exactly)."""
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
s = open(S + '/build/ref.py').read()
R = [
 ("    kzOn=False, kz=(True, True, True, True), kzShift=0)",
  "    kzOn=False, kz=(True, True, True, True), kzShift=0,\n"
  "    # VWAP-settings research: computed VWAP (source / anchor / equal weights) and a minimum-distance gate\n"
  "    vwCompute=False, vwSrc='hlc3', vwAnchor='session', vwEqual=False, minDistAtr=0.0, minDistSig=0.0)"),
 ("    w = weights(sym) if p['noChase'] else None\n",
  "    w = weights(sym) if (p['noChase'] or p['minDistSig'] > 0) else None\n"
  "    # VWAP anchor flags (session = the CSV day start; week / month = first session of a new IST week / month)\n"
  "    ANCH = list(P['daystart'])\n"
  "    if p['vwAnchor'] != 'session':\n"
  "        last = None\n"
  "        for j in range(n):\n"
  "            k_ = T[j].isocalendar()[:2] if p['vwAnchor'] == 'week' else (T[j].year, T[j].month)\n"
  "            ANCH[j] = j == 0 or (P['daystart'][j] and k_ != last)\n"
  "            if ANCH[j]: last = k_\n"
  "    if p['vwCompute']:\n"
  "        wv = [1.0] * n if p['vwEqual'] else weights(sym)\n"
  "        src = {'hlc3': lambda j: (H[j] + L[j] + C[j]) / 3, 'close': lambda j: C[j], 'hl2': lambda j: (H[j] + L[j]) / 2,\n"
  "               'ohlc4': lambda j: (O[j] + H[j] + L[j] + C[j]) / 4}[p['vwSrc']]\n"
  "        V = [None] * n; cpv = cw = 0.0\n"
  "        for j in range(n):\n"
  "            if ANCH[j]: cpv = cw = 0.0\n"
  "            cpv += src(j) * wv[j]; cw += wv[j]\n"
  "            V[j] = cpv / cw if cw > 0 else src(j)\n"),
 ("        newAnchor = P['daystart'][i]; newDay = newAnchor\n",
  "        newDay = P['daystart'][i]; newAnchor = ANCH[i]\n"),
 ("                ghost = ghost or chopNo or emaNo\n",
  "                distNo = (p['minDistAtr'] > 0 and d * (C[i] - V[i]) < p['minDistAtr'] * A) or \\\n"
  "                         (p['minDistSig'] > 0 and vwSd is not None and vwSd > 0 and d * (C[i] - V[i]) < p['minDistSig'] * vwSd)\n"
  "                ghost = ghost or chopNo or emaNo or distNo\n"),
]
for a, b in R:
    assert s.count(a) == 1, a[:80]
    s = s.replace(a, b)
# T must exist before the anchor code: it is defined right after the OHLC lists in ref.py
assert s.index("T = [datetime.datetime.strptime") < s.index("ANCH = list(P['daystart'])")
open(S + '/research/vwap_set/ref_vw.py', 'w').write(s)
open(S + '/research/vwap_set/score_vw.py', 'w').write(
    "import sys; sys.path.insert(0, '%s/research/vwap_set'); sys.path.insert(0, '%s/build')\nimport ref_vw\n"
    "def run(sym, inp=None): return ref_vw.shown(sym, inp)\n" % (S, S))
print('written')
