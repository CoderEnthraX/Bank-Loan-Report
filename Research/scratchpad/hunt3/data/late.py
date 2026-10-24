"""SENSEX data ends 15:10 each day (15:15-15:25 bars absent). If the original's feed had them, ATR14 would differ esp. early session.
Insert k synthetic bars per day with TR = x * ATR and check the fit of logged/screenshot R/1.8 to the resulting ATR at the signal bar."""
import sys, os, json
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S+'/fit'); sys.path.insert(0, S+'/xl'); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load_xl import load
from engine2 import prepare
import dm
P = prepare('SENSEX'); T = P['T']; D = P['daystart']; tr = P['tr']; idx = {t:i for i,t in enumerate(T)}
trades = dm.run('SENSEX', {"dayStopR":0})
obs = []  # (signal bar, R)
for x in load():
    if x['sym'] != 'SENSEX': continue
    f = idx.get(x['date'] + ' ' + {66:'09:40'}.get(x['n'], x['tin']))
    m = next((t for t in trades if t['dir']==x['d'] and abs(t['fill']-f)<=1), None)
    if m and not m['tight']: obs.append((m['arm'], abs(x['entry']-x['stop']), 'B', T[m['arm']]))
    if x['n'] == 77: obs.append((idx['2026-10-15 09:15'], abs(x['entry']-x['stop']), 'B', '2026-10-15 09:15'))
g = json.load(open(S+'/gt/final/sensex_us30.json'))
for t in g['orig_trades']:
    if t['symbol']=='SENSEX' and t.get('r_from_green_box'):
        f = idx[t['fill_bar']]; m = next((u for u in trades if abs(u['fill']-f)<=0), None)
        if m: obs.append((m['arm'], t['r_from_green_box'], 'A', T[m['arm']]))
def atr_with(k, x):
    out = [None]*len(tr); s = None; n = 14; buf = []
    for i in range(len(tr)):
        seq = []
        if k and D[i] and i > 0 and s is not None: seq = [x*s]*k   # synthetic late bars before the session's first bar
        for v in seq: s = (s*13 + v)/14
        if s is None:
            buf.append(tr[i])
            if len(buf) == n: s = sum(buf)/n
        else: s = (s*13 + tr[i])/14
        out[i] = s
    return out
for k, x in ((0,0),(3,0.0),(3,0.5),(3,1.0),(3,1.5),(3,2.0)):
    A = atr_with(k, x)
    e = [R/1.8/A[a]-1 for a, R, src, t in obs]
    early = [R/1.8/A[a]-1 for a, R, src, t in obs if t[11:] <= '09:45']
    rms = lambda v: (sum(z*z for z in v)/len(v))**.5
    print(f'late bars k={k} TR={x}*ATR: all n={len(e)} RMS {rms(e)*100:.2f}% mean {sum(e)/len(e)*100:+.2f}% | signals<=09:45 n={len(early)} RMS {rms(early)*100:.2f}% mean {sum(early)/len(early)*100:+.2f}%')
