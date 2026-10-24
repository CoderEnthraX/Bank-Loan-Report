import sys
# usage: fit.py "p1:y1,p2:y2,..." y_a y_b ...   -> prints price for each y
pts=[tuple(map(float,s.split(':'))) for s in sys.argv[1].split(',')]
n=len(pts); mp=sum(p for p,_ in pts)/n; my=sum(y for _,y in pts)/n
b=sum((p-mp)*(y-my) for p,y in pts)/sum((p-mp)**2 for p,_ in pts); a=my-b*mp
print('px/unit',round(b,5),'resid',[round(y-(a+b*p),2) for p,y in pts])
for s in sys.argv[2:]:
    y=float(s); print(s, round((y-a)/b,2))
