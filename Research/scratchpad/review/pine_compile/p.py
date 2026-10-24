import sys,time
from pynescript.ast import parse
f=sys.argv[1]
t=time.time()
try:
    tree=parse(open(f,encoding='utf8').read())
    print(f,"PARSE OK",len(tree.body),"top-level stmts",round(time.time()-t),"s")
except Exception as e:
    print(f,"PARSE FAIL",repr(e)[:800])
