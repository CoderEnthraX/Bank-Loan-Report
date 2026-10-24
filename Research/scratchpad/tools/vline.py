import sys
from PIL import Image
import numpy as np
U='/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'
f=sys.argv[1]; xg=int(sys.argv[2]); win=int(sys.argv[3]); ys=[int(v) for v in sys.argv[4].split(',')]
im=np.asarray(Image.open(U+f).convert('L')).astype(float)
for y in ys:
    row=im[y-15:y+15, xg-win:xg+win].max(axis=0)
    bg=np.median(row); x=np.argmax(row)
    print(y, xg-win+x, round(row[x]-bg,1))
