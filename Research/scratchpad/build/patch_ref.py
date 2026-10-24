"""Apply the v3.1 optional filters (halfCap, VWAP-cross gate, 1h EMA speed gate) to ref.py and ref_ev.py identically."""
import sys
B = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/'
R = [
 ("halfStopOn=True, halfStopAtr=0.9, biasNet=3, impBodyPct=50.0, halfOpenOut=True, halfStrict=False,",
  "halfStopOn=True, halfStopAtr=0.9, biasNet=3, impBodyPct=50.0, halfOpenOut=True, halfStrict=False, halfCap=False,"),
 ("    noChase=False, noChaseSig=2.4, lossBlock=False,",
  "    noChase=False, noChaseSig=2.4, lossBlock=False, chopOn=False, chopMax=12.0, emaOn=False, emaMax=1.65,"),
 ("    trades = []; cur = None\n",
  "    trades = []; cur = None\n"
  "    # optional filters: VWAP crosses this VWAP period; 1-hour (UTC) candles built from the bars and their EMA20 (hE[0..3] = last 4 completed hours)\n"
  "    vxSide = vxN = 0; hK = hC = None; hNum = 0; hSum = 0.0; hE = [None] * 4; hA = 2.0 / 21.0\n"
  "    EP = datetime.datetime(1970, 1, 1)\n"),
 ("        warm = i >= max(",
  "        A_ = atr[i]\n"
  "        if newAnchor: vxSide = 0; vxN = 0\n"
  "        vxDev = (C[i] - V[i]) / A_ if (A_ is not None and A_ > 0) else 0.0\n"
  "        vxZ = 1 if vxDev > 0.2 else -1 if vxDev < -0.2 else 0\n"
  "        if vxZ != 0:\n"
  "            if vxSide != 0 and vxZ != vxSide: vxN += 1\n"
  "            vxSide = vxZ\n"
  "        vxRate = 100.0 * vxN / (vwBars + 1)\n"
  "        hKey = int((T[i] - datetime.timedelta(hours=5, minutes=30) - EP).total_seconds() // 3600)\n"
  "        if hK is not None and hKey != hK:\n"
  "            hNum += 1\n"
  "            if hNum <= 20:\n"
  "                hSum += hC; e_ = hSum / 20.0 if hNum == 20 else None\n"
  "            else:\n"
  "                e_ = hA * hC + (1.0 - hA) * hE[0]\n"
  "            hE = [e_, hE[0], hE[1], hE[2]]\n"
  "        hK = hKey; hC = C[i]\n"
  "        emaSpd = abs(hE[0] - hE[3]) / A_ if (hE[0] is not None and hE[3] is not None and A_ is not None and A_ > 0) else None\n"
  "        warm = i >= max("),
 ("            hStop = min(entry - p['halfStopAtr'] * A, L[i]) if isL else max(entry + p['halfStopAtr'] * A, H[i])\n",
  "            hStop = min(entry - p['halfStopAtr'] * A, L[i]) if isL else max(entry + p['halfStopAtr'] * A, H[i])\n"
  "            if p['halfCap']: hStop = max(hStop, cStop) if isL else min(hStop, cStop)\n"),
 ("                ghost = p['noChase'] and z is not None and z > p['noChaseSig']\n",
  "                ghost = p['noChase'] and z is not None and z > p['noChaseSig']\n"
  "                chopNo = p['chopOn'] and vxRate > p['chopMax']\n"
  "                emaNo = p['emaOn'] and emaSpd is not None and emaSpd > p['emaMax']\n"
  "                ghost = ghost or chopNo or emaNo\n"),
]
for f in ('ref.py', 'ref_ev.py'):
    s = open(B + 'bak/' + f).read()
    for a, b in R:
        assert s.count(a) == 1, (f, a[:60], s.count(a))
        s = s.replace(a, b)
    open(B + f, 'w').write(s)
    print('patched', f)
