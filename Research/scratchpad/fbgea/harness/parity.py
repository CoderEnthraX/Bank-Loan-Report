"""The EA's own rules (fbg_harness, compiled from the EA) vs the Python twin of the Pine code (pine_twin2.twin2) on gold 1-minute bars
2021-2026, trade for trade: entry time and price, exit time and price, reason, $ risk; all 12 strategies. Usage: parity.py SEED N (N random
option / money sets after the defaults; SEED 0 N 0 = defaults only)"""
import sys, os, subprocess, math, numpy as np
FR = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fractal'
sys.path.insert(0, FR)
import engine as EN, pine_twin2 as TW
from final11 import ALL12
HERE = os.path.dirname(os.path.abspath(__file__))
B = EN.load()
for k in ('t', 'O', 'H', 'L', 'C'): B['M1_' + k] = B[k]
TFS = ','.join(p[0] for p in ALL12)
REC = {m: i for i, m in enumerate(TW.MODES)}
TZ = {'Asia/Kolkata': 5.5, 'UTC': 0.0}
CAP = {'clamp': 0, 'stop': 1, 'reset': 2}
LADN = {'Off': 0, 'Low': 1, 'Medium': 2, 'High': 3, 'Extra high': 4, 'Max': 5}
PRN = {'off': 0, 'forget': 1, 'pct': 2, 'wait': 3}
TFN = {'M1': 1, 'M5': 5, 'M15': 15, 'H1': 16385, 'H4': 16388, 'D1': 16408}


def ea_args(kw):
    p = TW.P(**kw)
    a = ['InpServerTz=0', 'InpUserGMT=%r' % TZ[p.tz], 'InpSpread=0.16', 'InpCommLot=7', 'InpEntry=%d' % (1 if p.entClose else 0), 'InpExpN=%d' % p.expN,
         'InpMaxDay=%d' % p.maxDay, 'InpTrA=%r' % p.trA, 'InpTrD=%r' % p.trD, 'InpTExitH=%r' % p.tExitH, 'InpWkOn=%d' % (1 if p.wkOn else 0), 'InpWkH=%d' % p.wkH,
         'InpTrnOn=%d' % (1 if p.trnOn else 0), 'InpTrnLen=%d' % p.trnLen, 'InpDayOn=%d' % (1 if p.dayOn else 0),
         'InpMon=%d' % p.days[0], 'InpTue=%d' % p.days[1], 'InpWed=%d' % p.days[2], 'InpThu=%d' % p.days[3], 'InpFri=%d' % p.days[4], 'InpSat=%d' % p.days[5], 'InpSun=%d' % p.days[6],
         'InpHoursOn=%d' % (1 if p.hoursOn else 0), 'InpHourFrom=%d' % ((p.sess[0] // 60) * 100 + p.sess[0] % 60), 'InpHourTo=%d' % ((p.sess[1] // 60) * 100 + p.sess[1] % 60),
         'InpStartB=%r' % p.startB, 'InpSizeMode=%d' % {'usd': 0, 'lot': 1, 'pct': 2}[p.szMode], 'InpBaseRisk=%r' % p.baseR, 'InpBaseLots=%r' % p.baseLot, 'InpEqPct=%r' % p.eqPct,
         'InpLev=%r' % p.levIn, 'InpCapOn=%d' % (1 if p.capOn else 0), 'InpHardCap=%r' % p.hardCap, 'InpCapAction=%d' % CAP[p.capAction], 'InpRec=%d' % p.recMode,
         'InpRecN=%d' % p.recN, 'InpRecPct=%r' % p.recPct, 'InpRecMult=%r' % p.recMult, 'InpRecStep=%r' % p.recStep, 'InpCSplit=%d' % p.cSplit, 'InpParN=%d' % p.parN,
         'InpDelayN=%d' % p.delayN, 'InpCrkCn=%d' % p.crkCn, 'InpCrkPr=%d' % PRN[p.crkPr], 'InpCrkPrN=%d' % p.crkPrN, 'InpCrkPrPct=%r' % p.crkPrPct, 'InpCrkPrM=%d' % p.crkPrM,
         'InpCrkELot=%r' % p.crkELot, 'InpCrkFK=%r' % p.crkFK, 'InpCrkGX=%r' % p.crkGX, 'InpCrkHPct=%r' % p.crkHPct, 'InpCrkJX=%r' % p.crkJX,
         'InpLadder=%d' % LADN[p.lad], 'InpLadT=%r' % p.ladT]
    if p.trnOn: a += ['InpTrnTf=%d' % TFN[p.trnTf], 'TREND=' + p.trnTf]
    return a


def run_ea(kw):
    out = subprocess.run([HERE + '/fbg_harness', HERE + '/data', TFS] + ea_args(kw), capture_output=True, text=True, check=True).stdout.split('\n')
    tr = {k: [] for k in range(1, 13)}
    for l in out:
        if l.startswith('T '):
            f = l.split(); tr[int(f[1])].append((int(f[2]), float(f[3]), int(f[4]), float(f[5]), int(f[6]), float(f[7])))
    return tr


def compare(kw, label, show=3):
    p = TW.P(**kw); ea = run_ea(kw); bad = 0; ntr = 0; worstR = 0.0
    t = B['t']
    for k, prm in enumerate(ALL12):
        s = TW.twin2(B, 'M1', prm, p)
        tw = [(int(t[a[0]]), a[1], int(t[a[2]]), a[3], a[4]) for a in s.trades]
        e = ea[k + 1]; n = min(len(tw), len(e)); ntr += n
        diff = None
        for i in range(n):
            a = tw[i]; b = e[i]
            if a[0] != b[0] or a[2] != b[2] or a[4] != b[4] or abs(a[1] - b[1]) > 1e-6 or abs(a[3] - b[3]) > 1e-6: diff = ('trade', i, a, b[:5]); break
            if i < len(s.risks):
                rr = abs(s.risks[i] - b[5]) / max(1.0, abs(s.risks[i])); worstR = max(worstR, rr)
                if rr > 1e-9: diff = ('risk', i, s.risks[i], b[5]); break
        if diff is None and len(tw) != len(e): diff = ('count', len(tw), len(e))
        if diff is not None:
            bad += 1
            if bad <= show: print('  MISMATCH %s S%d: %s' % (label, k + 1, diff))
    print('%-28s strategies 12, trades compared %6d, mismatching strategies %d, worst $ risk difference %.1e' % (label, ntr, bad, worstR))
    return bad


def random_kw(rng):
    kw = dict(tz=str(rng.choice(['Asia/Kolkata', 'UTC'])))
    if rng.random() < 0.3: kw['entClose'] = True
    if rng.random() < 0.4: kw['expN'] = int(rng.choice([2, 5, 12, 30]))
    if rng.random() < 0.4: kw['maxDay'] = int(rng.choice([1, 2]))
    if rng.random() < 0.4: kw['trA'] = float(rng.choice([0.0, 0.5])); kw['trD'] = float(rng.choice([0.3, 1.0]))
    if rng.random() < 0.4: kw['tExitH'] = float(rng.choice([4.0, 24.0, 72.0]))
    if rng.random() < 0.4: kw['wkOn'] = True; kw['wkH'] = int(rng.choice([10, 16]))
    if rng.random() < 0.4: kw['trnOn'] = True; kw['trnTf'] = str(rng.choice(['H1', 'H4', 'D1'])); kw['trnLen'] = int(rng.choice([20, 50]))
    if rng.random() < 0.4: kw['dayOn'] = True; kw['days'] = tuple(bool(x) for x in rng.random(7) < 0.7)
    if rng.random() < 0.4: kw['hoursOn'] = True; kw['sess'] = tuple(int(x) for x in rng.choice([(360, 1380), (120, 1020), (1200, 300)]))
    kw['recMode'] = int(rng.integers(28)); kw['capAction'] = str(rng.choice(['clamp', 'reset', 'stop'])); kw['capOn'] = bool(rng.random() < 0.7)
    kw['hardCap'] = float(rng.choice([250.0, 500.0, 1000.0])); kw['lad'] = str(rng.choice(list(LADN))); kw['ladT'] = float(rng.choice([300.0, 1000.0]))
    kw['szMode'] = str(rng.choice(['usd', 'lot', 'pct'])); kw['baseLot'] = float(rng.choice([0.01, 0.05, 0.2])); kw['eqPct'] = float(rng.choice([0.5, 1.0, 2.0]))
    kw['baseR'] = float(rng.choice([25.0, 50.0, 100.0])); kw['startB'] = float(rng.choice([10000.0, 2000.0]))
    kw['crkCn'] = int(rng.choice([1, 1, 2])); kw['crkPr'] = str(rng.choice(['off', 'off', 'forget', 'pct', 'wait'])); kw['crkPrN'] = int(rng.choice([1, 2, 3]))
    kw['crkFK'] = float(rng.choice([2.0, 3.0])); kw['crkGX'] = float(rng.choice([5.0, 10.0])); kw['crkJX'] = float(rng.choice([10.0, 20.0])); kw['levIn'] = float(rng.choice([100.0, 30.0]))
    return kw


if __name__ == '__main__':
    seed, N = int(sys.argv[1]), int(sys.argv[2])
    bad = compare({}, 'defaults')
    rng = np.random.default_rng(seed)
    for it in range(N):
        kw = random_kw(rng)
        bad += compare(kw, 'random set %d' % (it + 1)) > 0
    print('PARITY: %s' % ('ALL IDENTICAL' if bad == 0 else '%d sets with mismatches' % bad))
