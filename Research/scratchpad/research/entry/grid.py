"""python3 -I grid.py FAMILY -> compact TRAIN/TEST lines per variant (appended to progress.md); selection is done on TRAIN only."""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ev, lib
F = {}
F['A_deep_atrstop'] = ([(f'candle{f}', dict(entryMode='candle', entryFib=f)) for f in (0.382, 0.5, 0.618, 0.786)] +
    [(f'candle{f}_deepOnly', dict(entryMode='candle', entryFib=f, deepOnly=True)) for f in (0.382, 0.5, 0.618, 0.786)] +
    [(f'leg{f}_L{n}_deepOnly', dict(entryMode='leg', entryFib=f, legLen=n, deepOnly=True)) for n in (10, 20) for f in (0.382, 0.5, 0.618, 0.786)] +
    [('vwap', dict(entryMode='vwap')), ('vwapLive', dict(entryMode='vwapLive'))] +
    [(f'atr{f}_deepOnly', dict(entryMode='atr', entryFib=f, deepOnly=True)) for f in (0.25, 0.5, 0.75, 1.0)])
F['B_deep_structstop'] = ([(f'candle{f}_basePx', dict(entryMode='candle', entryFib=f, deepOnly=True, stopMode='basePx', stopMinAtr=0.5)) for f in (0.382, 0.5, 0.618, 0.786)] +
    [(f'leg{f}_basePx', dict(entryMode='leg', entryFib=f, deepOnly=True, stopMode='basePx', stopMinAtr=0.5)) for f in (0.382, 0.5, 0.618)] +
    [(f'candle{f}_cstop{b}', dict(entryMode='candle', entryFib=f, deepOnly=True, stopMode='candle', stopBuf=b, stopMinAtr=0.5)) for f in (0.5, 0.618) for b in (0.0, 0.3, 0.6)] +
    [(f'leg{f}_lstop{b}', dict(entryMode='leg', entryFib=f, deepOnly=True, stopMode='leg', stopBuf=b, stopMinAtr=0.5)) for f in (0.382, 0.5, 0.618) for b in (0.0, 0.3)] +
    [(f'base_cstop{b}', dict(stopMode='candle', stopBuf=b, stopMinAtr=0.5)) for b in (0.0, 0.3, 0.6)] +
    [(f'base_lstop{b}', dict(stopMode='leg', stopBuf=b, stopMinAtr=0.5)) for b in (0.0, 0.3)])
F['C_window'] = ([(f'base_rb{r}', dict(retestBars=r)) for r in (3, 8, 12)] +
    [(f'candle{f}_rb{r}', dict(entryMode='candle', entryFib=f, deepOnly=True, retestBars=r)) for f in (0.5, 0.618) for r in (3, 8, 12)] +
    [(f'leg{f}_rb{r}', dict(entryMode='leg', entryFib=f, deepOnly=True, retestBars=r)) for f in (0.382, 0.5) for r in (3, 8, 12)])
F['D_confirm'] = [(f'conf_{t}_{s}_cb{cb}', dict(confirm=True, confType=t, confStop=s, confBars=cb, stopBuf=0.1 if s == 'pull' else 0.0, stopMinAtr=0.5 if s == 'pull' else 0.0))
                  for t in ('bull', 'reclaim', 'both', 'brk') for s in ('pull', 'orig', 'atr') for cb in (2, 4)]
F['E_stopatr'] = ([(f'base_sa{k}', dict(stopAtr=k)) for k in (1.2, 1.5, 2.1, 2.4)] +
    [(f'candle0.5_sa{k}', dict(entryMode='candle', entryFib=0.5, deepOnly=True, stopAtr=k)) for k in (1.2, 1.5, 2.1, 2.4)] +
    [(f'leg0.382_sa{k}', dict(entryMode='leg', entryFib=0.382, deepOnly=True, stopAtr=k)) for k in (1.2, 1.5, 2.1, 2.4)])
F['F_manage'] = ([(f'be{r}', dict(beR=r)) for r in (1.0, 1.5)] + [('be1_off0.1', dict(beR=1.0, beOff=0.1))] +
    [('part1_50', dict(partR=1.0, partFrac=0.5)), ('part1_50_BE', dict(partR=1.0, partFrac=0.5, partBE=True)), ('part1.5_50_BE', dict(partR=1.5, partFrac=0.5, partBE=True))] +
    [(f'ts{n}_0.5', dict(tsBars=n, tsR=0.5)) for n in (3, 6, 10, 15, 20)] + [(f'ts{n}_0.3', dict(tsBars=n, tsR=0.3)) for n in (6, 10)])
def go(fam, extra=None):
    b = ev.base(); bn, be = lib.split(b); rows = []
    for name, o in F[fam] if extra is None else extra:
        tr = ev.aug(lib.run_all(ev.MOD, o)); tn, te = lib.split(tr)
        imp = sum(1 for s in lib.SYMS if [x for x in tr if x['sym'] == s] and ev.m([x for x in tr if x['sym'] == s], 'res') > ev.m([x for x in b if x['sym'] == s], 'res'))
        ln = f"- {fam}/{name} {json.dumps(o)} | ALL kept {len(tr)/len(b):.0%} tot {sum(x['res'] for x in tr):+.0f} syms+ {imp}/10 | TRAIN {ev.line(tn)} | TEST {ev.line(te)}"
        print(ln, flush=True); rows.append(ln)
    open(os.path.join(ev.HERE, 'progress.md'), 'a').write('\n'.join(rows) + '\n')
def _main():
    for fam in sys.argv[1:]: go(fam)
F['G_ext_hybrid'] = ([(f'ext_{r}{k}_candle{f}', dict(entryMode='candle', entryFib=f, deepOnly=True, extK=k, extRef=r)) for r in ('leg', 'vwap') for k in (1.5, 2.5, 3.5) for f in (0.5, 0.618)])
F['H_closestop'] = ([(f'cs{c}_b{nb}', dict(csR=c, csBars=nb)) for c in (0.5, 0.7) for nb in (0, 3)] + [(f'cs{c}_fill', dict(csR=c, csFill=True)) for c in (0.5, 0.7)])
F['I_be_more'] = ([(f'be{r}', dict(beR=r)) for r in (0.8, 1.25, 1.75)] + [('be1.5_off0.5', dict(beR=1.5, beOff=0.5)), ('be1.25_off0.25', dict(beR=1.25, beOff=0.25))])
if __name__ == '__main__' and False: pass

F['J_combo'] = [('rb3_be1', dict(retestBars=3, beR=1.0)), ('rb3_be1.25', dict(retestBars=3, beR=1.25)), ('extvwap2.5_c0.5_be1', dict(entryMode='candle', entryFib=0.5, deepOnly=True, extK=2.5, extRef='vwap', beR=1.0)),
                ('tp1.0', dict(tp4R=1.0)), ('tp1.5', dict(tp4R=1.5)), ('tp1.5_be1', dict(tp4R=1.5, beR=1.0))]
F['K_rb_nbhd'] = [('rb2', dict(retestBars=2)), ('rb4', dict(retestBars=4)), ('rb2_be1', dict(retestBars=2, beR=1.0)), ('rb4_be1', dict(retestBars=4, beR=1.0)), ('rb3_be1.25', dict(retestBars=3, beR=1.25)), ('rb3_be1.5', dict(retestBars=3, beR=1.5))]
if __name__ == '__main__': _main()
