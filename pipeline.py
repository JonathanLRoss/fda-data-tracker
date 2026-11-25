import csv, gzip, json, urllib.request, urllib.parse, sys
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data'
CITIES={'little-rock':('Little Rock',34.75,-92.29),'fayetteville':('Fayetteville',36.06,-94.16),'dallas':('Dallas',32.78,-96.8),'houston':('Houston',29.76,-95.37),'new-york':('New York',40.71,-74.01),'chicago':('Chicago',41.88,-87.63),'los-angeles':('Los Angeles',34.05,-118.24),'miami':('Miami',25.76,-80.19),'denver':('Denver',39.74,-104.99),'atlanta':('Atlanta',33.75,-84.39)}
METRICS=['temperature_2m_max','temperature_2m_min','precipitation_sum','wind_speed_10m_max']
FIELDS=['date','item_id','item','source']+METRICS

def convert(day,key,payload):
    daily=payload['daily']; i=daily['time'].index(day)
    return dict(date=day,item_id=key,item=CITIES[key][0],source=key,**{m:daily[m][i] for m in METRICS})

def build(data=DATA):
    rows=[]
    for p in sorted((data/'raw').glob('*/*.json.gz')):
        with gzip.open(p,'rt') as f: rows.append(convert(p.parent.name,p.name.removesuffix('.json.gz'),json.load(f)))
    rows.sort(key=lambda r:(r['date'],r['item_id']))
    data.mkdir(exist_ok=True,parents=True)
    with (data/'history.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS); w.writeheader(); w.writerows(rows)
    return rows

def moves(old,new):
    a={r['item_id']:r for r in old}; b={r['item_id']:r for r in new}; m=METRICS[0]
    changes=[(k,a[k][m],b[k][m]) for k in a.keys() & b.keys() if a[k][m] is not None and b[k][m] is not None]
    return sorted(changes,key=lambda x:(-abs(x[2]-x[1]),x[0]))[:5],sorted(b.keys()-a.keys()),sorted(a.keys()-b.keys())

def run():
    now=datetime.now(timezone.utc); day=now.date().isoformat(); folder=DATA/'raw'/day; folder.mkdir(parents=True,exist_ok=True)
    statuses=[]
    for key,(_,lat,lon) in CITIES.items():
        p=folder/f'{key}.json.gz'; p.unlink(missing_ok=True)
        try:
            params=dict(latitude=lat,longitude=lon,daily=','.join(METRICS),timezone='UTC',start_date=day,end_date=day,temperature_unit='fahrenheit',wind_speed_unit='mph',precipitation_unit='inch')
            with urllib.request.urlopen('https://api.open-meteo.com/v1/forecast?'+urllib.parse.urlencode(params),timeout=30) as response: raw=response.read()
            convert(day,key,json.loads(raw)); p.write_bytes(gzip.compress(raw,mtime=0)); statuses.append(dict(name=key,ok=True,count=1))
        except Exception as e: print(key,e); statuses.append(dict(name=key,ok=False,count=0))
    rows=build(); dates=sorted({r['date'] for r in rows}); previous=[d for d in dates if d<day]; old=[r for r in rows if previous and r['date']==previous[-1]]; new=[r for r in rows if r['date']==day]; changes,added,gone=moves(old,new)
    status=dict(run_time=now.isoformat(),first_run_date=dates[0] if dates else None,days_with_success=len(dates),items=len(new),new_today=added,gone_today=gone,sources=statuses)
    (DATA/'status.json').write_text(json.dumps(status,indent=2)+'\n')
    report=['# Daily weather changes',f'Date: {day}','Maximum temperature changes (°F):']+[f'- {k}: {a} → {b} ({b-a:+.1f})' for k,a,b in changes]+['New: '+(', '.join(added) or 'None'),'Gone: '+(', '.join(gone) or 'None')]
    (DATA/'issue.md').write_text('\n'.join(report)+'\n')

if __name__=='__main__':
    build() if '--build' in sys.argv else run()
