from pathlib import Path
import json,re,textwrap,zipfile,sys
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT

B=Path(__file__).resolve().parent
R=B.parent.parent
OUT=R/'Reports/Defense_20261004/Bao_cao_Ticketing_ELT_20261004.docx'
if len(sys.argv)>1:OUT=Path(sys.argv[1])
def read_schema(rel,indent):
 result=[];column=None
 for line in (R/rel).read_text(encoding='utf-8').splitlines():
  top=re.match(r'^'+(' '*indent)+r'- name: (.+)$',line)
  col=re.match(r'^'+(' '*(indent+4))+r'- name: (.+)$',line)
  if top:result.append({'name':top.group(1).strip(),'columns':[]});column=None
  elif col:
   column={'name':col.group(1).strip()};result[-1]['columns'].append(column)
  elif column and line.strip().startswith('data_type:'):column['data_type']=line.split(':',1)[1].strip().strip('"')
 return result
d=Document();sec=d.sections[0]
sec.page_width=Inches(8.5);sec.page_height=Inches(11)
sec.top_margin=Inches(.85);sec.bottom_margin=Inches(.85);sec.left_margin=Inches(1.05);sec.right_margin=Inches(.85)
for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Heading 3','Caption']:
 st=d.styles[name];st.font.name='Times New Roman';st.font.color.rgb=RGBColor(0,0,0)
st=d.styles['Normal'];st.font.size=Pt(12);st.paragraph_format.line_spacing=1.3;st.paragraph_format.space_after=Pt(7)
for n,size in [('Heading 1',17),('Heading 2',14),('Heading 3',12)]:
 st=d.styles[n];st.font.size=Pt(size);st.font.bold=True;st.paragraph_format.space_before=Pt(14);st.paragraph_format.space_after=Pt(9)
st=d.styles.add_style('Code',1);st.font.name='Consolas';st.font.size=Pt(9.5);st.paragraph_format.line_spacing=1.05;st.paragraph_format.space_after=Pt(0)
st=d.styles['Caption'];st.font.size=Pt(10);st.font.italic=True
footer=sec.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');footer._p.append(field)
d.core_properties.title='Quy trình ELT phân tích dữ liệu bán vé sự kiện'
d.core_properties.author='Nguyễn Hoàng Hiệp'
d.core_properties.subject='Khóa luận Khoa học máy tính'
def p(t,style=None):return d.add_paragraph(t,style)
def h(t,l=1):
 if l==1:d.add_page_break()
 return d.add_heading(t,l)
def table(headers,rows,widths=None):
 t=d.add_table(rows=1,cols=len(headers));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
 if widths:
  for c,w in zip(t.columns,widths):c.width=Inches(w)
 for c,v in zip(t.rows[0].cells,headers):c.text=str(v)
 for row in rows:
  cells=t.add_row().cells
  for c,v in zip(cells,row):c.text=str(v)
 for ri,row in enumerate(t.rows):
  for ci,c in enumerate(row.cells):
   if widths:c.width=Inches(widths[ci])
   c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
   pr=c._tc.get_or_add_tcPr();shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'E6EDF2' if ri==0 else ('F5F7F9' if ri%2 else 'FFFFFF'));pr.append(shade)
   margins=OxmlElement('w:tcMar')
   for side in ['top','left','bottom','right']:
    el=OxmlElement('w:'+side);el.set(qn('w:w'),'85');el.set(qn('w:type'),'dxa');margins.append(el)
   pr.append(margins)
   for par in c.paragraphs:
    par.paragraph_format.line_spacing=1.1;par.paragraph_format.space_after=Pt(3)
    if len(rows)<9 and ri<len(rows):par.paragraph_format.keep_with_next=True
    for run in par.runs:run.font.size=Pt(10);run.font.bold=ri==0
  cant=OxmlElement('w:cantSplit');row._tr.get_or_add_trPr().append(cant)
 hdr=OxmlElement('w:tblHeader');t.rows[0]._tr.get_or_add_trPr().append(hdr)
 borders=OxmlElement('w:tblBorders')
 for side in ['top','left','bottom','right','insideH','insideV']:
  el=OxmlElement('w:'+side);el.set(qn('w:val'),'single');el.set(qn('w:sz'),'4');el.set(qn('w:color'),'D9D9D9');borders.append(el)
 t._tbl.tblPr.append(borders);p('')
 return t
def code(text):
 for ln in text.splitlines():
  for part in textwrap.wrap(ln,width=84,expand_tabs=True,replace_whitespace=False,drop_whitespace=False,break_long_words=True,break_on_hyphens=False) or ['']:
   p(part,'Code')
 p('')
def filecode(rel,title,explain):
 h(title,2);p(explain);p('Tệp mã nguồn: '+rel,'Caption');code((R/rel).read_text(encoding='utf-8-sig'))

for t in ['KHÓA LUẬN TỐT NGHIỆP','CHUYÊN NGÀNH KHOA HỌC MÁY TÍNH']:
 par=p(t);par.alignment=1;par.runs[0].bold=True
p('');p('')
par=p('Thiết kế và xây dựng quy trình ELT xử lý dữ liệu bán vé sự kiện ứng dụng kiến trúc Medallion và Data Modeling để hỗ trợ ra quyết định','Title');par.alignment=1;par.runs[0].font.size=Pt(23)
p('');par=p('Nguyễn Hoàng Hiệp');par.alignment=1;par.runs[0].font.size=Pt(16)
par=p('Năm 2026');par.alignment=1
h('Tóm tắt')
p('Khóa luận xây dựng quy trình ELT phân tích dữ liệu bán vé sự kiện trên môi trường local. SQL Server lưu năm bảng nghiệp vụ; Airbyte đồng bộ Full Refresh Overwrite vào PostgreSQL Bronze; dbt-postgres chuẩn hóa Silver và xây dựng Gold; Airflow điều phối theo lịch và Dataset; Power BI cung cấp bốn trang phân tích. Thiết kế tập trung vào mức chi tiết của dữ liệu, xử lý bản ghi thay đổi và ý nghĩa chỉ tiêu bán vé.')
p('Bộ dữ liệu tổng hợp hiện có 357.000 đơn hàng trong giai đoạn 2020–2026, 399.696 chi tiết đơn và 420.792 lần thử thanh toán. Năm model Silver và fact sử dụng incremental merge với hash; năm dimensions cùng mart tổng hợp tạo lại bảng. Kết quả đọc Gold ngày 04 tháng 10 năm 2026 ghi nhận 636.959 vé thuộc đơn PAID và giá trị vé 188.306.020.500 VND.')
p('Đề tài sử dụng dữ liệu mô phỏng nhằm bảo vệ dữ liệu doanh nghiệp và hỗ trợ tái lập. Các chỉ tiêu phản ánh bộ sinh dữ liệu, không đại diện thị trường. Thiết kế chưa bảo đảm batch chung cho mọi stream hoặc công bố nguyên tử toàn bộ Gold. Báo cáo phân biệt kết quả quan sát với các ca kiểm thử và đo hiệu năng cần bổ sung.')
p('Từ khóa: ELT, Medallion, Airbyte, dbt-postgres, Airflow Dataset, mô hình sao, Power BI.')
h('Abstract')
p('This thesis presents a local ELT pipeline for event ticket sales analytics. SQL Server stores five operational tables. Airbyte loads complete snapshots into a PostgreSQL Bronze schema. dbt-postgres standardizes the data in Silver and builds analytical models in Gold. Airflow coordinates synchronization and transformations using time schedules and Dataset events. Power BI provides four report pages for business overview, event performance, event details, and sales channels with order status.')
p('The synthetic dataset contains 357,000 orders across 2020–2026, 399,696 order lines, and 420,792 payment attempts at the observation date of 4 October 2026. Five Silver models and the sales fact use incremental merge with business hashes. Dimensions and the daily aggregate are rebuilt as tables. The observed Gold results include 636,959 tickets on paid orders and a paid ticket value of VND 188,306,020,500. These figures describe a generated dataset and do not represent market evidence or company transactions.')
p('The design separates order lines from payment attempts to prevent duplicated sales amounts. It also documents the limits of snapshot based deletion detection, cross table consistency, and Dataset scheduling. Dataset events indicate successful task completion but do not enforce a common batch version. Evaluation distinguishes observed row counts and metrics from controlled change scenarios and performance measurements that require further execution.')
p('Keywords: ELT, Medallion architecture, dimensional modeling, Airbyte, dbt-postgres, Airflow, Power BI.')
h('Mục lục')
toc=OxmlElement('w:fldSimple');toc.set(qn('w:instr'),'TOC \\o "1-2" \\h \\z \\u');d.add_paragraph()._p.append(toc)
h('Danh mục thuật ngữ')
table(['Thuật ngữ','Ý nghĩa trong đề tài'],[['ELT','Trích xuất, nạp và biến đổi tại đích'],['Bronze','Schema chứa dữ liệu gần nguồn do Airbyte quản lý'],['Silver','Schema chuẩn hóa dữ liệu hiện tại theo khóa'],['Gold','Schema phục vụ phân tích'],['Grain','Mức chi tiết được quy định cho một dòng'],['Fact','Bảng giá trị đo lường ở grain xác định'],['Dimension','Bảng thuộc tính dùng để lọc và nhóm'],['Dataset','Tín hiệu cập nhật dữ liệu để lập lịch Airflow'],['Snapshot','Trạng thái dữ liệu tại một lần đọc'],['CDC','Thu thập sự kiện thay đổi từ nguồn'],['MERGE','Ghép khóa để thêm hoặc cập nhật dữ liệu'],['Idempotence','Chạy lại không làm tăng bản ghi hoặc sai kết quả nghiệp vụ']],[1.4,5.2])

for block in (B/'report.md').read_text(encoding='utf-8').split('\n\n'):
 for part in re.split(r'(?m)(?=^#{1,2} )',block):
  part=part.strip()
  if not part:continue
  if part.startswith('# '):h(part[2:],1)
  elif part.startswith('## '):
   lines=part.splitlines();h(lines[0][3:],2)
   if lines[0][3:]=='Kiến trúc thành phần':
    p('Bảng 1 Ánh xạ thành phần và dữ liệu','Caption')
    table(['Thành phần','Đầu vào','Đầu ra'],[['Airbyte','5 bảng SQL Server','5 bảng Bronze'],['dbt Silver','Bronze snapshot','5 bảng chuẩn hóa'],['dbt Gold','Silver và dimensions','Fact cùng mart'],['Airflow','Lịch và trạng thái task','Tín hiệu Dataset'],['Power BI','Các bảng Gold','4 trang phân tích']],[1.4,2.2,3.0])
   if lines[0][3:]=='Quy mô tại thời điểm khảo sát':
    p('Bảng 2 Số đơn theo năm đặt tại nguồn','Caption')
    table(['Năm','Số đơn'],[['2020','42.000'],['2021','20.000'],['2022','30.000'],['2023','40.000'],['2024','55.000'],['2025','70.867'],['2026','99.133']],[2.0,4.6])
   if lines[0][3:]=='Mô hình ngữ nghĩa':
    img=Path('C:/Users/zicza/AppData/Local/Temp/codex-clipboard-176a6a01-1a87-4270-8aa6-200a9897805c.png')
    if img.exists():
     d.add_picture(str(img),width=Inches(6.4))
     p('Hình 1 Quan hệ bảng trong Power BI từ ảnh mô hình của project','Caption')
   if len(lines)>1:p('\n'.join(lines[1:]))
  else:p(part)

h('Tài liệu tham khảo')
refs=[
('[1] Apache Airflow','Data aware scheduling, Airflow 2.10.5','https://airflow.apache.org/docs/apache-airflow/2.10.5/authoring-and-scheduling/datasets.html'),
('[2] dbt Labs','Configure incremental models','https://docs.getdbt.com/docs/build/incremental-models'),
('[3] Microsoft Learn','Understand star schema and the importance for Power BI','https://learn.microsoft.com/en-us/power-bi/guidance/star-schema'),
('[4] Mã nguồn đề tài','Cấu hình triển khai và mô hình SQL','compose.yaml; Dbt/Dbt-Postgres/models; Dbt/Dbt-Postgres/macros'),
('[5] Mã nguồn đề tài','Điều phối dữ liệu','Airflow/dags/bronze; Airflow/dags/silver; Airflow/dags/gold'),
('[6] Bộ dữ liệu đề tài','DDL và bộ sinh có seed','Source/SqlServer/schema.sql; events.py; append_history.py'),
('[7] Báo cáo Power BI','Định nghĩa bốn trang báo cáo','PowerBI/Dashboards.pbix'),
('[8] Truy vấn khảo sát','Số lượng nguồn và tổng hợp đích ngày 04 tháng 10 năm 2026','Truy vấn cụ thể trong Phụ lục E')]
for who,title,url in refs:p(who+'. '+title+'. '+url+'. Ngày tham chiếu 04/10/2026.')

h('Phụ lục A Từ điển dữ liệu nguồn và đích')
p('Các trường dưới đây lấy từ sources.yml và schema.yml hiện tại. Kiểu của Bronze mô tả hợp đồng đọc tại PostgreSQL; kiểu nguồn SQL Server được trình bày trong DDL ở phụ lục B. Khóa id trong kho được chuẩn hóa sang bigint, không có nghĩa mọi khóa nguồn đều là bigint.')
desc={'event_id':'Khóa sự kiện','event_code':'Mã nghiệp vụ sự kiện','event_name':'Tên sự kiện','category':'Nhóm chương trình','organizer_name':'Đơn vị tổ chức mô phỏng','venue_name':'Tên địa điểm','province':'Tỉnh hoặc thành phố','capacity':'Sức chứa sự kiện','starts_at':'Thời điểm bắt đầu sự kiện','ends_at':'Thời điểm kết thúc sự kiện','sales_start_at':'Bắt đầu cửa sổ mở bán','sales_end_at':'Kết thúc cửa sổ mở bán','event_status':'Trạng thái sự kiện','created_at':'Thời điểm tạo bản ghi','updated_at':'Thời điểm cập nhật nghiệp vụ','ticket_type_id':'Khóa hạng vé','ticket_type_code':'Mã hạng trong sự kiện','ticket_type_name':'Tên hạng vé','list_price':'Giá niêm yết hiện hành VND','sale_quota':'Hạn mức bán của hạng vé','order_id':'Khóa đơn hàng','order_code':'Mã nghiệp vụ đơn','ordered_at':'Thời điểm đặt đơn','expires_at':'Hạn thanh toán đơn','sales_channel':'Kênh WEB hoặc APP','order_status':'Trạng thái hiện tại của đơn','subtotal_amount':'Tổng tiền trước giảm giá','discount_amount':'Giảm giá nguyên đồng VND','total_amount':'Giá trị phải thanh toán của đơn','currency':'Mã tiền tệ VND','order_item_id':'Khóa dòng đơn và grain của fact','quantity':'Số lượng vé được đặt','unit_price':'Đơn giá đã chốt trên dòng','line_amount':'Giá trị dòng sau giảm giá','payment_id':'Khóa lần thử thanh toán','merchant_transaction_id':'Mã giao dịch nội bộ','partner_transaction_id':'Mã giao dịch đối tác nếu có','payment_partner':'Đối tác thanh toán mô phỏng','payment_method':'WALLET DOMESTIC_CARD hoặc QR_BANK','payment_amount':'Số tiền của lần thử','payment_status':'SUCCESS FAILED hoặc PENDING','failure_reason':'Lý do thất bại nếu có','initiated_at':'Thời điểm bắt đầu lần thử','completed_at':'Thời điểm hoàn tất nếu có','paid_at':'Thời điểm thành công nếu có','_record_hash':'Hash các cột nghiệp vụ','_is_deleted':'Đánh dấu không còn trong snapshot','_loaded_at':'Thời điểm ghi nhận ở kho','channel_key':'Khóa dimension kênh','status_key':'Khóa dimension trạng thái','date_key':'Khóa ngày dạng YYYYMMDD','gross_amount':'quantity nhân unit_price','net_amount':'Giá trị dòng sau giảm giá','sold_quantity':'quantity khi PAID ngược lại bằng 0','sales_amount':'Giá trị dòng khi PAID ngược lại bằng 0','paid_orders':'Số đơn PAID phân biệt','total_orders':'Tổng số đơn phân biệt','full_date':'Ngày lịch','year':'Năm lịch','month':'Tháng trong năm','day':'Ngày trong tháng','weekday':'Thứ trong tuần theo model','is_weekend':'Cờ cuối tuần'}
sources=read_schema('Dbt/Dbt-Postgres/models/sources.yml',6)
for t in sources:
 h('Bảng nguồn '+t['name'],2)
 p('Ánh xạ trực tiếp từ dbo.'+t['name']+' sang bronze.'+t['name']+'. Các cột kỹ thuật Airbyte bổ sung nằm ngoài nhóm nghiệp vụ dưới đây.')
 table(['Cột','Kiểu đích','Ý nghĩa'],[(c['name'],c['data_type'],desc.get(c['name'],c.get('description',''))) for c in t['columns']],[1.8,1.7,3.1])
h('Metadata dùng chung tại Silver',2)
table(['Trường','Vai trò'],[['_source_extracted_at','Dùng trong CTE xếp hạng, lấy từ metadata Airbyte'],['_source_raw_id','Tie-break khi nhiều dòng có cùng thời điểm'],['_record_hash','So sánh nội dung ứng viên với dòng đích'],['_is_deleted','Xóa mềm tại Silver'],['_loaded_at','Thời điểm ghi dòng mới hoặc dòng thay đổi']],[2.0,4.6])
p('Các trường _source_extracted_at và _source_raw_id không được xuất ra bảng Silver cuối cùng trong model hiện tại. Silver giữ các cột nghiệp vụ của bảng tương ứng cùng ba cột _record_hash, _is_deleted, _loaded_at.')
gold=read_schema('Dbt/Dbt-Postgres/models/gold/schema.yml',2)
for t in gold:
 h('Bảng Gold '+t['name'],2)
 table(['Cột','Kiểu','Ý nghĩa'],[(c['name'],c['data_type'],desc.get(c['name'],c.get('description',''))) for c in t['columns']],[1.8,1.7,3.1])

h('Phụ lục B Mã tạo dữ liệu và cấu trúc nguồn')
p('DDL được trích từ mã hiện tại để giải thích các ràng buộc nguồn. Chỉ chạy schema.sql trên database trống theo hướng dẫn trong mã. Không chạy các lệnh tạo lại nguồn trên môi trường đã có dữ liệu nếu chưa lập kế hoạch sao lưu.')
filecode('Source/SqlServer/schema.sql','Cấu trúc năm bảng SQL Server','Các CHECK và khóa ngoại mô tả ràng buộc tại nguồn. Toàn vẹn tổng tiền giữa nhiều dòng vẫn cần phép đối chiếu riêng.')
filecode('Source/SqlServer/append_history.py','Bổ sung dữ liệu lịch sử','Mỗi lô theo năm dùng transaction và khóa để phân bổ id. --load mới ghi dữ liệu. Seed mới tạo lô mới, không thay thế lô cũ. Kiểm tra already_loaded dựa số lượng không thay thế kiểm tra hash toàn bộ lô.')

h('Phụ lục C Mã biến đổi dbt')
p('Các đoạn mã là bản chụp tại thời điểm biên soạn. Bảng dữ liệu chạy thực tế phụ thuộc phiên bản project, profile và snapshot đầu vào. Không sửa SQL compiled trong Runtime để thay đổi model.')
filecode('Dbt/Dbt-Postgres/dbt_project.yml','Cấu hình dự án','Silver incremental merge, Gold mặc định table. Fact ghi đè materialization bằng cấu hình riêng. Hợp đồng cấu trúc được bật.')
filecode('Dbt/Dbt-Postgres/macros/business_hash.sql','Hash nội dung nghiệp vụ','Danh sách trường được truyền từ model. Metadata lần trích xuất không thuộc hash nghiệp vụ.')
filecode('Dbt/Dbt-Postgres/macros/incremental_changes.sql','Chọn tập dòng cần cập nhật','Macro dùng so sánh hash và anti-join trên snapshot đầy đủ, gồm nhánh khôi phục bản ghi xóa mềm.')
for name in ['events','ticket_types','orders','order_items','payments']:
 filecode(f'Dbt/Dbt-Postgres/models/silver/silver_{name}.sql','Model Silver '+name,'Nguồn bronze.'+name+' và đích silver.'+name+'. Các bước chuẩn hóa, xếp hạng và merge thực hiện theo khóa chính của bảng.')
for f in sorted((R/'Dbt/Dbt-Postgres/models/gold/dimensions').glob('*.sql')):
 filecode(f.relative_to(R).as_posix(),'Model '+f.stem,'Dimension giữ thuộc tính hiện hành và được tạo lại theo cấu hình table của tầng Gold.')
filecode('Dbt/Dbt-Postgres/models/gold/facts/fact_ticket_sales.sql','Model fact bán vé','Grain order_item_id. Không nối bảng payments. Đơn PAID mới đóng góp số vé bán và giá trị vé.')
filecode('Dbt/Dbt-Postgres/models/gold/marts/agg_daily_sales.sql','Model tổng hợp ngày','Mart nhóm theo ngày đặt đơn, sự kiện và kênh. Không có mức chi tiết hạng vé.')

h('Phụ lục D Điều phối và vận hành')
p('Các DAG mẫu dưới đây thể hiện đầu vào, đầu ra và đường dẫn model trực tiếp. Những DAG nghiệp vụ còn lại áp dụng cùng mẫu với định danh riêng. Không đưa client secret hoặc thông tin đăng nhập vào tài liệu.')
for rel,title,why in [
 ('Airflow/dags/bronze/bronze_ticket_events.py','DAG Bronze sự kiện','Outlet đặt ở sensor, chỉ phát sau khi Airbyte hoàn tất thành công.'),
 ('Airflow/dags/silver/silver_ticket_events.py','DAG Silver sự kiện','Schedule chờ Dataset Bronze tương ứng. Câu lệnh chọn đúng model qua đường dẫn.'),
 ('Airflow/dags/gold/gold_ticket_dim_event.py','DAG dimension sự kiện','Danh sách đầu vào chờ đủ năm Dataset Silver.'),
 ('Airflow/dags/gold/gold_ticket_fact_ticket_sales.py','DAG fact bán vé','Fact chờ các dimension theo định nghĩa hiện tại.'),
 ('Airflow/dags/gold/gold_ticket_agg_daily_sales.py','DAG mart ngày','Mart chạy sau Dataset fact.'),
 ('Airflow/plugins/ticketing/dbt_defaults.py','Tham số vận hành chung','full_refresh mặc định false. Start date dùng Asia/Ho_Chi_Minh.')]:filecode(rel,title,why)
h('Danh sách DAG theo tầng',2)
rows=[]
for stage in ['bronze','silver','gold']:
 for f in sorted((R/f'Airflow/dags/{stage}').glob('*.py')):
  text=f.read_text(encoding='utf-8-sig');m=re.search(r'dag_id\s*=\s*"([^"]+)"',text)
  if m:rows.append((stage,m.group(1)))
table(['Tầng','DAG ID'],rows,[1.2,5.4])
h('Khởi động và truy cập',2)
p('Mở Docker Desktop trước. Tại thư mục Ticket_Project, chạy script khởi động. PowerShell có thể dùng phạm vi tiến trình riêng qua tham số -ExecutionPolicy Bypass cho lệnh bên dưới, không cần thay đổi chính sách toàn máy. Chỉ áp dụng với script project đã kiểm tra.')
code('powershell -ExecutionPolicy Bypass -File .\\Scripts\\start.ps1\n# Giao diện Airflow: http://localhost:8080\n# Giao diện Airbyte local: http://localhost:8000\n# PostgreSQL trên Windows: localhost:5433\n# Database: ticketing_analytics')
p('Airbyte có vòng đời riêng. Kiểm tra abctl local status và hướng dẫn Airbyte trong project khi cổng 8000 chưa truy cập được. Không dùng mật khẩu minh họa trong báo cáo để đăng nhập. Truy xuất thông tin đăng nhập từ cấu hình local và không chụp secret vào slide.')
h('Nạp thêm dữ liệu lịch sử',2)
p('Lệnh đầu chỉ sinh dữ liệu và manifest, không ghi SQL Server. Lệnh thứ hai nạp cùng cấu hình khi đã xác nhận. Năm được hỗ trợ hiện tại là 2020 đến 2025. Seed nằm trong miền của chương trình. Mỗi seed mới cho cùng năm có thể làm tăng dữ liệu thay vì ghi đè.')
code('python .\\Source\\SqlServer\\append_history.py --start-year 2020 --end-year 2020 --orders-per-year 2000 --seed 2\npython .\\Source\\SqlServer\\append_history.py --start-year 2020 --end-year 2020 --orders-per-year 2000 --seed 2 --load')
p('Nếu có thông báo Batch exists with different counts, không bỏ cơ chế bảo vệ. Cần quyết định đang muốn thêm lô hay thay dữ liệu cũ. Tham số đúng là --seed với hai dấu gạch. Trạng thái loaded cho biết transaction đã commit; generated_only không nạp và already_loaded bỏ qua lô theo kiểm tra hiện tại.')
h('Chạy dbt và làm mới Power BI',2)
p('Trong môi trường dbt đã cấu hình profile và biến kết nối, các lệnh dưới đây cho phép chạy model. Trong Airflow, nên dùng DAG đã cấu hình để giữ đường artifacts và các kiểm soát vận hành. Full refresh chỉ dùng khi có lý do tạo lại cấu trúc hoặc dữ liệu, không phải đường chạy mặc định.')
code('dbt run --select path:models/silver/silver_events.sql\ndbt run --select tag:silver\ndbt run --select tag:gold\n# Chỉ khi chủ động tạo lại bảng:\ndbt run --select tag:silver --full-refresh')
p('Sau khi Bronze, Silver, dimensions, fact và mart hoàn thành, refresh Power BI Desktop trong cửa sổ không có pipeline ghi mới. Kiểm tra lại khoảng ngày, số đơn và giá trị tiền. Lưu PBIX sau khi xác nhận. Khi triển khai Power BI Service, cần cấu hình gateway và lịch refresh riêng; đó chưa phải chức năng đã cấu hình trong phạm vi local.')
h('Xử lý lỗi theo thành phần',2)
table(['Hiện tượng','Điểm kiểm tra'],[['Airflow 8080 không mở','Docker, trạng thái webserver, scheduler, metadata DB và log init'],['Airbyte không kích hoạt','API URL từ container, client credential, connection ID'],['Sensor chờ lâu','Trạng thái đúng Job ID trong Airbyte, timeout và kết nối mạng'],['Broken DAG','Import package, đường mount và lỗi Python trong scheduler'],['Silver chờ không chạy','Dataset URI, trạng thái pause và task Bronze có thành công'],['dbt lỗi schema','Đối chiếu YAML, cột thực tế và log compiled SQL'],['Gold chưa cập nhật','Các Dataset Silver hoặc dimension còn thiếu'],['Power BI thiếu dữ liệu mới','Gold đã xong, Desktop đã refresh và bộ lọc ngày']],[2.1,4.5])

h('Phụ lục E Truy vấn và kịch bản nghiệm thu')
h('Truy vấn số lượng tại nguồn',2)
code("SELECT 'events' AS table_name, COUNT_BIG(*) AS row_count FROM dbo.events\nUNION ALL SELECT 'ticket_types', COUNT_BIG(*) FROM dbo.ticket_types\nUNION ALL SELECT 'orders', COUNT_BIG(*) FROM dbo.orders\nUNION ALL SELECT 'order_items', COUNT_BIG(*) FROM dbo.order_items\nUNION ALL SELECT 'payments', COUNT_BIG(*) FROM dbo.payments;\nSELECT YEAR(ordered_at) AS order_year, COUNT_BIG(*) AS orders\nFROM dbo.orders GROUP BY YEAR(ordered_at) ORDER BY order_year;")
table(['Bảng','Số dòng nguồn ngày 04 tháng 10 năm 2026'],[['events','360'],['ticket_types','1.080'],['orders','357.000'],['order_items','399.696'],['payments','420.792']],[2,4.6])
h('Truy vấn chỉ tiêu Gold',2)
code("SELECT s.order_status, COUNT(DISTINCT f.order_id) AS orders,\n       SUM(f.sold_quantity) AS tickets, SUM(f.sales_amount) AS sales\nFROM gold.fact_ticket_sales f\nJOIN gold.dim_status s USING (status_key)\nGROUP BY s.order_status ORDER BY s.order_status;")
table(['Trạng thái','Số đơn','Vé bán','Giá trị VND'],[['CANCELLED','16.657','0','0'],['EXPIRED','47.059','0','0'],['PAID','293.274','636.959','188.306.020.500'],['PENDING','10','0','0']],[1.4,1.2,1.2,2.8])
h('Ma trận kịch bản nghiệm thu',2)
p('Các ca dưới đây là kế hoạch thực hiện trên môi trường thử có thể phục hồi. Chưa gán trạng thái đạt cho các thao tác thay đổi hoặc lỗi không được chạy trong lần khảo sát. Lưu kết quả thực tế cùng Job ID, DAG run ID và truy vấn trước sau.')
tests=[('T01','Nạp snapshot đầu','Đủ khóa và giá trị nguồn ở Bronze, Silver'),('T02','Chạy lại không đổi','Không tăng số khóa hoặc thay đổi KPI'),('T03','Thêm đơn hợp lệ','Fact tăng đúng số dòng chi tiết'),('T04','Đơn cũ sang PAID','KPI ngày đặt cũ tăng đúng giá trị'),('T05','Thay giá trị dòng','Hash và fact phản ánh thay đổi'),('T06','Xóa trên snapshot đầy đủ','Silver xóa mềm, Gold loại khỏi báo cáo'),('T07','Khóa xuất hiện lại','Khôi phục đúng một dòng hoạt động'),('T08','Trùng khóa đầu vào','Dedup chọn theo quy tắc xác định'),('T09','Airbyte thất bại','Không phát Dataset thành công từ sensor'),('T10','Model SQL thất bại','Không công bố outlet của task lỗi'),('T11','Thiếu một Dataset Silver','Dimensions không tự chạy vì các tín hiệu còn lại'),('T12','PBIX refresh sau pipeline','KPI thống nhất với truy vấn Gold')]
table(['Mã','Tình huống','Kết quả mong đợi'],tests,[.55,2.0,4.05])
h('Mẫu chỉ tiêu đo hiệu năng',2)
p('Ghi riêng thời gian Airbyte, dbt và toàn tuyến. Với mỗi quy mô, giữ cùng phần cứng và so sánh ít nhất ba lượt mỗi cấu hình. Chỉ báo cáo kết quả sau khi lưu bằng chứng. Bảng dưới liệt kê phép đo cần thu thập, không điền số giả định.')
table(['Phép đo','Đơn vị','Điều kiện'],[['Airbyte sync','Giây','Cùng nguồn và chế độ Full Refresh Overwrite'],['Silver dbt','Giây','Snapshot không đổi và snapshot có thay đổi'],['Fact dbt','Giây','Có thay đổi trạng thái đơn cũ'],['Dòng ghi','Dòng','Khóa mới và hash thay đổi'],['Toàn tuyến','Giây','Từ trigger đến mart thành công'],['Refresh Desktop','Giây','Cùng model và phạm vi dữ liệu']],[1.5,.8,4.3])

h('Phụ lục F Chỉ tiêu DAX và hướng dẫn bảo vệ')
p('DAX dưới đây sử dụng tên bảng có tiền tố gold như trong mô hình Power BI. Đây là công thức tham chiếu tương ứng định nghĩa chỉ tiêu, cần đối chiếu tên bảng và measure khi sửa PBIX.')
code('Doanh thu vé = SUM(\'gold fact_ticket_sales\'[sales_amount])\n\nSố vé đã bán = SUM(\'gold fact_ticket_sales\'[sold_quantity])\n\nTổng số đơn = DISTINCTCOUNT(\'gold fact_ticket_sales\'[order_id])\n\nSố đơn thanh toán =\nCALCULATE(\n    DISTINCTCOUNT(\'gold fact_ticket_sales\'[order_id]),\n    \'gold dim_status\'[order_status] = "PAID"\n)\n\nTỷ lệ thanh toán = DIVIDE([Số đơn thanh toán], [Tổng số đơn])\n\nGiá trị TB mỗi đơn thanh toán =\nDIVIDE([Doanh thu vé], [Số đơn thanh toán])')
h('Trình tự trình diễn',2)
p('Mở SQL Server và chỉ ra năm bảng cùng grain. Mở Airbyte để xác nhận connection đang dùng, che các trường nhạy cảm. Trên Airflow, giải thích khác nhau giữa trigger và sensor, sau đó mở Dataset và DAG Silver. Mở file SQL theo đường dẫn hiển thị để chứng minh công việc thực tế là câu lệnh dbt cụ thể.')
p('Tiếp theo mở Gold để trình bày fact và dimensions. Trong Power BI, bắt đầu ở Tổng quan, chọn khoảng ngày, chuyển sang hiệu quả sự kiện rồi chi tiết hạng vé. Kết thúc ở kênh bán và trạng thái đơn. Không chạy lô tạo dữ liệu lớn ngay giữa bài nếu chưa đo thời gian và có kế hoạch dự phòng.')
h('Câu hỏi phản biện thường gặp',2)
qa=[('Vì sao nguồn full refresh mà đích incremental','Nguồn quyết định cách đọc và nạp snapshot. Model đích so sánh khóa cùng hash để giảm ghi. Hai cơ chế ở hai bước khác nhau.'),('Incremental có nhanh hơn bao nhiêu','Chưa có số benchmark được nghiệm thu. Thiết kế vẫn quét snapshot, chỉ có cơ sở nói bỏ ghi các dòng không đổi.'),('Dataset có bảo đảm cùng batch không','Không tự bảo đảm. Dataset list chờ cập nhật, cần batch ID hoặc một cơ chế xác nhận bổ sung nếu yêu cầu cùng phiên bản.'),('Vì sao payments không vào fact bán vé','Một đơn có nhiều lần thử. Nối trực tiếp với dòng đơn có thể nhân bản số tiền. Fact bán vé dùng trạng thái đơn PAID.'),('Medallion có bắt buộc Lakehouse không','Trong đề tài, Medallion phân tầng trách nhiệm bằng schema PostgreSQL. Không có time travel của định dạng bảng Lakehouse.'),('Đây có phải dữ liệu thật không','Đây là dữ liệu mô phỏng có seed và ràng buộc nghiệp vụ. Không phải giao dịch của Ticketbox hoặc doanh nghiệp.'),('Vì sao cần thêm đánh giá','Số dòng và tổng tiền tại một thời điểm chưa chứng minh xử lý đúng mọi thay đổi, lỗi và chạy lại. Cần ca nghiệm thu có kiểm soát.')]
for q,a in qa:h(q,3);p(a)

settings=d.settings.element
uf=OxmlElement('w:updateFields');uf.set(qn('w:val'),'true');settings.append(uf)
d.save(OUT)
print(str(OUT))
print('words',sum(len(p.text.split()) for p in d.paragraphs),'tables',len(d.tables))
