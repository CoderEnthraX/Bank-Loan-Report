#!/bin/bash
# summary of the v4.4 simulator runs (sc_ / x_ / z_ logs) -> final_summary.txt, then the checks. Bookings: unbooked.py (hedge pairs are one
# booking; a trade may stay unbooked only when it closed while the EA was off with the restart memory off, the z_ runs)
S=/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad; cd $S/sim
num() { grep -o "$1 [0-9]*" | head -1 | grep -o '[0-9]*$'; }
for f in sc_*_44.log x_*_44.log z_*_44.log; do
  r=$(python3 -I analyze.py $f); u=$(python3 -I unbooked.py $f)
  echo "$f | noTP $(echo "$r" | num 'broker:') | dup $(echo "$r" | num 'before):') | stale $(echo "$r" | num 'restart:') | booked $(echo "$u" | num ', booked') of $(echo "$u" | num 'positions'), unbooked $(echo "$u" | num 'unbooked') (off $(echo "$u" | num 'was off')), stray $(echo "$u" | num 'stray bookings') | rejects $(grep -c '^SIM REJECT' $f) | initfail $(grep -c 'INIT FAILED' $f) | M1 adopt $(awk '/DRIVER timeframe switch to M1/{m=1} /DRIVER timeframe switch to M5/{m=0} m && (/Adopted open position/ || /kept: it filled before/){a++} END{print a+0}' $f) | EA closes: $(echo "$r" | grep 'closed by EA' | sed 's/  */ /g;s/closed by EA: //;s/ (avg.*//;s/ trades, P&L.*//' | tr '\n' ';') | $(grep -h '^VWLINE' $f | sed 's/ (created [0-9]*, deleted [0-9]*)//;s/ | first [^|]*| last [^|]*|/ |/')"
done > final_summary.txt
echo "runs: $(wc -l < final_summary.txt), trades: $(cat sc_*_44.log x_*_44.log z_*_44.log | grep -c '^SIM OPEN')"
python3 -I - final_summary.txt <<'EOPY'
import sys, re
bad = 0
for l in open(sys.argv[1]):
    f = l.split(' |')[0]
    m = re.search(r'noTP (\d+) \| dup (\d+) \| stale (\d+) \| booked (\d+) of (\d+), unbooked (\d+) \(off (\d+)\), stray (\d+) \| rejects (\d+) \| initfail (\d+) \| M1 adopt (\d+)', l)
    if not m: print('NO DATA:', l.strip()[:160]); bad += 1; continue
    notp, dup, stale, b, n, u, o, st, rej, initf, adopt = map(int, m.groups())
    memoff = f.startswith('z_')
    if notp or dup or stale or rej or initf or adopt: print('PROBLEM:', l.strip()[:200]); bad += 1
    if st or (u and not memoff) or u > o or b + u != n: print('BOOKING PROBLEM:', l.strip()[:200]); bad += 1
    m = re.search(r'last point ([0-9.]+) \| engine VWAP ([0-9.]+)', l)
    if m and float(m.group(1)) > 0 and abs(float(m.group(1)) - float(m.group(2))) > 1e-6: print('VWAP LAST POINT MISMATCH:', l.strip()[:200]); bad += 1
    if 'VWLINE' not in l or 'gaps 0 | backwards 0' not in l: print('VWAP LINE CHECK:', l.strip()[:200]); bad += 1
print('problems:', bad)
EOPY
