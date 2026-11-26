from pathlib import Path
from docx import Document
from docx.oxml.ns import qn
from lxml import etree
from zipfile import ZipFile
from hashlib import sha256
from collections import defaultdict
import difflib,json,re

HERE=Path(__file__).parent
ROOT=HERE.parents[2]
SOURCE=ROOT/'12220016-NguyenHoangHiep.docx'
OUT=HERE/'pass3';OUT.mkdir(exist_ok=True)
baseline=json.loads((HERE/'pass2'/'audit.json').read_text(encoding='utf8'))
before=sha256(SOURCE.read_bytes()).hexdigest()
d=Document(SOURCE); new=[p.text for p in d.paragraphs]
print('COUNTS',len(d.paragraphs),len(d.tables),len(d.inline_shapes))
print('CONTENT CHANGES SINCE PREVIOUS REVIEW')
for tag,a,b,c,e in difflib.SequenceMatcher(None,baseline['paragraphs'],new,autojunk=False).get_opcodes():
    if tag=='equal':continue
    print('CHANGE',tag,'OLD',a,b,'NEW',c,e)
    print('OLD:','\n'.join(baseline['paragraphs'][a:b]))
    print('NEW:','\n'.join(new[c:e]))

old_hash={sha256(Path(x['path']).read_bytes()).hexdigest() for x in baseline['images']}
imgs=[]
for i,p in enumerate(d.paragraphs):
    for b in p._p.findall('.//'+qn('a:blip')):
        rid=b.get(qn('r:embed'))
        if not rid:continue
        part=d.part.related_parts[rid]
        caption=next((p.text for p in d.paragraphs[i+1:i+4] if p.text.strip()),'')
        dest=OUT/f'P{i:03d}_{Path(str(part.partname)).name}'
        dest.write_bytes(part.blob)
        imgs.append({'p':i,'caption':caption,'changed':sha256(part.blob).hexdigest() not in old_hash,'path':str(dest)})
print('IMAGES',json.dumps(imgs,ensure_ascii=False))
ref_start=next(i for i,p in enumerate(d.paragraphs) if p.text.strip()=='TÀI LIỆU THAM KHẢO')
print('CITATIONS',[(i,p.text) for i,p in enumerate(d.paragraphs[:ref_start]) if re.search(r'\[\s*\d+',p.text)])
print('FIGURE_SOURCES',[(i,p.text) for i,p in enumerate(d.paragraphs) if p.text.startswith('Nguồn:')])
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with ZipFile(SOURCE) as z:
    xml=etree.fromstring(z.read('word/document.xml'))
    toc=[' | '.join(s.xpath('.//w:t/text()',namespaces=ns)) for s in xml.xpath('//w:sdt',namespaces=ns)]
    print('TOC',*toc)
    print('TRACKED',len(xml.xpath('//w:ins|//w:del',namespaces=ns)))
print('HEADINGS',[(i,p.style.name,p.text) for i,p in enumerate(d.paragraphs) if p.style.name.startswith('Heading')])
print('PAPER',[(s.page_width.cm,s.page_height.cm,s.left_margin.cm,s.right_margin.cm) for s in d.sections])
available=d.sections[0].page_width-d.sections[0].left_margin-d.sections[0].right_margin
print('OVERSIZE',[(i+1,round(s.width.cm,2)) for i,s in enumerate(d.inline_shapes) if s.width>available])
snapshot={'sha256':before,'paragraphs':new,'tables':[[[c.text for c in r.cells] for r in t.rows] for t in d.tables],'images':imgs}
(OUT/'audit.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2),encoding='utf8')
assert sha256(SOURCE.read_bytes()).hexdigest()==before
print('SOURCE_UNCHANGED',before)
