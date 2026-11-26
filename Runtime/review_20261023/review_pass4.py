from pathlib import Path
from docx import Document
from docx.oxml.ns import qn
from zipfile import ZipFile
from lxml import etree
from hashlib import sha256
import json,re,difflib

HERE=Path(__file__).parent
ROOT=HERE.parents[2]
SOURCE=ROOT/'12220016-NguyenHoangHiep.docx'
OUT=HERE/'pass4'; OUT.mkdir(exist_ok=True)
old=json.loads((HERE/'pass3'/'audit.json').read_text(encoding='utf8'))
initial=sha256(SOURCE.read_bytes()).hexdigest()
d=Document(SOURCE); new=[p.text for p in d.paragraphs]
print('COUNTS',len(new),len(d.tables),len(d.inline_shapes))
for tag,a,b,c,e in difflib.SequenceMatcher(None,old['paragraphs'],new,autojunk=False).get_opcodes():
    if tag=='equal':continue
    print('CHANGE',tag,'OLD',a,b,'NEW',c,e)
    print('OLD:','\n'.join(old['paragraphs'][a:b]))
    print('NEW:','\n'.join(new[c:e]))
tables=[[[c.text for c in r.cells] for r in t.rows] for t in d.tables]
print('TABLES_UNCHANGED',tables==old['tables'])
if tables!=old['tables']:
    for i,t in enumerate(tables):
        if i>=len(old['tables']) or t!=old['tables'][i]:print('TABLE_CHANGE',i,t)
old_hash={sha256(Path(x['path']).read_bytes()).hexdigest() for x in old['images']}
imgs=[]
for i,p in enumerate(d.paragraphs):
    for b in p._p.findall('.//'+qn('a:blip')):
        rid=b.get(qn('r:embed'))
        if not rid:continue
        part=d.part.related_parts[rid]
        caption=next((p.text for p in d.paragraphs[i+1:i+4] if p.text.strip()),'')
        changed=sha256(part.blob).hexdigest() not in old_hash
        dest=OUT/f'P{i:03d}_{Path(str(part.partname)).name}'
        dest.write_bytes(part.blob)
        imgs.append({'p':i,'caption':caption,'changed':changed,'path':str(dest)})
print('IMAGE_CHANGES',json.dumps([x for x in imgs if x['changed']],ensure_ascii=False))
ref=next(i for i,p in enumerate(d.paragraphs) if p.text.strip()=='TÀI LIỆU THAM KHẢO')
print('CITATIONS',[(i,p.text) for i,p in enumerate(d.paragraphs[:ref]) if re.search(r'\[\s*\d+',p.text)])
print('FIGURE_SOURCES',[(i,p.text) for i,p in enumerate(d.paragraphs) if p.text.startswith('Nguồn:')])
print('PAPER',[(s.page_width.cm,s.page_height.cm,s.left_margin.cm,s.right_margin.cm) for s in d.sections])
available=d.sections[0].page_width-d.sections[0].left_margin-d.sections[0].right_margin
print('OVERSIZE',[(i+1,round(s.width.cm,2)) for i,s in enumerate(d.inline_shapes) if s.width>available])
print('HEADINGS',[(i,p.style.name,p.text) for i,p in enumerate(d.paragraphs) if p.style.name.startswith('Heading')])
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with ZipFile(SOURCE) as z:
    xml=etree.fromstring(z.read('word/document.xml'))
    toc=[' | '.join(s.xpath('.//w:t/text()',namespaces=ns)) for s in xml.xpath('//w:sdt',namespaces=ns)]
    print('TOC',*toc)
    print('NOTES',len(xml.xpath('//w:footnoteReference|//w:endnoteReference',namespaces=ns)))
    print('TRACKED',len(xml.xpath('//w:ins|//w:del',namespaces=ns)))
    print('COMMENTS','word/comments.xml' in z.namelist())
    print('APP',etree.fromstring(z.read('docProps/app.xml')).find('{http://schemas.openxmlformats.org/officeDocument/2006/extended-properties}Pages').text)
print('TAIL',new[-7:])
(OUT/'audit.json').write_text(json.dumps({'sha256':initial,'paragraphs':new,'tables':tables,'images':imgs},ensure_ascii=False,indent=2),encoding='utf8')
assert sha256(SOURCE.read_bytes()).hexdigest()==initial
print('SOURCE_UNCHANGED',initial)
