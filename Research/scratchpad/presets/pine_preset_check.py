"""Reads the generated TradingView files (not the generators) and evaluates every preset expression for every preset index, then compares
with presets/preset_data.py: ARS (strategy and indicator: all engine values, own session, timeframe, partial at TP1) and the grid (strategies on,
their settings, entry options, money). Pine `c ? a : b` chains with `PI == k or ...` conditions are evaluated by a small parser."""
import re, sys
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/presets'); sys.path.insert(0, S + '/fractal'); sys.path.insert(0, S + '/fractal/pine'); sys.path.insert(0, S + '/fractal/pine3')
import preset_data as PD
R = '/home/user/Bank-Loan-Report/TradingView/'


def split_top(s, ch):
    d = 0; q = False
    for i, c in enumerate(s):
        if c == '"': q = not q
        elif not q and c in '([': d += 1
        elif not q and c in ')]': d -= 1
        elif not q and d == 0 and s.startswith(ch, i): return s[:i], s[i + len(ch):]
    return None


def ev(expr, env, consts):
    expr = expr.strip()
    t = split_top(expr, ' ? ')
    if t:
        c, rest = t; a, b = split_top(rest, ' : ')
        return ev(a, env, consts) if evc(c, env) else ev(b, env, consts)
    if expr in ('true', 'false'): return expr == 'true'
    if expr.startswith('"'): return expr.strip('"')
    if expr in consts: return consts[expr]
    if expr == 'hlc3': return 'hlc3'
    if re.fullmatch(r'-?\d+', expr): return int(expr)
    if re.fullmatch(r'[A-Za-z_]\w*', expr): return expr
    return float(expr)


def evc(c, env):
    return any(int(env[a]) == int(b) for a, b in re.findall(r'(\w+) == (\d+)', c)) if ' == ' in c else bool(env[c.strip()])


def read(path, idx):
    s = open(path, encoding='utf8').read()
    consts = dict(re.findall(r'^(\w+)\s*=\s*"([^"]*)"\s*$', s, re.M))
    eff = {}
    for m in re.finditer(r'^(?:int|float|bool|string)\s+(\w+)\s*=\s*(\w+) \? (\w+) : (.+)$', s, re.M):
        name, guard, alt, ex = m.groups(); eff[name] = (guard, alt, ex)
    return s, consts, eff


def check_ars(path):
    s, consts, eff = read(path, 'PI')
    P = PD.ars_presets(); bad = 0; n = 0
    labels = [consts['PS_%d' % i] for i in range(1, len(P) + 1)]
    assert all(l.startswith(p['key'] + ' ') for l, p in zip(labels, P)), labels
    inv = {'REARM_KEEP': True, 'REARM_NEW': False, 'STOP_ATR': 'atr', 'STOP_SWING': 'swing', 'E_MODEL': 'model', 'E_PCT': 'pct', 'E_MARKET': 'market',
           'VWD_ATR': 'atr', 'VWD_PX': 'price'}
    for k, p in enumerate(P, 1):
        env = dict(PI=k)
        for pv, key, kind, _ in PD.PARAMS:
            g, alt, ex = eff[pv]; assert g == 'PC' and alt == pv + 'In', pv
            raw = ex.strip()
            val = ev(raw, env, {})
            if kind in ('rearm', 'stopmode', 'entry', 'vwunit'):
                val = inv[val] if val in inv else inv[[c for c in inv if consts.get(c) == val][0]]
            if kind == 'anchor': val = val.lower()
            if kind == 'exit': val = int(val[2:])
            want = p['v'][key]
            if kind == 'float': ok = abs(float(val) - float(want)) < 1e-12
            else: ok = val == want
            n += 1
            if not ok: bad += 1; print('  ARS %s %s: file %r want %r' % (p['key'], pv, val, want))
        h, hs, kz, z, auto, sh = PD.session(p)
        tests = [('hoursOn', h), ('hoursSess', hs or '0000-0000'), ('kzOn', kz), ('kzAsia', z[0]), ('kzLon', z[1]), ('kzNy', z[2]), ('kzLc', z[3]), ('kzAuto', auto), ('kzShift', sh)]
        for nm, want in tests:
            ex = re.search(r'^\w+\s+%s\s*=\s*ownS \? (.+) : %sIn$' % (nm, nm), s, re.M).group(1)
            v = ev(ex, env, {}); n += 1
            if v != want: bad += 1; print('  ARS %s %s: file %r want %r' % (p['key'], nm, v, want))
        ex = re.search(r'^string presetTf = PC \? "" : (.+)$', s, re.M).group(1); v = ev(ex, env, {}); n += 1
        if v != PD.TF_PINE[p['tf']]: bad += 1; print('  ARS %s tf %r' % (p['key'], v))
        if 'p1Pct' in eff:
            v = ev(eff['p1Pct'][2], env, {}); n += 1
            if abs(v - p['p1'] * 100) > 1e-9: bad += 1; print('  ARS %s p1 %r' % (p['key'], v))
    # Custom: every effective value is the input itself
    custom = all(alt == name + 'In' for name, (g, alt, ex) in eff.items() if g == 'PC')
    print('%s: %d preset values checked, %d wrong; Custom = the inputs: %s' % (path.split('/')[-1], n, bad, custom))
    return bad + (not custom)


def check_grid(path):
    from build_fbg3 import T9
    import json
    strats = T9 + [tuple(x) for x in json.load(open(S + '/fractal/pick_10_12.json'))]
    from build_fbg import TFV as TFV11
    TFV = dict(TFV11, M1='1')
    s, consts, eff = read(path, 'GI')
    G = PD.GRID_PRESETS; bad = 0; n = 0
    assert [consts['GP_%d' % i] for i in range(1, len(G) + 1)] == [g['name'] for g in G]
    cmap = {'CAP_CLAMP': 'clamp', 'CAP_RESET': 'reset', 'CAP_STOP': 'stop', 'L_EXACT': 'EXACT', 'L_OFF': 'OFF'}
    rc = {consts[c]: v for c, v in cmap.items() if c in consts}
    for gi, g in enumerate(G, 1):
        env = dict(GI=gi)
        for i, p in enumerate(strats, 1):
            tf, r, l, off, sl, tp, be, sv = p
            for nm, want in (('s%dOn' % i, i in g['strats']), ('s%dTf' % i, TFV[tf]), ('s%dR' % i, r), ('s%dL' % i, l), ('s%dOff' % i, off), ('s%dSl' % i, sl),
                             ('s%dTp' % i, tp), ('s%dBe' % i, be), ('s%dSv' % i, sv)):
                gg, alt, ex = eff[nm]; assert gg == 'PC' and alt == nm + 'In'
                v = ev(ex, env, {}); n += 1
                if (abs(v - want) > 1e-12 if isinstance(want, float) else v != want): bad += 1; print('  GRID %s %s: %r want %r' % (g['key'], nm, v, want))
        # identifiers (E_STOP, RUN_TCK, SZ_USD, CAP_*, L_*) are compared by name; literals by value
        for nm, want in (('entMode', 'E_STOP'), ('expN', 0), ('maxDay', 0), ('trA', 0.0), ('trD', 0.0), ('tExitH', 0.0), ('trnOn', False), ('runMode', 'RUN_TCK')):
            v = ev(eff[nm][2], env, {}); n += 1
            if v != want: bad += 1; print('  GRID %s %s %r' % (g['key'], nm, v))
        for nm, want in (('baseR', g['base']), ('capOn', g['cap'] is not None), ('hardCap', g['cap'] or 500.0), ('capAction', g['act']), ('recMode', g['rec']),
                         ('ladMode', 'Off'), ('mRestart', True), ('szMode', 'SZ_USD')):
            gg, alt, ex = eff[nm]; assert gg == 'PM', nm
            v = ev(ex, env, {}); v = cmap.get(v, v) if nm in ('capAction', 'recMode') else v; n += 1
            if v != want: bad += 1; print('  GRID %s %s %r want %r' % (g['key'], nm, v, want))
    custom = all(alt == name + 'In' for name, (gg, alt, ex) in eff.items() if gg in ('PC', 'PM'))
    print('%s: %d preset values checked, %d wrong; Custom = the inputs: %s' % (path.split('/')[-1], n, bad, custom))
    return bad + (not custom)


if __name__ == '__main__':
    b = check_ars(R + 'Auction_Retest_Strategy.pine') + check_ars(R + 'Auction_Retest_Model.pine')
    b += check_grid(R + 'Fractal_Breakout_Grid.pine') + check_grid(R + 'Fractal_Breakout_Grid_Strategy.pine')
    print('PINE PRESETS: %s' % ('ALL CORRECT' if b == 0 else '%d problems' % b))
