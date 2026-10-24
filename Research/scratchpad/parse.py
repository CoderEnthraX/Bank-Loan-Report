import sys
from pynescript.ast import parse
src = open(sys.argv[1], encoding='utf-8').read()
tree = parse(src)
print("parsed OK, top-level statements:", len(tree.body))
