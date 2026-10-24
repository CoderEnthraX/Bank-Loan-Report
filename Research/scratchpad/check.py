import sys, re
src = open(sys.argv[1], encoding='utf-8').read().split('\n')
errs = []
for i, line in enumerate(src, 1):
    if '\t' in line: errs.append((i, 'tab'))
    s = line.rstrip()
    if not s.strip() or s.strip().startswith('//'): continue
    ind = len(s) - len(s.lstrip(' '))
    if ind % 4: errs.append((i, f'indent {ind}'))
    # strip strings and comments
    code = re.sub(r'"(?:[^"\\]|\\.)*"', '""', s)
    code = code.split('//')[0]
    if code.count('"') % 2: errs.append((i, 'quote'))
    for a, b in ['()', '[]']:
        if code.count(a) != code.count(b): errs.append((i, f'unbalanced {a}{b}: {code.count(a)} vs {code.count(b)}'))
print('\n'.join(f'{i}: {e}' for i, e in errs) or 'OK: no indentation/bracket issues')
