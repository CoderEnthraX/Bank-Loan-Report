import pickle, os
HERE = os.path.dirname(os.path.abspath(__file__))
P = pickle.load(open(os.path.join(HERE, 'pbank.pkl'), 'rb'))
B2 = pickle.load(open(os.path.join(HERE, 'bank2.pkl'), 'rb'))
idx = {(t['sym'], t['fill']): k for k, t in enumerate(B2['trades'])}
out = []
for t, f in P:
    g = dict(f); k = idx[(t['sym'], t['fill'])]
    for nm, v in zip(B2['names'], B2['X'][k]): g['B_' + nm] = float(v)
    out.append((t, g))
pickle.dump(out, open(os.path.join(HERE, 'pbank_all.pkl'), 'wb'))
print(len(out), len(out[0][1]))
