from docx import Document
from pathlib import Path
from docx.oxml.ns import qn
p=Path('C:/Users/zicza/AppData/Local/Temp/ticket_report_20261004/report.docx')
d=Document(p)
for root in [d.element,d.styles.element]:
 for el in list(root.iter(qn('w:pBdr'))):el.getparent().remove(el)
for par in d.paragraphs:
 if par.text=='Bảng 2 Số đơn theo năm đặt tại nguồn':
  par.text='Bảng 1 Số đơn theo năm đặt tại nguồn'
 if par.text=='Bảng 1 Ánh xạ thành phần và dữ liệu':
  par.text='Bảng 2 Ánh xạ thành phần và dữ liệu'
 if par.text.startswith('Ghi riêng thời gian Airbyte, dbt và toàn tuyến.'):
  par.paragraph_format.keep_with_next=True
for table in d.tables:
 for cell in table.rows[0].cells:
  for par in cell.paragraphs:par.paragraph_format.keep_with_next=True
d.save(p)
