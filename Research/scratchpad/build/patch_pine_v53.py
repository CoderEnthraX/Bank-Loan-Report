"""Strategy v5.3 (2026-11-19, spec v50/SPEC_v50.md section 7): "Recovery Part Size": Recalculate after each win (default) / Fixed when
recovery starts. Applied to build/bak/strategy_template_v52.pine, then assemble.py. The same as the MT5 EA v5.3."""
B = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/'
t = open(B + 'bak/strategy_template_v52.pine').read()


def sub1(a, b):
    global t
    assert t.count(a) == 1, (a[:100], t.count(a))
    t = t.replace(a, b)


sub1('''//  ($1,000 by default, up to the best), won back over N trades; an optional per-trade limit. The same as in the MT5 EA.
''', '''//  ($1,000 by default, up to the best), won back over N trades; an optional per-trade limit. The same as in the MT5 EA.
//  v5.3: Recovery Part Size: recalculate after each win (as before) or fixed when recovery starts (the same amount for the N trades).
''')
i = t.index('crkCn     = input.int(1, "", minval = 1, inline = "ccn", group = GRP_L')
j = t.index('\n', i) + 1
t = t[:j] + '''CPS_RECALC = "Recalculate after each win"
CPS_FIXED  = "Fixed when recovery starts"
crkPart   = input.string(CPS_RECALC, "Crooks C: Recovery Part Size", options = [CPS_RECALC, CPS_FIXED], group = GRP_L, tooltip = "Crooks C and E - X with Win The Loss Back Over N Wins. Recalculate after each win: every recovery trade goes for what is still owed / the parts left (a win that brings back more or less changes the next part). Fixed when recovery starts: at the first win the part is set (owed / N) and every recovery trade goes for that same amount; after the last part, a leftover smaller than the base amount is forgotten (base trades), a bigger one gets one more trade for exactly what is left. A loss on the way: 0.01 lot / base until a win, then new parts from everything owed.")
''' + t[j:]
sub1('var float crkL      = 0.0    // Crooks: $ loss to win back in this cycle\n',
     'var float crkL      = 0.0    // Crooks: $ loss to win back in this cycle\nvar float crkFx     = 0.0    // v5.3: the fixed recovery part ($ to win back; 0 = not set)\n')
sub1('    float crkX  = crkL / (recMode == L_CRB ? cSplit : crkCFam ? crkP : 1) * (crkPrOn and crkPr == CPR_PCT ? crkPrPct / 100.0 : 1.0)',
     '    float crkX  = (crkCFam and crkPart == CPS_FIXED and crkFx > 0 ? math.min(crkFx, crkL) : crkL / (recMode == L_CRB ? cSplit : crkCFam ? crkP : 1)) * (crkPrOn and crkPr == CPR_PCT ? crkPrPct / 100.0 : 1.0)   // v5.3: the fixed part')
sub1('''        if xNew
            crkP := crkNp                                // v5.2 Crooks X: a new step is won back in N trades
''', '''        if xNew
            crkP := crkNp                                // v5.2 Crooks X: a new step is won back in N trades
        if crkPart == CPS_FIXED and crkCFam              // v5.3: the recovery part fixed at the first win
            if not win
                crkFx := 0.0
            else
                if xNew
                    crkFx := 0.0
                if crkRec and crkLast and not xNew       // the last part won: a leftover below the base amount is forgotten, else one more trade for it
                    if crkL < (sizeBy == SB_PROFIT ? exBaseWin : exBase)
                        crkNew := true
                    else
                        crkFx := crkL
                        crkP  := 1
                else if crkFx <= 0
                    crkFx := crkL / crkP
''')
sub1('''    if crkNew                    // a new cycle at the base risk
        crkL     := 0.0
''', '''    if crkNew                    // a new cycle at the base risk
        crkL     := 0.0
        crkFx    := 0.0
''')
sub1('''    crkL        := 0.0
    crkN        := 0
''', '''    crkL        := 0.0
    crkFx       := 0.0
    crkN        := 0
''')
sub1('''            crkL      := 0.0
            crkN      := 0
''', '''            crkL      := 0.0
            crkFx     := 0.0
            crkN      := 0
''')
sub1('string kTxt = f_usd(crkL) + ', 'string kTxt = f_usd(crkL) + (crkCFam and crkPart == CPS_FIXED and crkFx > 0 ? " · part fixed " + f_usd(crkFx) : "") + ')
open(B + 'strategy_template.pine', 'w').write(t)
print('strategy template v5.3 written', t.count('\\n'), 'lines')
