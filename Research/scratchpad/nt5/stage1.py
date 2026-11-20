"""Stage 1 edge search: random settings per timeframe on the user's EA rules (edge.trades_for), every year's result kept.
Run: python3 -I stage1.py TF N SEED -> stage1_TF.pkl (appended in batches; a restart resumes)."""
import sys, os, random, pickle, itertools, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from multiprocessing import Pool
TF, NRUN, SEED = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
OUT = os.path.dirname(os.path.abspath(__file__)) + '/stage1_%s.pkl' % TF
SPACE = dict(tp=[0.1, 0.2, 0.3, 0.5, 0.6, 1.0, 1.5, 2.0], stopAtr=[1.8, 2.4, 3.0, 4.0], entryMode=['model', 'market'], entryPct=[25.0, 50.0],
             chop=[None, 8.0, 13.5], hours=[(600, 2300), (1830, 2230), (1200, 2300), None], kz=['user', None, 'LNY'],
             days=['TWT', 'MF'], vw=['session', 'month'], momAtr=[0.85, 0.6, 1.1], mv=[None, 'mv2', 'mv3'])


def cfg_of(c):
    eng = dict(halfCap=True, maxFills=10, entryPct=c['entryPct'], noChaseSig=2.0, kzShift=0, kzAuto=True, stopAtr=c['stopAtr'], entryMode=c['entryMode'],
               momAtr=c['momAtr'], vwAnchorG=c['vw'])
    if c['chop']: eng.update(chopOn=True, chopMax=c['chop'])
    else: eng.update(chopOn=False, chopMax=13.5)
    if c['mv'] == 'mv2': eng.update(mv2On=True)
    if c['mv'] == 'mv3': eng.update(mv3On=True, mv3R=0.0)
    on = dict(dayOn=True, days=(False, True, True, True, False, False, False) if c['days'] == 'TWT' else (True, True, True, True, True, False, False))
    if c['hours']: on.update(hoursOn=True, hoursSess=c['hours'])
    else: on.update(hoursOn=False)
    if c['kz'] == 'user': on.update(kzOn=True, kz=(True, True, True, False))
    elif c['kz'] == 'LNY': on.update(kzOn=True, kz=(False, True, True, False))
    else: on.update(kzOn=False)
    return on, eng


def one(c):
    import edge
    on, eng = cfg_of(c)
    try: tr = edge.trades_for(TF, c['tp'], on, eng)
    except Exception as e: return c, None, repr(e)[:200]
    yr = {y: edge.stats(tr, y) for y in range(2021, 2027)}
    m24 = collections.defaultdict(float)
    for x in tr:
        if x['t'].year == 2024: m24[x['t'].month] += x['net']
    return c, dict(years=yr, m24=dict(m24), n=len(tr)), None


if __name__ == '__main__':
    done = pickle.load(open(OUT, 'rb')) if os.path.exists(OUT) else []
    seen = {tuple(sorted(c.items())) for c, *_ in done}
    rng = random.Random(SEED); todo = []
    keys = list(SPACE)
    # always include the user's own settings at every target
    for tp in SPACE['tp']:
        todo.append(dict(tp=tp, stopAtr=1.8, entryMode='model', entryPct=25.0, chop=None, hours=(600, 2300), kz='user', days='TWT', vw='session', momAtr=0.85, mv=None))
    while len(todo) < NRUN: todo.append({k: rng.choice(SPACE[k]) for k in keys})
    todo = [c for c in todo if tuple(sorted(c.items())) not in seen]
    print(TF, 'to run', len(todo), 'done before', len(done), flush=True)
    with Pool(4) as pool:
        for i, r in enumerate(pool.imap_unordered(one, todo)):
            done.append(r)
            if (i + 1) % 20 == 0 or i + 1 == len(todo):
                pickle.dump(done, open(OUT + '.tmp', 'wb')); os.replace(OUT + '.tmp', OUT)
                print(TF, i + 1, '/', len(todo), flush=True)
