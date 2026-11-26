import json,sys,os
sys.path.insert(0,'/tmp/mr/build')
OUT='/home/claude/ww2dispatches-cards/campaign-series/bulge-1944'; os.makedirs(OUT,exist_ok=True)
from mr18 import MR
try:
    from mr930 import MR as MR2; MR.update(MR2)
except ImportError: pass
try: from text import TEXT
except ImportError: TEXT={}
import datetime
for n,mr in sorted(MR.items()):
    date=(datetime.date(1944,12,16)+datetime.timedelta(days=n-1)).isoformat()
    p=f'{OUT}/day-{n:02d}.json'
    rec=json.load(open(p)) if os.path.exists(p) else {}
    rec.update({"campaign":"bulge-1944","seriesName":"The Bulge","days":30,"time":"06:30","day":n,"date":date})
    rec.update(TEXT.get(n,{}))
    rec["mapRoom"]=mr
    json.dump(rec,open(p,'w'),indent=1,ensure_ascii=False)
print('wrote',len(MR))
