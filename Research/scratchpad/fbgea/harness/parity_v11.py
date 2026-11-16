"""Grid EA v1.1 vs the Python twin (pine_twin2 with the v3.2 monthly restart), trade for trade and $ risk, all 12 strategies, gold M1 2021-2026:
  custom: the defaults (= v1.0); the monthly restart on (defaults money, and random money / option sets);
  presets G1-G6 with random settings in every other input (the EA must ignore them; kept: time zone, weekend close, start balance, leverage);
  a preset with Add my days and hours, and with Use my money settings (random money, restart on / off).
Usage: parity_v11.py [SEED] (runs the configurations in 4 processes)"""
import sys, os
from multiprocessing import Pool
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/presets')
import parity as PA, numpy as np, subprocess
import preset_data as PD
TW = PA.TW; B = PA.B; ALL12 = PA.ALL12
KEEP = ('tz', 'wkOn', 'wkH', 'startB', 'levIn')
OPT_TESTED = dict(entClose=False, expN=0, maxDay=0, trA=0.0, trD=0.0, tExitH=0.0, trnOn=False)
MONEY = ('recMode', 'capAction', 'capOn', 'hardCap', 'lad', 'ladT', 'szMode', 'baseLot', 'eqPct', 'baseR', 'crkCn', 'crkPr', 'crkPrN', 'crkFK', 'crkGX', 'crkJX', 'mRestart')


def run(ea_kw, extra, twin_kw, strats, label):
    args = PA.ea_args(ea_kw) + ['InpMRestart=%d' % (1 if TW.P(**ea_kw).mRestart else 0)] + extra
    out = subprocess.run([H + '/fbg_harness', H + '/data', PA.TFS] + args, capture_output=True, text=True, check=True).stdout.split('\n')
    ea = {k: [] for k in range(1, 13)}
    for l in out:
        if l.startswith('T '):
            f = l.split(); ea[int(f[1])].append((int(f[2]), float(f[3]), int(f[4]), float(f[5]), int(f[6]), float(f[7])))
    p = TW.P(**twin_kw); bad = 0; ntr = 0; worst = 0.0; msgs = []; t = B['t']
    for k, prm in enumerate(ALL12):
        e = ea[k + 1]
        if (k + 1) not in strats:
            if e: bad += 1; msgs.append('S%d should not trade (%d trades)' % (k + 1, len(e)))
            continue
        s = TW.twin2(B, 'M1', prm, p)
        tw = [(int(t[a[0]]), a[1], int(t[a[2]]), a[3], a[4]) for a in s.trades]
        n = min(len(tw), len(e)); ntr += n; diff = None
        for i in range(n):
            a = tw[i]; b = e[i]
            if a[0] != b[0] or a[2] != b[2] or a[4] != b[4] or abs(a[1] - b[1]) > 1e-6 or abs(a[3] - b[3]) > 1e-6: diff = ('trade', i, a, b[:5]); break
            if i < len(s.risks):
                rr = abs(s.risks[i] - b[5]) / max(1.0, abs(s.risks[i])); worst = max(worst, rr)
                if rr > 1e-9: diff = ('risk', i, s.risks[i], b[5]); break
        if diff is None and len(tw) != len(e): diff = ('count', len(tw), len(e))
        if diff is not None: bad += 1; msgs.append('S%d %s' % (k + 1, diff))
    return '%-44s trades compared %6d, mismatching strategies %d, worst $ risk difference %.1e%s' % (label, ntr, bad, worst, ''.join('\n   ' + m for m in msgs[:3])), bad


def preset_twin(g, user, add=False, mine=False):
    kw = {k: user[k] for k in KEEP if k in user}
    kw.update(OPT_TESTED)
    if add: kw.update({k: user[k] for k in ('dayOn', 'days', 'hoursOn', 'sess') if k in user})
    if mine: kw.update({k: user[k] for k in MONEY if k in user})
    else:
        kw.update(recMode=TW.L_EXACT if g['rec'] == 'EXACT' else TW.L_OFF, baseR=g['base'], capOn=g['cap'] is not None, hardCap=g['cap'] or 500.0,
                  capAction=g['act'], lad='Off', mRestart=True, szMode='usd')
    return kw


def jobs(seed):
    rng = np.random.default_rng(seed); J = []
    J.append(({}, [], {}, range(1, 13), 'custom: defaults'))
    J.append((dict(mRestart=True), [], dict(mRestart=True), range(1, 13), 'custom: defaults + monthly restart'))
    for it in range(4):
        kw = PA.random_kw(rng); kw['mRestart'] = True; kw['startB'] = 1e6
        J.append((kw, [], kw, range(1, 13), 'custom: random set %d + monthly restart' % (it + 1)))
    for gi, g in enumerate(PD.GRID_PRESETS, 1):
        kw = PA.random_kw(rng); kw['mRestart'] = bool(rng.random() < 0.5)
        J.append((kw, ['InpPreset=%d' % gi], preset_twin(g, kw), g['strats'], 'preset %s (random other inputs)' % g['key']))
    g = PD.GRID_PRESETS[1]; kw = PA.random_kw(rng); kw.update(dayOn=True, days=(False, True, True, True, False, False, False), hoursOn=True, sess=(360, 1380))
    J.append((kw, ['InpPreset=2', 'InpAddMine=1'], preset_twin(g, kw, add=True), g['strats'], 'preset G2 + my days and hours'))
    for mr in (True, False):
        g = PD.GRID_PRESETS[0]; kw = PA.random_kw(rng); kw['mRestart'] = mr; kw['startB'] = 1e6
        J.append((kw, ['InpPreset=1', 'InpMyMoney=1'], preset_twin(g, kw, mine=True), g['strats'], 'preset G1 + my money (restart %s)' % ('on' if mr else 'off')))
    return J


def work(j): return run(*j)


if __name__ == '__main__':
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 21
    with Pool(4) as pool:
        bad = 0
        for txt, b in pool.imap(work, jobs(seed)):
            print(txt, flush=True); bad += b > 0
    print('PARITY v1.1: %s' % ('ALL IDENTICAL' if bad == 0 else '%d configurations with mismatches' % bad))
