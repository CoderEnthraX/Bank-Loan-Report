"""Every EA input default vs the user's TradingView settings (user_settings.USER), through a Pine -> EA name and value map."""
import re, sys
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/v40')
from user_settings import USER
EA = sys.argv[1]
src = open(EA, encoding='utf8').read()
ea = dict(re.findall(r'^input\s+\w+\s+(Inp\w+)\s*=\s*([^;]+);', src, re.M))
same = lambda *k: {x: 'Inp' + x[0].upper() + x[1:] for x in k}
M = {}
M.update(same('structLen', 'brkLen', 'entryLen', 'retestBars', 'dispAtr', 'momLen', 'momAtr', 'cmoMin', 'stopMode', 'stopAtr', 'stopLen', 'stopBufAtr',
              'halfStopAtr', 'biasNet', 'halfOpenOut', 'halfStrict', 'halfCap', 'maxFills', 'dayStopR', 'fillBarStopR', 'legReset', 'atrLen', 'vwapFilter',
              'slopeBars', 'slopeCross', 'minOpenBars', 'skipSunday', 'deepOn', 'deepFar', 'allowLong', 'allowShort', 'vwapAnchor', 'vwapSrc', 'entryMode',
              'entryPct', 'exitAt', 'noChase', 'noChaseSig', 'lossBlock', 'minVwOn', 'minVwAtr', 'maxVwOn', 'maxVwDist', 'maxVwUnit', 'stopVwOn', 'stopVwBuf',
              'touchVwOn', 'touchVwN', 'entVwOn', 'entVwAtr', 'chopOn', 'chopMax', 'emaOn', 'emaMax', 'dayOn', 'hoursOn', 'kzOn', 'kzAsia', 'kzLon', 'kzNy',
              'kzLc', 'kzAuto', 'kzShift', 'baseRisk', 'capOn', 'hardCap', 'capAction', 'leverage', 'lotStep', 'lotRound', 'commLot', 'earnBack', 'lStopOn',
              'lStopN', 'wStopOn', 'wStopN', 'pauseOn', 'pauseN', 'pauseDays', 'fcOn', 'weekendOn', 'newsPre', 'dNewsOn', 'recN', 'recPct', 'recMult',
              'recStep', 'cSplit', 'crkT1Stop', 'crkT1Pct', 'crkT1Any', 'crkCnOn', 'crkCn', 'crkPr', 'crkPrN', 'crkPrPct', 'crkPrM', 'crkPrD', 'crkPrForget',
              'crkPrAll', 'parN', 'delayN', 'eqPct'))
M.update(tp1R='InpTp1R', tp2R='InpTp2R', tp3R='InpTp3R', tp4R='InpTp4R', mv1On='InpMv1On', mv1R='InpMv1R', mv2On='InpMv2On', mv2R='InpMv2R',
         mv3On='InpMv3On', mv3R='InpMv3R', dispBodyPct='InpBodyPct', dispClosePct='InpClosePct', rearmMode='InpRearm', halfStopOn='InpHalfStop',
         impBodyPct='InpImpBody', cooldownBars='InpCooldown', dMon='InpMon', dTue='InpTue', dWed='InpWed', dThu='InpThu', dFri='InpFri', dSat='InpSat',
         dSun='InpSun', p1Pct='InpP1', p2Pct='InpP2', p3Pct='InpP3', smallMode='InpSmallLot', spreadIn='InpSpread', fcHour='InpFcH', fcMin='InpFcM',
         dnAuto='InpDNewsAuto', recMode='InpRec', crkT1On='InpCrkT1')
for k in range(1, 6): M.update({'n%dOn' % k: 'InpN%dOn' % k, 'n%dDur' % k: 'InpN%dDur' % k, 'n%dT' % k: 'InpN%dT' % k})
VAL = {'REARM_KEEP': 'REARM_KEEP', 'STOP_ATR': 'STOP_ATR', '"Session"': 'VW_SESSION', 'hlc3': 'PRICE_TYPICAL', 'E_MODEL': 'ENTRY_MODEL', '"TP1"': 'EXIT_TP1',
       'VWD_ATR': 'VWU_ATR', 'CAP_RESET': 'CAP_RESET', 'RND_DOWN': 'LOTR_DOWN', 'SMALL_MIN': 'SMALLL_MIN', 'L_CRC': 'REC_CRC', 'T1S_FULL': 'T1S_FULL',
       'CPR_OFF': 'CPR_OFF', 'timestamp("2026-01-01T18:00:00")': "D'2026.01.01 23:30'"}
def norm(v):
    v = v.strip()
    try: return float(v)
    except ValueError: return v
bad = 0; n = 0
for p, v in USER.items():
    if p in ('tzIn', 'hoursSess', 'dNewsSess', 'kzShift', 'lotMode', 'unitsLot', 'showMarks', 'showVwap', 'boxBorderW', 'maxDrawn'): continue
    e = M[p]; want = VAL.get(v, v); got = ea.get(e)
    n += 1
    if got is None or norm(got) != norm(want): print('DIFF %-12s %-16s EA %-20s user %s' % (p, e, got, want)); bad += 1
extra = [('tzIn', 'InpUserGMT', '5.5'), ('hoursSess', 'InpStartH', '6'), ('hoursSess', 'InpStartM', '0'), ('hoursSess', 'InpEndH', '23'),
         ('hoursSess', 'InpEndM', '0'), ('dNewsSess', 'InpDNewsH', '17'), ('dNewsSess', 'InpDNewsM', '45'), ('dNewsSess', 'InpDNewsDur', '30'),
         ('kzShift', 'InpKzShift', 'KZ_0'), ('(FxPro)', 'InpServerTz', 'SRV_EET'), ('(bid chart)', 'InpBidChart', 'true'), ('(1:100)', 'InpLeverage', '100.0')]
for p, e, want in extra:
    n += 1
    if norm(ea.get(e, '?')) != norm(want): print('DIFF %-12s %-16s EA %-20s want %s' % (p, e, ea.get(e), want)); bad += 1
print('EA inputs %d; checked %d settings, %d differ' % (len(ea), n, bad))
print('EA inputs not compared:', sorted(set(ea) - set(M.values()) - {e for _, e, _ in extra}))
