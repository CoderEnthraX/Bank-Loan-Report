"""analyze.py LOG [LOG2]: per-trade checks of a broker-simulator run.
- every position: stop loss and take profit when it opened (TP = 0 means the broker had no target);
- who closed it: SL, TP, the EA (its reason from 'Closing #..' or v4.3's SIMTAG lines), by hand / another EA;
- bookings: every BOOK line (the EA's BookClosed) against the broker's P&L of the trade(s) that closed (profit + commission);
- with LOG2 (same data, other scenario): the trade lists compared (entry time, side, lots, result)."""
import sys, re, collections

REASON = {0: 'hand (PC)', 1: 'hand (phone)', 2: 'hand (web)', 3: 'EA', 4: 'SL', 5: 'TP', 6: 'stop-out'}


def parse(path):
    pos, order, books, closes_ea, tags, drv, ea_lines = {}, [], [], {}, [], [], []
    last_tag = None; early = {}
    for ln in open(path):
        if ln.startswith('SIM OPEN'):
            m = re.match(r'SIM OPEN (\S+ \S+) pos=(\d+) (\w+) vol=([\d.]+) px=([\d.]+) sl=([\d.]+) tp=([\d.]+)', ln)
            p = dict(t=m.group(1), id=int(m.group(2)), side=m.group(3), vol=float(m.group(4)), px=float(m.group(5)), sl=float(m.group(6)),
                     tp=float(m.group(7)), pnl=early.pop(int(m.group(2)), 0.0), out=[], close_t=None, why=None)
            pos[p['id']] = p; order.append(p['id'])
        elif ln.startswith('SIM DEAL'):
            m = re.match(r'SIM DEAL (\S+ \S+) tk=\d+ pos=(\d+) \w+ (IN|OUT) vol=([\d.]+) px=([\d.]+) profit=(-?[\d.]+) comm=(-?[\d.]+) magic=(-?\d+) reason=(\d+)', ln)
            pid = int(m.group(2)); p = pos.get(pid)
            if p is None:                                   # the entry deal is logged just before its SIM OPEN line
                early[pid] = early.get(pid, 0.0) + float(m.group(6)) + float(m.group(7)); continue
            p['pnl'] += float(m.group(6)) + float(m.group(7))
            if m.group(3) == 'OUT':
                r = int(m.group(9)); p['out'].append(r); p['close_t'] = m.group(1)
                if r == 3 and int(m.group(8)) == 240611:
                    p['why'] = closes_ea.get(pid) or last_tag or 'EA (no reason logged)'
                elif r == 3: p['why'] = 'another EA'
                else: p['why'] = REASON.get(r, str(r))
        elif ln.startswith('EA '):
            ea_lines.append(ln.rstrip())
            m = re.match(r'EA \S+ \S+ Closing #(\d+) \([\d.]+ lots\): (.*)$', ln)
            if m: closes_ea[int(m.group(1))] = 'EA: ' + m.group(2).strip()
            m = re.match(r'EA \S+ \S+ SIMTAG close: (.*)$', ln)
            if m: last_tag = 'EA: ' + m.group(1).strip()
        elif ln.startswith('BOOK'):
            m = re.match(r'BOOK (\S+ \S+) pnl=(-?[\d.]+) hedge=(\d)', ln)
            books.append((m.group(1), float(m.group(2)), int(m.group(3))))
        elif ln.startswith('DRIVER'):
            drv.append(ln.strip())
    return pos, order, books, drv, ea_lines


def report(path):
    pos, order, books, drv, ea_lines = parse(path)
    closed = [pos[i] for i in order if pos[i]['close_t']]
    print('== %s: %d trades opened, %d closed, %d bookings, driver events %d' % (path, len(order), len(closed), len(books), len(drv)))
    print('   opened without a take profit at the broker: %d' % sum(1 for i in order if pos[i]['tp'] == 0))
    dup = sum(1 for x, y in zip(order, order[1:]) if pos[x]['side'] == pos[y]['side'] and pos[x]['sl'] == pos[y]['sl'] and pos[x]['sl'] > 0)
    print('   same signal traded twice (same side and stop as the trade before): %d' % dup)
    cat = collections.Counter(p['why'] for p in closed)
    for k, v in cat.most_common():
        sub = [p for p in closed if p['why'] == k]
        print('   closed by %-62s %4d trades, P&L %9.2f (avg %7.2f)' % (k, v, sum(p['pnl'] for p in sub), sum(p['pnl'] for p in sub) / v))
    # bookings vs broker P&L, in close order (a hedge booking covers the trades closed since the last booking)
    by_close = sorted(closed, key=lambda p: (p['close_t'], p['id']))
    bi, ok, bad = 0, 0, []
    pend = 0.0; npend = 0
    for p in by_close:
        pend += p['pnl']; npend += 1
        if bi < len(books) and (books[bi][2] == 0 or npend >= 2):
            if abs(books[bi][1] - round(pend, 2)) < 0.011: ok += 1
            else: bad.append((books[bi], round(pend, 2), p['id'], p['why']))
            bi += 1; pend = 0.0; npend = 0
    print('   bookings equal to the broker P&L: %d of %d%s' % (ok, len(books), '' if not bad else '  MISMATCHES: %s' % bad[:5]))
    tot_b = sum(b[1] for b in books); tot_p = sum(p['pnl'] for p in closed)
    print('   total booked %.2f, total broker P&L of closed trades %.2f' % (tot_b, tot_p))
    return pos, order, books


def compare(a, b):
    pa, oa, ba = parse(a)[:3]; pb, ob, bb = parse(b)[:3]
    ka = [(pa[i]['t'], pa[i]['side'], pa[i]['vol'], round(pa[i]['pnl'], 2)) for i in oa]
    kb = [(pb[i]['t'], pb[i]['side'], pb[i]['vol'], round(pb[i]['pnl'], 2)) for i in ob]
    same = sum(1 for x, y in zip(ka, kb) if x == y)
    first = next((k for k, (x, y) in enumerate(zip(ka, kb)) if x != y), None)
    print('== compare %s vs %s: trades %d vs %d, identical in order %d%s' % (a, b, len(ka), len(kb), same,
          '' if first is None else ', first difference at trade %d: %s vs %s' % (first, ka[first], kb[first])))
    print('   bookings %d vs %d, identical %d' % (len(ba), len(bb), sum(1 for x, y in zip(ba, bb) if x == y)))


if __name__ == '__main__':
    report(sys.argv[1])
    if len(sys.argv) > 2:
        report(sys.argv[2]); compare(sys.argv[1], sys.argv[2])
