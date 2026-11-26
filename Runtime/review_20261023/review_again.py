from pathlib import Path
from docx import Document
from docx.oxml.ns import qn
from zipfile import ZipFile
from lxml import etree
from collections import defaultdict
from hashlib import sha256
import json, re

ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'12220016-NguyenHoangHiep.docx'
OUT=Path(__file__).parent/'pass2'
OUT.mkdir(exist_ok=True)
initial=sha256(SOURCE.read_bytes()).hexdigest()
d=Document(SOURCE)
baseline=json.loads((OUT.parent/'audit.json').read_text(encoding='utf8'))
old_hashes={sha256(Path(x['path']).read_bytes()).hexdigest():x['caption'] for x in baseline['images']}
images=[]
for i,p in enumerate(d.paragraphs):
    for b in p._p.findall('.//'+qn('a:blip')):
        rid=b.get(qn('r:embed'))
        if not rid: continue
        part=d.part.related_parts[rid]
        caption=next((x.text for x in d.paragraphs[i+1:i+4] if x.text.strip()),'')
        digest=sha256(part.blob).hexdigest()
        dest=OUT/f'P{i:03d}_{Path(str(part.partname)).name}'
        dest.write_bytes(part.blob)
        images.append({'p':i,'caption':caption,'changed':digest not in old_hashes,'path':str(dest)})
print('IMAGES',json.dumps(images,ensure_ascii=False))
ref_start=next(i for i,p in enumerate(d.paragraphs) if p.text.strip()=='TÀI LIỆU THAM KHẢO')
print('CITATIONS',[(i,p.text) for i,p in enumerate(d.paragraphs[:ref_start]) if re.search(r'\[\s*\d+',p.text)])
duplicates=defaultdict(list)
for i,p in enumerate(d.paragraphs):
    if len(p.text)>100: duplicates[p.text].append(i)
print('DUPLICATE_PARAGRAPHS',[(idx,s[:100]) for s,idx in duplicates.items() if len(idx)>1])
print('PAPER',[(s.page_width.cm,s.page_height.cm,s.left_margin.cm,s.right_margin.cm) for s in d.sections])
print('TABLES',[[[c.text for c in r.cells] for r in t.rows] for t in d.tables])
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with ZipFile(SOURCE) as z:
    xml=etree.fromstring(z.read('word/document.xml'))
    for sdt in xml.xpath('//w:sdt',namespaces=ns):
        print('TOC',' | '.join(sdt.xpath('.//w:t/text()',namespaces=ns)))
    print('TRACKED',len(xml.xpath('//w:ins|//w:del',namespaces=ns)))
    print('NOTES',len(xml.xpath('//w:footnoteReference|//w:endnoteReference',namespaces=ns)))
result={'sha256':initial,'images':images,'paragraphs':[p.text for p in d.paragraphs]}
(OUT/'audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
assert sha256(SOURCE.read_bytes()).hexdigest()==initial
print('SOURCE_UNCHANGED',initial)
