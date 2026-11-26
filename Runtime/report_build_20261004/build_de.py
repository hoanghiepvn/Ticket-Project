from pathlib import Path
import ast,re,textwrap
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION_START
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
B=Path(__file__).resolve().parent
R=B.parent.parent
OUT=Path('C:/Users/zicza/AppData/Local/Temp/ticket_report_de_20261006')
OUT.mkdir(parents=True,exist_ok=True)
d=Document()
def el(tag,**attrs):
 e=OxmlElement('w:'+tag)
 for k,v in attrs.items():e.set(qn('w:'+k),str(v))
 return e
for sec in d.sections:
 sec.page_width=Inches(8.5);sec.page_height=Inches(11)
 sec.top_margin=Inches(.85);sec.bottom_margin=Inches(.85);sec.left_margin=Inches(1.1);sec.right_margin=Inches(.85)
 sec.footer_distance=Inches(.4)
for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Heading 3','Caption']:
 st=d.styles[name];st.font.name='Times New Roman';st.font.color.rgb=RGBColor(0,0,0)
 rf=st.element.get_or_add_rPr().get_or_add_rFonts()
 for a in list(rf.attrib):del rf.attrib[a]
 for a in ['ascii','hAnsi','eastAsia','cs']:rf.set(qn('w:'+a),'Times New Roman')
n=d.styles['Normal'];n.font.size=Pt(13);n.paragraph_format.line_spacing=1.5;n.paragraph_format.space_after=Pt(6);n.paragraph_format.first_line_indent=Inches(.28);n.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
for name,size in [('Heading 1',16),('Heading 2',14),('Heading 3',13)]:
 st=d.styles[name];st.font.size=Pt(size);st.font.bold=True;f=st.paragraph_format;f.first_line_indent=Inches(0);f.alignment=WD_ALIGN_PARAGRAPH.LEFT;f.space_before=Pt(12);f.space_after=Pt(6);f.keep_with_next=True;f.line_spacing=1.2
d.styles['Heading 1'].paragraph_format.page_break_before=True
for name,parent,size in [('Unnumbered','Heading 1',16),('FrontTitle','Title',16),('AppendixTitle','Heading 1',16),('AppendixSection','Heading 2',14),('TableCaption','Caption',11),('FigureCaption','Caption',11),('CodeDE','Normal',10)]:
 st=d.styles.add_style(name,1);st.base_style=d.styles[parent];st.font.name='Times New Roman';st.font.size=Pt(size);st.font.color.rgb=RGBColor(0,0,0);st.paragraph_format.first_line_indent=Inches(0)
 if name in ['Unnumbered','AppendixTitle','AppendixSection']:st.element.get_or_add_pPr().append(el('numPr'));st.paragraph_format.keep_with_next=True
 if 'Caption' in name:st.paragraph_format.line_spacing=1.1;st.paragraph_format.keep_with_next=True;st.paragraph_format.alignment=1
 if name=='CodeDE':st.font.name='Consolas';st.paragraph_format.line_spacing=1.05;st.paragraph_format.space_after=Pt(0);st.paragraph_format.alignment=0
numroot=d.part.numbering_part.element
absid=81;numid=81
a=el('abstractNum',abstractNumId=absid);a.append(el('multiLevelType',val='multilevel'))
for level in range(3):
 lv=el('lvl',ilvl=level);lv.append(el('start',val=1));lv.append(el('numFmt',val='decimal'));lv.append(el('pStyle',val=f'Heading{level+1}'));lv.append(el('lvlText',val='Chương %1' if level==0 else '.'.join('%'+str(i+1) for i in range(level+1))));lv.append(el('suff',val='space'));a.append(lv)
numroot.append(a);nn=el('num',numId=numid);nn.append(el('abstractNumId',val=absid));numroot.append(nn)
for level in range(3):
 np=el('numPr');np.append(el('ilvl',val=level));np.append(el('numId',val=numid));d.styles[f'Heading {level+1}'].element.get_or_add_pPr().append(np)
for name in ['Unnumbered','AppendixTitle','AppendixSection']:
 pp=d.styles[name].element.get_or_add_pPr();np=pp.find(qn('w:numPr'));np.append(el('numId',val=0))
for i in range(1,4):
 name=f'TOC {i}'
 if name not in d.styles:d.styles.add_style(name,1)
 st=d.styles[name];st.font.name='Times New Roman';st.font.size=Pt(11);st.font.color.rgb=RGBColor(0,0,0);st.paragraph_format.line_spacing=1.05;st.paragraph_format.space_after=Pt(3);st.paragraph_format.first_line_indent=Inches(0);st.paragraph_format.left_indent=Inches((i-1)*.22)
def p(t='',style=None):return d.add_paragraph(t,style)
def field(par,code):
 r=par.add_run();r._r.append(el('fldChar',fldCharType='begin'));r=par.add_run();it=el('instrText');it.set(qn('xml:space'),'preserve');it.text=' '+code+' ';r._r.append(it);par.add_run()._r.append(el('fldChar',fldCharType='separate'));par.add_run('');par.add_run()._r.append(el('fldChar',fldCharType='end'))
def page_number(sec,fmt):
 sec.footer.is_linked_to_previous=False
 par=sec.footer.paragraphs[0];par.paragraph_format.first_line_indent=Inches(0);par.alignment=1;field(par,'PAGE')
 sec._sectPr.append(el('pgNumType',fmt=fmt,start=1))
def caption(label,title):
 par=p('', 'TableCaption' if label=='Bảng' else 'FigureCaption');par.add_run(label+' ');field(par,'SEQ '+('Bang' if label=='Bảng' else 'Hinh')+' \\* ARABIC');par.add_run(' '+title)
def table(title,headers,rows,widths=None):
 if title:caption('Bảng',title)
 t=d.add_table(rows=1,cols=len(headers));t.autofit=False
 if widths is None:widths=[6.55/len(headers)]*len(headers)
 for col,w in zip(t.columns,widths):col.width=Inches(w)
 for c,v in zip(t.rows[0].cells,headers):c.text=str(v)
 for row in rows:
  for c,v in zip(t.add_row().cells,row):c.text=str(v)
 for ri,row in enumerate(t.rows):
  row._tr.get_or_add_trPr().append(el('cantSplit'))
  if ri==0:row._tr.get_or_add_trPr().append(el('tblHeader'))
  for ci,c in enumerate(row.cells):
   c.width=Inches(widths[ci]);c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
   pr=c._tc.get_or_add_tcPr();pr.append(el('shd',fill='E6EDF2' if ri==0 else 'FFFFFF'))
   mar=el('tcMar')
   for side in ['top','left','bottom','right']:mar.append(el(side,w=80,type='dxa'))
   pr.append(mar)
   for par in c.paragraphs:
    f=par.paragraph_format;f.first_line_indent=Inches(0);f.space_after=Pt(3);f.line_spacing=1.1;f.alignment=0;f.keep_with_next=ri==0
    for run in par.runs:run.font.size=Pt(10.5);run.bold=ri==0
 borders=el('tblBorders')
 for side in ['top','left','bottom','right','insideH','insideV']:borders.append(el(side,val='single',sz=4,color='D9D9D9'))
 t._tbl.tblPr.append(borders);p('')
 return t
def code(t):
 for line in t.strip().splitlines():
  for part in textwrap.wrap(line,width=78,replace_whitespace=False,drop_whitespace=False) or ['']:p(part,'CodeDE')
 p('')
def front(title,text):
 par=p(title,'Unnumbered')
 for block in text.split('\n\n'):p(block)
d.core_properties.title='Thiết kế và xây dựng hệ thống tích hợp và xử lý dữ liệu bán vé sự kiện theo kiến trúc Medallion'
d.core_properties.author='Nguyễn Hoàng Hiệp';d.core_properties.subject='Khóa luận Khoa học máy tính theo hướng Kỹ thuật dữ liệu'
for t in ['KHÓA LUẬN TỐT NGHIỆP','CHUYÊN NGÀNH KHOA HỌC MÁY TÍNH']:
 par=p(t);par.alignment=1;par.paragraph_format.first_line_indent=Inches(0);par.runs[0].bold=True
p('');p('')
par=p('Thiết kế và xây dựng hệ thống tích hợp và xử lý dữ liệu bán vé sự kiện theo kiến trúc Medallion','Title');par.alignment=1;par.paragraph_format.first_line_indent=Inches(0);par.runs[0].font.size=Pt(22)
p('');par=p('Nguyễn Hoàng Hiệp');par.alignment=1;par.paragraph_format.first_line_indent=Inches(0)
par=p('Năm 2026');par.alignment=1;par.paragraph_format.first_line_indent=Inches(0)
sec=d.add_section(WD_SECTION_START.NEW_PAGE);page_number(sec,'lowerRoman')
par=p('Lời cảm ơn','Unnumbered');par.paragraph_format.page_break_before=False
p('Em xin gửi lời cảm ơn đến quý thầy cô đã giảng dạy các kiến thức nền tảng của chuyên ngành Khoa học máy tính. Những kiến thức về cơ sở dữ liệu, lập trình và thiết kế hệ thống là cơ sở để em tiếp cận bài toán tích hợp dữ liệu trong khóa luận này.')
p('Em trân trọng những nhận xét của giảng viên hướng dẫn và hội đồng để tiếp tục hoàn thiện cách lập luận, phương pháp kiểm chứng và nội dung trình bày. Em cũng xin ghi nhận sự đóng góp của các cộng đồng phát triển công cụ và tài liệu kỹ thuật được sử dụng, tham khảo trong đề tài.')
front('Thông tin về dữ liệu và phạm vi kết quả','Dữ liệu nghiệp vụ trong đề tài do chương trình Python tạo tổng hợp để phục vụ xây dựng và đánh giá hệ thống. Báo cáo không sử dụng giao dịch nội bộ hoặc thông tin cá nhân của khách hàng. Các tên gọi gần thực tế chỉ tạo ngữ cảnh minh họa, không xác nhận một giao dịch thật đã phát sinh.\n\nCác số liệu có ngày khảo sát được trình bày đúng phạm vi quan sát. Những ca kiểm thử thay đổi dữ liệu và số đo hiệu năng chưa có bằng chứng hoàn tất được tách khỏi kết quả đã ghi nhận. Mã nguồn của dự án và tài liệu kỹ thuật tham khảo được chỉ dẫn để người đọc có thể kiểm tra cách hình thành kết luận.')
front('Tóm tắt','Khóa luận xây dựng hệ thống tích hợp và xử lý dữ liệu bán vé sự kiện theo ba tầng Bronze, Silver và Gold. Nguồn gồm năm bảng quan hệ trong SQL Server. Airbyte đồng bộ bản chụp vào PostgreSQL, dbt-postgres chuẩn hóa và mô hình hóa dữ liệu, còn Airflow điều phối theo lịch và tín hiệu hoàn thành. Power BI minh họa việc sử dụng dữ liệu công bố.\n\nTrọng tâm kỹ thuật là xác định mức chi tiết của bảng đo lường, khử trùng theo khóa, phát hiện thay đổi nội dung và xử lý dữ liệu biến mất hoặc xuất hiện trở lại. Tầng Silver cùng bảng đo lường bán vé sử dụng cập nhật tăng dần; các bảng chiều và bảng tổng hợp được tạo lại theo cấu hình hiện tại. Cơ chế này giảm ghi lại bản ghi không đổi nhưng vẫn đọc bản chụp để so sánh.\n\nLần khảo sát ngày 04 tháng 10 năm 2026 ghi nhận 357.000 đơn và 399.696 chi tiết đơn ở nguồn. Số lượng đơn ở Silver và dòng bảng đo lường tương ứng phù hợp với quan sát nguồn. Báo cáo phân biệt kết quả đối chiếu số lượng với kiểm thử toàn bộ nội dung và đo hiệu năng cần bổ sung. Những giới hạn chính gồm độ đầy đủ bản chụp, tính nhất quán giữa các lô và việc công bố Gold theo từng mô hình.\n\nTừ khóa: kỹ thuật dữ liệu, ELT, Medallion, cập nhật tăng dần, khử trùng, mô hình chiều, điều phối dữ liệu.')
par=p('Mục lục','FrontTitle');par.paragraph_format.page_break_before=True
field(p(),'TOC \\o "1-3" \\t "Unnumbered,1,AppendixTitle,1,AppendixSection,2" \\h \\z')
par=p('Danh mục bảng','FrontTitle');par.paragraph_format.page_break_before=True
field(p(),'TOC \\t "TableCaption,1" \\h \\z')
par=p('Danh mục hình','FrontTitle');par.paragraph_format.page_break_before=True
field(p(),'TOC \\t "FigureCaption,1" \\h \\z')
p('Danh mục thuật ngữ','Unnumbered')
table(None,['Thuật ngữ','Nghĩa sử dụng trong báo cáo'],[['Kỹ thuật dữ liệu','Thiết kế và vận hành hệ thống đưa dữ liệu đến dạng sử dụng được'],['ELT','Trích xuất, nạp rồi biến đổi tại hệ thống đích'],['Bản chụp','Tập trạng thái dữ liệu trong phạm vi một lần đọc'],['Cập nhật tăng dần','Ghi phần mới hoặc thay đổi theo quy tắc mô hình'],['Khử trùng','Chọn bản ghi đại diện theo khóa và thứ tự xác định'],['Dấu vân tay','Giá trị rút gọn dùng để so sánh nội dung'],['Mức chi tiết','Ý nghĩa của một dòng trong bảng'],['Bảng đo lường','Bảng fact lưu đại lượng tại mức chi tiết đã chọn'],['Bảng chiều','Bảng dimension dùng phân loại và lọc'],['Dataset','Đối tượng tín hiệu cập nhật trong Airflow'],['DAG','Đồ thị có hướng không chu trình của công việc'],['CDC','Thu thập dữ liệu thay đổi, chưa triển khai trong đề tài'],['Lô dữ liệu','Đơn vị đồng bộ hoặc xử lý có phạm vi xác định']],[1.7,4.85])
sec=d.add_section(WD_SECTION_START.NEW_PAGE);page_number(sec,'decimal')
tables={
'requirements':('Ánh xạ yêu cầu và bằng chứng cần thu thập',['Yêu cầu','Đối tượng kiểm tra','Bằng chứng'],[['Không nhân bản','Khóa dòng đơn','Đếm khóa trùng và đối chiếu từng dòng'],['Chạy lại an toàn','Cùng bản chụp','So sánh khóa, dấu vân tay và chỉ tiêu'],['Cập nhật đơn cũ','Trạng thái đơn','Truy vấn trước và sau khi đổi trạng thái'],['Đúng phụ thuộc','Tác vụ và Dataset','Nhật ký công việc cùng lượt chạy'],['Có thể tái lập','Cấu hình và bộ sinh','Phiên bản mã, tham số và hồ sơ lô']],[1.4,1.6,3.55]),
'relations':('Quan hệ chính giữa các bảng nguồn',['Bảng cha','Bảng phụ thuộc','Quan hệ'],[['events','ticket_types','Một sự kiện có nhiều hạng vé'],['events','orders','Một sự kiện có nhiều đơn'],['orders','order_items','Một đơn có nhiều dòng'],['ticket_types','order_items','Một hạng có nhiều dòng đặt'],['orders','payments','Một đơn có nhiều lần thử']],[1.5,1.8,3.25]),
'change_cases':('Các nhánh của thuật toán cập nhật',['Tình huống','Điều kiện','Kết quả'],[['Mới','Khóa chưa có ở đích','Thêm dòng'],['Sửa','Khóa có và nội dung khác','Cập nhật dòng'],['Giữ nguyên','Nội dung và trạng thái không đổi','Không ghi lại'],['Xóa','Khóa đích vắng ở bản chụp đầy đủ','Đánh dấu xóa tại Silver'],['Khôi phục','Khóa quay lại khi đích đang xóa','Cập nhật và bỏ dấu xóa']],[1.05,3.0,2.5]),
'folders':('Trách nhiệm các nhóm mã nguồn',['Đường dẫn','Nội dung'],[['Source/SqlServer','Cấu trúc nguồn và bộ sinh dữ liệu'],['Airflow/dags','Đồ thị công việc chia theo tầng'],['Airflow/plugins','Thao tác và bộ cảm biến dùng chung'],['Dbt/Dbt-Postgres/models','Mô hình nguồn, Silver và Gold'],['Dbt/Dbt-Postgres/macros','Hàm dùng chung khi biên dịch SQL'],['Docker và compose.yaml','Đóng gói và cấu hình dịch vụ'],['PowerBI','Tệp báo cáo tiêu thụ Gold']],[2.9,3.65]),
'counts':('Quy mô nguồn tại ngày khảo sát 04 tháng 10 năm 2026',['Bảng','Số dòng','Ý nghĩa'],[['events','360','Sự kiện'],['ticket_types','1.080','Hạng vé'],['orders','357.000','Đơn'],['order_items','399.696','Chi tiết đơn'],['payments','420.792','Lần thử thanh toán']],[2.0,1.5,3.05]),
'years':('Đơn theo năm đặt tại thời điểm khảo sát',['Năm','Số đơn'],[['2020','42.000'],['2021','20.000'],['2022','30.000'],['2023','40.000'],['2024','55.000'],['2025','70.867'],['2026','99.133']],[2.0,4.55]),
'status':('Tổng hợp Gold theo trạng thái đơn tại thời điểm khảo sát',['Trạng thái','Số đơn','Số vé bán','Giá trị đồng'],[['PAID','293.274','636.959','188.306.020.500'],['EXPIRED','47.059','0','0'],['CANCELLED','16.657','0','0'],['PENDING','10','0','0']],[1.35,1.2,1.25,2.75]),
'tests':('Kế hoạch kiểm thử có kiểm soát chưa gán kết quả nghiệm thu',['Mã','Ca kiểm tra','Kết quả mong đợi'],[['T01','Nạp ban đầu','Khóa hợp lệ xuất hiện ở đúng tầng'],['T02','Chạy lại không đổi','Không tăng khóa hoặc chỉ tiêu'],['T03','Thêm đơn','Tăng đúng số đơn và dòng liên quan'],['T04','Đơn cũ chuyển PAID','Cập nhật giá trị tại ngày đặt'],['T05','Sửa giá trị dòng','Cập nhật đúng các tổng hợp'],['T06','Xóa khỏi bản chụp','Silver xóa mềm, Gold loại dòng'],['T07','Khôi phục khóa','Hoạt động lại, không tạo bản sao'],['T08','Trùng khóa ứng viên','Chọn theo thứ tự đã định'],['T09','Airbyte thất bại','Không phát thành công từ công việc lỗi'],['T10','dbt thất bại','Không phát đầu ra từ tác vụ lỗi'],['T11','Thiếu tín hiệu đầu vào','Chờ theo phụ thuộc khai báo'],['T12','Đối chiếu báo cáo','Kết quả cùng bộ lọc khớp SQL']],[.6,2.2,3.75])}
codes={
'dedup':'''row_number() over (
    partition by event_id
    order by updated_at desc nulls last,
             _source_extracted_at desc nulls last,
             _source_raw_id desc nulls last,
             _record_hash desc
) as version_rank
-- Tap ung vien giu version_rank = 1''',
'changed':'''select c.*
from candidate c
left join target t on c.event_id = t.event_id
where t.event_id is null
   or c._record_hash is distinct from t._record_hash
   or t._is_deleted''',
'dag':'''with DAG(
    dag_id="silver_ticket_events",
    schedule=INPUTS,
    **dag_options(),
) as dag:
    run_model = DbtBashOperator(
        task_id="run_silver_events",
        bash_command="dbt run --select "
          "path:models/silver/silver_events.sql",
        outlets=OUTPUTS,
        stage="silver",
    )'''}
first=True
for block in (B/'report_de.md').read_text(encoding='utf-8').split('\n\n'):
 block=block.strip()
 if not block:continue
 if block.startswith('#'):
  for ln in block.splitlines():
   m=re.match(r'^(#{1,3}) (.*)$',ln)
   if m:
    par=d.add_heading(m[2],len(m[1]))
    if first:par.paragraph_format.page_break_before=False;first=False
   elif ln.strip():p(ln)
 elif block.startswith('@TABLE '):table(*tables[block.split()[1]])
 elif block.startswith('@CODE '):code(codes[block.split()[1]])
 elif block=='@FIG architecture':
  table('Luồng dữ liệu và trách nhiệm điều khiển',['Bước','Dữ liệu','Thành phần thực hiện'],[['1','SQL Server tới Bronze','Airbyte đọc và nạp'],['2','Bronze tới Silver','dbt chuẩn hóa và hợp nhất'],['3','Silver tới Gold','dbt xây mô hình phân tích'],['4','Gold tới báo cáo','Power BI đọc bảng công bố'],['Điều phối','Lịch và trạng thái hoàn thành','Airflow gọi dịch vụ và phát tín hiệu']],[.85,2.6,3.1])
 elif block=='@FIG bi':
  pic=Path('C:/Users/zicza/AppData/Local/Temp/codex-clipboard-176a6a01-1a87-4270-8aa6-200a9897805c.png')
  if pic.exists():
   par=p();par.paragraph_format.keep_with_next=True;par.paragraph_format.first_line_indent=Inches(0);par.add_run().add_picture(str(pic),width=Inches(6.3));caption('Hình','Quan hệ bảng trong mô hình Power BI của dự án')
 else:p(block)
p('Tài liệu tham khảo','Unnumbered')
refs=[
('Databricks','Giới thiệu kiến trúc Medallion','https://www.databricks.com/blog/what-is-medallion-architecture'),
('Airbyte','Chế độ đồng bộ đầy đủ và ghi đè','https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite'),
('dbt Labs','Cấu hình mô hình cập nhật tăng dần','https://docs.getdbt.com/docs/build/incremental-models'),
('PostgreSQL Global Development Group','Lệnh MERGE trong PostgreSQL 17','https://www.postgresql.org/docs/17/sql-merge.html'),
('Microsoft','Mô hình sao và vai trò trong Power BI','https://learn.microsoft.com/en-us/power-bi/guidance/star-schema'),
('Apache Software Foundation','Lập lịch theo dữ liệu trong Airflow 2.10.5','https://airflow.apache.org/docs/apache-airflow/2.10.5/authoring-and-scheduling/datasets.html'),
('Docker','Mô hình ứng dụng Compose','https://docs.docker.com/compose/intro/compose-application-model/'),
('Nguyễn Hoàng Hiệp','Mã nguồn và cấu hình hệ thống Ticket_Project','Source/SqlServer; Dbt/Dbt-Postgres; Airflow/dags; Airflow/plugins; compose.yaml'),
('Hồ sơ khảo sát dự án','Truy vấn số lượng và tổng hợp ngày 04 tháng 10 năm 2026','Báo cáo khảo sát trong Reports/Defense_20261004 và truy vấn tái kiểm tra ở Phụ lục B')]
for i,(who,title,url) in enumerate(refs,1):
 par=p(f'[{i}] {who}. {title}. {url}. '+('Truy cập ngày 06/10/2026.' if i<=7 else 'Tài liệu dự án.'));par.paragraph_format.first_line_indent=Inches(0);par.paragraph_format.line_spacing=1.2
p('Phụ lục A Từ điển dữ liệu và ánh xạ mô hình','AppendixTitle')
p('Từ điển sau mô tả các trường do mô hình đọc hoặc công bố tại PostgreSQL, đối chiếu với khai báo YAML của dự án [8]. Kiểu của nguồn SQL Server có thể khác kiểu chuẩn hóa tại đích. Các trường kỹ thuật của Airbyte không được xem là nội dung nghiệp vụ để tính dấu vân tay.')
old=ast.parse((B/'report_builder.py').read_text(encoding='utf-8'))
desc={}
for node in old.body:
 if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='desc' for t in node.targets):desc=ast.literal_eval(node.value)
desc.update({'order_item_id':'Khóa duy nhất của dòng đơn','channel_key':'Khóa chiều kênh bán','status_key':'Khóa chiều trạng thái','_record_hash':'Dấu vân tay nội dung nghiệp vụ','_is_deleted':'Dấu xóa khỏi bản chụp đầy đủ','_loaded_at':'Thời điểm ghi tại kho','paid_orders':'Số đơn thanh toán phân biệt','total_orders':'Số đơn phân biệt'})
def schema(rel,indent):
 result=[];c=None
 for line in (R/rel).read_text(encoding='utf-8').splitlines():
  t=re.match(r'^'+(' '*indent)+r'- name: (.+)$',line);co=re.match(r'^'+(' '*(indent+4))+r'- name: (.+)$',line)
  if t:result.append({'name':t[1].strip(),'columns':[]});c=None
  elif co:c={'name':co[1].strip()};result[-1]['columns'].append(c)
  elif c and line.strip().startswith('data_type:'):c['type']=line.split(':',1)[1].strip().strip('"')
 return result
for t in schema('Dbt/Dbt-Postgres/models/sources.yml',6):
 p('Bảng '+t['name'],'AppendixSection')
 table('Các trường nghiệp vụ của '+t['name'],['Trường','Kiểu tại đích','Ý nghĩa'],[(c['name'],c.get('type','Theo khai báo nguồn'),desc.get(c['name'],c['name'])) for c in t['columns']],[1.8,1.6,3.15])
for rel in ['Dbt/Dbt-Postgres/models/gold/schema.yml']:
 for t in schema(rel,2):
  p('Bảng '+t['name'],'AppendixSection')
  rows=[]
  for c in t['columns']:
   meaning=desc.get(c['name'],c['name'])
   if t['name']=='agg_daily_sales' and c['name'] in ['sales_amount','sold_quantity']:meaning='Tổng giá trị vé theo nhóm' if c['name']=='sales_amount' else 'Tổng số vé đã bán theo nhóm'
   rows.append((c['name'],c.get('type','Theo mô hình'),meaning))
  table('Các trường công bố của '+t['name'],['Trường','Kiểu','Ý nghĩa'],rows,[1.8,1.6,3.15])
p('Ánh xạ mô hình và đầu ra','AppendixSection')
table('Ánh xạ các mô hình chính',['Mô hình','Đầu vào','Đích'],[[f'silver_{n}.sql',f'bronze.{n}',f'silver.{n}'] for n in ['events','ticket_types','orders','order_items','payments']]+[['fact_ticket_sales.sql','Silver và các bảng chiều','gold.fact_ticket_sales'],['agg_daily_sales.sql','Bảng đo lường bán vé','gold.agg_daily_sales']],[2.25,2.15,2.15])
p('Phụ lục B Truy vấn đối chiếu và hồ sơ thử nghiệm','AppendixTitle')
p('Các truy vấn chỉ đọc dưới đây dùng tái kiểm tra dữ liệu. Số lượng mới có thể khác kết quả khảo sát nếu đã nạp thêm lô. Khi lưu kết quả cần ghi ngày, cơ sở dữ liệu và phạm vi lọc. Không ghi đè kết quả cũ rồi coi đó là cùng một lần thực nghiệm.')
p('Đếm nguồn và kiểm tra khóa','AppendixSection')
code("SELECT 'orders' AS ten_bang, COUNT_BIG(*) AS so_dong\nFROM dbo.orders;\nSELECT order_item_id, COUNT(*) AS so_lan\nFROM dbo.order_items\nGROUP BY order_item_id\nHAVING COUNT(*) > 1;")
p('Truy vấn thứ hai trả các khóa xuất hiện nhiều hơn một lần. Kết quả rỗng chỉ xác nhận tính duy nhất trong bảng được hỏi ở thời điểm đọc, chưa xác nhận nội dung tương ứng ở kho đích.')
p('Đối chiếu giá trị Gold','AppendixSection')
code("SELECT s.order_status,\n       COUNT(DISTINCT f.order_id) AS so_don,\n       SUM(f.sold_quantity) AS so_ve,\n       SUM(f.sales_amount) AS gia_tri\nFROM gold.fact_ticket_sales f\nJOIN gold.dim_status s USING (status_key)\nGROUP BY s.order_status\nORDER BY s.order_status;")
p('Cần giữ cùng bộ lọc ngày, sự kiện và kênh khi đối chiếu với Power BI. Nếu bảng đo lường đã loại dòng xóa theo quy tắc công bố, không tự thêm một tập dòng lịch sử khác vào phép so sánh.')
p('Kiểm tra quan hệ và quy tắc đo lường','AppendixSection')
code("SELECT f.order_item_id\nFROM gold.fact_ticket_sales f\nLEFT JOIN gold.dim_event e ON e.event_id = f.event_id\nWHERE e.event_id IS NULL;\n\nSELECT f.order_item_id\nFROM gold.fact_ticket_sales f\nJOIN gold.dim_status s USING (status_key)\nWHERE s.order_status <> 'PAID'\n  AND (f.sales_amount <> 0 OR f.sold_quantity <> 0);")
p('Truy vấn quan hệ phát hiện dòng không tra được chiều sự kiện, còn truy vấn trạng thái phát hiện đóng góp khác không từ đơn chưa PAID. Các trường hợp rỗng cần được kiểm tra riêng theo khai báo không rỗng, vì phép so sánh số thông thường không phát hiện mọi giá trị NULL.')
p('Hồ sơ của một ca kiểm thử','AppendixSection')
table('Thông tin cần lưu cho từng ca kiểm thử',['Thông tin','Nội dung cần ghi'],[['Định danh','Mã ca, ngày và người thực hiện'],['Phiên bản','Mã nguồn, cấu hình và tham số'],['Trạng thái đầu','Khóa chọn, giá trị và bản chụp trước'],['Thao tác','Thay đổi cụ thể trong môi trường thử'],['Dấu vết chạy','Mã Airbyte, mã lượt DAG và nhật ký'],['Kết quả','Truy vấn trước sau, so với kỳ vọng'],['Hoàn tác','Cách đưa môi trường thử về trạng thái đã định']],[1.6,4.95])
p('Hồ sơ đo hiệu năng','AppendixSection')
table('Thông tin cho một lượt đo hiệu năng',['Nhóm','Thông tin'],[['Môi trường','CPU, bộ nhớ, cấu hình PostgreSQL và số luồng'],['Dữ liệu','Số dòng, tỷ lệ thay đổi, bản chụp và phiên bản bộ sinh'],['Cách chạy','Khởi tạo hay tăng dần, trạng thái bộ nhớ đệm'],['Thời gian','Airbyte, dbt và toàn tuyến được đo riêng'],['Khối lượng ghi','Số dòng thêm, cập nhật và loại bỏ'],['Tổng hợp','Số lượt lặp, trung vị và khoảng dao động']],[1.6,4.95])
p('Phụ lục C Hướng dẫn vận hành và trình diễn','AppendixTitle')
p('Khởi động và truy cập','AppendixSection')
p('Mở Docker Desktop và đứng tại thư mục Ticket_Project trước khi gọi các chương trình vận hành. Airbyte có vòng đời riêng qua abctl. Một dịch vụ khởi tạo đã kết thúc thành công không nhất thiết phải duy trì trạng thái đang chạy như dịch vụ web.')
code('powershell -ExecutionPolicy Bypass -File .\\Scripts\\start.ps1')
table('Địa chỉ truy cập cục bộ',['Thành phần','Địa chỉ'],[['Airflow','http://localhost:8080'],['Airbyte','http://localhost:8000'],['Kho PostgreSQL từ Windows','localhost:5433'],['Cơ sở dữ liệu phân tích','ticketing_analytics']],[2.5,4.05])
p('Nạp bổ sung dữ liệu lịch sử','AppendixSection')
p('Lệnh đầu chỉ sinh và ghi hồ sơ lô. Lệnh thứ hai thêm dữ liệu nguồn khi người vận hành đã quyết định nạp. Giá trị khởi tạo mới có thể tạo một lô mới cùng năm, không thay thế dữ liệu đã có. Dùng python để chạy tệp trong terminal thay vì phụ thuộc liên kết mở tệp của Windows.')
code('python .\\Source\\SqlServer\\append_history.py --start-year 2020 --end-year 2020 --orders-per-year 1000 --seed 3\n\npython .\\Source\\SqlServer\\append_history.py --start-year 2020 --end-year 2020 --orders-per-year 1000 --seed 3 --load')
p('Nếu gặp thông báo lô có số lượng khác, cần kiểm tra lô cũ và mục đích thêm hay thay dữ liệu. Không bỏ cơ chế bảo vệ hoặc liên tục đổi giá trị khởi tạo chỉ để làm thông báo lỗi biến mất. Sau nạp, chạy tuyến đồng bộ phù hợp rồi làm mới báo cáo khi Gold hoàn thành.')
p('Chạy biến đổi theo phạm vi','AppendixSection')
code('dbt run --select path:models/silver/silver_events.sql\ndbt run --select tag:silver\ndbt run --select tag:gold\ndbt test')
p('Các lệnh cần môi trường có dbt và cấu hình kết nối hợp lệ. Lệnh kiểm tra cuối được gọi riêng, không suy ra đã chạy từ trạng thái thành công của dbt run. Chế độ tạo lại toàn bộ chỉ nên dùng khi có lý do về cấu trúc hoặc dữ liệu và đã biết phạm vi tác động.')
p('Trình tự minh họa khi bảo vệ','AppendixSection')
p('Bắt đầu từ quan hệ năm bảng nguồn và giải thích một đơn có nhiều dòng, nhiều lần thử thanh toán. Tiếp theo mở DAG Bronze để chỉ ra vị trí gửi yêu cầu và vị trí chờ kết quả. Chuyển sang mô hình Silver để giải thích xếp hạng, dấu vân tay và các nhánh thay đổi. Ở Gold, chỉ rõ mức chi tiết và điều kiện PAID. Cuối cùng dùng một bộ lọc Power BI đối chiếu với SQL.')
p('Khi không có đủ thời gian chạy toàn bộ trong buổi bảo vệ, sử dụng nhật ký và kết quả đã lưu có ngày, phiên bản rõ ràng. Không trình bày một ảnh cũ như trạng thái đang chạy trực tiếp. Các câu hỏi phản biện nên tập trung vào giả thiết bản chụp, độ nhất quán, khả năng chạy lại và giới hạn chưa có số đo.')
for rootel in [d.element,d.styles.element]:
 for x in list(rootel.iter(qn('w:pBdr'))):x.getparent().remove(x)
d.settings.element.append(el('updateFields',val='true'))
d.save(OUT/'report.docx')
print('Paragraph words:',sum(len(x.text.split()) for x in d.paragraphs),'Tables:',len(d.tables),'Headings:',sum(x.style.name.startswith('Heading') for x in d.paragraphs))
print(OUT/'report.docx')
