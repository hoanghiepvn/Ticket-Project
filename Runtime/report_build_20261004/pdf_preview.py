from pathlib import Path
import pypdfium2 as pdfium
import pdfplumber,json,hashlib
base=Path('C:/Users/zicza/AppData/Local/Temp/ticket_report_20261004')
out=base/'pages';out.mkdir(exist_ok=True)
pdf=pdfium.PdfDocument(str(base/'report.pdf'))
changed=[]
for i,page in enumerate(pdf):
 target=out/f'page-{i+1}.png'
 old=hashlib.sha256(target.read_bytes()).hexdigest() if target.exists() else None
 page.render(scale=1.4).to_pil().save(target)
 if old!=hashlib.sha256(target.read_bytes()).hexdigest():changed.append(i+1)
with pdfplumber.open(base/'report.pdf') as pp:
 stats=[{'page':i+1,'words':len(page.extract_words()),'start':(page.extract_text() or '')[:95]} for i,page in enumerate(pp.pages)]
print('Changed pages:',changed)
print('Total pages:',len(pdf))
