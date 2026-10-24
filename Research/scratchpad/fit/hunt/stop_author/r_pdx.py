"""Configurable tight-stop rule (env RULECFG json):
 tight iff no earlier same-direction displacement EVENT in the current session AND previous session moved against d.
 keys: ev (tuple of extra event conds: vsl,vw,mom,first,sun), merge (bool), meas ('body'|'c2c'), unit ('atr'|'datr'|'none'), th (float)
"""
import os, json, sys
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_author')
from dlib import sessions, event
CFG = dict(ev=['vsl'], merge=True, meas='body', unit='atr', th=1.0)
CFG.update(json.loads(os.environ.get('RULECFG', '{}')))
def prev_against(P, i, d):
    out, idx = sessions(P, CFG['merge']); k = idx[i]
    if k < 2: return False
    s1, s2 = out[k - 1], out[k - 2]
    if CFG['meas'] == 'net':
        ex = tuple(CFG.get('nev', ['vsl'])); key = ('pdx_net', ex, CFG['merge'], k)
        if key not in P:
            P[key] = sum(1 for j in range(s1['a'], s1['b']) if event(P, j, 1, ex)) - sum(1 for j in range(s1['a'], s1['b']) if event(P, j, -1, ex))
        return d * P[key] <= -CFG['th']
    mv = d * ((s1['c'] - s1['o']) if CFG['meas'] == 'body' else (s1['c'] - s2['c']))
    u = CFG['unit']
    if u == 'atr': sc = P[('atr', 14)][i]
    elif u == 'datr': rr = [x['h'] - x['l'] for x in out[max(0, k - 14):k]]; sc = sum(rr) / len(rr)
    elif u == 'datrr':
        tr = [max(out[j]['h'] - out[j]['l'], abs(out[j]['h'] - out[j - 1]['c']), abs(out[j]['l'] - out[j - 1]['c'])) for j in range(1, k)]
        x = sum(tr[:14]) / 14
        for v in tr[14:]: x = (x * 13 + v) / 14
        sc = x
    elif u == 'range': sc = s1['h'] - s1['l']
    else: sc = 1.0
    return mv < -CFG['th'] * sc
def is_tight(P, i, d):
    if not prev_against(P, i, d): return False
    out, idx = sessions(P, CFG['merge']); a = out[idx[i]]['a']
    return not any(event(P, j, d, tuple(CFG['ev'])) for j in range(a, i))
def stop_fn(P, i, d, entry, stop, A, ctx):
    if is_tight(P, i, d):
        ext = P['L'][i] if d > 0 else P['H'][i]
        return entry - d * max(0.9 * A, d * (entry - ext))
    return stop
