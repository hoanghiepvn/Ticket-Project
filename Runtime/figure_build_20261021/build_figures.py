from pathlib import Path
from html import escape
from PIL import ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Reports' / 'Figures_Thesis'
OUT.mkdir(parents=True, exist_ok=True)
NAVY, INK, GRAY = '#203D54', '#172B3A', '#526572'
LINE, LIGHT = '#607582', '#F4F7F9'
BRONZE, SILVER, GOLD = '#A86729', '#507985', '#987619'
BF, SF, GF = '#FBF3EA', '#EFF5F6', '#FCF7E8'


class Figure:
    def __init__(self, name, w, h, title, subtitle):
        self.name, self.w, self.h = name, w, h
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">',
            f'<title>{escape(title)}</title>',
            '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#607582"/></marker></defs>',
            f'<rect width="{w}" height="{h}" fill="white"/>']
        self.text(w/2, 65, title, 43, NAVY, True, 'middle')
        self.text(w/2, 112, subtitle, 30, GRAY, anchor='middle')

    def rect(self,x,y,w,h,fill='white',stroke='#C5D0D7',radius=14,dash=False):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="2"'+(' stroke-dasharray="10 8"' if dash else '')+'/>')

    def text(self,x,y,s,size=34,color=INK,bold=False,anchor='start'):
        font = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf' if bold else 'C:/Windows/Fonts/arial.ttf', size)
        width = font.getlength(s)
        left = x if anchor == 'start' else x-width if anchor == 'end' else x-width/2
        assert left >= -2 and left+width <= self.w+2, (self.name,s,left,width)
        assert y >= 0 and y <= self.h, (self.name,s,y)
        self.parts.append(f'<text x="{x}" y="{y}" font-family="Arial, sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="{color}" text-anchor="{anchor}">{escape(s)}</text>')

    def lines(self,x,y,items,size=34,gap=49,color=INK,bold=False,anchor='start'):
        for i,s in enumerate(items): self.text(x,y+i*gap,s,size,color,bold,anchor)

    def path(self,pts,dashed=False,arrow=True,color=LINE,width=3):
        d='M '+' L '.join(f'{x} {y}' for x,y in pts)
        self.parts.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round"'+(' stroke-dasharray="11 9"' if dashed else '')+(' marker-end="url(#arrow)"' if arrow else '')+'/>')

    def box(self,x,y,w,h,title,body=(),fill=LIGHT,accent=NAVY,title_size=37,body_size=32):
        self.rect(x,y,w,h,fill)
        self.parts.append(f'<path d="M {x+20} {y+2} H {x+w-20}" stroke="{accent}" stroke-width="5"/>')
        self.text(x+w/2,y+60,title,title_size,accent,True,'middle')
        self.lines(x+w/2,y+115,body,body_size,48,anchor='middle')

    def table(self,x,y,w,title,fields,accent=NAVY,fill=LIGHT,row=49,size=34):
        h=86+len(fields)*row+18
        self.rect(x,y,w,h,'white')
        self.rect(x,y,w,79,fill,stroke='#C5D0D7',radius=12)
        self.text(x+26,y+53,title,37,accent,True)
        for i,line in enumerate(fields):
            self.text(x+26,y+119+i*row,line,size,bold=line.startswith('PK'))
        return h

    def diamond(self,cx,cy,w,h,lines):
        self.parts.append(f'<polygon points="{cx},{cy-h/2} {cx+w/2},{cy} {cx},{cy+h/2} {cx-w/2},{cy}" fill="{SF}" stroke="{SILVER}" stroke-width="2"/>')
        self.lines(cx,cy-(len(lines)-1)*22+11,lines,33,44,anchor='middle')

    def save(self):
        self.parts.append('</svg>')
        p=OUT/(self.name+'.svg'); p.write_text('\n'.join(self.parts),encoding='utf-8')
        print(p.name)


def medallion():
    f=Figure('Hinh_2_1_Nguyen_tac_Medallion',1800,850,'NGUYÊN TẮC TỔ CHỨC DỮ LIỆU MEDALLION','Phân tầng theo vai trò xử lý và mục đích sử dụng')
    for x,title,body,accent,fill in [
        (70,'BRONZE',['Tiếp nhận dữ liệu nguồn','Giữ dữ liệu đầu vào','cho bước xử lý tiếp theo'],BRONZE,BF),
        (650,'SILVER',['Chuẩn hóa và khử trùng','Đối chiếu thay đổi','Tạo dữ liệu nhất quán'],SILVER,SF),
        (1230,'GOLD',['Mô hình chiều','Tổng hợp chỉ tiêu','Phục vụ phân tích'],GOLD,GF)]:
        f.box(x,240,500,350,title,body,fill,accent,46,35)
    f.path([(570,410),(650,410)]); f.path([(1150,410),(1230,410)])
    f.text(900,705,'Dữ liệu được xử lý qua các tầng để phù hợp hơn với nhu cầu khai thác.',34,anchor='middle')
    f.text(900,765,'Sơ đồ nguyên lý; không biểu diễn lịch sử lưu trữ hay một công nghệ cụ thể.',30,GRAY,anchor='middle')
    f.save()


def architecture():
    f=Figure('Hinh_3_1_Kien_truc_tong_the',1800,1390,'KIẾN TRÚC TỔNG THỂ HỆ THỐNG','SQL Server → Airbyte → PostgreSQL → Power BI')
    f.rect(620,190,660,1050,'#FAFBFC',stroke='#A6B8C4',radius=20)
    f.text(950,248,'PostgreSQL',41,NAVY,True,'middle')
    f.text(950,290,'ticketing_analytics',33,GRAY,anchor='middle')
    f.box(60,330,430,240,'SQL Server',['TicketingDB','5 bảng nghiệp vụ'],title_size=39)
    f.box(60,730,430,240,'Airbyte',['Full Refresh','Overwrite'],title_size=39)
    f.path([(275,570),(275,730)])
    f.text(300,660,'Trích xuất',30,GRAY)
    f.box(670,340,560,210,'BRONZE',['5 bảng dữ liệu tiếp nhận'],BF,BRONZE,42,32)
    f.box(670,650,560,210,'SILVER',['5 bảng chuẩn hóa','Incremental / merge'],SF,SILVER,42,32)
    f.box(670,960,560,230,'GOLD',['5 chiều + 1 fact + 1 tổng hợp','Mô hình dữ liệu phân tích'],GF,GOLD,42,32)
    f.path([(490,850),(555,850),(555,445),(670,445)])
    f.path([(950,550),(950,650)]); f.text(976,612,'dbt-postgres',29,GRAY)
    f.path([(950,860),(950,960)]); f.text(976,920,'dbt-postgres',29,GRAY)
    f.box(1360,340,380,260,'Airflow',['Lập lịch','Theo dõi Airbyte','Điều phối dbt'],title_size=39,body_size=32)
    f.path([(1360,420),(1320,420),(1320,755),(1230,755)],True)
    f.path([(1320,755),(1320,1070),(1230,1070)],True)
    f.path([(1550,600),(1550,670),(1300,670),(1300,1280),(530,1280),(530,920),(490,920)],True)
    f.box(1360,1020,380,210,'Power BI',['Báo cáo phân tích','Dữ liệu từ Gold'],title_size=39,body_size=31)
    f.path([(1230,1125),(1360,1125)])
    f.path([(80,1340),(190,1340)]); f.text(215,1350,'Luồng dữ liệu',30)
    f.path([(690,1340),(800,1340)],True); f.text(825,1350,'Lệnh điều phối và theo dõi',30)
    f.save()


def source_erd():
    f=Figure('Hinh_3_2_ERD_nguon_SQL_Server',1800,1910,'MÔ HÌNH QUAN HỆ DỮ LIỆU NGUỒN','TicketingDB · Các thuộc tính chính và khóa tham chiếu')
    f.table(600,185,600,'events',['PK  event_id','event_code','event_name','starts_at / ends_at','sales_start_at / sales_end_at','capacity'],size=34)
    f.table(65,760,650,'orders',['PK  order_id','FK  event_id','ordered_at','sales_channel / order_status','subtotal_amount','discount_amount / total_amount'],size=34)
    f.table(1085,760,650,'ticket_types',['PK  ticket_type_id','FK  event_id','ticket_type_code','ticket_type_name','list_price / sale_quota'],size=34)
    f.table(65,1360,650,'payments',['PK  payment_id','FK  order_id','payment_partner / payment_method','payment_status / payment_amount','initiated_at / paid_at'],size=32)
    f.table(1085,1360,650,'order_items',['PK  order_item_id','FK1  order_id','FK1, FK2  event_id','FK2  ticket_type_id','quantity / unit_price','discount_amount / line_amount'],size=34)
    # Logical cardinality is optional on the child set: FKs do not force children.
    f.path([(900,583),(900,675),(390,675),(390,760)],arrow=False)
    f.path([(900,675),(1410,675),(1410,760)],arrow=False)
    f.text(925,630,'1',32); f.text(405,737,'0..N',32); f.text(1425,737,'0..N',32)
    f.path([(390,1158),(390,1360)],arrow=False)
    f.text(413,1205,'1',32); f.text(413,1335,'0..N',32)
    f.path([(1410,1109),(1410,1360)],arrow=False)
    f.text(1434,1155,'1',32); f.text(1434,1335,'0..N',32)
    f.path([(715,965),(865,965),(865,1250),(1120,1250),(1120,1360)],arrow=False)
    f.text(738,945,'1',32); f.text(1128,1335,'0..N',32)
    f.text(900,1810,'FK1: (order_id, event_id) → orders    |    FK2: (ticket_type_id, event_id) → ticket_types',31,anchor='middle')
    f.text(900,1860,'PK: khóa chính · FK: khóa ngoại · 1–0..N: một bản ghi cha có thể có nhiều bản ghi con.',30,GRAY,anchor='middle')
    f.save()


def gold_model():
    f=Figure('Hinh_3_3_Mo_hinh_Gold',2000,1730,'MÔ HÌNH DỮ LIỆU PHÂN TÍCH TẠI GOLD','Quan hệ logic theo khóa · Mức chi tiết fact: một dòng chi tiết đơn hàng')
    f.table(60,190,530,'dim_event',['PK*  event_id','event_code / event_name','category / organizer_name','venue_name / province','capacity / starts_at'],fill=GF,accent=GOLD,size=31)
    f.table(60,790,530,'dim_date',['PK*  date_key','full_date','year / month / day','weekday / is_weekend'],fill=GF,accent=GOLD,size=33)
    f.table(1410,190,530,'dim_ticket_type',['PK*  ticket_type_id','event_id','ticket_type_code','ticket_type_name','list_price / sale_quota'],fill=GF,accent=GOLD,size=33)
    f.table(1410,790,530,'dim_channel',['PK*  channel_key','sales_channel'],fill=GF,accent=GOLD,size=33)
    f.table(1410,1190,530,'dim_status',['PK*  status_key','order_status'],fill=GF,accent=GOLD,size=33)
    f.table(690,530,620,'fact_ticket_sales',[
        'PK*  order_item_id','order_id','FK*  event_id / ticket_type_id','FK*  date_key','FK*  channel_key / status_key','quantity / gross_amount','discount_amount / net_amount','sold_quantity / sales_amount'],fill='#EAF1F6',size=33,row=51)
    f.path([(590,400),(640,400),(640,665),(690,665)],arrow=False)
    f.text(600,379,'1',31); f.text(663,645,'N',31)
    f.path([(590,985),(690,985)],arrow=False); f.text(602,965,'1',31); f.text(660,965,'N',31)
    f.path([(1410,400),(1360,400),(1360,715),(1310,715)],arrow=False)
    f.text(1380,378,'1',31); f.text(1320,692,'N',31)
    f.path([(1410,900),(1310,900)],arrow=False); f.text(1380,878,'1',31); f.text(1325,878,'N',31)
    f.path([(1410,1300),(1360,1300),(1360,1035),(1310,1035)],arrow=False)
    f.text(1378,1278,'1',31); f.text(1325,1014,'N',31)
    f.box(640,1350,720,220,'agg_daily_sales',['Ngày đặt đơn × Sự kiện × Kênh bán','sales_amount · sold_quantity','paid_orders · total_orders'],GF,GOLD,37,31)
    f.path([(1000,1042),(1000,1350)],True)
    f.text(1027,1210,'Tổng hợp từ fact',31,GRAY)
    f.text(1000,1630,'* PK/FK biểu diễn vai trò khóa logic; không khẳng định có ràng buộc khóa ngoại vật lý tại Gold.',29,GRAY,anchor='middle')
    f.text(1000,1680,'Bảng tổng hợp dùng chung chiều ngày, sự kiện và kênh; không chứa khóa hạng vé hoặc trạng thái.',29,GRAY,anchor='middle')
    f.save()


def incremental():
    f=Figure('Hinh_3_4_Luu_do_incremental_Silver',1900,2150,'XỬ LÝ CẬP NHẬT TĂNG DẦN TẠI SILVER','Đối chiếu toàn bộ tập ứng viên với trạng thái hiện tại của bảng đích')
    f.box(250,170,1400,150,'Bản chụp Bronze đầy đủ',['Chuẩn hóa → Khử trùng theo khóa → Tính _record_hash'],BF,BRONZE,36,33)
    f.path([(950,320),(950,380),(470,380),(470,450)])
    f.path([(950,380),(1510,380),(1510,450)])
    f.rect(55,450,1070,1350,'#FAFCFD',radius=18)
    f.text(590,510,'ĐỐI CHIẾU BẢN GHI ỨNG VIÊN',34,NAVY,True,'middle')
    f.rect(1200,450,620,1350,'#FAFCFD',radius=18)
    f.text(1510,510,'TÌM KHÓA BIẾN MẤT',34,NAVY,True,'middle')
    f.diamond(365,690,470,205,['Khóa đã có','ở bảng đích?'])
    f.path([(600,690),(720,690)]); f.text(632,670,'Không',29)
    f.box(720,620,350,145,'Thêm mới',[],SF,SILVER,35)
    f.path([(365,793),(365,918)]); f.text(385,855,'Có',29)
    f.diamond(365,1020,470,205,['Đích đang','bị xóa mềm?'])
    f.path([(600,1020),(720,1020)]); f.text(640,999,'Có',29)
    f.box(720,950,350,145,'Khôi phục',[],SF,SILVER,35)
    f.path([(365,1123),(365,1248)]); f.text(387,1185,'Không',29)
    f.diamond(365,1350,470,205,['_record_hash','khác nhau?'])
    f.path([(600,1350),(720,1350)]); f.text(640,1329,'Có',29)
    f.box(720,1280,350,145,'Cập nhật',[],SF,SILVER,35)
    f.path([(365,1453),(365,1570)]); f.text(385,1510,'Không',29)
    f.box(145,1570,440,150,'Giữ nguyên',['Không ghi lại bản ghi'],LIGHT,NAVY,35,29)
    f.box(1240,630,540,290,'Bản ghi đích còn hiệu lực',[
        'Khóa không còn xuất hiện','trong tập ứng viên hiện tại','(đối chiếu NOT EXISTS)'],SF,SILVER,31,31)
    f.path([(1510,920),(1510,1080)])
    f.box(1240,1080,540,240,'Đánh dấu xóa mềm',[
        '_is_deleted = true','Giữ lại thông tin bản ghi'],SF,SILVER,34,32)
    f.text(1510,1485,'Khóa vẫn có ở nguồn hoặc',30,GRAY,anchor='middle')
    f.text(1510,1535,'đã xóa mềm: không tạo',30,GRAY,anchor='middle')
    f.text(1510,1585,'thêm dòng cập nhật ở nhánh này.',30,GRAY,anchor='middle')
    # Gather only rows needing writes; unchanged rows do not reach MERGE.
    f.path([(1070,690),(1100,690),(1100,1860)],arrow=False)
    f.path([(1070,1020),(1100,1020)],arrow=False)
    f.path([(1070,1350),(1100,1350)],arrow=False)
    f.path([(1510,1320),(1160,1320),(1160,1860),(1100,1860)],arrow=False)
    f.path([(1100,1860),(950,1860),(950,1890)])
    f.box(600,1890,700,145,'MERGE theo khóa nghiệp vụ',[],SF,SILVER,37)
    f.text(950,2080,'Lần đầu: tạo bảng từ tập ứng viên. Sơ đồ này mô tả lượt chạy tăng dần khi bảng đích đã tồn tại.',29,GRAY,anchor='middle')
    f.save()


def orchestration():
    f=Figure('Hinh_3_5_Dieu_phoi_Dataset',1800,1870,'ĐIỀU PHỐI CÁC TẦNG THEO DATASET','Các nút biểu diễn nhóm DAG nghiệp vụ; đường nối biểu diễn phụ thuộc lập lịch')
    xs=[60,400,740,1080,1420]
    businesses=[('Sự kiện','events'),('Hạng vé','ticket_types'),('Đơn hàng','orders'),('Chi tiết đơn','order_items'),('Thanh toán','payments')]
    f.text(60,190,'BRONZE · Airbyte hoàn tất thành công mới phát Dataset',33,BRONZE,True)
    for x,(label,code) in zip(xs,businesses):
        f.box(x,230,300,145,label,[code],BF,BRONZE,32,28)
        f.path([(x+150,375),(x+150,500)])
    f.rect(40,425,1720,55,'white',stroke='white',radius=0)
    f.text(60,465,'SILVER · Mỗi DAG nhận Dataset Bronze tương ứng',33,SILVER,True)
    for x,(label,code) in zip(xs,businesses):
        f.box(x,500,300,145,label,[code],SF,SILVER,32,28)
        f.path([(x+150,645),(x+150,720)],arrow=False)
    f.path([(210,720),(1570,720)],arrow=False)
    f.path([(900,720),(900,790)])
    f.box(480,790,840,135,'Chờ đủ 5 Dataset Silver (AND)',[],LIGHT,NAVY,36)
    f.path([(900,925),(900,990)],arrow=False)
    f.path([(210,990),(1570,990)],arrow=False)
    dims=[('Sự kiện','dim_event'),('Hạng vé','dim_ticket_type'),('Ngày','dim_date'),('Kênh bán','dim_channel'),('Trạng thái','dim_status')]
    f.text(60,970,'GOLD · Các bảng chiều',33,GOLD,True)
    for x,(label,code) in zip(xs,dims):
        f.path([(x+150,990),(x+150,1040)])
        f.box(x,1040,300,145,label,[code],GF,GOLD,32,27)
        f.path([(x+150,1185),(x+150,1250)],arrow=False)
    f.path([(210,1250),(1570,1250)],arrow=False)
    f.path([(900,1250),(900,1320)])
    f.box(480,1320,840,190,'fact_ticket_sales',['Chờ đủ 5 Dataset bảng chiều (AND)'],GF,GOLD,38,32)
    f.path([(900,1510),(900,1590)])
    f.box(480,1590,840,170,'agg_daily_sales',['Chạy sau khi fact hoàn tất'],GF,GOLD,38,32)
    f.text(900,1830,'Dataset là tín hiệu hoàn thành, không tự bảo đảm các bảng thuộc cùng một lô dữ liệu.',30,GRAY,anchor='middle')
    f.save()


if __name__ == '__main__':
    medallion(); architecture(); source_erd(); gold_model(); incremental(); orchestration()
