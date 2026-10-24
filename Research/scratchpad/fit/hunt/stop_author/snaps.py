import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_author')
from alib import *
SN = [('CRUDE','2026-10-09 13:40','TRANS',20,'BEAR'),('EURUSD','2026-10-12 12:50','TRANS',21,'BEAR'),('GC','2026-10-12 13:00','TRANS/RANG',34,'NEUT'),
      ('NASDAQ','2026-10-12 12:50','RANG',32,'NEUT'),('NASDAQ','2026-10-09 13:40','RANG',36,'NEUT'),('NIFTY','2026-10-12 12:40','TREND',36,'BEAR'),('NIFTY','2026-10-12 12:20','TREND',39,'BEAR'),
      ('SENSEX','2026-10-12 12:40','TRANS',38,'BEAR'),('US30','2026-10-12 13:00','RANG',29,'NEUT')]
W = int(sys.argv[1]) if len(sys.argv) > 1 else 6
for s, t, lab, a, b in SN:
    P = get(s); T = P['T']; i0 = T.index(t)
    print(f'=== {s} {t} {lab} ADX{a} {b}')
    for i in range(i0 - W, i0 + W + 1):
        if i >= len(T): break
        f = feats(P, i)
        mk = '*' if round(f['adx']) == a else ' '
        print(f"{mk}{T[i][5:]} adx {f['adx']:5.1f} di {f['dip']:4.1f}/{f['dim']:4.1f} spr {f['spr']:+5.1f} sl1 {f['sl1']:+4.1f} sl3 {f['sl3']:+4.1f} pk20 {f['pk20']:5.1f} pk50 {f['pk50']:5.1f} er14 {f['er14']:.2f} er20 {f['er20']:.2f} ch14 {f['chop14']:4.1f} cv {f['cv']:+5.2f} cvs {f['cvs']:+5.2f} vsl10 {f['vsl10']:+5.2f} ce20 {f['ce20']:+5.2f} e2050 {f['e2050']:+5.2f} e50200 {f['e50200']:+5.2f} r2 {f['r2_20']:.2f} lr {f['lr20']:+.2f}")
