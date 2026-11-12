"""Bookings vs broker trades with gaps allowed: walks the closed positions and the EA's BOOK lines in order; a position whose P&L is not the
next booking is 'unbooked' (and marked 'off' when it closed while the EA was off: after a DRIVER restart line and before the EA's next line)."""
import sys, re
L = open(sys.argv[1]).read().split('\n')
pnl, close_line, order = {}, {}, []
books = []
off = False; off_close = set()
for i, l in enumerate(L):
    if l.startswith('DRIVER restart'): off = True
    elif l.startswith('EA ') and off: off = False
    m = re.match(r'SIM DEAL \S+ \S+ tk=\d+ pos=(\d+) \w+ (IN|OUT) vol=\S+ px=\S+ profit=(\S+) comm=(\S+)', l)
    if m:
        p = m.group(1); pnl[p] = pnl.get(p, 0.0) + float(m.group(3)) + float(m.group(4))
        if m.group(2) == 'IN' and float(m.group(4)) != 0: pass
    m = re.match(r'SIM CLOSE \S+ \S+ pos=(\d+)', l)
    if m:
        p = m.group(1); order.append(p); close_line[p] = i
        if off: off_close.add(p)
    m = re.match(r'BOOK \S+ \S+ pnl=(\S+)', l)
    if m: books.append(float(m.group(1)))
j = 0; unb = []; k = 0; pairs = 0
while k < len(order):
    p = order[k]
    if j < len(books) and abs(books[j] - pnl[p]) < 0.015: j += 1; k += 1; continue
    if j < len(books) and k + 1 < len(order) and abs(books[j] - pnl[p] - pnl[order[k + 1]]) < 0.015:   # a hedge pair: one booking of both trades
        j += 1; k += 2; pairs += 1; continue
    unb.append(p); k += 1
print(f'{sys.argv[1]}: positions {len(order)}, bookings {len(books)}, booked {len(order) - len(unb)} (hedge pairs {pairs}), unbooked {len(unb)} '
      f'(closed while the EA was off {sum(p in off_close for p in unb)}), stray bookings {len(books) - j}')
