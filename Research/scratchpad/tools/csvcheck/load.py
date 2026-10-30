"""Load a TradingView 'List of trades' CSV export (two rows per trade: Exit, Entry) into one dict per trade, in trade-number order."""
import csv, sys
def load(path):
    rows = list(csv.DictReader(open(path, encoding='utf-8-sig')))
    T = {}
    for r in rows:
        n = int(r['Trade number']); t = T.setdefault(n, {'n': n})
        side = 'entry' if r['Type'].startswith('Entry') else 'exit'
        t[side + '_time'] = r['Date and time']; t[side + '_px'] = float(r['Price USD']); t[side + '_sig'] = r['Signal']
        t['dir'] = 1 if 'long' in r['Type'] else -1
        t['qty'] = float(r['Size (qty)']); t['value'] = float(r['Size (value)']); t['pnl'] = float(r['Net PnL USD'])
        t['comm'] = float(r['Commission USD']); t['cum'] = float(r['Cumulative PnL USD']); t['cumpct'] = float(r['Cumulative PnL %'])
        t['mfe'] = float(r['Favorable excursion USD']); t['mae'] = float(r['Adverse excursion USD']); t['bars'] = r['Duration (bars)']
    return [T[k] for k in sorted(T)]
if __name__ == '__main__':
    import collections
    for p in sys.argv[1:]:
        tr = load(p)
        print(p.split('/')[-2], len(tr), 'trades | first', tr[0]['entry_time'], 'last', tr[-1]['exit_time'] if 'exit_time' in tr[-1] else 'open')
        print('   exit signals', collections.Counter(t.get('exit_sig') for t in tr).most_common(), '| entry signals', collections.Counter(t.get('entry_sig') for t in tr).most_common())
        big = max(tr, key=lambda t: abs(t['cum']))
        print('   initial capital estimate from cumulative %%: %.0f' % (big['cum'] / (big['cumpct'] / 100.0)))
        same = collections.Counter((t['entry_time'], t['entry_px']) for t in tr)
        print('   trade numbers sharing one entry (partial exits):', sum(1 for v in same.values() if v > 1))
