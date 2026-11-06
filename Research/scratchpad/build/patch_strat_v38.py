"""v3.8 strategy template patch: Crooks TP1 rule % at TP1 and any final exit; daily news window follows New York time."""
import sys
F = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/strategy_template.pine'
s = open(F).read()
def rep(old, new, n=1):
    global s
    c = s.count(old)
    if c != n: sys.exit('count %d != %d for: %s' % (c, n, old[:90]))
    s = s.replace(old, new)

# news inputs
rep('''dNewsSess = input.session("1800-1900", "", inline = "dn", group = GRP_X, tooltip = "Repeats every day in the time zone of DAYS AND HOURS (e.g. US data at 8:30 New York = 18:00 IST).")
''', '''dNewsSess = input.session("1800-1900", "", inline = "dn", group = GRP_X, tooltip = "Repeats every day in the time zone of DAYS AND HOURS, set as it is in New York summer time (e.g. US data at 8:30 New York = 18:00 IST). The option below keeps it at the same New York time in winter.")
dnAuto    = input.bool(true, "Daily News Window Follows New York Time", group = GRP_X, tooltip = "On (default): the daily window keeps the same New York time all year. Set it as it is in New York summer time; while New York is on winter time (first Sunday of November to second Sunday of March) it moves 1 hour later in IST (18:00-19:00 -> 19:00-20:00). It works for any time zone in DAYS AND HOURS: the window moves by the change in the gap between that zone and New York (London: only in the weeks when the two switch on different dates).\\nOff: the window stays at the same time in your time zone all year.")
''')

# Crooks TP1 rule inputs
old_tip = s[s.index('crkT1On  = input.bool(true, "Crooks At Exit TP1: Bank The Loss At TP1, Rest To TP2", group = GRP_L, tooltip = "'):]
old_tip = old_tip[:old_tip.index('\n') + 1]
rep(old_tip, '''crkT1On  = input.bool(true, "Crooks At Exit TP1: Bank The Loss At TP1, Rest To TP2", group = GRP_L, tooltip = "Only with Crooks A / B / C / D, Final Exit At TP1 (any Final Exit with Crooks TP1 Rule: Works With Any Final Exit), and only on the recovery trades (A / B: 3, 5, 7 ...; C: the trade after a win; D: 3, 6, 9 ...). The position is made bigger: the part set in Crooks TP1 Rule: % Closed At TP1 (default 50, half) closes at TP1 and alone banks the whole recovery amount, then the stop of the rest moves to the entry and the rest closes at TP2. Where the stop sits before TP1 is set by Crooks TP1 Rule: Stop Before TP1 (default Tight: % x TP1 minus the costs from the entry, 0.3R with half and TP1 = 0.6R, so a stop-out loses exactly the recovery amount). Costs too big for that stop (above TP1 / 3 with half) -> that trade uses the normal Crooks size. While the rest runs on, new signals are skipped.\\nGold 2021-2026: the tight stop is hit on most of these trades; see the workbook before using it.")
''')
rep('''crkCnOn   = input.bool(false, "Crooks C: Win The Loss Back Over N Wins", inline = "ccn", group = GRP_L)''',
'''crkT1Pct  = input.float(50.0, "Crooks TP1 Rule: % Closed At TP1", minval = 10.0, maxval = 90.0, step = 5.0, group = GRP_L, tooltip = "Only for the Crooks TP1-rule trades. This share of the position closes at TP1 and alone banks the whole recovery amount; the rest's stop moves to the entry and it runs to TP2.\\nThe position risks 1 / (% x TP1) times the amount (no costs): 50% with TP1 = 0.6R -> 3.33x (the 'owed / 0.3' size), 30% -> 5.6x, 70% -> 2.4x. With the tight stop a stop-out loses exactly the amount; with the normal stop it loses that many times the amount, and a win at TP2 brings the amount plus (100 - %) / % x TP2 / TP1 times it (50%, TP2 = 1R: +1.67x).")
crkT1Any  = input.bool(false, "Crooks TP1 Rule: Works With Any Final Exit", group = GRP_L, tooltip = "Off (default): the TP1 rule acts only with Final Exit At TP1.\\nOn: it acts on the recovery trades whatever the Final Exit is: the part closes at TP1, the rest runs to TP2 with its stop at the entry after TP1 (with Final Exit TP3 / TP4 too, the rest closes at TP2). The other trades keep the normal exits. The stop moves (When TP1 / TP2 / TP3 Hits, Move Stop) and the partial profits do not apply to the TP1-rule trades.\\nHalf at TP1 and the rest at TP2 with the normal stop: tick Crooks At Exit TP1, Stop Before TP1 = Normal stop, % Closed At TP1 = 50 and this.")
crkCnOn   = input.bool(false, "Crooks C: Win The Loss Back Over N Wins", inline = "ccn", group = GRP_L)''')

# exits: the TP1 part
rep('''// Crooks TP1 rule: half closes at TP1, the rest at TP2; once TP1 is booked the rest's stop is the entry''',
    '''// Crooks TP1 rule: the TP1 part (crkT1Pct) closes at TP1, the rest at TP2; once TP1 is booked the rest's stop is the entry''')
rep('''            strategy.exit("X1", eid, qty = exQty * 0.5, limit = f_tgtPx(isL, exT1Tp1), stop = sPx)''',
    '''            strategy.exit("X1", eid, qty = exQty * crkT1Pct / 100.0, limit = f_tgtPx(isL, exT1Tp1), stop = sPx)''')
rep('''        strategy.exit("X1", eid, qty = exQty * 0.5, stop = sPx)''',
    '''        strategy.exit("X1", eid, qty = exQty * crkT1Pct / 100.0, stop = sPx)''')

# sizing
rep('''    // TP1 rule (Final Exit At TP1): half of a double position banks the recovery amount at TP1, the rest runs to TP2; the stop sits where
    // a stop-out loses exactly that amount: TP1 / 2 - 1.5 x costs from the entry, on the tick grid toward the entry
    float pvf   = syminfo.pointvalue * fx
    float eP    = f_entryPx(isL)
    float t1D   = pvf > 0 ? tp1R * rp / 2.0 - 1.5 * costUnit / pvf : 0.0
    float t1S   = isL ? f_ceilTick(eP - t1D) : f_floorTick(eP + t1D)
    bool  t1Ok  = crkT1On and exitK == 1 and f_crkRecNext() and t1D > 0 and (isL ? eP - t1S : t1S - eP) >= syminfo.mintick * 0.5''',
'''    // TP1 rule (Final Exit At TP1, or any with crkT1Any): the part p closed at TP1 banks the recovery amount, the rest runs to TP2; the size is
    // the one whose stop-out at t1D loses exactly that amount: p x TP1 - (1 + p) x costs from the entry (half: TP1 / 2 - 1.5 x costs), on the tick grid toward the entry
    float pvf   = syminfo.pointvalue * fx
    float eP    = f_entryPx(isL)
    float t1P   = crkT1Pct / 100.0
    float t1D   = pvf > 0 ? t1P * tp1R * rp - (1.0 + t1P) * costUnit / pvf : 0.0
    float t1S   = isL ? f_ceilTick(eP - t1D) : f_floorTick(eP + t1D)
    bool  t1Ok  = crkT1On and (exitK == 1 or crkT1Any) and f_crkRecNext() and t1D > 0 and (isL ? eP - t1S : t1S - eP) >= syminfo.mintick * 0.5''')
rep('''    // the stop before TP1 (Crooks TP1 Rule: Stop Before TP1): the size stays the one whose half banks the amount at TP1, the stop-out loss is t1Mul x the amount''',
    '''    // the stop before TP1 (Crooks TP1 Rule: Stop Before TP1): the size stays the one whose TP1 part banks the amount, the stop-out loss is t1Mul x the amount''')

# daily news window
rep('''// computed on every bar (outside the and/or chains) so their history is consistent
bool  inDNews   = not na(time(timeframe.period, dNewsSess, tzUse))
bool  dNewsIn   = dNewsOn and inDNews
bool  dNewsPrev = dNewsOn and inDNews[1]
// daily window: block from newsPre minutes before its start until it ends
bool  dPre = false
if dNewsOn and newsPre > 0
    int sH = int(str.tonumber(str.substring(dNewsSess, 0, 2)))
    int sM = int(str.tonumber(str.substring(dNewsSess, 2, 4)))
    int dStart = sH * 60 + sM
    int diff = (dStart - curM + 1440) % 1440
    dPre := diff > 0 and diff <= newsPre''',
'''// daily window (set in New York summer time): with dnAuto it moves by the change in the gap between the time zone of DAYS AND HOURS and
// New York against 1 July, so it keeps the same New York time all year (IST: 1 hour later while New York is on winter time)
f_nyGap(int t) => ((hour(t, tzUse) - hour(t, "America/New_York")) * 60 + minute(t, tzUse) - minute(t, "America/New_York") + 2880) % 1440
int   dnSh  = dnAuto ? (f_nyGap(time) - f_nyGap(timestamp("UTC", year(time, "UTC"), 7, 1, 12, 0)) + 2160) % 1440 - 720 : 0
int   dnS   = (int(str.tonumber(str.substring(dNewsSess, 0, 2))) * 60 + int(str.tonumber(str.substring(dNewsSess, 2, 4))) + dnSh + 1440) % 1440
int   dnE   = (int(str.tonumber(str.substring(dNewsSess, 5, 7))) * 60 + int(str.tonumber(str.substring(dNewsSess, 7, 9))) + dnSh + 1440) % 1440
// computed on every bar (outside the and/or chains) so their history is consistent; a moved window: the bar opens inside it, like the session
bool  inDSess   = not na(time(timeframe.period, dNewsSess, tzUse))
bool  inDNews   = dnSh == 0 ? inDSess : dnS < dnE ? curM >= dnS and curM < dnE : curM >= dnS or curM < dnE
bool  dNewsIn   = dNewsOn and inDNews
bool  dNewsPrev = dNewsOn and inDNews[1]
// daily window: block from newsPre minutes before its start until it ends
bool  dPre = false
if dNewsOn and newsPre > 0
    int diff = (dnS - curM + 1440) % 1440
    dPre := diff > 0 and diff <= newsPre''')
open(F, 'w').write(s)
print('patched', len(s))
