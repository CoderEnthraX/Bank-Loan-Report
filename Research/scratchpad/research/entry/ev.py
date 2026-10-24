"""Driver: python3 -I ev.py NAME '<json opts>' [nolog] -> one summary line vs baseline (appended to progress.md)."""
import sys, json, os
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/research')
import lib
HERE = os.path.dirname(os.path.abspath(__file__)); MOD = os.path.join(HERE, 'combo_entry.py')
_base = None
def aug(tr):
    for x in tr:
        x['e1'] = 1.0 if x['hit1'] else -1.0; x['e15'] = 1.5 if x['hit15'] else -1.0; x['eatr'] = x['res'] * x['R'] / x['atr']; x['riskA'] = x['R'] / x['atr']
    return tr
def base():
    global _base
    if _base is None: _base = aug(lib.run_all(MOD, {}))
    return _base
def m(tr, k): return sum(x[k] for x in tr) / len(tr) if tr else float('nan')
def line(tr):
    s = lib.stats(tr)
    if not s['n']: return 'n=0'
    return (f"n={s['n']} h1 {s['hit1']:.1%} h15 {s['hit15']:.1%} h2 {s['hit2']:.1%} E1 {s['E1']:+.3f} E15 {s['E15']:+.3f} E2 {s['E2']:+.3f} "
            f"tot {s['totR2']:+.0f} PF {s['PF2']:.2f} Eatr {m(tr,'eatr'):+.3f} riskA {m(tr,'riskA'):.2f}")
def evaluate(name, opts, log=True, quiet=False):
    b = base(); tr = aug(lib.run_all(MOD, opts)); tn, te = lib.split(tr); bn, be = lib.split(b)
    imp = impA = 0; per = []
    for s in lib.SYMS:
        a = [x for x in b if x['sym'] == s]; c = [x for x in tr if x['sym'] == s]
        if c and m(c, 'res') > m(a, 'res'): imp += 1
        if c and m(c, 'eatr') > m(a, 'eatr'): impA += 1
        per.append(f"{s}:{m(c,'res'):+.2f}/{len(c)}" if c else f"{s}:-")
    ci2 = lib.boot_diff(be, te, 'res'); ci1 = lib.boot_diff(be, te, 'e1'); ci15 = lib.boot_diff(be, te, 'e15'); cia = lib.boot_diff(be, te, 'eatr')
    out = (f"- {name}: opts={json.dumps(opts)}\n    ALL {line(tr)} kept {len(tr)/len(b):.0%} | syms improved E2 {imp}/10, Eatr {impA}/10\n"
           f"    TRAIN {line(tn)}\n    TEST  {line(te)}\n"
           f"    TEST diff E2 {m(te,'res')-m(be,'res'):+.3f} CI[{ci2[0]:+.3f},{ci2[1]:+.3f}] E1 {m(te,'e1')-m(be,'e1'):+.3f} CI[{ci1[0]:+.3f},{ci1[1]:+.3f}] "
           f"E15 {m(te,'e15')-m(be,'e15'):+.3f} CI[{ci15[0]:+.3f},{ci15[1]:+.3f}] Eatr {m(te,'eatr')-m(be,'eatr'):+.3f} CI[{cia[0]:+.3f},{cia[1]:+.3f}]\n"
           f"    per-sym E2/n: {' '.join(per)}\n")
    if not quiet: print(out, end='')
    if log: open(os.path.join(HERE, 'progress.md'), 'a').write(out)
    return tr, tn, te
def train_line(name, opts):
    tr = aug(lib.run_all(MOD, opts)); tn, te = lib.split(tr)
    return tr, tn
if __name__ == '__main__':
    evaluate(sys.argv[1], json.loads(sys.argv[2]), log='nolog' not in sys.argv[3:])
