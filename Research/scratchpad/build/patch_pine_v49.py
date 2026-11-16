"""v4.9 (asked 2026-11-16): BE trigger and salvage trigger in the engine (shared: indicator and strategy), the same rule as the research engine
bese/ref_gbe.py (checked independently) and the EA v4.9:
  BE trigger (beOn, beR): a candle after the fill reaches entry + beR x risk -> the stop moves to the entry (from the next candle)
  salvage trigger (svOn, svR): a candle reaches entry - svR x risk -> the final target moves to the entry (from the next candle; out at 0R)
  only the first of the two acts in a trade; both on one candle: the extreme nearer the open came first; never on the fill candle.
Not set by a preset (they work on top of any preset; off = as tested). Applied to the v4.8 sources (backups build/bak/*_v48.pine), then assemble.py."""
import os, shutil
B = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/'
FILES = ('shared_inputs.pine', 'shared_engine.pine', 'strategy_template.pine', 'indicator_template.pine')
for f in FILES:
    bk = B + 'bak/' + f.replace('.pine', '_v48.pine')
    if not os.path.exists(bk): shutil.copy(B + f, bk)
src = {f: open(B + 'bak/' + f.replace('.pine', '_v48.pine')).read() for f in FILES}


def sub1(s, a, b):
    assert s.count(a) == 1, (a[:90], s.count(a))
    return s.replace(a, b)


TT_BE = ("Off (default). On: once a candle after the fill reaches this many R in profit (the high for a long, the low for a short), the stop moves to "
         "the entry from the next candle; the trade then ends at the target or at break-even (costs paid). Only the first of the BE and salvage triggers "
         "acts in a trade. Works with any preset (off = as tested). 1R = the stop distance (gold: about 0.27% of the price on M5, 0.52% on M15).\\n"
         "Gold 2021-2026 test (after costs): 1.5R was the best value on M5 and on M15. It helps strategies without a stop move of their own "
         "(M15-S8: +51R -> +83R in 2021-23, +44R -> +91R in 2024-26; M5-S1: +67R -> +68R, +45R -> +57R); early values cost a lot "
         "(0.3R: the 4 M5 presets -241R in 2021-23, the 6 M15 presets without a partial -468R).")
TT_SV = ("Off (default). On: once a candle after the fill reaches this many R against the trade (the low for a long, the high for a short), the final "
         "target moves to the entry from the next candle: if the price comes back, the trade ends at break-even instead of waiting for the full target. "
         "Below 1 (the stop is at 1R). Only the first of the BE and salvage triggers acts in a trade. Works with any preset (off = as tested).\\n"
         "Gold 2021-2026 test (after costs): every value lowered the results on M5 and M15; 0.9R did the least harm (the 4 M5 presets -33R in "
         "2021-23 and -25R in 2024-26; 0.5R: -170R and -79R), so it is best left off.")
# ---- inputs (in TARGETS, EXIT AND STOP MOVES, after the TP3 stop move; not renamed: a preset does not set them)
s = src['shared_inputs.pine']
a = 'mv3RIn = input.float(0.0, "", step = 0.1, inline = "m3", group = GRP_T)\n'
s = sub1(s, a, a + '''beOn   = input.bool(false, "BE Trigger: Stop To Entry Once Up (R)", inline = "trbe", group = GRP_T)
beR    = input.float(1.5, "", minval = 0.05, step = 0.05, inline = "trbe", group = GRP_T, tooltip = "%s")
svOn   = input.bool(false, "Salvage Trigger: Target To Entry Once Down (R)", inline = "trsv", group = GRP_T)
svR    = input.float(0.9, "", minval = 0.05, maxval = 0.95, step = 0.05, inline = "trsv", group = GRP_T, tooltip = "%s")
''' % (TT_BE, TT_SV))
open(B + 'shared_inputs.pine', 'w').write(s)

# ---- engine
e = src['shared_engine.pine']
e = sub1(e, 'var int   tpHit    = 0\n', 'var int   tpHit    = 0\nvar string trTrig  = ""      // v4.9: the BE / salvage trigger that acted in the live trade ("be", "sv" or "")\n')
e = sub1(e, 'bool   evTp      = false\n', 'bool   evTp      = false\nbool   evSalv    = false   // v4.9: the exit was at the entry, by the salvage target\nstring evTrig    = ""      // v4.9: a BE / salvage trigger acted on this bar ("be" / "sv")\n')
e = sub1(e, '''        bool  win = not stopHit
        float res = win ? exitR : stp == stp0 ? -1.0 : d * (stp - lim) / trRisk
''', '''        bool  salv = not stopHit and trTrig == "sv"     // v4.9: the salvage target (the entry): 0R, not a win
        bool  win  = not stopHit and not salv
        float res  = win ? exitR : salv ? 0.0 : stp == stp0 ? -1.0 : d * (stp - lim) / trRisk
''')
e = sub1(e, '''            lastRes    := (win ? "TP" + str.tostring(exitK) + " " : "STOP ") + (res >= 0 ? "+" : "") + str.tostring(res, "0.00") + "R"
            evExit     := true
            evWin      := win
            evRes      := res
''', '''            lastRes    := (win ? "TP" + str.tostring(exitK) + " " : salv ? "SALVAGE " : "STOP ") + (res >= 0 ? "+" : "") + str.tostring(res, "0.00") + "R"
            evExit     := true
            evWin      := win
            evRes      := res
            evSalv     := salv
''')
e = sub1(e, '''    else if tpHit > prevHit
        float ns = stp
        if mv1On and tpHit >= 1
            ns := isL ? math.max(ns, lim + mv1R * trRisk) : math.min(ns, lim - mv1R * trRisk)
        if mv2On and tpHit >= 2
            ns := isL ? math.max(ns, lim + mv2R * trRisk) : math.min(ns, lim - mv2R * trRisk)
        if mv3On and tpHit >= 3
            ns := isL ? math.max(ns, lim + mv3R * trRisk) : math.min(ns, lim - mv3R * trRisk)
        if ns != stp
            stp    := ns
            evMove := not trGhost
        evTp := not trGhost
''', '''    else
        if tpHit > prevHit
            float ns = stp
            if mv1On and tpHit >= 1
                ns := isL ? math.max(ns, lim + mv1R * trRisk) : math.min(ns, lim - mv1R * trRisk)
            if mv2On and tpHit >= 2
                ns := isL ? math.max(ns, lim + mv2R * trRisk) : math.min(ns, lim - mv2R * trRisk)
            if mv3On and tpHit >= 3
                ns := isL ? math.max(ns, lim + mv3R * trRisk) : math.min(ns, lim - mv3R * trRisk)
            if ns != stp
                stp    := ns
                evMove := not trGhost
            evTp := not trGhost
        // v4.9 BE / salvage trigger: only the first acts in a trade; both on one bar: the extreme nearer the open came first (from the next bar)
        if trTrig == "" and (beOn or svOn)
            float beL = lim + d * beR * trRisk
            float svL = lim - d * svR * trRisk
            bool  beH = beOn and (isL ? high >= beL - syminfo.mintick * 0.001 : low <= beL + syminfo.mintick * 0.001)
            bool  svH = svOn and (isL ? low <= svL + syminfo.mintick * 0.001 : high >= svL - syminfo.mintick * 0.001)
            if beH and svH
                bool hiFirst = math.abs(high - open) < math.abs(open - low)
                if hiFirst == isL
                    svH := false
                else
                    beH := false
            if beH
                trTrig := "be"
                evTrig := trGhost ? "" : "be"
                float nb = isL ? math.max(stp, lim) : math.min(stp, lim)
                if nb != stp
                    stp    := nb
                    evMove := not trGhost
            else if svH
                trTrig := "sv"
                evTrig := trGhost ? "" : "sv"
                tF     := lim
                evMove := not trGhost
''')
e = sub1(e, '''        tpHit    := 0
        dayFills += 1
''', '''        tpHit    := 0
        trTrig   := ""
        dayFills += 1
''')
# stats: the BREAKEVEN row also with the triggers, salvage exits counted
e = sub1(e, 'var int lkN = 0      // closed at a stop moved into profit (locked profit)\n',
         'var int lkN = 0      // closed at a stop moved into profit (locked profit)\nvar int svN = 0      // v4.9: closed at the entry by the salvage target (0R)\n')
e = sub1(e, '''    if not evWin and stp != stp0
        if evRes == 0.0
            beN += 1
        else if evRes > 0.0
            lkN += 1
''', '''    if evSalv
        svN += 1
    else if not evWin and stp != stp0
        if evRes == 0.0
            beN += 1
        else if evRes > 0.0
            lkN += 1
''')
e = sub1(e, 'bool mvAny  = mv1On or mv2On or mv3On\n', 'bool mvAny  = mv1On or mv2On or mv3On or beOn or svOn\n')
e = sub1(e, 'f_beTxt() => "BE " + str.tostring(beN) + " (" + f_share(beN, totW + totL) + ") · locked profit " + str.tostring(lkN) + " (" + f_share(lkN, totW + totL) + ")"',
         'f_beTxt() => "BE " + str.tostring(beN) + " (" + f_share(beN, totW + totL) + ") · locked profit " + str.tostring(lkN) + " (" + f_share(lkN, totW + totL) + ")" + (svOn ? " · salvage " + str.tostring(svN) + " (" + f_share(svN, totW + totL) + ")" : "")')
open(B + 'shared_engine.pine', 'w').write(e)

# ---- strategy: header note (the execution already re-sends its stop and target when the engine moves them: evMove)
t = src['strategy_template.pine']
t = sub1(t, '''//  zones and news. The monthly restart now also restarts the profit ladder and a hard-cap stop (the same in the MT5 EA).
''', '''//  zones and news. The monthly restart now also restarts the profit ladder and a hard-cap stop (the same in the MT5 EA).
//  v4.9: BE TRIGGER (stop to the entry once the trade is X R up) and SALVAGE TRIGGER (target to the entry once it is X R down), in
//  TARGETS, EXIT AND STOP MOVES; off by default, they work with any preset (the same in the indicator and the MT5 EA).
''')
t = sub1(t, 'f_tgtPx(bool isL, float lvl) => isL ? f_ceilTick(lvl + exCostPx - syminfo.mintick * 0.001) : f_floorTick(lvl - exCostPx + syminfo.mintick * 0.001)\n',
         'f_tgtPx(bool isL, float lvl) => isL ? f_ceilTick(lvl + exCostPx - syminfo.mintick * 0.001) : f_floorTick(lvl - exCostPx + syminfo.mintick * 0.001)\n'
         '// v4.9: the salvage target is the entry itself (no earn-back push), so the strategy leaves on the same bar and at the same price as the engine\n'
         'f_tgtPx0(bool isL, float lvl) => isL ? f_ceilTick(lvl - syminfo.mintick * 0.001) : f_floorTick(lvl + syminfo.mintick * 0.001)\n')
t = sub1(t, '        strategy.exit("X4", eid, qty_percent = 100, limit = f_tgtPx(isL, tF), stop = sPx)\n',
         '        strategy.exit("X4", eid, qty_percent = 100, limit = trTrig == "sv" ? f_tgtPx0(isL, tF) : f_tgtPx(isL, tF), stop = sPx)\n')
open(B + 'strategy_template.pine', 'w').write(t)

# ---- indicator: header note, alerts for the triggers and the salvage exit
d = src['indicator_template.pine']
d = sub1(d, '''//  kill zones (the same presets as the strategy and the MT5 EA).
''', '''//  kill zones (the same presets as the strategy and the MT5 EA).
//  v4.9: BE trigger and salvage trigger (TARGETS, EXIT AND STOP MOVES; off by default; the same in the strategy and the EA).
''')
d = sub1(d, '''    if evExit
        string exitMsg = tag + (evWin ? "TP" + str.tostring(exitK) + " HIT " : "STOP HIT ") + f_r(evRes)''', '''    if evTrig != ""
        alert(tag + (evTrig == "be" ? "BE TRIGGER: stop moved to the entry " : "SALVAGE TRIGGER: target moved to the entry ") + f_px(lim), alert.freq_once_per_bar_close)
    if evExit
        string exitMsg = tag + (evWin ? "TP" + str.tostring(exitK) + " HIT " : evSalv ? "SALVAGE EXIT AT ENTRY " : "STOP HIT ") + f_r(evRes)''')
open(B + 'indicator_template.pine', 'w').write(d)
print('v4.9 Pine sources written')
