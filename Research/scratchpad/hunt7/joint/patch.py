import sys
f='j.py'; s=open(f).read()
def rep(a,b):
    global s
    assert s.count(a)==1, a
    s=s.replace(a,b)
rep("capK=0.0, capN=0)", "capK=0.0, capN=0,\n          impNoSlope=False, vrt=False, vrtLook=6, vrtTol=0.0, tightAny=False, cdRaw=False, tightGap=0.0, vwStretch=0.0,\n          dsMode='R', dsLoss=3, eodFlat=False, eodCancel=False, legWin=0, legSameDay=False, legLossOnly=False, prevBrk='', prevLvl='h', prevGated=True,\n          prevDay=False, prevAge=0, prevMinAge=0, lossWin=0, lossFrom='exit', rearmMode='keep', rearmGap=0, noNextFill=False, minCE=0.0, freshBreak=False)")
rep("    sesH = sesL = sesO = pdH = pdL = None\n",
    "    sesH = sesL = sesO = pdH = pdL = None\n    gapPts = 0.0; dayLoss = {1: 0, -1: 0}; dayLossAll = 0; lastBull = lastBear = None\n    dayIdx = []; _d = 0\n    for _i in range(n): _d += 1 if P['daystart'][_i] else 0; dayIdx.append(_d)\n    def book(res, d):\n        nonlocal dayLossAll\n        if res < 0: dayLoss[d] += 1; dayLossAll += 1\n")
rep("        vwBars = 0 if newAnchor else vwBars + 1\n",
    "        if p['eodCancel'] and newAnchor and abs(st) == 1: st = 0\n        vwBars = 0 if newAnchor else vwBars + 1\n")
rep("            dayFills = 0; dayR = 0.0; dayRiskR = 0.0\n",
    "            dayFills = 0; dayR = 0.0; dayRiskR = 0.0; dayLoss = {1: 0, -1: 0}; dayLossAll = 0\n            gapPts = O[i] - C[i - 1] if i > 0 else 0.0\n            if p['prevDay']: lastBull = lastBear = None\n")
rep("                dayR += res; dayRiskR += res; lastExit = i; st = 0; cur.update(exit=i, res=res)\n",
    "                dayR += res; dayRiskR += res; lastExit = i; st = 0; cur.update(exit=i, res=res); book(res, cur['dir'])\n            if st != 0 and p['eodFlat'] and i + 1 < n and P['daystart'][i + 1]:\n                risk0 = abs(cur['entry'] - cur['stop'])\n                res = (C[i] - cur['entry']) / risk0 * (1 if isL else -1) if risk0 > 0 else 0.0\n                dayR += res; dayRiskR += res; lastExit = i; st = 0; cur.update(exit=i, res=res, eod=True); book(res, cur['dir'])\n")
rep("        if abs(st) == 1 and i > armBar:", "        if abs(st) == 1 and i > armBar + (1 if p['noNextFill'] else 0):")
rep("lastExit = i; st = 0; cur.update(exit=i, res=-1.0)\n", "lastExit = i; st = 0; cur.update(exit=i, res=-1.0)\n                    if p['sameBarDayStop']: book(-1.0, cur['dir'])\n")
rep("        if p['legReset'] and cur is not None and cur['exit'] is not None and 0 < i - cur[p['legFrom']] < p['structLen']:",
    "        if p['legReset'] and cur is not None and cur['exit'] is not None and 0 < i - cur[p['legFrom']] < (p['legWin'] or p['structLen']) and not (p['legSameDay'] and dayIdx[cur['fill']] != dayIdx[i]) and not (p['legLossOnly'] and cur['res'] > 0):")
rep("            else: brkL = min(L[cur['fill']:i])\n",
    "            else: brkL = min(L[cur['fill']:i])\n        if p['lossWin'] and cur is not None and cur['exit'] is not None and cur['res'] < 0 and 0 < i - cur[p['lossFrom']] < p['lossWin']:\n            if cur['dir'] == 1: brkH = max(brkH, max(H[cur['fill']:i]))\n            else: brkL = min(brkL, min(L[cur['fill']:i]))\n")
rep("        bullEvt = bullShape and sU; bearEvt = bearShape and sD\n",
    "        bullEvt = bullShape and sU; bearEvt = bearShape and sD\n        if p['freshBreak'] and i > p['structLen'] + 1:\n            pH = max(H[i - 1 - p['structLen']:i - 1]); pL = min(L[i - 1 - p['structLen']:i - 1])\n            if C[i - 1] > pH: bullEvt = False\n            if C[i - 1] < pL: bearEvt = False\n")
rep("<= p['dispClosePct'] + e and slopeUp\n", "<= p['dispClosePct'] + e and (slopeUp or p['impNoSlope'])\n")
rep("<= p['dispClosePct'] + e and slopeDn\n", "<= p['dispClosePct'] + e and (slopeDn or p['impNoSlope'])\n")
rep("            bullDisp = bullDisp or b2; bearDisp = bearDisp or s2_\n",
    "            bullDisp = bullDisp or b2; bearDisp = bearDisp or s2_\n"
    "        if p['vrt'] and setupOk and not (bullDisp or bearDisp) and bigCandle:\n            k = p['vrtLook']; tolA = p['vrtTol']\n"
    "            if C[i] > O[i] and C[i] > entHigh and (H[i]-C[i])/rng*100 <= p['dispClosePct'] + e and sU and C[i] > V[i] and min(L[i-k:i+1]) <= V[i] + tolA*A:\n                bullDisp = True\n"
    "            elif C[i] < O[i] and C[i] < entLow and (C[i]-L[i])/rng*100 <= p['dispClosePct'] + e and sD and C[i] < V[i] and max(H[i-k:i+1]) >= V[i] - tolA*A:\n                bearDisp = True\n"
    "        if p['prevBrk']:\n            rawL = dict(imp=bullImp, shape=bullShape, evt=bullEvt, disp=bullDisp).get(p['prevBrk'], False)\n            rawS = dict(imp=bearImp, shape=bearShape, evt=bearEvt, disp=bearDisp).get(p['prevBrk'], False)\n"
    "            if lastBull is not None and (not p['prevAge'] or i - lastBull[1] <= p['prevAge']) and i - lastBull[1] > p['prevMinAge']:\n                bullDisp = bullDisp and C[i] > lastBull[0]\n"
    "            if lastBear is not None and (not p['prevAge'] or i - lastBear[1] <= p['prevAge']) and i - lastBear[1] > p['prevMinAge']:\n                bearDisp = bearDisp and C[i] < lastBear[0]\n"
    "            if p['prevGated'] and p['prevBrk'] == 'disp': rawL, rawS = bullDisp, bearDisp\n"
    "            if rawL: lastBull = (H[i] if p['prevLvl'] == 'h' else C[i], i)\n            if rawS: lastBear = (L[i] if p['prevLvl'] == 'h' else C[i], i)\n")
rep("        tightL = p['tightOn'] and bullN == 0 and prevNet", "        tightL = p['tightOn'] and (bullN == 0 or p['tightAny']) and prevNet")
rep("        tightS = p['tightOn'] and bearN == 0 and prevNet", "        tightS = p['tightOn'] and (bearN == 0 or p['tightAny']) and prevNet")
rep("            tightS = tightS or (p['tightOn'] and bearN == 0 and sesO > pdH)\n",
    "            tightS = tightS or (p['tightOn'] and bearN == 0 and sesO > pdH)\n"
    "        if p['tightGap'] > 0 and prevNet is not None:\n            tightL = tightL or (p['tightOn'] and bullN == 0 and gapPts <= -p['tightGap'] * A)\n            tightS = tightS or (p['tightOn'] and bearN == 0 and gapPts >= p['tightGap'] * A)\n"
    "        if p['vwStretch'] > 0:\n            tightL = tightL or (p['tightOn'] and bullN == 0 and C[i] - V[i] >= p['vwStretch'] * A)\n            tightS = tightS or (p['tightOn'] and bearN == 0 and V[i] - C[i] >= p['vwStretch'] * A)\n")
rep("        cooled = lastExit is None or i - lastExit >= max(p['cooldownBars'], 1)\n        dayOpen = p['dayStopR'] <= 0 or dayRiskR > -p['dayStopR']\n        if p['cancelBlock'] and expBar == i: cooled = False\n",
    "        cooled = lastExit is None or i - lastExit >= (p['cooldownBars'] if p['cdRaw'] else max(p['cooldownBars'], 1))\n"
    "        if p['dsMode'] == 'loss': dayOpen = dayLossAll < p['dsLoss']\n        else: dayOpen = p['dayStopR'] <= 0 or dayRiskR > -p['dayStopR']\n"
    "        if p['dsMode'] == 'lossDir':\n            if bullDisp and dayLoss[1] >= p['dsLoss']: bullDisp = False\n            if bearDisp and dayLoss[-1] >= p['dsLoss']: bearDisp = False\n"
    "        if p['cancelBlock'] and expBar is not None and i - expBar < int(p['cancelBlock']): cooled = False\n")
rep("        keepArm = p['rearmKeep'] and ((st == 1 and bullDisp) or (st == -1 and bearDisp))\n",
    "        keepArm = p['rearmKeep'] and ((st == 1 and bullDisp) or (st == -1 and bearDisp))\n"
    "        if keepArm and p['rearmMode'] != 'keep':\n            _d = 1 if st == 1 else -1\n            _e = max(bodyMid, entHigh) if _d > 0 else min(bodyMid, entLow)\n            _gap = _d * (_e - lim) / A\n"
    "            if p['rearmMode'] == 'higher' and _gap > p['rearmGap']: keepArm = False\n            if p['rearmMode'] == 'lower' and _gap < -p['rearmGap']: keepArm = False\n"
    "            if p['rearmMode'] == 'nextbar' and i - armBar == 1: keepArm = False\n            if p['rearmMode'] == 'nexthigher' and i - armBar == 1 and _gap > p['rearmGap']: keepArm = False\n")
rep("            if risk >= mt and rtick(stop, mt) != rtick(entry, mt):", "            if risk >= mt and rtick(stop, mt) != rtick(entry, mt) and d * (C[i] - entry) >= p['minCE'] * A:")
open(f,'w').write(s)
