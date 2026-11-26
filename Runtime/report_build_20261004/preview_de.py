from pathlib import Path
import pypdfium2 as pdfium
from pypdf import PdfReader
p=Path('C:/Users/zicza/AppData/Local/Temp/ticket_report_de_20261006')
(p/'pages').mkdir(exist_ok=True)
pdf=pdfium.PdfDocument(str(p/'report.pdf'))
for i in range(len(pdf)):
 image=pdf[i].render(scale=1.25).to_pil()
 image.save(p/'pages'/f'page-{i+1}.png')
reader=PdfReader(p/'report.pdf')
(p/'pages.txt').write_text('\n\n'.join(f'PAGE {i+1}\n'+page.extract_text() for i,page in enumerate(reader.pages)),encoding='utf-8')
print('Pages',len(pdf))
for i,page in enumerate(reader.pages):
 t=page.extract_text()
 if 'Chương ' in t[:180] or i<10:print(i+1,t[:230].replace('\n',' / '))
