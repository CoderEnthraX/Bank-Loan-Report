"""Stage A: every indicator setting, one at a time (all others default), on M1 / M5 / M15 / H1. Final exit TP4 (TP1-TP3 = reached before the stop)."""
import sys, pickle, multiprocessing as mp
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
C = [('default', {})]
def add(name, vals, key=None, fmt='%s'):
    for v in vals: C.append(('%s = %s' % (name, fmt % (v,)), {key or name: v}))
add('structLen', (6, 8, 12, 15, 20)); add('brkLen', (3, 4, 8, 10)); add('entryLen', (3, 4, 8, 10)); add('retestBars', (2, 3, 8, 12))
add('dispAtr', (0.5, 0.65, 1.0, 1.2)); add('dispBodyPct', (45.0, 50.0, 60.0, 70.0)); add('dispClosePct', (15.0, 20.0, 30.0, 35.0))
add('momLen', (5, 8, 15, 20)); add('momAtr', (0.0, 0.5, 1.2, 1.5)); add('cmoMin', (0.0, 10.0, 30.0, 40.0))
C.append(('Re-arm = replace with newer', dict(rearmKeep=False)))
C.append(('Stop mode = swing (6 bars + 0.22 ATR)', dict(stopMode='swing'))); C.append(('Stop mode = swing (10 bars + 0.22 ATR)', dict(stopMode='swing', stopLen=10)))
add('stopAtr', (1.2, 1.5, 2.2, 2.5, 3.0))
C.append(('Half stop = off', dict(halfStopOn=False))); add('halfStopAtr', (0.6, 1.2)); add('biasNet', (2, 4, 5)); add('impBodyPct', (40.0, 60.0))
C.append(('Half stop when opening outside prev range = off', dict(halfOpenOut=False))); C.append(('Strict bias check = on', dict(halfStrict=True)))
C.append(('Half stop never wider than normal = on', dict(halfCap=True)))
add('cooldownBars', (3, 6, 12)); add('maxFills', (1, 2, 3, 10)); add('dayStopR', (1.0, 2.0, 3.0))
C.append(('Count fill-bar stops in daily stop = on', dict(fillBarStopR=True, dayStopR=2.0)))
C.append(('Re-anchor breakout after a trade = off', dict(legReset=False))); add('atrLen', (7, 21, 30))
C.append(('Longs above VWAP / shorts below = off', dict(vwapFilter=False))); add('slopeBars', (0, 1, 2, 5, 10))
C.append(('Slope across session start = off', dict(slopeCross=False))); add('minOpenBars', (3, 6, 12))
C.append(('Skip Sunday = off', dict(skipSunday=False))); C.append(('Deep pullback signal = on', dict(deepOn=True)))
C.append(('Longs only', dict(allowShort=False))); C.append(('Shorts only', dict(allowLong=False)))
for a in ('week', 'month'): C.append(('VWAP anchor = %s' % a, dict(vwAnchorG=a)))
for s in ('close', 'hl2', 'ohlc4'): C.append(('VWAP source = %s' % s, dict(vwSrcG=s)))
for pc in (30.0, 50.0, 70.0): C.append(('Entry = %d%% of signal candle' % pc, dict(entryMode='pct', entryPct=pc)))
C.append(('Entry = market (next bar)', dict(entryMode='market')))
for t4 in (1.5, 2.5, 3.0): C.append(('TP4 = %.1fR' % t4, dict(tp4R=t4)))
for k in (1, 2, 3): C.append(('Final exit at TP%d' % k, dict(exitAt=k)))
C.append(('Stop to breakeven at TP1', dict(mv1On=True, mv1R=0.0))); C.append(('Stop to breakeven at TP2', dict(mv2On=True, mv2R=0.0)))
C.append(('Stop to +0.6R at TP2', dict(mv2On=True, mv2R=0.6))); C.append(('Stop to +1R at TP3', dict(mv3On=True, mv3R=1.0)))
C.append(('BE at TP1, +0.6R at TP2, +1R at TP3', dict(mv1On=True, mv1R=0.0, mv2On=True, mv2R=0.6, mv3On=True, mv3R=1.0)))
for s in (1.5, 2.0, 2.4, 3.0): C.append(("Don't Chase = %.1f sigma" % s, dict(noChase=True, noChaseSig=s)))
C.append(('After a loss no same-direction trade = on', dict(lossBlock=True)))
for m in (8.0, 12.0, 16.0): C.append(('Choppy sessions max crosses = %d' % m, dict(chopOn=True, chopMax=m)))
for m in (1.2, 1.65, 2.0): C.append(('1h EMA20 speed cap = %.2f' % m, dict(emaOn=True, emaMax=m)))
for m in (0.5, 1.0, 1.5): C.append(('Min distance from VWAP = %.1f ATR' % m, dict(minVwOn=True, minVwAtr=m)))
for k, dn in enumerate(('Mon', 'Tue', 'Wed', 'Thu', 'Fri')):
    days = [True] * 7; days[k] = False; C.append(('Days: no %s' % dn, dict(dayOn=True, days=tuple(days))))
for (a, b), lab in (((1230, 1630), 'London 12:30-16:30 IST'), ((1830, 2230), 'New York 18:30-22:30 IST'), ((1230, 2230), 'London+NY 12:30-22:30 IST'),
                    ((430, 1230), 'Asia 04:30-12:30 IST'), ((1230, 230), 'Europe+US 12:30-02:30 IST')):
    C.append(('Hours: ' + lab, dict(hoursOn=True, hoursSess=(a, b))))
KZN = ('Asia', 'London', 'New York', 'London close')
for mask in ((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1), (0, 1, 1, 0), (0, 1, 1, 1), (1, 1, 1, 0), (1, 1, 1, 1), (1, 0, 1, 0), (1, 1, 0, 0)):
    C.append(('Kill zones: ' + '+'.join(n for n, m in zip(KZN, mask) if m), dict(kzOn=True, kz=tuple(bool(m) for m in mask))))
for sh in (-1, 1):
    C.append(('Kill zones: all four, shift %+d h' % sh, dict(kzOn=True, kz=(True,) * 4, kzShift=sh)))
def job(arg):
    tf, name, o = arg
    import geng, ref_gs
    ref_gs.eprep = geng.ref_g.eprep; geng.ref_g = ref_gs
    tr = geng.run(tf, o)
    return tf, name, [(x['t'], x['res'], x['win'], tuple(x['hits']), x['sp'], x['risk'], x['be']) for x in tr]
if __name__ == '__main__':
    tfs = sys.argv[1].split(',') if len(sys.argv) > 1 else ['H1', 'M15', 'M5', 'M1']
    for tf in tfs:
        out = {}
        with mp.Pool(4) as pool:
            for k, (t, name, tr) in enumerate(pool.imap_unordered(job, [(tf, n, o) for n, o in C])):
                out[name] = tr
        pickle.dump(dict(configs=C, res=out), open(S + '/gold/sweep_%s.pkl' % tf, 'wb'))
        print(tf, 'done', len(out), flush=True)
