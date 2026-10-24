import sys
sys.path.insert(0, D := '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
from bias import feats as bfeats
from pfeat import pf
from engine2 import prepare
from tightdata import TRADES
from sub import search
rows = []
for t in TRADES:
    P = prepare(t['sym']); d = t['d']; b = bfeats(P, t['arm_i']); f = pf(t)
    for k, v in b.items(): f['b_' + k] = d * v
    rows.append((t, f))
def cnt(pred):
    tp = sum(1 for t, f in rows if pred(f) and t['tight']); fp = sum(1 for t, f in rows if pred(f) and not t['tight']); return tp, fp
print('pdDir<0', cnt(lambda f: f['b_pdDir'] < 0)); print('pd2<0', cnt(lambda f: f['b_pd2'] < 0))
print('fd', cnt(lambda f: f['sameSigDay'] == 0)); print('fd & pdDir<0', cnt(lambda f: f['sameSigDay'] == 0 and f['b_pdDir'] < 0))
print('fd & pd2<0', cnt(lambda f: f['sameSigDay'] == 0 and f['b_pd2'] < 0))
print('fd & pdDir<0 & pd2<0', cnt(lambda f: f['sameSigDay'] == 0 and f['b_pdDir'] < 0 and f['b_pd2'] < 0))
print([f"{t['sym']} {t['fill'][5:]} {'T' if t['tight'] else ''}" for t, f in rows if f['sameSigDay'] == 0 and f['b_pdDir'] < 0])
print('-- search all 80 with bias feats')
for r in search(rows, 15): print(r)
sub = [(t, f) for t, f in rows if f['sameSigDay'] == 0 and f['b_pdDir'] < 0]
print('-- search within fd & pdDir<0')
for r in search(sub, 15): print(r)
