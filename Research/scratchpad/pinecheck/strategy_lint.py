"""TradingView warning for strategies that only calculate on confirmed candles (no calc_on_every_tick = true): barstate.islast (and the
other barstates that describe the unconfirmed live candle) may not behave as on an indicator. Prints every use."""
import re, sys
for p in sys.argv[1:]:
    raw = open(p, encoding='utf8').read()
    # drop // comments (outside strings), keeping the line count
    out, q, i = [], None, 0
    while i < len(raw):
        ch = raw[i]
        if q:
            out.append(ch); q = None if ch == q else q
        elif ch in '"\'':
            out.append(ch); q = ch
        elif raw.startswith('//', i):
            j = raw.find('\n', i); i = len(raw) if j < 0 else j; continue
        else:
            out.append(ch)
        i += 1
    src = ''.join(out)
    m = re.search(r'^strategy\((.*)\)\s*$', src, re.M)
    if not m:
        print('%s: not a strategy' % p.split('/')[-1]); continue
    tick = re.search(r'calc_on_every_tick\s*=\s*true', m.group(1)) is not None
    bad = [] if tick else [(src.count('\n', 0, x.start()) + 1, x.group(0)) for x in re.finditer(r'barstate\.(islast|isnew|isrealtime|isconfirmed|islastconfirmedhistory)\b', src)]
    print('%s: calc_on_every_tick %s, %d confirmed-candle barstate warnings' % (p.split('/')[-1], tick, len(bad)))
    for ln, w in bad: print('   line %d: %s' % (ln, w))
