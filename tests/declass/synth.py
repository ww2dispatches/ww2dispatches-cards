# Synthetic catalog: two dispatches a day 1 Aug 2026 to 31 Jan 2027, film every third morning, Name This Wed and Sat.
import datetime, json, sys
from zoneinfo import ZoneInfo
D=ZoneInfo('America/Denver')
def utc(day,hm): return datetime.datetime.fromisoformat(f"{day}T{hm}:00").replace(tzinfo=D).astimezone(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
cards=[]; d=datetime.date(2026,8,1); n=0; nts=[]
while d<=datetime.date(2027,1,31):
    day=d.isoformat()
    for hm,tag in (('08:00','m'),('17:00','e')):
        n+=1; film=None
        if tag=='m' and n%3==1: film={"postAt":utc(day,'12:00'),"mp4":"x","poster":"x","caption":"c","sourceUrl":"","sound":False,"links":{}}
        cards.append({"kind":"dispatch","id":f"s-{day}-{tag}","num":n,"series":"battle","seriesName":"Battle Lines","short":f"S{n}","title":"t","date":"1944-01-01","place":"","era":"1944","format":"story","postAt":utc(day,hm),"img":"x","story":"","photoCredit":"","photoUrl":"","sources":[],"links":{},"film":film,"subjects":[],"theater":[],"nations":[]})
    if d.weekday() in (2,5): nts.append(day)
    d+=datetime.timedelta(1)
for i,day in enumerate(nts):
    cards.append({"kind":"namethis","id":f"namethis-s-{day}","num":None,"series":"namethis","seriesName":"Name This","short":"N","title":"a","answer":"a","clue":"c","date":"1944-01-01","place":"","era":"1944","format":"namethis","postAt":utc(day,'10:00'),"answerAt":utc(nts[i+1],'10:00') if i+1<len(nts) else None,"img":"x","imgPuzzle":"x","gameImages":False,"story":"","photoCredit":"","photoUrl":"","sources":[],"links":{},"film":None,"subjects":[],"theater":[],"nations":[]})
cards.sort(key=lambda c:(c['postAt'],c['id']))
json.dump({"version":1,"cards":cards},open(sys.argv[1],'w'))
print(len(cards))
