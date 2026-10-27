import base64, glob, json, os, re, io, sys, time
from PIL import Image
RES='/root/.claude/projects/-home-claude/05ad12da-e9fa-5c6f-a6a7-c2722d9e34f3/tool-results/'
DST='/home/claude/work/farvalle2/tiles/'
since=float(sys.argv[1]) if len(sys.argv)>1 else time.time()-3600
n=0
for f in sorted(glob.glob(RES+'mcp-remote-devices-Claude_Browser__javascript_tool-*.txt')):
    if os.path.getmtime(f) < since: continue
    try: d=json.load(open(f)); txt=''.join(x.get('text','') for x in d)
    except Exception: txt=open(f,errors='ignore').read()
    txt=txt.replace('\\n','\n')
    for m in re.finditer(r'NFTILE:(\d+/\d+/\d+):([A-Za-z0-9+/]+=*)', txt):
        t=m.group(1); p=DST+t+'.png'
        if os.path.exists(p): continue
        try: data=base64.b64decode(m.group(2)); im=Image.open(io.BytesIO(data)); im.load()
        except Exception as e: print('inválido',t,str(e)[:50]); continue
        os.makedirs(os.path.dirname(p),exist_ok=True); open(p,'wb').write(data); n+=1
print('novos',n, 'total', len(glob.glob(DST+'*/*/*.png')))
