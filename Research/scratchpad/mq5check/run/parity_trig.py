"""v4.9 BE / salvage triggers: the EA engine (compiled harness) vs the research engine bese/ref_gbe.py (checked independently against the
written rules), trade for trade, on the parity symbols. Cases: the v3.9 engine defaults (Custom, inputs given explicitly) with BE 0.3R,
salvage 0.5R, both, BE 1.5R + salvage 0.9R, and with the TP stop moves; presets (with their own stop moves / anchors) + triggers.
Run: python3 -I parity_trig.py [SYM ...]"""
import sys, os
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/mq5check/run'); sys.path.insert(0, S + '/bese'); sys.path.insert(0, S + '/gold'); sys.path.insert(0, S + '/presets')
import parity as PA, parity_presets as PP
import ref_gbe
import preset_data as PD
from multiprocessing import Pool

PRE = PD.ars_presets()
TRIG = [('BE 0.3', dict(beOn=True, beR=0.3), dict(InpBeOn=1, InpBeR=0.3)), ('salvage 0.5', dict(svOn=True, svR=0.5), dict(InpSvOn=1, InpSvR=0.5)),
        ('BE 0.3 + salvage 0.5', dict(beOn=True, beR=0.3, svOn=True, svR=0.5), dict(InpBeOn=1, InpBeR=0.3, InpSvOn=1, InpSvR=0.5)),
        ('BE 1.5 + salvage 0.9', dict(beOn=True, beR=1.5, svOn=True, svR=0.9), dict(InpBeOn=1, InpBeR=1.5, InpSvOn=1, InpSvR=0.9))]


def cases():
    C = []
    for nm, ro, ea in TRIG:
        C.append(('defaults + ' + nm, dict(ro), dict(PA.V39_EA, **ea), None))
        C.append(('defaults, TP2 stop to 0 + ' + nm, dict(ro, mv2On=True, mv2R=0.0), dict(PA.V39_EA, InpMv2On=1, InpMv2R=0, **ea), None))
    for key in ('M5-S1', 'M5-S2', 'M15-S1', 'M15-S8', 'H1-S1'):
        p = [x for x in PRE if x['key'] == key][0]; k = PRE.index(p) + 1
        for nm, ro, ea in TRIG[2:]:
            C.append((key + ' preset + ' + nm, ro, dict(InpPreset=k, PERIOD=PP.TFN[p['tf']], **ea), p))
    return C


def work(sym):
    P, path, srv = PA.prep_sym(sym)
    res = []
    for name, ro, ea, p in cases():
        v = dict(ref_gbe.IN) if p is None else {k: x for k, x in p['v'].items() if k not in PD.RESEARCH_ONLY and k != 'p1'}
        v.update(ro)
        look = max(v['structLen'], v['brkLen'] + 1, v['momLen'] + 1, v['stopLen']) + 2
        G = PP.prep_gs(P, srv, look, v.get('vwAnchorG', 'session'))
        ref_gbe.eprep = lambda s, G=G: G
        eat, eas = PA.run_ea(path, P['mt'], ea)
        shown = [x for x in ref_gbe.run(sym, {k: x for k, x in v.items() if k not in ('vwAnchorG', 'vwSrcG')}) if not x['ghost']]
        diffs = []
        for i in range(max(len(eat), len(shown))):
            a = eat[i] if i < len(eat) else None; b = shown[i] if i < len(shown) else None
            if a is None or b is None or not PA.same_trade(a, b): diffs.append((i, a, b))
        res.append((name, len(shown), len(eat), max(len(eat), len(shown)) - len(diffs), diffs[:2]))
    return sym, res


if __name__ == '__main__':
    syms = sys.argv[1:] or PA.SYMS
    with Pool(min(len(syms), os.cpu_count() or 2)) as pool:
        out = dict(pool.map(work, syms))
    rows = {}
    for sym in syms:
        for name, nr, ne, idn, d in out[sym]:
            a = rows.setdefault(name, [0, 0, 0, []]); a[0] += nr; a[1] += ne; a[2] += idn
            if d: a[3].append((sym, d))
    bad = 0
    for name, (nr, ne, idn, d) in rows.items():
        ok = nr == ne == idn and not d; bad += not ok
        print('%-44s ref %6d EA %6d identical %6d %s' % (name, nr, ne, idn, '' if ok else 'DIFFER ' + ','.join(s for s, _ in d)))
    for name, (nr, ne, idn, d) in rows.items():
        for sym, dd in d[:1]:
            for i, a, b in dd: print('DIFF %s / %s trade#%d\n   EA : %s\n   ref: %s' % (name, sym, i, a, b))
    print('ALL IDENTICAL' if not bad else '%d cases differ' % bad)
