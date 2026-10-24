import pickle
D = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_volatility/'
base = pickle.load(open(D + 'featall.pkl', 'rb'))
for fn in ('feat3.pkl', 'feat4.pkl', 'feat5.pkl'):
    r = pickle.load(open(D + fn, 'rb'))
    for (t, f), (t2, g) in zip(base, r):
        assert t['sym'] == t2['sym'] and t['fill'] == t2['fill']
        f.update(g)
pickle.dump(base, open(D + 'merged.pkl', 'wb'))
print(len(base), len(base[0][1]))
