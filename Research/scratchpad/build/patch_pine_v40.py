"""v4.0: the user's TradingView settings (screenshots of 7 Nov 2026) become the defaults of the indicator and the strategy,
plus the cost suggestions (commission $7 per lot = FxPro, Properties commission = the table's value). Every replacement must match once."""
B = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/'

def patch(fn, reps):
    s = open(B + fn, encoding='utf8').read()
    for old, new in reps:
        n = s.count(old)
        assert n == 1, (fn, n, old[:90])
        s = s.replace(old, new)
    open(B + fn, 'w', encoding='utf8').write(s)
    print(fn, len(reps), 'replacements')

patch('shared_inputs.pine', [
    ('halfCap      = input.bool(false, "Half Stop Never Wider Than The Normal Stop (optional)", group = GRP_M, tooltip = "Off by default. When on, a half stop',
     'halfCap      = input.bool(true, "Half Stop Never Wider Than The Normal Stop (optional)", group = GRP_M, tooltip = "On by default (v4.0). When on, a half stop'),
    ('maxFills     = input.int(5, "Max Fills Per Day"', 'maxFills     = input.int(10, "Max Fills Per Day"'),
    ('entryPct  = input.float(50.0, "Custom % (0 = close, 50 = mid, 100 = low/high)"', 'entryPct  = input.float(25.0, "Custom % (0 = close, 50 = mid, 100 = low/high)"'),
    ('exitAt = input.string("TP4", "Final Exit At"', 'exitAt = input.string("TP1", "Final Exit At"'),
    ('mv3R   = input.float(1.0, "", step = 0.1, inline = "m3", group = GRP_T)', 'mv3R   = input.float(0.0, "", step = 0.1, inline = "m3", group = GRP_T)'),
    ('noChaseSig = input.float(2.4, ""', 'noChaseSig = input.float(2.0, ""'),
    ('chopMax    = input.float(12.0, ""', 'chopMax    = input.float(13.5, ""'),
    ('dayOn     = input.bool(false, "Trade Only On The Ticked Days", group = GRP_W, tooltip = "Off (default) = every day. On = new setups',
     'dayOn     = input.bool(true, "Trade Only On The Ticked Days", group = GRP_W, tooltip = "Off = every day. On (default: Tuesday, Wednesday, Thursday) = new setups'),
    ('dMon      = input.bool(true, "Mon"', 'dMon      = input.bool(false, "Mon"'),
    ('dFri      = input.bool(true, "Fri"', 'dFri      = input.bool(false, "Fri"'),
    ('dSat      = input.bool(true, "Sat"', 'dSat      = input.bool(false, "Sat"'),
    ('dSun      = input.bool(true, "Sun"', 'dSun      = input.bool(false, "Sun"'),
    ('hoursOn   = input.bool(false, "Trade Only Between"', 'hoursOn   = input.bool(true, "Trade Only Between"'),
    ('kzOn      = input.bool(false, "Trade Only In Kill Zones (Indian time)", group = GRP_W, tooltip = "Off (default) = all hours. On = new setups',
     'kzOn      = input.bool(true, "Trade Only In Kill Zones (Indian time)", group = GRP_W, tooltip = "Off = all hours. On (default: Asia, London, New York) = new setups'),
    ('kzLc      = input.bool(true, "London Close 19:30-21:30"', 'kzLc      = input.bool(false, "London Close 19:30-21:30"'),
    ('boxBorderW = input.int(2, "Box Border Width"', 'boxBorderW = input.int(1, "Box Border Width"'),
])

patch('strategy_template.pine', [
    ('//  With the default settings the strategy takes every trade the indicator shows. Execution settings\n'
     '//  (risk, costs, partials, streak stops, force-close, news) are strategy-only and OFF by default; when\n'
     '//  they block a signal it is counted in the table as SKIPPED.\n',
     '//  Execution settings (risk, costs, partials, streak stops, force-close, news) are strategy-only; when\n'
     '//  they block a signal it is counted in the table as SKIPPED. With every execution setting off the\n'
     '//  strategy takes every trade the indicator shows.\n'
     '//  v4.0 DEFAULTS = the settings traded on gold with FxPro, the same as the defaults of the MT5 EA:\n'
     '//  Tue / Wed / Thu 06:00-23:00 IST in the Asia, London and New York kill zones, exit at TP1, $50 base\n'
     '//  risk with Crooks C, news window 17:45-18:15 IST, force-close 23:55, spread 0.16 + $7 commission per lot.\n'),
    ('//  the value shown in the table row "SET PROPERTIES COMMISSION" (it includes the spread input).\n',
     '//  the value shown in the table row "SET PROPERTIES COMMISSION" (it includes the spread input). The\n'
     '//  default 0.115 per contract is that value for the default costs ($7 per lot + 0.16 spread, gold).\n'),
    ('commission_type = strategy.commission.cash_per_contract, commission_value = 0, slippage = 0',
     'commission_type = strategy.commission.cash_per_contract, commission_value = 0.115, slippage = 0'),
    ('hardCap    = input.float(500.0, ""', 'hardCap    = input.float(250.0, ""'),
    ('capAction  = input.string(CAP_CLAMP, "If The Risk Would Exceed The Cap"', 'capAction  = input.string(CAP_RESET, "If The Risk Would Exceed The Cap"'),
    ('The MT5 EA has the same setting (default: nearest).")', 'The MT5 EA has the same setting (default: down, like here).")'),
    ('smallMode  = input.string(SMALL_FRAC, "If Size Is Below 1 Lot Step"', 'smallMode  = input.string(SMALL_MIN, "If Size Is Below 1 Lot Step"'),
    ('spreadIn  = input.float(0.0, "Spread (price)"', 'spreadIn  = input.float(0.16, "Spread (price)"'),
    ('commLot   = input.float(0.0, "Commission ($ per lot, round trip)"', 'commLot   = input.float(7.0, "Commission ($ per lot, round trip)"'),
    ('earnBack  = input.bool(false, "Extend Targets To Earn Back Commission + Spread"', 'earnBack  = input.bool(true, "Extend Targets To Earn Back Commission + Spread"'),
    ('lStopN    = input.int(2, ""', 'lStopN    = input.int(23, ""'),
    ('fcOn      = input.bool(false, "Force-Close Open Trades At (hour : minute)"', 'fcOn      = input.bool(true, "Force-Close Open Trades At (hour : minute)"'),
    ('fcHour    = input.int(2, ""', 'fcHour    = input.int(23, ""'),
    ('fcMin     = input.int(0, "", minval = 0, maxval = 59, inline = "fc"', 'fcMin     = input.int(55, "", minval = 0, maxval = 59, inline = "fc"'),
    ('weekendOn = input.bool(false, "Close Open Trades When Saturday Starts"', 'weekendOn = input.bool(true, "Close Open Trades When Saturday Starts"'),
    ('dNewsOn   = input.bool(false, "Daily News Window"', 'dNewsOn   = input.bool(true, "Daily News Window"'),
    ('dNewsSess = input.session("1800-1900", ""', 'dNewsSess = input.session("1745-1815", ""'),
    ('recMode  = input.string(L_OFF, "Loss Recovery"', 'recMode  = input.string(L_CRC, "Loss Recovery"'),
    ('cSplit   = input.int(3, "Split The Loss Over This Many Trades', 'cSplit   = input.int(2, "Split The Loss Over This Many Trades'),
    ('crkT1On  = input.bool(true, "Crooks At Exit TP1: Bank The Loss At TP1, Rest To TP2"', 'crkT1On  = input.bool(false, "Crooks At Exit TP1: Bank The Loss At TP1, Rest To TP2"'),
    ('Where the stop sits before TP1 is set by Crooks TP1 Rule: Stop Before TP1 (default Tight: % x TP1 minus the costs from the entry, 0.3R with half and TP1 = 0.6R, so a stop-out loses exactly the recovery amount).',
     'Where the stop sits before TP1 is set by Crooks TP1 Rule: Stop Before TP1 (default Normal stop; Tight: % x TP1 minus the costs from the entry, 0.3R with half and TP1 = 0.6R, so a stop-out loses exactly the recovery amount).'),
    ('crkT1Stop = input.string(T1S_TIGHT, "Crooks TP1 Rule: Stop Before TP1"', 'crkT1Stop = input.string(T1S_FULL, "Crooks TP1 Rule: Stop Before TP1"'),
    ('crkPrD    = input.int(3, "Crooks C Rule: D Trading Days To Skip"', 'crkPrD    = input.int(4, "Crooks C Rule: D Trading Days To Skip"'),
])
