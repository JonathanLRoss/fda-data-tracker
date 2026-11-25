import gzip,json
from pipeline import convert,build,moves,METRICS

def payload(day,value):
    return {'daily':{'time':[day],**{m:[value] for m in METRICS}}}

def test_conversion():
    r=convert('2026-11-25','dallas',payload('2026-11-25',70)); assert r['item']=='Dallas'; assert r[METRICS[0]]==70

def test_history_replacement(tmp_path):
    d='2026-11-25'; p=tmp_path/'raw'/d/'dallas.json.gz'; p.parent.mkdir(parents=True)
    for value in [70,75]:
        p.write_bytes(gzip.compress(json.dumps(payload(d,value)).encode())); rows=build(tmp_path); assert len(rows)==1; assert rows[0][METRICS[0]]==value
    original=(tmp_path/'history.csv').read_bytes(); build(tmp_path); assert original==(tmp_path/'history.csv').read_bytes()

def test_moves():
    d='2026-11-25'; a=convert(d,'dallas',payload(d,70)); b=convert(d,'dallas',payload(d,75)); c=convert(d,'miami',payload(d,80)); assert moves([a],[b,c])==([('dallas',70,75)],['miami'],[])
