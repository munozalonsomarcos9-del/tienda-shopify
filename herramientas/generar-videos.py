import os,sys,subprocess,glob,json
from PIL import Image,ImageFilter,ImageDraw,ImageFont,ImageEnhance
R='/home/user/tienda-shopify/fotos-volantes/'
W,H,FPS=1280,720,25
T={p['handle']:p['title'] for p in json.load(open('bp.json'))}
T.update({'volante-mercedes-benz-estilo-amg':'Volante Mercedes-Benz · Estilo AMG','volante-mercedes-benz-estilo-butterfly':'Volante Mercedes-Benz · Estilo Butterfly',
'volante-mercedes-benz-amg-generacion-anterior':'Volante Mercedes-Benz · AMG Generación Anterior','volante-mercedes-benz-linea-confort':'Volante Mercedes-Benz · Línea Confort',
'volante-volkswagen-cuero':'Volante Volkswagen · Cuero','volante-volkswagen-fibra-de-carbono':'Volante Volkswagen · Fibra de Carbono'})
FB=ImageFont.truetype('inter/InterVariable.ttf',40); FB.set_variation_by_axes([32,800])
FS=ImageFont.truetype('inter/InterVariable.ttf',20); FS.set_variation_by_axes([14,700])
def slide(path):
    im=Image.open(path).convert('RGB')
    bg=im.copy(); s=max(W/bg.width,H/bg.height); bg=bg.resize((int(bg.width*s)+2,int(bg.height*s)+2),Image.LANCZOS)
    bg=bg.crop(((bg.width-W)//2,(bg.height-H)//2,(bg.width-W)//2+W,(bg.height-H)//2+H)).filter(ImageFilter.GaussianBlur(28))
    bg=ImageEnhance.Brightness(bg).enhance(0.45)
    s=min(640/im.height,1180/im.width,2.5); fg=im.resize((int(im.width*s),int(im.height*s)),Image.LANCZOS)
    return bg,fg
def overlay(fr,title):
    d=ImageDraw.Draw(fr)
    brand,model=(title.replace('Volante ','').split(' · ')+[''])[:2]
    d.rectangle([48,H-118,54,H-46],fill=(255,194,26))
    d.text((70,H-122),brand.upper(),font=FS,fill=(255,194,26))
    d.text((68,H-96),model,font=FB,fill=(241,239,234),stroke_width=2,stroke_fill=(15,17,19))
def render(h):
    files=sorted(glob.glob(R+h+'/*.jpg')); n=len(files)
    per=6.0 if n==1 else max(1.4,min(4.0,8.0/n)); xf=0.4
    slides=[slide(f) for f in files]
    total=per*n; nf=int(total*FPS)
    out=f'vid/{h}.mp4'
    p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-preset','medium','-crf','21','-pix_fmt','yuv420p','-movflags','+faststart',out],stdin=subprocess.PIPE)
    def frame(k,t):
        bg,fg=slides[k]; z=1.0+0.07*(t/per)
        f2=fg.resize((int(fg.width*z),int(fg.height*z)),Image.BILINEAR)
        fr=bg.copy(); fr.paste(f2,((W-f2.width)//2,(H-f2.height)//2-10)); return fr
    for i in range(nf):
        t=i/FPS; k=min(int(t/per),n-1); lt=t-k*per
        fr=frame(k,lt)
        if n>1 and lt>per-xf:
            a=(lt-(per-xf))/xf; nk=(k+1)%n
            fr=Image.blend(fr,frame(nk,lt-per),a)
        overlay(fr,T[h]); p.stdin.write(fr.tobytes())
    p.stdin.close(); p.wait()
    print(h,n,round(total,1),os.path.getsize(out))
for h in sys.argv[1:]: render(h)
