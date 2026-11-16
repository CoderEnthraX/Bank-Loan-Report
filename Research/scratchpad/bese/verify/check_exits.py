"""Independent check of the BE/salvage exit rules in SPEC_BE.md against bese/ref_gbe.run trades. Usage: python3 check_exits.py [tf idx ...]"""
import sys, os, time
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
for d in ('/bese', '/gold', '/build'): sys.path.insert(0, S + d)
PROG = S + '/bese/verify/progress.md'
CASES = [('M15', 1), ('M15', 6), ('H1', 1), ('M5', 1), ('M5', 2)]
TRIG = [('be0.3', dict(beOn=True, beR=0.3)), ('sv0.5', dict(svOn=True, svR=0.5)),
        ('be0.3+sv0.5', dict(beOn=True, beR=0.3, svOn=True, svR=0.5)), ('be1.0+sv0.8', dict(beOn=True, beR=1.0, svOn=True, svR=0.8))]

def sim(p, mt, O, H, L, C, tr):
    """independent trade manager: returns (exit candle or None, res, trigger kind)"""
    d = tr['dir']; fill = tr['fill']; ent = tr['entry']; stp = tr['stop']; risk = d * (ent - stp)
    tol = 0.001 * mt
    tk = [ent + d * p['tp%dR' % k] * risk for k in (1, 2, 3, 4)]
    exitR = p['tp%dR' % p['exitAt']]
    tF = tk[p['exitAt'] - 1]
    cur = stp; kind = None; salv = False; seen = [False] * 3
    def touch_below(x, lvl): return x <= lvl + tol        # a low reaches lvl (long side down)
    def touch_above(x, lvl): return x >= lvl - tol
    # fill candle: initial stop only
    if (d > 0 and L[fill] <= stp + tol) or (d < 0 and H[fill] >= stp - tol):
        return fill, -1.0, None
    n = len(O)
    for i in range(fill + 1, n):
        sh = (L[i] <= cur + tol) if d > 0 else (H[i] >= cur - tol)
        if sh: return i, d * (cur - ent) / risk, kind
        th = (H[i] >= tF - tol) if d > 0 else (L[i] <= tF + tol)
        if th: return i, (0.0 if salv else exitR), kind
        # step 2: TP stop moves
        for k in range(3):
            if p.get('mv%dOn' % (k + 1)) and not seen[k]:
                lv = tk[k]
                if (H[i] >= lv - tol) if d > 0 else (L[i] <= lv + tol):
                    seen[k] = True
                    ns = ent + d * p['mv%dR' % (k + 1)] * risk
                    if (ns > cur) if d > 0 else (ns < cur): cur = ns
        # step 3: triggers
        if kind is None and (p.get('beOn') or p.get('svOn')):
            beL = ent + d * p['beR'] * risk; svL = ent - d * p['svR'] * risk
            be = bool(p.get('beOn')) and ((H[i] >= beL - tol) if d > 0 else (L[i] <= beL + tol))
            sv = bool(p.get('svOn')) and ((L[i] <= svL + tol) if d > 0 else (H[i] >= svL - tol))
            if be and sv:
                hi_first = abs(H[i] - O[i]) < abs(O[i] - L[i])
                be_first = hi_first if d > 0 else (not hi_first)
                be, sv = (True, False) if be_first else (False, True)
            if be:
                kind = 'be'
                if (ent > cur) if d > 0 else (ent < cur): cur = ent
            elif sv:
                kind = 'sv'; salv = True; tF = ent
    return None, None, kind

def main():
    import geng, ref_gbe, crooks
    from ref_gbe import IN
    ref_gbe.eprep = geng.ref_g.eprep
    done = set()
    if os.path.exists(PROG):
        for ln in open(PROG):
            if ln.startswith('|'): done.add(tuple(c.strip() for c in ln.split('|')[1:3]))
    args = sys.argv[1:]
    cases = [(args[i], int(args[i + 1])) for i in range(0, len(args), 2)] if args else CASES
    for tf, idx in cases:
        cfg0 = dict(crooks.sources(tf)[idx]['cfg']); cfg0.pop('p1', None)
        vw = cfg0.pop('vwAnchorG', 'session'); src = cfg0.pop('vwSrcG', 'hlc3')
        P = geng.prepare(tf, vw, src); geng._CUR['vw'] = vw; geng._CUR['src'] = src
        O, H, L, C = P['O'], P['H'], P['L'], P['C']; mt = P['mt']
        for name, tset in TRIG:
            cname = '%s-%d' % (tf, idx)
            if (cname, name) in done: print('skip', cname, name); continue
            o = dict(cfg0); o.update(tset)
            p = dict(IN); p.update(o)
            t0 = time.time()
            trades = [x for x in ref_gbe.run(tf, o) if not x['ghost'] and x['exit'] is not None]
            mism = []; ntrig = {'be': 0, 'sv': 0, None: 0}
            for x in trades:
                ex, res, kind = sim(p, mt, O, H, L, C, x)
                ntrig[kind] += 1
                ok = ex == x['exit'] and res is not None and abs(res - x['res']) <= 1e-9 and kind == x.get('trig')
                if not ok: mism.append((x, ex, res, kind))
            line = '| %s | %s | trades=%d | mismatches=%d | be=%d sv=%d none=%d | %.0fs |\n' % (cname, name, len(trades), len(mism), ntrig['be'], ntrig['sv'], ntrig[None], time.time() - t0)
            open(PROG, 'a').write(line); print(line, end='')
            for x, ex, res, kind in mism[:3]:
                f = x['fill']; lo = min(x['exit'], ex if ex is not None else x['exit'])
                print('  MISMATCH dir=%d fill=%d entry=%.2f stop=%.2f | engine exit=%s res=%s trig=%s | mine exit=%s res=%s kind=%s' % (x['dir'], f, x['entry'], x['stop'], x['exit'], x['res'], x.get('trig'), ex, res, kind))
                for j in range(f, min(lo + 2, f + 8)): print('    c%d O=%.2f H=%.2f L=%.2f C=%.2f' % (j, O[j], H[j], L[j], C[j]))
if __name__ == '__main__': main()
