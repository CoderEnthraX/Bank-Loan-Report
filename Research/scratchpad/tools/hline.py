import sys
from PIL import Image
import numpy as np
U='/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'
# find y of a thin bright horizontal line near y_guess at several x positions
f=sys.argv[1]; yg=int(sys.argv[2]); win=int(sys.argv[3]); xs=[int(v) for v in sys.argv[4].split(',')]
im=np.asarray(Image.open(U+f).convert('L')).astype(float)
for x in xs:
    col=im[yg-win:yg+win, x-15:x+15].max(axis=1)
    bg=np.median(col)
    y=np.argmax(col)
    print(x, yg-win+y, round(col[y]-bg,1))
