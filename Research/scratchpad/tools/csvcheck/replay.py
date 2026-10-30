"""Replay Crooks C on the trade list's own P&L: owed before each trade, whether it should be a recovery trade, the expected $ risk
(max(base, owed / final R)), the actual $ risk (qty x |exit - entry| + commission, exact for trades closed at the stop or at the final
target), and the leverage limit (position value <= equity x leverage). Usage: replay.py FILE exitR [from to] [capital] [leverage]"""
import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/tools/csvcheck')
from load import load
def group(tr):
    """one position = trades sharing one entry (time, price, direction): the TP1-rule half (X1) and the rest (X4)"""
    out = []
    for t in tr:
        if out and out[-1][0]['entry_time'] == t['entry_time'] and out[-1][0]['entry_px'] == t['entry_px'] and out[-1][0]['dir'] == t['dir']: out[-1].append(t)
        else: out.append([t])
    return out
def replay(pos, exitR, base=50.0, capital=100000.0, lev=100.0):
    L = 0.0; N = 0; W = False; cum = 0.0; rows = []
    for k, p in enumerate(pos):
        rec = W and L > 0
        exp = max(base, L / exitR) if rec else base
        pnl = sum(t['pnl'] for t in p); qty = sum(t['qty'] for t in p); val = sum(t['value'] for t in p)
        eq = capital + cum
        rows.append(dict(k=k + 1, nums=[t['n'] for t in p], owed=L, rec=rec, exp=exp, pnl=pnl, qty=qty, val=val, eq=eq, levcap=eq * lev, parts=p))
        cum += pnl; win = pnl > 0
        L = max(0.0, L - pnl)
        if L < 0.01 or (win and rec): L = 0.0; N = 0
        else: N += 1
        W = win
    return rows
if __name__ == '__main__':
    path, exitR = sys.argv[1], float(sys.argv[2])
    a = int(sys.argv[3]) if len(sys.argv) > 3 else 1; b = int(sys.argv[4]) if len(sys.argv) > 4 else 10 ** 9
    tr = load(path); pos = group(tr); rows = replay(pos, exitR)
    print('positions', len(pos), 'trade rows', len(tr))
    print('  pos  trade#   entry time        dir  entry      exit(s)            qty      value(k)  P&L       owed before  type      expected risk  equity     value/(equity x100)')
    for r in rows:
        if not (a <= r['k'] <= b): continue
        p = r['parts']; ex = '/'.join('%.2f %s' % (t['exit_px'], t['exit_sig']) for t in p)
        print('  %4d %-9s %s %3s %9.2f  %-18s %8.2f %9.0f %+9.0f %11.0f   %-8s %10.0f %10.0f   %.2f' % (
            r['k'], ','.join(map(str, r['nums'])), p[0]['entry_time'], 'L' if p[0]['dir'] > 0 else 'S', p[0]['entry_px'], ex, r['qty'], r['val'] / 1000,
            r['pnl'], r['owed'], 'RECOVERY' if r['rec'] else 'base', r['exp'], r['eq'], r['val'] / r['levcap'] if r['levcap'] > 0 else 0))
