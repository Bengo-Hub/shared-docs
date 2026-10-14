import sys
from PIL import Image, ImageChops, ImageFilter, ImageDraw, ImageOps
S=sys.argv[1]
src=Image.open('assets/agent-source.jpg').convert('RGB')
im=src.resize((src.width*2,src.height*2),Image.LANCZOS)
lg=Image.open('assets/codevertex-logo.png').convert('RGBA')
lg=lg.crop(lg.getbbox())
W=int(sys.argv[2]) if len(sys.argv)>2 else 150
SC=4  # work at 4x then downsample for smooth edges
big=lg.resize((W*SC,int(lg.height*W*SC/lg.width)),Image.LANCZOS)
a=big.split()[3].point(lambda p:255 if p>110 else 0).filter(ImageFilter.GaussianBlur(1.2))
# thread colour: keep logo hue, slightly richer
rgb=big.convert('RGB')
# stitch texture: fine diagonal satin lines
tex=Image.new('L',big.size,0); d=ImageDraw.Draw(tex)
for k in range(-big.height,big.width,6):
    d.line([(k,big.height),(k+big.height,0)],fill=255,width=3)
tex=tex.filter(ImageFilter.GaussianBlur(1))
shade=tex.point(lambda p:int(205+p*50/255))  # 205..255
thread=ImageChops.multiply(rgb,Image.merge('RGB',[shade]*3))
# bevel: highlight top-left, shadow bottom-right inside the shape
blur=a.filter(ImageFilter.GaussianBlur(3))
hi=ImageChops.subtract(blur,ImageChops.offset(blur,3,3))
lo=ImageChops.subtract(blur,ImageChops.offset(blur,-3,-3))
thread=Image.composite(Image.new('RGB',big.size,(255,255,255)),thread,hi.point(lambda p:min(255,p*2)).point(lambda p:int(p*.45)))
thread=Image.composite(Image.new('RGB',big.size,(0,0,0)),thread,lo.point(lambda p:min(255,p*2)).point(lambda p:int(p*.45)))
# downsample
w,h=W,big.height//SC
thread=thread.resize((w,h),Image.LANCZOS); a=a.resize((w,h),Image.LANCZOS)
rot=-3
thread=thread.rotate(rot,resample=Image.BICUBIC,expand=True,fillcolor=(255,255,255)); a=a.rotate(rot,resample=Image.BICUBIC,expand=True)
x,y=int(sys.argv[3]),int(sys.argv[4])
region=im.crop((x,y,x+a.width,y+a.height))
# cast shadow of raised thread onto fabric
sh=a.filter(ImageFilter.GaussianBlur(2)); 
shadow=ImageChops.offset(sh,1,2).point(lambda p:int(p*.35))
region=Image.composite(Image.new('RGB',region.size,(60,50,60)),region,shadow)
# fabric shading: modulate thread by local fabric luminance (folds)
lum=ImageOps.grayscale(region).filter(ImageFilter.GaussianBlur(4))
mx=max(1,lum.getextrema()[1])
lumn=lum.point(lambda p:int(min(255,p*255/mx*1.02)))
thread=ImageChops.multiply(thread,Image.merge('RGB',[lumn]*3))
region.paste(thread,(0,0),a)
im.paste(region,(x,y))
im.crop((440,620,940,1080)).save(S+'/embroidery-zoom.png')
# extend to landscape 1640x1280
CW,CH=1640,1280
person=im.crop((0,0,1024,CH))
bg=person.resize((CW,int(CH*CW/1024))).crop((0,0,CW,CH)).filter(ImageFilter.GaussianBlur(40))
px=CW-1024-40
mask=Image.new('L',(1024,CH),255); d=ImageDraw.Draw(mask)
for i in range(120): d.line([(i,0),(i,CH)],fill=int(255*i/120))
for i in range(40): d.line([(1023-i,0),(1023-i,CH)],fill=int(255*i/40))
bg.paste(person,(px,0),mask)
bg.save('assets/codevertex-agent.jpg',quality=93)
