"""Generate deterministic, interrelated synthetic ticketing data; events entry point.
Shared engine is here so the package contains exactly five Python files.
No third-party Python dependencies. SQL loading uses Microsoft's sqlcmd CLI.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import hashlib
import json
import math
from pathlib import Path
import random
import re
import shutil
import subprocess

VERSION = '1.1'
TABLES = ('events', 'ticket_types', 'orders', 'order_items', 'payments')
AS_OF = datetime(2026, 9, 1, 0, 0, 0)


def build_dataset(count=100000, seed=20260909, year=None):
    rng = random.Random(seed)
    data = {t: [] for t in TABLES}
    cities = [('Hà Nội','Không gian Sông Xanh'),('TP. Hồ Chí Minh','Nhà hát Ánh Sao'),
              ('Đà Nẵng','Sân khấu Biển Chiều'),('Đà Lạt','Vườn nhạc Sương Mai')]
    genres = [('CONCERT','Giai điệu mùa hạ',450000),('ACOUSTIC','Lời hát trong mây',250000),
              ('THEATRE','Chuyện của phố',180000),('WORKSHOP','Xưởng sáng tạo',150000)]
    # Fictional business names; keep provenance in metadata, not display values.
    titles = {
        'CONCERT': ['Thanh âm đầu năm', 'Những ngày rực rỡ', 'Thành phố lên đèn',
                    'Giai điệu mùa hạ', 'Chạm vào thanh xuân', 'Bầu trời ký ức',
                    'Đêm của những giấc mơ', 'Nhịp đập phố thị', 'Hẹn mùa thu'],
        'ACOUSTIC': ['Lời hát trong mây', 'Một chiều bình yên', 'Tháng ba dịu dàng',
                     'Những bản tình ca', 'Mình kể chuyện nhau', 'Nắng qua hiên nhà',
                     'Gửi người thương nhớ', 'Lặng nghe mùa về', 'Hẹn nhau cuối tuần'],
        'THEATRE': ['Chuyện của phố', 'Căn nhà cuối ngõ', 'Bức thư chưa gửi',
                    'Người về từ ký ức', 'Một ngày khác', 'Sau cánh cửa',
                    'Chuyến tàu đêm', 'Khoảng trời riêng', 'Bên kia mùa hạ'],
        'WORKSHOP': ['Làm gốm thủ công', 'Vẽ màu nước cơ bản', 'Pha cà phê tại nhà',
                     'Cắm hoa theo mùa', 'Làm nến thơm', 'Nhiếp ảnh đường phố',
                     'Làm bánh cuối tuần', 'Vẽ túi canvas', 'Thiết kế sổ tay']}
    organizers = {'CONCERT': 'Thanh Âm Entertainment', 'ACOUSTIC': 'Mộc Music',
                  'THEATRE': 'Sân khấu Phố Nhỏ', 'WORKSHOP': 'Hiên Nhà Creative Studio'}
    weights, type_map = [], {}
    # Demand/quota scale with requested volume; small events have fewer orders.
    raw_weights = [rng.lognormvariate(0,0.9) for _ in range(36)]
    for i in range(1,37):
        category, title, base = genres[(i-1)%4]
        title = titles[category][(i-1)//4]
        city, venue = cities[(i//4)%4]
        start = datetime(year or 2026,2,7,19) + timedelta(days=(i-1)*(9 if year else 6))
        start += timedelta(days=(5-start.weekday())%7)  # Saturday evenings
        opening = start - timedelta(days=rng.choice([35,45,60]))
        if year:
            opening = max(opening, datetime(year, 1, 1))
            base = round(base * (0.80 + 0.05 * (year - 2022)) / 1000) * 1000
        closing = start - timedelta(hours=2)
        popularity = raw_weights[i-1] * (1.5 if category == 'CONCERT' else 1)
        weights.append(popularity)
        event = dict(event_id=i,event_code=f'EVT{start:%Y%m}{i:03}',event_name=f'{title} | {city}' + (f' | {year}' if year else ''),
                     category=category,organizer_name=organizers[category],
                     venue_name=venue,province=city,capacity=1,
                     starts_at=start,ends_at=start+timedelta(hours=3),sales_start_at=opening,
                     sales_end_at=closing,event_status='COMPLETED' if start < AS_OF else 'ON_SALE',
                     created_at=opening-timedelta(days=7),updated_at=min(start+timedelta(hours=3),AS_OF))
        data['events'].append(event)
        type_map[i] = []
        for j,(code,name,mult) in enumerate([('STANDARD','Phổ thông',1),('PREMIUM','Ưu tiên',1.5),('VIP','VIP',2.5)]):
            row = dict(ticket_type_id=(i-1)*3+j+1,event_id=i,ticket_type_code=code,ticket_type_name=name,
                       list_price=int(base*mult),sale_quota=1,created_at=event['created_at'],updated_at=opening)
            type_map[i].append(row)
            data['ticket_types'].append(row)
    sold = Counter()
    for event,w in zip(data['events'],weights):
        expected = count*w/sum(weights)
        # Different sell-through targets; approximate 1.9 tickets/paid order.
        cap = max(80,math.ceil(expected*1.9/rng.uniform(.55,.93)))
        quotas = [int(cap*.70),int(cap*.20)]
        quotas.append(cap-sum(quotas))
        for t,q in zip(type_map[event['event_id']],quotas):
            t['sale_quota'] = q
        event['capacity'] = cap

    for oid in range(1,count+1):
        e = rng.choices(data['events'],weights=weights)[0]
        end = min(e['sales_end_at']-timedelta(minutes=20),AS_OF-timedelta(minutes=20))
        phase = rng.choices(['EARLY','REGULAR','LATE'],[.30,.45,.25])[0]
        frac = {'EARLY':rng.uniform(.001,.18),'REGULAR':rng.uniform(.18,.82),'LATE':rng.uniform(.82,.999)}[phase]
        at = e['sales_start_at'] + (end-e['sales_start_at'])*frac
        at = at.replace(hour=rng.choices([9,12,15,18,19,20,21,22],[1,2,1,2,3,4,3,1])[0],
                        minute=rng.randrange(60),second=rng.randrange(60),microsecond=0)
        at = min(max(at,e['sales_start_at']),end)
        types = type_map[e['event_id']]
        first = rng.choices(types,[.68,.23,.09])[0]
        selected = [first]
        if rng.random()<.12:
            selected.append(rng.choice([t for t in types if t != first]))
        lines = []
        for t in selected:
            qty = rng.choices([1,2,3,4,5,6],[38,43,10,6,2,1])[0]
            rate = rng.choice([10,15]) if phase == 'EARLY' else rng.choices([0,5,10],[85,10,5])[0]
            gross = qty*t['list_price']
            discount = (gross*rate//100//1000)*1000
            lines.append(dict(order_item_id=len(data['order_items'])+len(lines)+1,order_id=oid,event_id=e['event_id'],
                              ticket_type_id=t['ticket_type_id'],quantity=qty,unit_price=t['list_price'],
                              discount_amount=discount,line_amount=gross-discount,created_at=at,updated_at=at))
        channel = None
        if year:
            app_share = .22 + .06 * (year - 2022)
            channel = rng.choices(['WEB', 'APP'], [1-app_share, app_share])[0]
            paid_rate = .79 + .015 * (year - 2022) + (.035 if channel == 'APP' else 0)
            status = rng.choices(['PAID','EXPIRED','CANCELLED'], [paid_rate, 1-paid_rate-.05, .05])[0]
        else:
            status = rng.choices(['PAID','EXPIRED','CANCELLED'],[86,10,4])[0]
        if any(sold[l['ticket_type_id']]+l['quantity'] > next(t['sale_quota'] for t in types if t['ticket_type_id']==l['ticket_type_id']) for l in lines):
            status = 'EXPIRED'
        # Include a few orders still pending at the observation cutoff.
        if oid%500==0 and e['sales_end_at']>AS_OF:
            status='PENDING'
            at=AS_OF-timedelta(minutes=2)
            for l in lines:
                l['created_at']=l['updated_at']=at
        gross=sum(l['quantity']*l['unit_price'] for l in lines)
        discount=sum(l['discount_amount'] for l in lines)
        order=dict(order_id=oid,event_id=e['event_id'],order_code=f'ORD{at:%Y%m%d}{oid:09}',ordered_at=at,
                   expires_at=at+timedelta(minutes=15),sales_channel=channel or rng.choices(['WEB','APP'],[.58,.42])[0],
                   order_status=status,subtotal_amount=gross,discount_amount=discount,total_amount=gross-discount,
                   currency='VND',created_at=at,updated_at=at)
        outcomes=[]
        if status == 'PAID':
            outcomes=['FAILED']*rng.choices([0,1,2],[80,17,3])[0]+['SUCCESS']
        elif status == 'PENDING':
            outcomes=['PENDING']
        elif rng.random()<.70:
            outcomes=['FAILED']*rng.choices([1,2,3],[70,25,5])[0]
        cursor=at
        for outcome in outcomes:
            pid=len(data['payments'])+1
            initiated=cursor+timedelta(seconds=rng.randint(15,40))
            finished=None if outcome=='PENDING' else initiated+timedelta(seconds=rng.randint(15,80))
            method=rng.choices(['WALLET','DOMESTIC_CARD','QR_BANK'],[40,20,40])[0]
            updated=finished+timedelta(seconds=rng.randint(1,20)) if finished else initiated
            data['payments'].append(dict(payment_id=pid,order_id=oid,merchant_transaction_id=f'TXN{initiated:%Y%m%d}{pid:010}',
                partner_transaction_id=f'PAY{initiated:%Y%m%d}{pid:010}' if outcome!='PENDING' else None,
                payment_partner='PAYGATE',payment_method=method,payment_amount=order['total_amount'],currency='VND',
                payment_status=outcome,failure_reason=rng.choice(['TIMEOUT','USER_ABORT','BANK_DECLINED']) if outcome=='FAILED' else None,
                initiated_at=initiated,completed_at=finished,paid_at=finished if outcome=='SUCCESS' else None,
                created_at=initiated,updated_at=updated))
            cursor=updated
        if status=='PAID':
            for l in lines:
                sold[l['ticket_type_id']]+=l['quantity']
            order['updated_at']=cursor
        elif status=='EXPIRED':
            order['updated_at']=order['expires_at']
        elif status=='CANCELLED':
            order['updated_at']=max(cursor,at+timedelta(minutes=10))
        data['orders'].append(order)
        data['order_items'].extend(lines)
    validate(data)
    return data


def validate(data):
    events={x['event_id']:x for x in data['events']}
    types={x['ticket_type_id']:x for x in data['ticket_types']}
    orders={x['order_id']:x for x in data['orders']}
    amounts=Counter(); gross=Counter(); discounts=Counter(); sold=Counter(); successes=Counter()
    for row in data['order_items']:
        o=orders[row['order_id']]; t=types[row['ticket_type_id']]
        assert o['event_id']==t['event_id']==row['event_id']
        assert row['line_amount']==row['quantity']*row['unit_price']-row['discount_amount']>0
        amounts[o['order_id']]+=row['line_amount']
        gross[o['order_id']]+=row['quantity']*row['unit_price']
        discounts[o['order_id']]+=row['discount_amount']
        if o['order_status']=='PAID': sold[t['ticket_type_id']]+=row['quantity']
    for p in data['payments']:
        o=orders[p['order_id']]
        assert p['payment_amount']==o['total_amount']
        assert o['ordered_at']<=p['initiated_at']<o['expires_at']
        assert p['updated_at']<=AS_OF
        if p['payment_status']=='SUCCESS':
            successes[o['order_id']]+=1
            assert p['paid_at']<o['expires_at'] and p['paid_at']<=events[o['event_id']]['sales_end_at']
    for o in orders.values():
        e=events[o['event_id']]
        assert e['sales_start_at']<=o['ordered_at']<e['sales_end_at']
        assert amounts[o['order_id']]==o['total_amount']
        assert gross[o['order_id']]==o['subtotal_amount'] and discounts[o['order_id']]==o['discount_amount']
        assert successes[o['order_id']]==(1 if o['order_status']=='PAID' else 0)
    assert all(sold[t['ticket_type_id']]<=t['sale_quota'] for t in types.values())
    for table in data.values():
        for row in table: assert row['created_at']<=row['updated_at']<=AS_OF


def literal(v):
    if v is None: return 'NULL'
    if isinstance(v,int): return str(v)
    if isinstance(v,datetime): return "'"+v.isoformat(timespec='seconds')+"'"
    return "N'"+str(v).replace("'","''")+"'"


def execute_file(path,server,database):
    executable=shutil.which('sqlcmd')
    if not executable: raise RuntimeError('Install sqlcmd or open the SQL files in SSMS.')
    result=subprocess.run([executable,'-S',server,'-d',database,'-E','-C','-b','-l','10','-t','120',
                    '-f','65001','-i',str(path)],capture_output=True,text=True,errors='replace')
    print(result.stdout)
    if result.returncode or 'timeout expired' in (result.stdout+result.stderr).lower():
        raise RuntimeError('SQL load failed: '+result.stdout+result.stderr)


def run(table):
    parser=argparse.ArgumentParser(description=f'Generate and optionally load dbo.{table}; all data SYNTHETIC.')
    parser.add_argument('--orders',type=int,default=100000)
    parser.add_argument('--seed',type=int,default=20260909)
    parser.add_argument('--output',type=Path,default=Path(__file__).parent/'generated')
    parser.add_argument('--load',action='store_true')
    parser.add_argument('--server',default='localhost')
    parser.add_argument('--database',default='TicketingDB')
    args=parser.parse_args()
    if args.orders<1: parser.error('--orders must be positive')
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*',args.database): parser.error('Use a simple database name')
    data=build_dataset(args.orders,args.seed)
    args.output.mkdir(parents=True,exist_ok=True)
    config={'generator_version':VERSION,'seed':args.seed,'orders':args.orders,'as_of':AS_OF.isoformat(),
            'time_zone':'Asia/Ho_Chi_Minh (UTC+07:00)','synthetic':True}
    manifest=args.output/'manifest.json'
    if manifest.exists() and json.loads(manifest.read_text(encoding='utf-8'))['config']!=config:
        raise RuntimeError('Output already contains another dataset. Choose a new --output directory.')
    summary={'config':config,'rows':{t:len(rows) for t,rows in data.items()},
             'order_status':dict(Counter(o['order_status'] for o in data['orders'])),
             'payment_status':dict(Counter(p['payment_status'] for p in data['payments'])),
             'paid_ticket_value_vnd':sum(o['total_amount'] for o in data['orders'] if o['order_status']=='PAID'),
             'validation':'PASS: foreign keys, totals, quotas, time windows, success per order'}
    manifest.write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    rows=data[table]; columns=list(rows[0])
    target=args.output/f'{TABLES.index(table)+1:02}_{table}.sql'
    with target.open('w',encoding='utf-8') as f:
        f.write(':ON ERROR EXIT\n')
        f.write(f'-- SYNTHETIC dataset {VERSION}, seed={args.seed}, orders={args.orders}\n')
        f.write(f'USE [{args.database}];\nSET XACT_ABORT ON;\nBEGIN TRANSACTION;\n')
        f.write('SET NOCOUNT ON; SET QUOTED_IDENTIFIER ON; SET ANSI_NULLS ON; SET ANSI_PADDING ON;\n'
                'SET ANSI_WARNINGS ON; SET ARITHABORT ON; SET CONCAT_NULL_YIELDS_NULL ON; SET NUMERIC_ROUNDABORT OFF;\n')
        f.write(f"IF EXISTS (SELECT 1 FROM dbo.[{table}]) THROW 50002, 'Table must be empty; no existing records will be overwritten.', 1;\n")
        f.write('GO\n')
        for start in range(0,len(rows),500):
            # OPENJSON avoids compiling hundreds of thousands of scalar VALUES expressions.
            payload=json.dumps(rows[start:start+500],ensure_ascii=False,default=lambda v:v.isoformat(timespec='seconds'))
            specs=[]
            for c in columns:
                if c.endswith('_at'): sqltype='datetime2(0)'
                elif c.endswith('_amount') or c in ('list_price','unit_price'): sqltype='decimal(18,0)'
                elif isinstance(rows[0][c],int): sqltype='bigint'
                else: sqltype='nvarchar(4000)'
                specs.append(f"[{c}] {sqltype} '$.{c}'")
            f.write(f"INSERT INTO dbo.[{table}] ("+','.join('['+c+']' for c in columns)+')\n')
            f.write('SELECT '+','.join('['+c+']' for c in columns)+' FROM OPENJSON('+literal(payload)+')\nWITH ('+','.join(specs)+');\nGO\n')
        f.write('COMMIT;\n')
    preview=args.output/f'{table}_preview.json'
    preview.write_text(json.dumps(rows[:10],ensure_ascii=False,indent=2,default=str),encoding='utf-8')
    digest=hashlib.sha256(target.read_bytes()).hexdigest()
    (args.output/f'{table}.sha256').write_text(digest+'\n',encoding='ascii')
    print(json.dumps({'table':table,'rows':len(rows),'sql_file':str(target),'sha256':digest}))
    if args.load: execute_file(target,args.server,args.database)


if __name__=='__main__':
    run('events')
