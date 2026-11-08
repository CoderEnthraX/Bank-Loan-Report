"""candidate A sensitivity: NY open range (from 09:30 NY, length L min) -> both stop orders at range hi/lo +-buf ATR, valid until T end, stop k ATR"""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/agentA')
import lib, numpy as np
lib.OUT = lib.A + '/rows_cand.jsonl'

def sigs(tf, start=570, L=30, end=780, buf=0.05):
    b = lib.ctx(tf); nm = b['ny_min']; wd = b['ny_wd'] < 5
    hi, lo, last = lib.win_range(b, (nm >= start) & (nm < start + L) & wd)
    i = np.flatnonzero((np.r_[last[1:], -1] >= 0) & (last < 0) & b['ok'] & wd & (nm >= start) & (nm < start + L))  # last bar of the range
    i = i[(nm[i] + b['tfmin']) == start + L]
    H = hi[i + 1]; Lo = lo[i + 1]; a = b['atr'][i]
    i2 = np.r_[i, i]; d2 = np.r_[np.ones(len(i)), -np.ones(len(i))].astype(int); a2 = np.r_[a, a]
    e = np.r_[H + buf * a, Lo - buf * a]
    win = int((end - start - L) / b['tfmin'])
    return b, i2, d2, e, a2, win, np.r_[H, H], np.r_[Lo, Lo]

def go(tf, tag, start=570, L=30, end=780, buf=0.05, k=1.8, stop='atr'):
    b, i, d, e, a, win, H, Lo = sigs(tf, start, L, end, buf)
    if stop == 'atr': st = e - d * k * a
    elif stop == 'mid': mid = (H + Lo) / 2; st = np.where(d == 1, np.minimum(mid, e - 0.5 * a), np.maximum(mid, e + 0.5 * a))
    name = 'A %s start %02d:%02d L%d end %02d:%02d buf %.2f %s' % (tag, start // 60, start % 60, L, end // 60, end % 60, buf, ('%.1fATR' % k) if stop == 'atr' else 'ORmid')
    return lib.run(tf, i, d, e, st, 2, window=win, name=name, family='candA')

if __name__ == '__main__':
    for tf in sys.argv[1].split(','):
        go(tf, 'base')
        for L in (15, 45, 60): go(tf, 'len', L=L)
        for st in (510, 540, 600): go(tf, 'start', start=st)
        for end in (720, 960): go(tf, 'end', end=end)
        for k in (1.0, 3.0): go(tf, 'stop', k=k)
        go(tf, 'buf', buf=0.3)
