import json
G='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/gt/'
L=[json.loads(l) for l in open(G+'ckpt_sensex_us30.jsonl') if l.strip()]
windows=[]; trades=[]; mvo=[]; seen=set()
for d in L:
    w=dict(d['window']); w['image']=d['image']; windows.append(w)
    if d['image']=='199401e9':
        w2=dict(w); w2['image']='06c042b4'; w2['anchor']='identical duplicate of 199401e9'; windows.append(w2)
    trades+=d['orig_trades']
for d in reversed(L):
    for m in d['my_vs_orig']:
        k=(m['symbol'],m.get('my_fill_bar'),m.get('orig_fill_bar'),m['status'])
        if k in seen: continue
        seen.add(k); mvo.append(m)
mvo.sort(key=lambda m:(m['symbol'],m.get('my_fill_bar') or m.get('orig_fill_bar')))
table=[
 "199401e9/06c042b4 (SENSEX, live state 2026-10-12 ~12:40, not the visible window): STATE SHORT ACTIVE; REGIME TRANSITION · ADX 38; BIAS BEARISH; ENTRY 71977.95; STOP 72131.62; TP1 71885.75; TP2 71824.28; TP3 71747.44; TP4 71670.61; LIVE/BARS -0.09R · 16; TARGETS HIT 1/3 reached; MODEL DAY 2W/0L · 100% · +4.00R; FILLS/CAP 2/5; LOADED BARS TP4 +2.00R · 34% · +13.00R",
 "e0514981 (SENSEX, live at 2026-10-12 12:40): SHORT ACTIVE; TRANSITION · ADX 38; BEARISH; ENTRY 71977.95; STOP 72131.62; TP1 71885.75; TP2 71824.28; TP3 71747.44; TP4 71670.61; LIVE/BARS -0.02R · 16; TARGETS HIT 1/3 reached; MODEL DAY 2W/0L · 100% · +4.00R; FILLS/CAP 2/5; LOADED BARS TP4 +2.00R · 34% · +13.00R",
 "758aa07c (US30): see checkpoint (no table values recorded for the window)",
 "dd1c136a (US30, state at chart end/realtime, does NOT match the visible 10-08 trades which show a live long): STATE SCANNING; REGIME RANGING · ADX 29; BIAS NEUTRAL; ENTRY —; STOP —; TP1-TP4 —; LIVE/BARS —; TARGETS HIT —; MODEL DAY 1W/1L · 50% · +1.00R; FILLS/CAP 2/5; LOADED BARS STOP -1.00R · 36% · +27.00R"]
obs = """RISK: every measured orig trade has R = 1.8 x ATR14 (Wilder/RMA) of the IMPULSE bar (US30 R/ATR 1.78-1.81, SENSEX 1.795-1.822); TPs at 0.6/1/1.5/2 R; my clone matches R and stops on all matched trades within pixel error (US30 10-08: 51137.0 vs 51137.06, 50855.0 vs 50855.38; SENSEX within ~5 pts).
ENTRY: limit = the level CLOSER to the impulse close among {body mid of impulse, the recent extreme the impulse broke}: short = min(mid, broken low), long = max(mid, broken high). The 'broken extreme' is a ROLLING ~19-20 bar extreme, not the true session extreme: US30 10-08 11:10 impulse broke the session low 51081 (06:45, 53 bars back) but the entry was the mid 51089.5 (no low <= mid in the last ~20 bars); SENSEX 10-07 10:55 used the 19-bar high excluding the 09:15 open bar. Cases: US30 10-08 06:05 -> 51110 = 06:00 low (mid 51114); SENSEX 10-08 10:35/13:15, 10-12 09:35 -> broken low; 10-09 10:05 -> broken high.
FILL: first bar AFTER the impulse that trades through the limit (exact touch counts: US30 11:15 H51090 vs 51089.5; 14:50 H50782 missed 50787.5 by 5.5, filled 14:55). The pending order is NOT re-armed by a following same-direction impulse while pending (US30 10-08 14:50 bearish bar ignored, 14:45 order kept). Exception low-confidence: US30 10-07 05:30 may have re-armed on 05:25.
EXITS: TP4 or stop by high/low; a trade stays open across sessions (SENSEX 10-08 13:20 short held overnight to 10-09 09:15; US30 10-08 23:15 long still open past the 02:25 session break). Only one position at a time.
CAPS: FILLS/CAP x/5 => max 5 fills per model day (US30 10-07: 5 fills 05:30-12:40 then no trades through the 14:35-17:45 selloff where mine took 13:40/15:30/16:40). SENSEX 10-07: after 3 straight losses (09:40,10:30,11:00) orig took nothing more (mine shorted 13:15) -> loss cap 3 (or 3 consecutive losses) per day.
SKIPPED IMPULSES (orig no trade, mine traded): (a) right after an exit: SENSEX 10-08 12:30 impulse 3 bars after orig TP4 12:15; US30 10-07 07:30 impulse on the very bar orig hit TP4 -> suggests a cooldown of a few bars after an exit / no signal on the exit bar. (b) weak bars: US30 10-08 08:40 body only 6 pts (0.38 ATR) - mine shorted 08:45 with an OLD level 51110 as entry (bug: my clone reused a stale broken level); US30 10-08 08:00 bull bar body 17 = 1.07 ATR, close 30 pts above VWAP, 12 bars after orig's 07:00 stop - orig skipped, mine long 08:05 stopped 08:10. (c) SENSEX 10-08 09:40 impulse closed only 7.7 below the session low; mine filled 09:45 with a 1.13-pt touch, orig did not trade (possibly orig's entry slightly different or minimum-break filter) - this then cascaded (mine busy until 11:25, missed orig 10:40). Cascades: most 'missed_mine' are caused by my extra trades occupying the single position slot (SENSEX 10-08 10:40 and 13:20, US30 10-07 06:05/10:05/11:30, US30 10-08 11:15).
Sessions: US30 VWAP/session resets 03:30 IST (data gap 02:30-03:25); SENSEX 09:15-15:30."""
out={"group":"sensex_us30","windows":windows,"orig_trades":trades,"my_vs_orig":mvo,"observations":obs,"table_readings":table}
import os; os.makedirs(G+'final',exist_ok=True)
json.dump(out,open(G+'final/sensex_us30.json','w'),indent=1)
print(len(windows),len(trades),len(mvo))
