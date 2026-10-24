import json
GT='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/gt/'
W=[
 dict(image='9cc9233b',symbol='NIFTY',first_bar='2026-10-01 14:50',last_bar='2026-10-07 09:30',anchor='crosshair header O22691.00 H22716.05 L22689.85 C22711.10 = bar 2026-10-06 12:35 (idx 1841); x(idx)=1091.77+8.6756*(idx-1841)'),
 dict(image='1bde1d4a',symbol='NIFTY',first_bar='2026-10-01 15:05',last_bar='2026-10-06 14:30',anchor='crosshair header O22507.15 H22507.75 L22472.90 C22476.30 = bar 2026-10-05 11:35 (idx 1757); x(idx)=446.86+12.3486*(idx-1757); table shows live state (Mon 12 Oct ~12:00-12:30)'),
 dict(image='5f988fe1',symbol='NIFTY',first_bar='2026-10-06 15:00',last_bar='2026-10-09 09:35',anchor='crosshair header O22469.05 H22483.00 L22464.15 C22464.30 = bar 2026-10-08 09:50 (idx 1952); x(idx)=796.16+8.6758*(idx-1952)'),
 dict(image='de06f3d8',symbol='NIFTY',first_bar='2026-10-08 09:35',last_bar='2026-10-12 10:15',anchor='header shows the LIVE bar 2026-10-12 12:40 (O22396.80 L22392.40 match idx 2130, H/C still forming: H22402.20 C22400.10, countdown 02:58) - chart scrolled back, last visible bar 10:15 (axis labels VWAP 22540.65 / 22492.20 = 10:15 values); x(idx)=474.97+8.6759*(idx-1994)'),
 dict(image='95f571d1',symbol='NIFTY',first_bar='~2026-10-01 15:05 (approx, photo)',last_bar='~2026-10-06 14:30 (approx: 6 bars after the 09:50 L box end at 14:05)',anchor='crosshair header O22589.20 H22590.30 L22560.75 C22584.05 = bar 2026-10-05 09:35 (idx 1733); legend ARP 22552.47 1.00 0.00 (long fill on 09:35). Same framing/table as 1bde1d4a'),
 dict(image='0bc8343a',symbol='NIFTY',first_bar='~2026-10-05 11:00 (approx, photo; inside the 10:40 S box)',last_bar='2026-10-07 10:30 (replay edge: last candle red close 22657.80 label 22,657.x, VWAP label 22,632.x, long triangle under it)',anchor='crosshair header O22720.05 H22728.15 L22712.75 C22714.75 = bar 2026-10-06 12:45 (idx 1843)'),
]
def T(sym,d,fill,em,ee,src,sm,exitb,out,conf,imgs,rg,notes,tv=''):
    return dict(symbol=sym,dir=d,fill_bar=fill,entry_measured=em,entry_exact=ee,entry_exact_source=src,stop_measured=sm,exit_bar=exitb,outcome=out,confidence=conf,images=imgs,r_from_green_box=rg,notes=notes,table_values=tv)
O=[
 T('NIFTY','long','2026-10-05 09:35',22564.65,22564.60,'HIGH of 2026-10-05 09:15 (session high before impulse 09:25; impulse closed 22568.85 above it)',22528.45,'2026-10-05 10:20','stop','high',['9cc9233b','1bde1d4a','95f571d1'],36.2,
   'Signal 09:25 (2nd bar after open). Fill 09:35 L22560.75; 09:30 L22568.40 did not touch. R=36.2 = 0.9*ATR14(RMA TR @09:25 = 40.23) -> exact stop 22528.39 (HALF the usual 1.8*ATR). Legend ARP 22552.47 1.00 0.00 on 09:35 confirms fill. TP4 22636.95/22637.14 measured. Exit 10:20 L22503.95.'),
 T('NIFTY','short','2026-10-05 10:40',22473.90,22474.00,'LOW of 2026-10-05 10:25 (session low; impulse 10:35 closed 22473.55 just below)',22540.80,'2026-10-05 13:40','stop','high',['9cc9233b','1bde1d4a','95f571d1','0bc8343a'],66.85,
   'Signal 10:35 (body 98%, rng 1.58 ATR). Fill 10:40 H22500.50. R=66.86 = 1.8*ATR14(37.14) -> exact stop 22540.86. TP4 22340.2 measured. Exit 13:40 (big green bar H22559.05).'),
 T('NIFTY','long','2026-10-06 09:50',22630.30,22629.95,'HIGH of 2026-10-06 09:40 (session high; impulse 09:45 closed 22633.45)',22580.35,'2026-10-06 14:05','tp4','high',['9cc9233b','1bde1d4a','95f571d1','0bc8343a'],49.6,
   'Signal 09:45. Fill 09:50 L22623.45. R=49.64=1.8*ATR14(27.58) -> exact stop 22580.31. TP4 measured 22729.3/22729.5 (exact 22729.23); hit 14:05 H22731.85.'),
 T('NIFTY','long','2026-10-07 10:30',22686.13,22686.00,'HIGH of 2026-10-07 10:20 (impulse 10:25 closed 22697.40 above HOD 22692.95)',22637.15,'2026-10-07 10:35','stop','high',['5f988fe1','0bc8343a'],None,
   'Signal 10:25. Fill 10:30 L22657.80. R=49.11=1.8*ATR14(27.285) -> exact stop 22636.89. One-bar box (green not measurable). 0bc8343a shows the up-triangle under the 10:30 bar at its right edge. Stopped 10:35 L22623.25.'),
 T('NIFTY','long','2026-10-07 11:00',22701.71,22701.60,'HIGH of 2026-10-07 10:25 (impulse 10:55 closed 22705.05)',22652.15,'2026-10-07 12:25','stop','high',['5f988fe1'],49.5,
   'Signal 10:55 (4 bars after previous stop). Fill 11:00 L22690.25. R=49.63=1.8*ATR14(27.57) -> exact stop 22651.97. TP4 ~22800.7 measured. Stopped 12:25 L22645.90. Second loss of the day; no further orig trades on 10-07.'),
 T('NIFTY','short','2026-10-08 10:40',22432.66,22432.60,'LOW of 2026-10-08 10:30 (impulse 10:35 closed 22427.00)',22482.40,'2026-10-08 11:25','tp4','high',['5f988fe1','de06f3d8'],49.75,
   'Signal 10:35. Fill 10:40 H22447.55. R=49.67=1.8*ATR14(27.595) -> exact stop 22482.27. TP4 measured 22333.18 (exact 22333.26); hit 11:25 L22328.45.'),
 T('NIFTY','short','2026-10-08 13:20',22254.40,22254.30,'LOW of 2026-10-08 12:55 (impulse 13:15 closed 22243.65)',22303.05,'2026-10-09 09:15','stop','high',['5f988fe1','de06f3d8'],48.6,
   'Signal 13:15 (body 96%, rng 1.30 ATR). Fill 13:20 H22269.10. R=48.59=1.8*ATR14(26.99) -> exact stop 22302.89. TP4 measured 22157.29. Held overnight; 10-09 09:15 gapped open 22317.00 above stop -> stop (box ends 09:15).'),
 T('NIFTY','long','2026-10-09 10:10',22480.60,22480.45,'HIGH of 2026-10-09 09:55 (impulse 10:05 closed 22482.20)',22449.38,'2026-10-09 11:55','stop','high',['de06f3d8'],31.3,
   'Signal 10:05. Fill 10:10 L22470.85. R=31.2 = 0.9*ATR14(34.83)=31.35 -> exact stop 22449.10 (HALF stop again). TP4 measured 22543.24 (exact 22543.15). Stopped 11:55 L22448.55.'),
 T('NIFTY','long','2026-10-09 13:50',22517.51,22517.65,'BODY MID of impulse 2026-10-09 13:40 (O22509.15 C22526.15); 6-bar high lower',22485.20,'2026-10-12 09:15','tp4','high',['de06f3d8'],32.25,
   'Signal 13:40 (close 22526.15 did NOT exceed session high 22534.40). 13:45 L22521.35 no touch; fill 13:50 L22515.05. R=32.46=1.8*ATR14(18.03) -> exact stop 22485.19. TP4 measured 22581.99 (exact 22582.57). Held over weekend; 10-12 09:15 gapped open 22593.65 above TP4 -> TP4 (box ends 09:15).'),
 T('NIFTY','short','2026-10-12 09:55',22499.25,22499.225,'BODY MID of impulse 2026-10-12 09:50 (O22521.60 C22476.85)',22559.84,'2026-10-12 11:10','tp4','high',['de06f3d8'],60.66,
   'Signal 09:50. Fill 09:55 H22527.40 (09:50 signal bar itself excluded). R=60.56=1.8*ATR14(33.645) -> exact stop 22559.79. TP4 measured 22377.94 (exact 22378.11). Box still open at de06 right edge (10:15); data: TP4 hit 11:10 L22376.25. Table at ~12:40 (MODEL DAY 2W/0L +4.00R, FILLS 1/5, LOADED BARS TP4 +2.00R) consistent with T9+T10 both TP4 on Mon 12.',
   'de06f3d8 table: STATE SCANNING | REGIME TRENDING · ADX 36 | BIAS BEARISH | ENTRY - | STOP - | TP1-4 - | LIVE/BARS - | TARGETS HIT - | MODEL DAY 2W/0L · 100% · +4.00R | FILLS / CAP 1/5 | LOADED BARS TP4 +2.00R · 35% · +22.00R'),
]
M=[
 dict(symbol='NIFTY',status='match',my_dir='long',my_fill_bar='2026-10-05 09:35',orig_fill_bar='2026-10-05 09:35',notes='my stop 22491.86 (7b9104ee; 22491.3 on 33b07bdc) vs orig 22528.45: mine R=1.8*ATR=72.4, orig 0.9*ATR=36.2. My exit 10:25 stop vs orig 10:20 stop.'),
 dict(symbol='NIFTY',status='match',my_dir='short',my_fill_bar='2026-10-05 10:40',orig_fill_bar='2026-10-05 10:40',notes='my stop 22540.37 (7b9104ee; 22540.1 on 33b07bdc) vs orig 22540.80 - same (exact 22540.86). Entry 22474.00 both.'),
 dict(symbol='NIFTY',status='match',my_dir='long',my_fill_bar='2026-10-06 09:50',orig_fill_bar='2026-10-06 09:50',notes='my stop 22580.05 (7b9104ee; ~22579.3 on 33b07bdc) vs orig 22580.26 - same (exact 22580.31). Both TP4 14:05.'),
 dict(symbol='NIFTY',status='extra_mine',my_dir='short',my_fill_bar='2026-10-07 09:40',orig_fill_bar='',notes='mine entry 22600.05 stop 22640.37 (56af2287), stopped 10:15. Orig: no box/triangle (5f988fe1, 0bc8343a). Yellow line Wed 07 10:00.'),
 dict(symbol='NIFTY',status='match',my_dir='long',my_fill_bar='2026-10-07 10:30',orig_fill_bar='2026-10-07 10:30',notes='my stop 22636.90 vs orig 22637.15 - same (exact 22636.89).'),
 dict(symbol='NIFTY',status='match',my_dir='long',my_fill_bar='2026-10-07 11:00',orig_fill_bar='2026-10-07 11:00',notes='my stop 22651.64 vs orig 22652.15 - same (exact 22651.97).'),
 dict(symbol='NIFTY',status='extra_mine',my_dir='short',my_fill_bar='2026-10-07 13:15',orig_fill_bar='',notes='mine entry 22589.65 stop 22629.96 (56af2287), stopped 14:25. Orig had 2 losses that day already (10:30 L, 11:00 L) -> no trade. Yellow Wed 07 13:50.'),
 dict(symbol='NIFTY',status='match',my_dir='short',my_fill_bar='2026-10-08 10:40',orig_fill_bar='2026-10-08 10:40',notes='my stop 22481.72 vs orig 22482.42 - same (exact 22482.27). Both TP4 11:25.'),
 dict(symbol='NIFTY',status='extra_mine',my_dir='short',my_fill_bar='2026-10-08 12:20',orig_fill_bar='',notes='mine entry 22336.51 stop 22382.89 TP4 22240.71 (56af2287); exit TP4 13:20. Orig flat (prior S TP4 at 11:25) but skipped the 12:15 impulse.'),
 dict(symbol='NIFTY',status='missed_mine',my_dir='',my_fill_bar='',orig_fill_bar='2026-10-08 13:20',notes='orig S entry 22254.30 stop 22302.89. Mine was still in the 12:20 S on the 13:15 signal bar (its TP4 hit only at 13:20) so it could not arm. Yellow Thu 08 13:20.'),
 dict(symbol='NIFTY',status='extra_mine',my_dir='short',my_fill_bar='2026-10-08 14:05',orig_fill_bar='',notes='mine entry 22226.41 stop 22275.39 (56af2287), stopped 10-09 09:15. Orig was inside its 13:20 S (one position at a time). Yellow Thu 08 14:35.'),
 dict(symbol='NIFTY',status='match',my_dir='long',my_fill_bar='2026-10-09 10:10',orig_fill_bar='2026-10-09 10:10',notes='my stop 22417.77 vs orig 22449.38 (f0411b87): mine 1.8*ATR=62.7, orig 0.9*ATR=31.3. Entry same (22480.31 vs 22480.45). Orig stopped 11:55; mine stayed in until TP4 10-12 09:15.'),
 dict(symbol='NIFTY',status='missed_mine',my_dir='',my_fill_bar='',orig_fill_bar='2026-10-09 13:50',notes='orig L entry 22517.65 (body mid 13:40) stop 22485.19, TP4 at 10-12 09:15 gap. Mine still in the 10:10 L (wide stop never hit) -> blocked. Fixing the half-stop fixes this. Yellow Fri 09 13:50.'),
 dict(symbol='NIFTY',status='match',my_dir='short',my_fill_bar='2026-10-12 09:55',orig_fill_bar='2026-10-12 09:55',notes='my stop 22559.64 vs orig 22559.84 - same (exact 22559.79). Mine TP4 11:10 (f0411b87 box end).'),
]
obs=("ENTRY RULE (all 10 exact): long limit = max(body mid of impulse bar, highest high of the previous bars = session/6-bar high), short = min(mid, lowest low); 8/10 are prior HOD/LOD retests, 2 are impulse body mids (10-09 13:40, 10-12 09:50). Fill = first bar after the impulse that trades the level. "
 "STOP: R = 1.8*ATR14 (RMA of TR, value on impulse bar) on 8 trades; R = 0.9*ATR14 (HALF) on 10-05 09:35 L and 10-09 10:10 L. Both half-R trades are early (15 and 55 min after open) longs whose impulse ran against the higher-timeframe bias (close below slow MA / 60m EMA - 'ctr' in every bias variant tested); mine uses 1.8 there -> wrong stop, and on 10-09 the wide stop kept mine in the trade so it missed the orig 13:50 L. TP4 = 2R, TP1-3 = 0.6/1/1.5R. "
 "ONE POSITION AT A TIME, exits checked from the fill bar; overnight gaps exit at the open (10-09 09:15 stop, 10-12 09:15 TP4). "
 "SKIPPED impulses (orig flat, mine traded): (a) 10-07 09:35 S: 25 min after open, rng 1.33 ATR, body 87%, close 36 below VWAP, new session low, no trade yet that day (prior day orig won); (b) 10-07 13:05 S: rng 2.20 ATR, body 94%, close 93 below VWAP, 235 min after open, orig already had 2 losses that day -> consistent with a 2-losses-per-day stop (10-05 also stopped after 2 losses); (c) 10-08 12:15 S: rng 1.24 ATR, body 69%, close off low 17%, close 126 below VWAP, 185 min after open, orig 1W 0L that day, broke session low only by 3.7 pts, entry 22336.10 still ABOVE the previous win's TP4 22332.96 (orig took the next one at 13:15, entry 22254.30, well beyond it) - possible rule: a same-direction re-entry must be beyond the previous trade's target. (d) 10-08 14:00 S: orig in a trade. "
 "Taken impulses: every one closed beyond VWAP in trade direction (+25.8..+175.7) and (except 10-09 13:40) beyond the prior session extreme; rng/ATR 0.82-1.58, body 63-98%. "
 "Tables (1bde1d4a, de06f3d8, photo 95f571d1) show LIVE state on Mon 12 Oct (~12:00-12:40), not the scrolled window: MODEL DAY 2W/0L +4.00R counts exits on the day (10-09 13:50 L TP4 at Mon 09:15 + 10-12 09:55 S TP4) while FILLS 1/5 counts fills; ADX 39 (1bde) / 36 (de06) matches ADX14 at ~12:10-12:30 / 12:40. Mine's 10-12 13:15 S is after the last orig evidence (12:40) - unverified.")
tr=['de06f3d8 (and identical 1bde1d4a except ADX 39, and photo 95f571d1): AUCTION RETEST | MODEL MONITOR; STATE SCANNING; REGIME TRENDING · ADX 36; BIAS BEARISH; ENTRY/STOP/TP1-4/LIVE/TARGETS -; MODEL DAY 2W/0L · 100% · +4.00R; FILLS / CAP 1/5; LOADED BARS TP4 +2.00R · 35% · +22.00R']
final=dict(group='nifty',windows=W,orig_trades=O,my_vs_orig=M,observations=obs,table_readings=tr)
json.dump(final,open(GT+'final/nifty.json','w'),indent=1)
# checkpoint lines per orig image
by={w['image']:w for w in W}
with open(GT+'ckpt_nifty.jsonl','w') as f:
    for im in by:
        f.write(json.dumps(dict(image=im,window=by[im],orig_trades=[o for o in O if im in o['images']],my_vs_orig=[],notes='see final/nifty.json'))+'\n')
print('ok')
