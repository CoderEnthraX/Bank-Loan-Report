import sys, pickle; sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_levels')
rows = pickle.load(open('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_levels/feat2.pkl','rb'))
from malv import mafeat
from lv import prepare
for t, x in rows:
    P = prepare(t['sym']); A = P[('atr',14)][t['arm_i']]; x.update(mafeat(P, t['arm_i'], t['d'], t['entry'], A))
Z = {'stop18': (-1.8, 0), 'stop09': (-0.9, 0), 'stop0918': (-1.8, -0.9), 'tgt36': (0, 3.6), 'tgt1836': (1.8, 3.6), 'tgt18': (0, 1.8), 'beyond18': (-3.6, -1.8)}
LV = ['vwap','ba1','ba2','ba3','bf1','bf2','bf3','sopen','sadv','sadvx','sfav','sfavx','pdfav','pdadv','pdc','pdo','pdmid','orfav1','oradv1','orfav3','oradv3','orfav6','oradv6','orfav12','oradv12',
      'wopen','wfav','wadv','pwfav','pwadv','rf2_1','ra2_1','rf2_5','ra2_5','rf2_2.5','ra2_2.5','rf1_1','ra1_1','rf3_5','ra3_5','ema20','ema50','ema200','sma200','ps_lo','po_ext']
res = []
for k in LV:
    for zn, (a, b) in Z.items():
        tp = sum(1 for t, x in rows if t['tight'] and x.get(k) is not None and a < x[k] < b)
        fp = sum(1 for t, x in rows if not t['tight'] and x.get(k) is not None and a < x[k] < b)
        res.append((tp - fp, tp, fp, k, zn))
for k in ['adr5_roomf','adr10_roomf','adr14_roomf','adr20_roomf','datr14_roomf']:
    for thr in (1.8, 3.6, 5.4):
        tp = sum(1 for t, x in rows if t['tight'] and x.get(k) is not None and x[k] < thr); fp = sum(1 for t, x in rows if not t['tight'] and x.get(k) is not None and x[k] < thr)
        res.append((tp - fp, tp, fp, k, f'<{thr}'))
res.sort(reverse=True)
for r in res[:25]: print(r)
print('... high-recall (tp>=6):', [r for r in res if r[1] >= 6][:10])
