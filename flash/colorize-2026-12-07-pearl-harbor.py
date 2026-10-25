import numpy as np, sys
from PIL import Image, ImageFilter
src=Image.open('shaw.jpg').convert('L'); W,H=src.size
L=np.asarray(src).astype(np.float32)/255
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
def sm(e0,e1,x): t=np.clip((x-e0)/(e1-e0),0,1); return t*t*(3-2*t)
def blur(m,r): return np.asarray(Image.fromarray((np.clip(m,0,1)*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))).astype(np.float32)/255
def hx(h): h=h.lstrip('#'); return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))
def ramp(stops,v=L):
    xs=[s[0] for s in stops]; o=np.zeros(v.shape+(3,),np.float32)
    for c in range(3): o[...,c]=np.interp(v,xs,[hx(s[1])[c] for s in stops])
    return o
# local variance (smoothness) to tell sky from smoke
Lb=blur(L,3); var=blur((L-Lb)**2,12)*400
smooth=1-sm(0.02,0.12,var)
# masks
fire_prior=np.exp(-(((xx-1830)/520)**2+((yy-1000)/360)**2))
fire=blur(fire_prior*sm(0.5,0.78,L),8)
core=blur(fire_prior*sm(0.8,0.97,L),4)
palm=blur((1-sm(0.18,0.32,L))*(1-sm(820,980,yy))*(1-fire_prior*2),2)
sky_prior=(1-sm(900,1150,yy))*(1-sm(1150,1700,xx))*(1-fire_prior*2.5)
sky=blur(sky_prior*sm(0.5,0.75,L)*(0.4+0.6*smooth),20)
smoke=blur((1-sm(1150,1300,yy))*sm(0.3,0.55,L)*(1-sky)*(1-fire)*(1-palm),10)
water=sm(1395,1470,yy)*(1-sm(1700,1760,yy))
pier=water*(1-sm(0.18,0.4,L))
ground=sm(1730,1790,yy)
grass=sm(1930,1975,yy)
right=sm(2250,2400,xx)*(1-sm(900,1150,yy))*sm(1000,1150,yy)*(1-sm(0.35,0.6,L))*(1-palm)
out=ramp([(0,'#120f0c'),(0.3,'#4a403a'),(0.65,'#a89c8c'),(1,'#f4efe4')])   # warm base (smoke, concrete, structures)
def mix(mask,col,k=1):
    global out; m=np.clip(mask*k,0,1)[...,None]; out=out*(1-m)+col*m
mix(smoke, ramp([(0,'#2a2522'),(0.4,'#6a625b'),(0.75,'#b7ada2'),(1,'#f2ede6')]),0.9)
mix(sky,   ramp([(0,'#2e4f73'),(0.6,'#5f8fbe'),(0.85,'#b9d2e8'),(1,'#f3f7fb')]),0.95)
mix(palm,  ramp([(0,'#0a1a0e'),(0.25,'#1f3a22'),(0.6,'#4f6d3c'),(1,'#9cb07a')]),0.95)
mix(water, ramp([(0,'#122a32'),(0.35,'#2a5a68'),(0.65,'#6d9ca4'),(0.85,'#bcd4d6'),(1,'#f0f6f4')]),0.75)
mix(pier,  ramp([(0,'#0d0c0a'),(0.5,'#4a3f33'),(1,'#9a8d7c')]),0.9)
mix(ground,ramp([(0,'#2e2a24'),(0.5,'#8f887a'),(0.8,'#d6cfbf'),(1,'#f3efe5')]),0.9)
mix(grass, ramp([(0,'#232a18'),(0.5,'#5c6a3c'),(1,'#a3ab78')]),0.8)
mix(right, ramp([(0,'#2b241e'),(0.5,'#6f6050'),(1,'#c9bba6')]),0.6)
mix(fire,  ramp([(0,'#3a1206'),(0.5,'#a63a12'),(0.68,'#e8721f'),(0.84,'#ffbf4d'),(1,'#fff3d2')]),0.97)
mix(core,  ramp([(0,'#ffd27a'),(1,'#fffaf0')]),0.8)
# Kodachrome grade: richer saturation, slight warm shift, gentle S curve
g=out.mean(2,keepdims=True); out=np.clip(g+(out-g)*1.22,0,1)
out=out*np.array([1.03,1.0,0.96],np.float32)
out=np.clip((out-0.5)*1.08+0.5,0,1)
# faint grain
rng=np.random.default_rng(7); out=np.clip(out+rng.normal(0,0.012,out.shape).astype(np.float32),0,1)
Image.fromarray((out*255).astype(np.uint8)).save('shaw-kodachrome.jpg',quality=95,subsampling=0)
Image.fromarray((out*255).astype(np.uint8)).resize((1250,1000),Image.LANCZOS).save('k_preview.jpg',quality=88)
print('ok')
