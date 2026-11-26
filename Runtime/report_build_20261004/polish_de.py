from pathlib import Path
import re
from docx import Document
from docx.oxml.ns import qn

path = Path('C:/Users/zicza/AppData/Local/Temp/ticket_report_de_20261006/report.docx')
doc = Document(path)
for p in doc.paragraphs:
    if re.match(r'^\[\d+\] ', p.text):
        p.alignment = 0
    if p.style.name == 'AppendixTitle':
        prev = p._p.getprevious()
        while prev is not None and prev.tag == qn('w:p') and not ''.join(prev.itertext()).strip() and prev.find('.//' + qn('w:sectPr')) is None:
            older = prev.getprevious()
            prev.getparent().remove(prev)
            prev = older
doc.save(path)
print('Reference alignment and empty appendix separators updated.')
