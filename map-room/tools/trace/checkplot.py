import cv2,numpy as np,json,sys
from georef import px
def plot(scan,x0,y0,geo,center,r,out,size=900):
    im=cv2.imread(scan); X,Y=px(*center); X=int(X-x0); Y=int(Y-y0)
    for k,pl in geo.items():
        for q in pl:
            x,y=px(*q); cv2.circle(im,(int(x-x0),int(y-y0)),max(3,r//150),(0,0,255),-1)
    cv2.imwrite(out,cv2.resize(im[Y-r:Y+r,X-r:X+r],(size,size)))
if __name__=='__main__':
    geo=json.load(open(sys.argv[1]));geo=geo.get('rivers',geo.get('roads',geo))
    plot('/home/claude/loc/dec25-main.jpg',700,450,geo,(float(sys.argv[2]),float(sys.argv[3])),int(sys.argv[4]),sys.argv[5])
