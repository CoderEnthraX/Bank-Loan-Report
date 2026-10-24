"""VWAP side margin and 3-bar VWAP slope (in ATR) of given signal bars under every VWAP variant."""
import sys, os
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S+'/fit'); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vwalt
from engine2 import prepare
from engine import rma
CASES = [('CRUDE','2026-10-12 13:40',1,'extra'),('CRUDE','2026-10-15 18:30',1,'extra'),('CRUDE','2026-10-15 21:35',1,'extra'),('CRUDE','2026-10-16 11:40',1,'extra'),
         ('CRUDE','2026-10-06 20:55',1,'A-extra'),('CRUDE','2026-10-16 11:45',1,'#60 orig'),('CRUDE','2026-10-12 14:15',1,'#50 orig'),('CRUDE','2026-10-15 18:50',1,'#58 orig')]
MODES = ['csv','twap','close','hl2','ohlc4','ny']
for sym, t, d, lab in CASES:
    P = prepare(sym); i = P['T'].index(t); A = rma(P['tr'], 14)[i]; C = P['C']
    out = []
    for m in MODES:
        V = vwalt.series(sym, m); out.append(f"{m} {d*(C[i]-V[i])/A:+.2f}/{d*(V[i]-V[i-3])/A:+.3f}")
    print(f"{sym} {t} {lab:8s} (c-vwap/ATR / slope3/ATR): " + '  '.join(out))
