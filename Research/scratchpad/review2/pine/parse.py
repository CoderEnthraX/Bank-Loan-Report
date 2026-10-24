import sys
from pynescript.ast import parse
src=open(sys.argv[1]).read()
t=parse(src)
print(sys.argv[1], "OK", len(t.body))
