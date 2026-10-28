"""Write the resumable checkpoint into the repo: Research/{scratchpad,inputs,results,deliverables} + restore.sh.
- scratchpad/: every code / text file of the scratchpad up to 2 MB, same relative paths (scripts use the absolute scratchpad path, restore.sh puts them back there)
- inputs/: the uploaded data files (no screenshots)
- results/gold/: compact gold results, xz-compressed (slim_* = metrics only; final_<TF> with the robustness runs as metrics)
- deliverables/: the workbook and the research reports
Run: python3 -I make_checkpoint.py   (idempotent; prints what it wrote)"""
import os, sys, shutil, pickle, subprocess, collections
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
UP = '/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18'
REPO = '/home/user/Bank-Loan-Report'; OUT = REPO + '/Research'
sys.path.insert(0, S + '/gold')
TEXT = ('.py', '.pine', '.mq5', '.mqh', '.h', '.cpp', '.sh', '.md', '.txt', '.json', '.csv', '.log', '.tsv')
SKIP_DIRS = {'__pycache__', 'render', 'gold_raw'}
TFS = ('M1', 'M5', 'M15', 'H1')

def slim_results():
    """metrics-only copies of the big result pickles (the workbook builder and the pickers read these when the big files are absent)"""
    import anaA, greedy, build_final
    made = []
    for tf in TFS:
        g = S + '/gold/'
        if os.path.exists(g + 'sweep_%s.pkl' % tf):
            D = pickle.load(open(g + 'sweep_%s.pkl' % tf, 'rb'))
            pickle.dump(dict(configs=D['configs'], metrics={n: anaA.metrics(t) for n, t in D['res'].items() if t}), open(g + 'slim_sweep_%s.pkl' % tf, 'wb'))
            made.append('slim_sweep_%s.pkl' % tf)
        if os.path.exists(g + 'stageB_%s.pkl' % tf):
            D = pickle.load(open(g + 'stageB_%s.pkl' % tf, 'rb'))
            pickle.dump(dict(ingredients=D['ingredients'], combos=D['combos'], metrics={n: anaA.metrics(t) for n, t in D['res'].items() if t}),
                        open(g + 'slim_stageB_%s.pkl' % tf, 'wb'))
            made.append('slim_stageB_%s.pkl' % tf)
        if os.path.exists(g + 'stageC_%s.pkl' % tf):
            D = pickle.load(open(g + 'stageC_%s.pkl' % tf, 'rb'))
            pickle.dump(dict(cands=D['cands'], metrics={k: build_final.exm(t) for k, t in D['res'].items()}), open(g + 'slim_stageC_%s.pkl' % tf, 'wb'))
            made.append('slim_stageC_%s.pkl' % tf)
        if os.path.exists(g + 'final_%s.pkl' % tf):
            F = pickle.load(open(g + 'final_%s.pkl' % tf, 'rb'))
            if 'neigh' in F:
                F['neigh'] = {p: [(mn, c, t if isinstance(t, dict) else (greedy.metrics(greedy.pack(t), {}) if t else None)) for mn, c, t in rows]
                              for p, rows in F['neigh'].items()}
            pickle.dump(F, open(g + 'slim_final_%s.pkl' % tf, 'wb'))
            made.append('slim_final_%s.pkl' % tf)
    return made

def mirror():
    dst = OUT + '/scratchpad'; n = size = 0; skipped = []
    for root, dirs, files in os.walk(S):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not d.startswith(('.', 'tmp')))
        rel = os.path.relpath(root, S)
        for f in sorted(files):
            p = os.path.join(root, f)
            if not f.endswith(TEXT) or os.path.islink(p): continue
            sz = os.path.getsize(p)
            if sz > 2 * 1024 * 1024: skipped.append((os.path.relpath(p, S), sz)); continue
            q = os.path.join(dst, rel, f); os.makedirs(os.path.dirname(q), exist_ok=True); shutil.copy2(p, q); n += 1; size += sz
    return n, size, skipped

def inputs():
    dst = OUT + '/inputs'; os.makedirs(dst, exist_ok=True); out = []
    for f in sorted(os.listdir(UP)):
        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')): continue
        name = f.split('-', 1)[1] if f.startswith('63a91c21-') else f        # the gold zip keeps its plain name (restore.sh uses it)
        shutil.copy2(os.path.join(UP, f), os.path.join(dst, name)); out.append(name)
    os.makedirs(dst + '/wheels', exist_ok=True)                            # offline Pine parser (pynescript) and its dependencies
    for f in sorted(os.listdir(S)):
        if f.endswith('.whl'): shutil.copy2(os.path.join(S, f), dst + '/wheels/' + f); out.append('wheels/' + f)
    return out

def results():
    dst = OUT + '/results/gold'; os.makedirs(dst, exist_ok=True); out = []
    g = S + '/gold/'
    names = [f for f in os.listdir(g) if f.startswith(('slim_', 'greedy_pool_', 'anaA_', 'cands_', 'rulec', 'catalog_', 'crooks')) and f.endswith('.pkl')
             and '_before_' not in f and '_v1' not in f]                      # backups made before a change stay local
    names += ['greedy_%s.pkl' % tf for tf in TFS if os.path.exists(g + 'greedy_%s.pkl' % tf)]
    for f in sorted(names):
        target = f[len('slim_'):] if f.startswith('slim_final_') else f      # slim final_<TF>.pkl is restored under its normal name
        with open(os.path.join(dst, target + '.xz'), 'wb') as fo:
            subprocess.run(['xz', '-9', '-T4', '-c', g + f], stdout=fo, check=True)
        out.append(target)
    return out

def deliverables():
    dst = OUT + '/deliverables'; os.makedirs(dst, exist_ok=True); out = []
    for f in ('Gold_2021_2026_Auction_Retest.xlsx', 'VWAP_vs_EMA_results.md', 'VWAP_settings_and_70pct_strategies.md'):
        if os.path.exists(S + '/' + f): shutil.copy2(S + '/' + f, dst + '/' + f); out.append(f)
    return out

if __name__ == '__main__':
    if os.path.isdir(OUT + '/scratchpad'): shutil.rmtree(OUT + '/scratchpad')
    print('slim results:', slim_results())
    n, size, skipped = mirror(); print('mirrored %d files, %.1f MB; skipped (over 2 MB): %s' % (n, size / 1e6, skipped))
    print('inputs:', inputs())
    print('results:', results())
    print('deliverables:', deliverables())
