"""Strategy presets (asked 2026-11-16): the single source of every preset value written into the TradingView files and the two EAs.

AUCTION RETEST: the 25 catalogue strategies (gold/crooks.sources: M1 S1-S4, M5 S1-S4, M15 S1-S9, H1 S1-S8). Each one = the research
defaults it was found with (greedy.defaults(), the v3.9 engine defaults) + its own changes. A preset sets EVERY engine value (the user's
defaults differ from the research defaults: half-stop cap, max fills, entry %, exit TP1, ...), its own session (hours / kill zone) and the
strategy's / EA's partial close at TP1. Time filters of the user (days, hours, kill zones, news) only with "Add My Filters".
GRID: combinations of the 12 Fractal Breakout Grid strategies with the money they were tested with in the $1,000-a-month study
(mcej3/final.txt, final_150.txt, combo.txt): fixed $ base, loss recovery, hard cap, monthly restart."""
import sys
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold'); sys.path.insert(0, S + '/build')

TFS = ('M1', 'M5', 'M15', 'H1')
TF_PINE = {'M1': '1', 'M5': '5', 'M15': '15', 'H1': '60'}
TF_MQL = {'M1': 'PERIOD_M1', 'M5': 'PERIOD_M5', 'M15': 'PERIOD_M15', 'H1': 'PERIOD_H1'}

# engine parameters: (Pine variable, research key, kind, EA input)
PARAMS = [
    ('structLen', 'structLen', 'int', 'InpStructLen'), ('brkLen', 'brkLen', 'int', 'InpBrkLen'), ('entryLen', 'entryLen', 'int', 'InpEntryLen'),
    ('retestBars', 'retestBars', 'int', 'InpRetestBars'), ('dispAtr', 'dispAtr', 'float', 'InpDispAtr'), ('dispBodyPct', 'dispBodyPct', 'float', 'InpBodyPct'),
    ('dispClosePct', 'dispClosePct', 'float', 'InpClosePct'), ('momLen', 'momLen', 'int', 'InpMomLen'), ('momAtr', 'momAtr', 'float', 'InpMomAtr'),
    ('cmoMin', 'cmoMin', 'float', 'InpCmoMin'), ('rearmMode', 'rearmKeep', 'rearm', 'InpRearm'), ('stopMode', 'stopMode', 'stopmode', 'InpStopMode'),
    ('stopAtr', 'stopAtr', 'float', 'InpStopAtr'), ('stopLen', 'stopLen', 'int', 'InpStopLen'), ('stopBufAtr', 'stopBufAtr', 'float', 'InpStopBufAtr'),
    ('halfStopOn', 'halfStopOn', 'bool', 'InpHalfStop'), ('halfStopAtr', 'halfStopAtr', 'float', 'InpHalfStopAtr'), ('biasNet', 'biasNet', 'int', 'InpBiasNet'),
    ('impBodyPct', 'impBodyPct', 'float', 'InpImpBody'), ('halfOpenOut', 'halfOpenOut', 'bool', 'InpHalfOpenOut'), ('halfStrict', 'halfStrict', 'bool', 'InpHalfStrict'),
    ('halfCap', 'halfCap', 'bool', 'InpHalfCap'), ('cooldownBars', 'cooldownBars', 'int', 'InpCooldown'), ('maxFills', 'maxFills', 'int', 'InpMaxFills'),
    ('dayStopR', 'dayStopR', 'float', 'InpDayStopR'), ('fillBarStopR', 'fillBarStopR', 'bool', 'InpFillBarStopR'), ('legReset', 'legReset', 'bool', 'InpLegReset'),
    ('atrLen', 'atrLen', 'int', 'InpAtrLen'), ('vwapFilter', 'vwapFilter', 'bool', 'InpVwapFilter'), ('slopeBars', 'slopeBars', 'int', 'InpSlopeBars'),
    ('slopeCross', 'slopeCross', 'bool', 'InpSlopeCross'), ('minOpenBars', 'minOpenBars', 'int', 'InpMinOpenBars'), ('skipSunday', 'skipSunday', 'bool', 'InpSkipSunday'),
    ('deepOn', 'deepOn', 'bool', 'InpDeepOn'), ('deepFar', 'deepFar', 'float', 'InpDeepFar'), ('allowLong', 'allowLong', 'bool', 'InpAllowLong'),
    ('allowShort', 'allowShort', 'bool', 'InpAllowShort'), ('vwapAnchor', 'vwAnchorG', 'anchor', 'InpVwapAnchor'), ('vwapSrc', 'vwSrcG', 'src', 'InpVwapSrc'),
    ('entryMode', 'entryMode', 'entry', 'InpEntryMode'), ('entryPct', 'entryPct', 'float', 'InpEntryPct'),
    ('tp1R', 'tp1R', 'float', 'InpTp1R'), ('tp2R', 'tp2R', 'float', 'InpTp2R'), ('tp3R', 'tp3R', 'float', 'InpTp3R'), ('tp4R', 'tp4R', 'float', 'InpTp4R'),
    ('exitAt', 'exitAt', 'exit', 'InpExitAt'), ('mv1On', 'mv1On', 'bool', 'InpMv1On'), ('mv1R', 'mv1R', 'float', 'InpMv1R'), ('mv2On', 'mv2On', 'bool', 'InpMv2On'),
    ('mv2R', 'mv2R', 'float', 'InpMv2R'), ('mv3On', 'mv3On', 'bool', 'InpMv3On'), ('mv3R', 'mv3R', 'float', 'InpMv3R'),
    ('noChase', 'noChase', 'bool', 'InpNoChase'), ('noChaseSig', 'noChaseSig', 'float', 'InpNoChaseSig'), ('lossBlock', 'lossBlock', 'bool', 'InpLossBlock'),
    ('minVwOn', 'minVwOn', 'bool', 'InpMinVwOn'), ('minVwAtr', 'minVwAtr', 'float', 'InpMinVwAtr'), ('maxVwOn', 'maxVwOn', 'bool', 'InpMaxVwOn'),
    ('maxVwDist', 'maxVwDist', 'float', 'InpMaxVwDist'), ('maxVwUnit', 'maxVwUnit', 'vwunit', 'InpMaxVwUnit'), ('stopVwOn', 'stopVwOn', 'bool', 'InpStopVwOn'),
    ('stopVwBuf', 'stopVwBuf', 'float', 'InpStopVwBuf'), ('touchVwOn', 'touchVwOn', 'bool', 'InpTouchVwOn'), ('touchVwN', 'touchVwN', 'int', 'InpTouchVwN'),
    ('entVwOn', 'entVwOn', 'bool', 'InpEntVwOn'), ('entVwAtr', 'entVwAtr', 'float', 'InpEntVwAtr'), ('chopOn', 'chopOn', 'bool', 'InpChopOn'),
    ('chopMax', 'chopMax', 'float', 'InpChopMax'), ('emaOn', 'emaOn', 'bool', 'InpEmaOn'), ('emaMax', 'emaMax', 'float', 'InpEmaMax'),
]
TIME_KEYS = ('dayOn', 'days', 'hoursOn', 'hoursSess', 'kzOn', 'kz', 'kzShift', 'kzAuto')
RESEARCH_ONLY = {'emaPos': (), 'stack': (), 'emaGhost': False}     # research filters with no input: must be off in every preset


def ars_presets():
    """[{key 'M5-S1', tf, n, goal, v (every engine value), p1 (partial close at TP1, 0..1)}] in dropdown order"""
    import crooks, greedy
    base = greedy.defaults(); out = []
    for tf in TFS:
        for i, d in enumerate(crooks.sources(tf)):
            if i == 0: continue
            v = dict(base); v.update(d['cfg'])
            for k, x in RESEARCH_ONLY.items(): assert v.get(k, x) == x, (tf, i, k)
            assert not v['dayOn'], (tf, i)                                   # no catalogue strategy has a day filter
            known = {p[1] for p in PARAMS} | set(TIME_KEYS) | set(RESEARCH_ONLY) | {'p1'}
            assert set(v) <= known, set(v) - known
            assert v['vwSrcG'] == 'hlc3'
            out.append(dict(key='%s-S%d' % (tf, i), tf=tf, n=i, goal=d['name'], v=v, p1=float(v.get('p1', 0.0))))
    return out


def label(p):
    """dropdown text, e.g. 'M5-S1 · Most profit'"""
    return '%s · %s' % (p['key'], p['goal'])


# ---- literal values ----
def fnum(x):
    s = repr(float(x))
    return s if ('.' in s or 'e' in s) else s + '.0'


def pine_lit(kind, x):
    if kind == 'int': return str(int(x))
    if kind == 'float': return fnum(x)
    if kind == 'bool': return 'true' if x else 'false'
    if kind == 'rearm': return 'REARM_KEEP' if x else 'REARM_NEW'
    if kind == 'stopmode': return {'atr': 'STOP_ATR', 'swing': 'STOP_SWING'}[x]
    if kind == 'anchor': return {'session': '"Session"', 'week': '"Week"', 'month': '"Month"'}[x]
    if kind == 'src': return {'hlc3': 'hlc3'}[x]
    if kind == 'entry': return {'model': 'E_MODEL', 'pct': 'E_PCT', 'market': 'E_MARKET'}[x]
    if kind == 'exit': return '"TP%d"' % int(x)
    if kind == 'vwunit': return {'atr': 'VWD_ATR', 'price': 'VWD_PX'}[x]
    raise ValueError(kind)


def mql_lit(kind, x):
    if kind == 'int': return str(int(x))
    if kind == 'float': return fnum(x)
    if kind == 'bool': return 'true' if x else 'false'
    if kind == 'rearm': return 'REARM_KEEP' if x else 'REARM_NEW'
    if kind == 'stopmode': return {'atr': 'STOP_ATR', 'swing': 'STOP_SWING'}[x]
    if kind == 'anchor': return {'session': 'VW_SESSION', 'week': 'VW_WEEK', 'month': 'VW_MONTH'}[x]
    if kind == 'src': return {'hlc3': 'PRICE_TYPICAL'}[x]
    if kind == 'entry': return {'model': 'ENTRY_MODEL', 'pct': 'ENTRY_PCT', 'market': 'ENTRY_MARKET'}[x]
    if kind == 'exit': return 'EXIT_TP%d' % int(x)
    if kind == 'vwunit': return {'atr': 'VWU_ATR', 'price': 'VWU_PRICE'}[x]
    raise ValueError(kind)


def session(p):
    """the preset's own session: (hoursOn, 'HHMM-HHMM' or None, kzOn, (asia, lon, ny, lc), kzAuto, kzShift)"""
    v = p['v']
    hs = '%04d-%04d' % tuple(v['hoursSess']) if v['hoursOn'] else None
    return (bool(v['hoursOn']), hs, bool(v['kzOn']), tuple(bool(b) for b in v['kz']) if v['kzOn'] else (False,) * 4, bool(v['kzAuto']), int(v['kzShift']))


def session_text(p):
    h, hs, kz, z, auto, sh = session(p)
    parts = []
    if h: parts.append('%s:%s-%s:%s IST' % (hs[:2], hs[2:4], hs[5:7], hs[7:9]))
    if kz: parts.append(' + '.join(n for n, b in zip(('Asia', 'London', 'New York', 'London Close'), z) if b) + ' kill zone')
    return ', '.join(parts) if parts else 'all day'


# ---- grid presets: (key, dropdown text, strategies, base $, loss recovery (grid Pine option constant / EA enum), cap $ or None, cap action) ----
GRID_PRESETS = [
    dict(key='G1', name='Best monthly: S7, S8, S10 · $10 · exact recovery · cap $100', strats=(7, 8, 10), base=10.0, rec='EXACT', cap=100.0, act='clamp'),
    dict(key='G2', name='Safest: S1, S2, S6, S7, S8, S10 · $5 · exact recovery · cap $50', strats=(1, 2, 6, 7, 8, 10), base=5.0, rec='EXACT', cap=50.0, act='clamp'),
    dict(key='G3', name='Steady, more profit: S1, S2, S6, S7, S8, S10 · $10 · exact recovery · cap $100 start again', strats=(1, 2, 6, 7, 8, 10), base=10.0,
         rec='EXACT', cap=100.0, act='reset'),
    dict(key='G4', name='Small: S7, S8, S10 · $5 · exact recovery · cap $50', strats=(7, 8, 10), base=5.0, rec='EXACT', cap=50.0, act='clamp'),
    dict(key='G5', name='No recovery: all 12 · $10 fixed risk', strats=tuple(range(1, 13)), base=10.0, rec='OFF', cap=None, act='clamp'),
    dict(key='G6', name='No recovery: 11 strategies (all but S4) · $10 fixed risk', strats=(1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12), base=10.0, rec='OFF', cap=None,
         act='clamp'),
]
REC_RESEARCH = {'EXACT': 'Exact recovery at final TP', 'OFF': 'Off'}


if __name__ == '__main__':
    P = ars_presets()
    print(len(P), 'ARS presets')
    for p in P:
        diff = {k: p['v'][k] for k in ('stopAtr', 'exitAt', 'entryMode', 'vwAnchorG', 'halfCap', 'maxFills') }
        print('%-7s %-45s %-30s p1 %.1f %s' % (p['key'], p['goal'], session_text(p), p['p1'], diff))
    for g in GRID_PRESETS: print(g['key'], g['name'])
