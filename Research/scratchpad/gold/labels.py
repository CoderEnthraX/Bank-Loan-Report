"""Readable settings: research option keys -> (indicator group, indicator input label, value, default, EA input)."""
KZN = ('Asia 05:30-09:30', 'London 11:30-14:30', 'New York 16:30-19:30', 'London Close 19:30-21:30')
EAKZ = ('InpKzAsia', 'InpKzLon', 'InpKzNy', 'InpKzLc')
DAYS = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
SIMPLE = {
    'structLen': ('SIGNAL MODEL', 'Structure Lookback (bars)', 'InpStructLen'), 'brkLen': ('SIGNAL MODEL', 'Signal Break Lookback (bars)', 'InpBrkLen'),
    'entryLen': ('SIGNAL MODEL', 'Entry Level Lookback (bars)', 'InpEntryLen'), 'retestBars': ('SIGNAL MODEL', 'Retest Window (bars)', 'InpRetestBars'),
    'dispAtr': ('SIGNAL MODEL', 'Min Displacement Range (x ATR)', 'InpDispAtr'), 'dispBodyPct': ('SIGNAL MODEL', 'Min Displacement Body (% of range)', 'InpBodyPct'),
    'dispClosePct': ('SIGNAL MODEL', 'Max Close Distance From Extreme (% of range)', 'InpClosePct'), 'momLen': ('SIGNAL MODEL', 'Momentum Lookback (bars)', 'InpMomLen'),
    'momAtr': ('SIGNAL MODEL', 'Momentum Min (x ATR)', 'InpMomAtr'), 'cmoMin': ('SIGNAL MODEL', 'Min CMO (clean move)', 'InpCmoMin'),
    'stopAtr': ('SIGNAL MODEL', 'Stop Distance (x ATR)', 'InpStopAtr'), 'stopLen': ('SIGNAL MODEL', 'Swing Lookback (bars)', 'InpStopLen'),
    'halfStopOn': ('SIGNAL MODEL', 'Half Stop On First Counter-Bias Impulse', 'InpHalfStop'), 'halfStopAtr': ('SIGNAL MODEL', 'Half Stop (x ATR)', 'InpHalfStopAtr'),
    'biasNet': ('SIGNAL MODEL', 'Prev Session Net Impulses', 'InpBiasNet'), 'impBodyPct': ('SIGNAL MODEL', 'Impulse Min Body (% of range)', 'InpImpBody'),
    'halfOpenOut': ('SIGNAL MODEL', 'Half Stop When Session Opens Outside Prev Range', 'InpHalfOpenOut'),
    'halfStrict': ('SIGNAL MODEL', 'Strict Bias Check (optional)', 'InpHalfStrict'), 'halfCap': ('SIGNAL MODEL', 'Half Stop Never Wider Than The Normal Stop (optional)', 'InpHalfCap'),
    'cooldownBars': ('SIGNAL MODEL', 'Cooldown After Exit (bars)', 'InpCooldown'), 'maxFills': ('SIGNAL MODEL', 'Max Fills Per Day', 'InpMaxFills'),
    'dayStopR': ('SIGNAL MODEL', 'Daily Stop (R lost, 0 = off)', 'InpDayStopR'), 'fillBarStopR': ('SIGNAL MODEL', 'Count Fill-Bar Stops In Daily Stop', 'InpFillBarStopR'),
    'legReset': ('SIGNAL MODEL', 'Re-anchor Breakout After A Trade', 'InpLegReset'), 'atrLen': ('SIGNAL MODEL', 'ATR Length', 'InpAtrLen'),
    'vwapFilter': ('SIGNAL MODEL', 'Longs Above VWAP / Shorts Below', 'InpVwapFilter'), 'slopeBars': ('SIGNAL MODEL', 'VWAP Slope Bars', 'InpSlopeBars'),
    'slopeCross': ('SIGNAL MODEL', 'Slope Looks Across The Session Start', 'InpSlopeCross'), 'minOpenBars': ('SIGNAL MODEL', 'Skip First Bars After VWAP Reset', 'InpMinOpenBars'),
    'skipSunday': ('SIGNAL MODEL', 'Skip Sunday (UTC) Weekly Open', 'InpSkipSunday'), 'deepOn': ('SIGNAL MODEL', 'Deep Pullback Signal (optional)', 'InpDeepOn'),
    'allowLong': ('SIGNAL MODEL', 'Longs', 'InpAllowLong'), 'allowShort': ('SIGNAL MODEL', 'Shorts', 'InpAllowShort'),
    'tp1R': ('TARGETS, EXIT AND STOP MOVES', 'TP1 (R)', 'InpTp1R'), 'tp2R': ('TARGETS, EXIT AND STOP MOVES', 'TP2 (R)', 'InpTp2R'),
    'tp3R': ('TARGETS, EXIT AND STOP MOVES', 'TP3 (R)', 'InpTp3R'), 'tp4R': ('TARGETS, EXIT AND STOP MOVES', 'TP4 (R)', 'InpTp4R'),
    'lossBlock': ('ACCURACY FILTERS', 'After A Loss, No Same-Direction Trade Until A Win', 'InpLossBlock'),
}
def yn(v): return 'On' if v else 'Off'
def fmt(v):
    if isinstance(v, bool): return yn(v)
    if isinstance(v, float): return ('%.2f' % v).rstrip('0').rstrip('.')
    return str(v)
def rows(cfg):
    """[(group, indicator input, new value, default value, EA input)] for every setting that differs from the default"""
    import greedy
    d = greedy.defaults(); c = dict(d); c.update(cfg); out = []
    for k, (g, lab, ea) in SIMPLE.items():
        if c[k] != d[k]: out.append((g, lab, fmt(c[k]), fmt(d[k]), ea))
    if c['rearmKeep'] != d['rearmKeep']: out.append(('SIGNAL MODEL', 'Same-Direction Re-arm', 'Replace with newer', 'Keep first', 'InpRearm = REARM_NEW'))
    if c['stopMode'] != d['stopMode']: out.append(('SIGNAL MODEL', 'Stop Mode', 'Swing + Buffer (ATR capped)', 'ATR Model', 'InpStopMode = STOP_SWING'))
    if c['vwAnchorG'] != 'session':
        out.append(('VWAP', 'Anchor', c['vwAnchorG'].capitalize(), 'Session', 'InpVwapAnchor = VW_%s' % c['vwAnchorG'].upper()))
    if c['vwSrcG'] != 'hlc3':
        ea = {'close': 'PRICE_CLOSE', 'hl2': 'PRICE_MEDIAN', 'ohlc4': '(not in MT5: use PRICE_WEIGHTED as nearest)'}[c['vwSrcG']]
        out.append(('VWAP', 'Source', c['vwSrcG'], 'hlc3', 'InpVwapSrc = ' + ea))
    if c['entryMode'] != 'model':
        if c['entryMode'] == 'pct':
            out.append(('ENTRY PRICE', 'Entry Price', 'Custom % of signal candle', 'Model', 'InpEntryMode = ENTRY_PCT'))
            out.append(('ENTRY PRICE', 'Custom %', fmt(c['entryPct']), '50', 'InpEntryPct'))
        else: out.append(('ENTRY PRICE', 'Entry Price', 'Market (next bar open)', 'Model', 'InpEntryMode = ENTRY_MARKET'))
    if c['exitAt'] != 4: out.append(('TARGETS, EXIT AND STOP MOVES', 'Final Exit At', 'TP%d' % c['exitAt'], 'TP4', 'InpExitAt = EXIT_TP%d' % c['exitAt']))
    for k in (1, 2, 3):
        if c['mv%dOn' % k]:
            out.append(('TARGETS, EXIT AND STOP MOVES', 'When TP%d Hits, Move Stop To (R)' % k, 'On, %s R%s' % (fmt(c['mv%dR' % k]), ' (breakeven)' if c['mv%dR' % k] == 0 else ''),
                        'Off', 'InpMv%dOn = true, InpMv%dR = %s' % (k, k, fmt(c['mv%dR' % k]))))
    if c['noChase']: out.append(('ACCURACY FILTERS', "Don't Chase: Skip Signals Beyond ... sigma From VWAP", 'On, %s' % fmt(c['noChaseSig']), 'Off (2.4)', 'InpNoChase = true, InpNoChaseSig = %s' % fmt(c['noChaseSig'])))
    if c['minVwOn']: out.append(('ACCURACY FILTERS', 'Skip Signals Too Close To VWAP: Min Distance (x ATR)', 'On, %s' % fmt(c['minVwAtr']), 'Off (1.0)', 'InpMinVwOn = true, InpMinVwAtr = %s' % fmt(c['minVwAtr'])))
    if c['chopOn']: out.append(('ACCURACY FILTERS', 'Skip Choppy Sessions: Max VWAP Crosses Per 100 Bars', 'On, %s' % fmt(c['chopMax']), 'Off (12)', 'InpChopOn = true, InpChopMax = %s' % fmt(c['chopMax'])))
    if c['emaOn']: out.append(('ACCURACY FILTERS', 'Skip When The 1h EMA20 Moved More Than ... ATR In 3 Hours', 'On, %s' % fmt(c['emaMax']), 'Off (1.65)', 'InpEmaOn = true, InpEmaMax = %s' % fmt(c['emaMax'])))
    if c['dayOn']: out.append(('DAYS AND HOURS', 'Trade Only On The Ticked Days', 'On: ' + ' '.join(n for n, v in zip(DAYS, c['days']) if v), 'Off', 'InpDayOn = true (untick the other days)'))
    if c['hoursOn']:
        a, b = c['hoursSess']; s = '%02d%02d-%02d%02d' % (a // 100, a % 100, b // 100, b % 100)
        out.append(('DAYS AND HOURS', 'Trade Only Between (Time Zone = Asia/Kolkata)', 'On, ' + s, 'Off', 'InpHoursOn = true, %02d:%02d to %02d:%02d, InpUserGMT = 5.5' % (a // 100, a % 100, b // 100, b % 100)))
    if c['kzOn']:
        out.append(('DAYS AND HOURS', 'Trade Only In Kill Zones (Indian time)', 'On: ' + ', '.join(n for n, v in zip(KZN, c['kz']) if v), 'Off',
                    'InpKzOn = true; ' + ', '.join('%s = %s' % (e, 'true' if v else 'false') for e, v in zip(EAKZ, c['kz']))))
        if c['kzShift']: out.append(('DAYS AND HOURS', 'Shift All Kill Zones (hours)', '%+d' % c['kzShift'], '0', 'InpKzShift'))
    if c.get('p1'): out.append(('PARTIAL PROFITS (strategy / EA only)', 'Close % At TP1', '%d' % round(100 * c['p1']), '0', 'InpP1 = %d' % round(100 * c['p1'])))
    return out
def short(cfg):
    r = rows(cfg)
    return ' | '.join('%s = %s' % (x[1], x[2]) for x in r) if r else 'default settings'
