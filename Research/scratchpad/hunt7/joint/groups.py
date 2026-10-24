# each group: list of alternative settings (dicts over the group's keys); first entry = off/default of j.py IN
def G():
    g = {}
    g['netMin'] = [dict(netMin=v) for v in (3, 2, 4, 5, 6)]
    g['tightAtr'] = [dict(tightAtr=v) for v in (0.9, 0.8, 0.85, 0.95, 1.0)]
    g['stopAtr'] = [dict(stopAtr=v) for v in (1.8, 1.7, 1.75, 1.85, 1.9)]
    g['erMin'] = [dict(erMin=v) for v in (0.0, 0.18, 0.19, 0.2, 0.21, 0.215, 0.219, 0.22)]
    g['retestBars'] = [dict(retestBars=v) for v in (5, 4, 6)]
    g['maxFills'] = [dict(maxFills=v) for v in (5, 6)]
    g['cooldown'] = [dict(cooldownBars=2, cdRaw=False), dict(cooldownBars=1, cdRaw=False), dict(cooldownBars=0, cdRaw=True), dict(cooldownBars=3, cdRaw=False)]
    g['minOpenBars'] = [dict(minOpenBars=v) for v in (1, 0, 2)]
    g['dayStop'] = [dict(dayStopR=3.0, dsMode='R', dsLoss=3), dict(dayStopR=0, dsMode='R', dsLoss=3), dict(dayStopR=2.0, dsMode='R', dsLoss=3),
                    dict(dayStopR=0, dsMode='loss', dsLoss=2), dict(dayStopR=0, dsMode='loss', dsLoss=3), dict(dayStopR=0, dsMode='lossDir', dsLoss=2), dict(dayStopR=0, dsMode='lossDir', dsLoss=3)]
    g['slopeCross'] = [dict(slopeCross=False), dict(slopeCross=True)]
    g['tightOut'] = [dict(tightOut=False), dict(tightOut=True)]
    g['tightOn'] = [dict(tightOn=True), dict(tightOn=False)]
    g['impNoSlope'] = [dict(impNoSlope=False), dict(impNoSlope=True)]
    g['vrt'] = [dict(vrt=False, vrtLook=6, vrtTol=0.0)] + [dict(vrt=True, vrtLook=k, vrtTol=t) for k in (3, 6) for t in (0.0, 0.3)]
    g['tightAny'] = [dict(tightAny=False), dict(tightAny=True)]
    g['tightGap'] = [dict(tightGap=v) for v in (0.0, 0.5, 1.0, 1.5, 2.0, 3.0)]
    g['vwStretch'] = [dict(vwStretch=v) for v in (0.0, 1.5, 2.0, 2.5, 3.0, 4.0)]
    g['eod'] = [dict(eodFlat=False, eodCancel=False), dict(eodFlat=True, eodCancel=False), dict(eodFlat=False, eodCancel=True), dict(eodFlat=True, eodCancel=True)]
    g['leg'] = [dict(legReset=True, legFrom='fill', legWin=0, legSameDay=False, legLossOnly=False)] + \
               [dict(legReset=True, legFrom=f, legWin=w, legSameDay=sd, legLossOnly=lo) for f in ('fill', 'exit', 'arm') for w in (0, 6, 15) for sd in (False, True) for lo in (False, True) if not (f == 'fill' and w == 0 and not sd and not lo)] + \
               [dict(legReset=False, legFrom='fill', legWin=0, legSameDay=False, legLossOnly=False)]
    g['prevBrk'] = [dict(prevBrk='', prevLvl='h', prevDay=False)] + [dict(prevBrk=b, prevLvl=l, prevDay=dd) for b in ('imp', 'shape', 'disp') for l in ('h', 'c') for dd in (False, True)]
    g['lossWin'] = [dict(lossWin=0, lossFrom='exit')] + [dict(lossWin=w, lossFrom=f) for w in (5, 10, 20, 40) for f in ('exit', 'fill')]
    g['rearm'] = [dict(rearmKeep=True, rearmMode='keep', rearmGap=0)] + [dict(rearmKeep=True, rearmMode=m, rearmGap=0) for m in ('higher', 'lower', 'nextbar', 'nexthigher')] + [dict(rearmKeep=False, rearmMode='keep', rearmGap=0)]
    g['noNextFill'] = [dict(noNextFill=False), dict(noNextFill=True)]
    g['minCE'] = [dict(minCE=v) for v in (0.0, -0.3, 0.1, 0.2, 0.3)]
    g['freshBreak'] = [dict(freshBreak=False), dict(freshBreak=True)]
    g['cancelBlock'] = [dict(cancelBlock=v) for v in (0, 1, 2, 3)]
    g['s2'] = [dict(s2Len=0, s2Far=0.0)] + [dict(s2Len=6, s2Far=f) for f in (1.5, 2.0, 2.5)]
    g['stopCap'] = [dict(capK=0.0, capN=0, stopVwap=0), dict(capK=1.0, capN=0, stopVwap=0), dict(capK=0.0, capN=3, stopVwap=0), dict(capK=0.0, capN=0, stopVwap=1), dict(capK=0.0, capN=0, stopVwap=3)]
    g['s2x'] = [dict(s2Len=0, s2Far=0.0, s2Vt=0, s2ER=True)] + [dict(s2Len=k, s2Far=f, s2Vt=v, s2ER=er) for k in (4, 5, 6, 8) for f in (1.0, 1.5, 2.0) for v in (0, 3) for er in (True, False) if not (k == 6 and v == 0 and er and f in (1.5, 2.0))]
    g['prevGate'] = [dict(prevGated=True, prevAge=0)] + [dict(prevGated=g_, prevAge=a) for g_ in (True, False) for a in (0, 12, 30) if not (g_ and a == 0)]
    return g
