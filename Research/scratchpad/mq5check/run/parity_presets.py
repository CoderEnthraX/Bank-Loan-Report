"""v4.8 presets: the EA engine (compiled harness, InpPreset = k, every other input at the EA's own defaults) vs the research engine
(gold/ref_gs.py, the engine the catalogue was found with) given the preset's values from presets/preset_data.py, trade for trade, on the
parity symbols. ref_gs gets the VWAP anchor (session / month) and equal weights like the harness (no volume). Variants:
  'as tested'          the preset alone (the EA's own defaults have days, hours, kill zones and news on: all must be ignored)
  'user GMT 0'         the same with "Your time zone" GMT+0: the preset's hours stay Indian times
  'add: my hours+kz'   Add my filters on, the EA defaults (Tue-Thu, 06:00-23:00, Asia/London/NY kill zones following summer time) replace its session
  'add: days only'     Add my filters on, my hours and kill zones off: Tue-Thu + the preset's own session
  'wrong chart'        the chart on another timeframe: no trade at all
Run: python3 -I parity_presets.py [SYM ...]"""
import sys, os, datetime, calendar
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/mq5check/run'); sys.path.insert(0, S + '/gold'); sys.path.insert(0, S + '/presets')
import parity as PA
import ref_gs
import preset_data as PD
from multiprocessing import Pool

PRE = PD.ars_presets()
TFN = {'M1': 1, 'M5': 5, 'M15': 15, 'H1': 16385}
OTHER = {'M1': 5, 'M5': 15, 'M15': 5, 'H1': 15}
USER_TIME = dict(dayOn=True, days=(False, True, True, True, False, False, False), hoursOn=True, hoursSess=(600, 2300),
                 kzOn=True, kz=(True, True, True, False), kzAuto=True, kzShift=0)      # the EA's own defaults (v4.0)


def variants(p):
    v = {k: x for k, x in p['v'].items() if k not in PD.RESEARCH_ONLY and k != 'p1'}
    k = PRE.index(p) + 1; per = TFN[p['tf']]
    own = {kk: v[kk] for kk in ('hoursOn', 'hoursSess', 'kzOn', 'kz', 'kzAuto', 'kzShift')}
    return [('as tested', v, dict(InpPreset=k, PERIOD=per)),
            ('user GMT 0', v, dict(InpPreset=k, PERIOD=per, InpUserGMT=0.0)),
            ('add: my hours+kz', dict(v, **USER_TIME), dict(InpPreset=k, PERIOD=per, InpAddMine=1)),
            ('add: days only', dict(v, dayOn=True, days=USER_TIME['days'], **own), dict(InpPreset=k, PERIOD=per, InpAddMine=1, InpHoursOn=0, InpKzOn=0)),
            ('wrong chart', None, dict(InpPreset=k, PERIOD=OTHER[p['tf']]))]


def prep_gs(P, srv, look, anchor):
    """ref_gs input from the parity rows (bars look .. n-2, as the harness processes them): IST times, server-day sessions, the anchor, equal weights"""
    rows = P['rows']; n = len(rows)
    sl = rows[look:n - 1]; ssrv = srv[look:n - 1]
    sd = [datetime.datetime.fromtimestamp(x, datetime.timezone.utc).replace(tzinfo=None) for x in ssrv]
    ds = [i == 0 or sd[i].date() != sd[i - 1].date() for i in range(len(sl))]
    an = ds if anchor == 'session' else [i == 0 or (ds[i] and (sd[i].year, sd[i].month) != (sd[i - 1].year, sd[i - 1].month)) for i in range(len(sl))] if anchor == 'month' \
        else [i == 0 or (ds[i] and sd[i].isocalendar()[:2] != sd[i - 1].isocalendar()[:2]) for i in range(len(sl))]
    O = [r['o'] for r in sl]; H = [r['h'] for r in sl]; L = [r['l'] for r in sl]; C = [r['c'] for r in sl]
    V = []; cpv = cw = 0.0
    for i in range(len(sl)):
        if an[i]: cpv = cw = 0.0
        cpv += (H[i] + L[i] + C[i]) / 3.0; cw += 1.0; V.append(cpv / cw)
    tr = [H[0] - L[0]] + [max(H[i] - L[i], abs(H[i] - C[i - 1]), abs(L[i] - C[i - 1])) for i in range(1, len(sl))]
    T = [datetime.datetime.strptime(r['t'], '%Y-%m-%d %H:%M') for r in sl]
    return dict(O=O, H=H, L=L, C=C, V=V, W=[1.0] * len(sl), T=T, tr=tr, daystart=ds, anch=an, mt=P['mt'])


def work(sym):
    P, path, srv = PA.prep_sym(sym)
    res = []
    for p in PRE:
        v = p['v']
        look = max(v['structLen'], v['brkLen'] + 1, v['momLen'] + 1, v['stopLen']) + 2
        G = prep_gs(P, srv, look, v['vwAnchorG'])
        ref_gs.eprep = lambda s, G=G: G
        for name, ro, ea in variants(p):
            eat, eas = PA.run_ea(path, P['mt'], ea)
            if ro is None:
                res.append((p['key'], name, 0, len(eat), 0 if eat else 0, [] if not eat else [(0, eat[0], None)])); continue
            shown = [x for x in ref_gs.run(sym, ro) if not x['ghost']]
            diffs = []
            for i in range(max(len(eat), len(shown))):
                a = eat[i] if i < len(eat) else None; b = shown[i] if i < len(shown) else None
                if a is None or b is None or not PA.same_trade(a, b): diffs.append((i, a, b))
            res.append((p['key'], name, len(shown), len(eat), max(len(eat), len(shown)) - len(diffs), diffs[:2]))
    return sym, res


if __name__ == '__main__':
    syms = sys.argv[1:] or PA.SYMS
    with Pool(min(len(syms), os.cpu_count() or 2)) as pool:
        out = dict(pool.map(work, syms))
    rows = {}
    for sym in syms:
        for key, name, nr, ne, idn, d in out[sym]:
            a = rows.setdefault((key, name), [0, 0, 0, []]); a[0] += nr; a[1] += ne; a[2] += idn
            if d: a[3].append((sym, d))
    bad = 0
    print('%-8s %-18s %7s %7s %9s' % ('preset', 'variant', 'ref', 'EA', 'identical'))
    for (key, name), (nr, ne, idn, d) in rows.items():
        ok = (nr == ne == idn) and not d
        bad += not ok
        print('%-8s %-18s %7d %7d %9d %s' % (key, name, nr, ne, idn, '' if ok else 'DIFFER ' + ','.join(s for s, _ in d)))
    for (key, name), (nr, ne, idn, d) in rows.items():
        for sym, dd in d[:2]:
            for i, a, b in dd: print('DIFF %s / %s / %s trade#%d\n   EA : %s\n   ref: %s' % (key, name, sym, i, a, b))
    print('ALL IDENTICAL' if not bad else '%d preset variants differ' % bad)
