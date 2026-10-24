import sys
from PIL import Image
im=Image.open('/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/%s-image.png'%sys.argv[1]).convert('RGB')
y0=int(sys.argv[2])
a=im.crop((0,y0,950,y0+20)); b=im.crop((950,y0,1900,y0+20))
c=Image.new('RGB',(950,40)); c.paste(a,(0,0)); c.paste(b,(0,20)); c=c.resize((1425,60)); c.save(sys.argv[3])
