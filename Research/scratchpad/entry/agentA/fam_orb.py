"""family 1: opening-range breakouts (London 08:00, NY 08:20 / 09:30 local), Asian-range breakout and fade at London"""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/agentA')
import lib, numpy as np
FAM = sys.argv[2] if len(sys.argv) > 2 else 'orb'

def inwin(m, a, z):  # local minutes window [a, z), wraps midnight
    return (m >= a) & (m < z) if a < z else (m >= a) | (m < z)

def breakout_sigs(b, hi, lo, trade):
    """first close above hi (long) / below lo (short) per day in trade window, prev close inside"""
    C = b['C']; pc = np.r_[C[0], C[:-1]]
    L = trade & ~np.isnan(hi) & (C > hi) & (pc <= hi) & b['ok']
    S = trade & ~np.isnan(lo) & (C < lo) & (pc >= lo) & b['ok']
    il = lib.first_per_day(b, L); is_ = lib.first_per_day(b, S)
    return il, is_

def orb(tf, name, zone, a, z, ta, tz):
    b = lib.ctx(tf); m = b['lon_min'] if zone == 'lon' else b['ny_min']
    wd_ok = b['ny_wd'] < 5
    hi, lo, last = lib.win_range(b, inwin(m, a, z) & wd_ok)
    trade = inwin(m, ta, tz) & wd_ok
    il, is_ = breakout_sigs(b, hi, lo, trade)
    i = np.r_[il, is_]; d = np.r_[np.ones(len(il)), -np.ones(len(is_))].astype(int)
    C = b['C'][i]; A = b['atr'][i]; H = hi[i]; Lo = lo[i]; mid = (H + Lo) / 2
    rng = (H - Lo) / A
    lib.run(tf, i, d, C, C - d * 1.8 * A, 1, name=name + ' mkt 1.8ATR', family=FAM)
    st = np.where(d == 1, np.minimum(mid, C - 0.5 * A), np.maximum(mid, C + 0.5 * A))
    lib.run(tf, i, d, C, st, 1, name=name + ' mkt stop=ORmid', family=FAM)
    st = np.where(d == 1, np.minimum(Lo, C - 0.5 * A), np.maximum(H, C + 0.5 * A))
    lib.run(tf, i, d, C, st, 1, name=name + ' mkt stop=ORopp', family=FAM)
    # stop-entry orders placed at the end of the range
    e_i = lib.first_per_day(b, (np.arange(b['n']) == last + 1) & (last >= 0) & b['ok'] & wd_ok)  # first bar after range: decision at its open ~ prev close
    e_i = e_i - 1  # decide at the close of the range's last bar
    e_i = e_i[e_i > 0]
    nbar = int(((tz - ta) % 1440) / b['tfmin'])
    hi2 = hi[e_i + 1]; lo2 = lo[e_i + 1]; A2 = b['atr'][e_i]; mid2 = (hi2 + lo2) / 2
    i2 = np.r_[e_i, e_i]; d2 = np.r_[np.ones(len(e_i)), -np.ones(len(e_i))].astype(int)
    ent = np.r_[hi2 + 0.05 * A2, lo2 - 0.05 * A2]; A22 = np.r_[A2, A2]; M2 = np.r_[mid2, mid2]
    ok = ~np.isnan(ent)
    st = np.where(d2 == 1, np.minimum(M2, ent - 0.5 * A22), np.maximum(M2, ent + 0.5 * A22))
    lib.run(tf, i2[ok], d2[ok], ent[ok], st[ok], 2, window=nbar, name=name + ' stopentry stop=ORmid', family=FAM)
    lib.run(tf, i2[ok], d2[ok], ent[ok], ent[ok] - d2[ok] * 1.8 * A22[ok], 2, window=nbar, name=name + ' stopentry 1.8ATR', family=FAM)

def asia(tf):
    b = lib.ctx(tf); m = b['ny_min']; wd_ok = b['ny_wd'] < 5
    hi, lo, last = lib.win_range(b, inwin(m, 19 * 60, 3 * 60) & wd_ok)
    lm = b['lon_min']; trade = inwin(lm, 8 * 60, 11 * 60) & wd_ok
    il, is_ = breakout_sigs(b, hi, lo, trade)
    i = np.r_[il, is_]; d = np.r_[np.ones(len(il)), -np.ones(len(is_))].astype(int)
    C = b['C'][i]; A = b['atr'][i]
    lib.run(tf, i, d, C, C - d * 1.8 * A, 1, name='Asia brk@London mkt 1.8ATR', family=FAM)
    mid = (hi[i] + lo[i]) / 2
    st = np.where(d == 1, np.minimum(mid, C - 0.5 * A), np.maximum(mid, C + 0.5 * A))
    lib.run(tf, i, d, C, st, 1, name='Asia brk@London mkt stop=mid', family=FAM)
    # fade: bar trades beyond the Asian high and closes back inside -> short (mirror long)
    H, L, C_ = b['H'], b['L'], b['C']
    S = trade & ~np.isnan(hi) & (H > hi) & (C_ < hi) & b['ok']
    Lg = trade & ~np.isnan(lo) & (L < lo) & (C_ > lo) & b['ok']
    is_ = lib.first_per_day(b, S); il = lib.first_per_day(b, Lg)
    i = np.r_[il, is_]; d = np.r_[np.ones(len(il)), -np.ones(len(is_))].astype(int)
    C = C_[i]; A = b['atr'][i]
    ext = np.where(d == 1, L[i], H[i])
    st = np.where(d == 1, np.minimum(ext - 0.1 * A, C - 0.5 * A), np.maximum(ext + 0.1 * A, C + 0.5 * A))
    lib.run(tf, i, d, C, st, 1, name='Asia sweep-fade@London mkt stop=ext', family=FAM)
    lib.run(tf, i, d, C, C - d * 1.8 * A, 1, name='Asia sweep-fade@London mkt 1.8ATR', family=FAM)

for tf in sys.argv[1].split(','):
    orb(tf, 'LonORB30', 'lon', 8 * 60, 8 * 60 + 30, 8 * 60 + 30, 12 * 60)
    orb(tf, 'LonORB60', 'lon', 8 * 60, 9 * 60, 9 * 60, 12 * 60)
    orb(tf, 'NYORB 0820-0850', 'ny', 8 * 60 + 20, 8 * 60 + 50, 8 * 60 + 50, 12 * 60)
    orb(tf, 'NYORB 0930-1000', 'ny', 9 * 60 + 30, 10 * 60, 10 * 60, 13 * 60)
    orb(tf, 'NYORB 0930-1030', 'ny', 9 * 60 + 30, 10 * 60 + 30, 10 * 60 + 30, 13 * 60)
    asia(tf)
