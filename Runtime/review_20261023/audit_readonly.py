from pathlib import Path
from docx import Document
from docx.oxml.ns import qn
from zipfile import ZipFile
from lxml import etree
from PIL import Image, ImageDraw, ImageFont
from collections import Counter
from hashlib import sha256
import json
import re

BASE=Path(__file__).resolve().parents[3]
SOURCE=BASE/'12220016-NguyenHoangHiep.docx'
OUT=Path(__file__).parent
payload=SOURCE.read_bytes()
digest=sha256(payload).hexdigest()
d=Document(SOURCE)
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
images=[]
for i,p in enumerate(d.paragraphs):
    for blip in p._p.findall('.//'+qn('a:blip')):
        rid=blip.get(qn('r:embed'))
        if not rid: continue
        part=d.part.related_parts[rid]
        ext=Path(str(part.partname)).suffix
        dest=OUT/f'P{i:03d}_{Path(str(part.partname)).name}'
        dest.write_bytes(part.blob)
        cap=next((q.text for q in d.paragraphs[i+1:i+4] if q.text.strip()),'')
        images.append({'p':i,'path':str(dest),'caption':cap})

with ZipFile(SOURCE) as z:
    doc=etree.fromstring(z.read('word/document.xml'))
    print('APP',z.read('docProps/app.xml').decode('utf8'))
    print('FIELDS',doc.xpath('//w:instrText/text()',namespaces=ns))
    print('SDT CONTENTS')
    for sdt in doc.xpath('//w:sdt',namespaces=ns):
        print(' | '.join(sdt.xpath('.//w:t/text()',namespaces=ns)))
    print('TRACKED',len(doc.xpath('//w:ins|//w:del',namespaces=ns)))
    print('EMBEDDED TEXTBOX TEXT',doc.xpath('//w:txbxContent//w:t/text()',namespaces=ns))
    print('COMMENTS', 'word/comments.xml' in z.namelist())
    print('CONTENT CITATIONS BEFORE REFERENCES',[(i,p.text) for i,p in enumerate(d.paragraphs[:604]) if re.search(r'\[\d+\]',p.text)])
    print('HYPERLINKS',[(r.rId,r.target_ref) for r in d.part.rels.values() if r.reltype.endswith('/hyperlink')])
    print('SECTIONS',[(s.page_width.cm,s.page_height.cm,s.top_margin.cm,s.bottom_margin.cm,s.left_margin.cm,s.right_margin.cm) for s in d.sections])
    print('INLINE DIMENSIONS',[(round(s.width.cm,2),round(s.height.cm,2)) for s in d.inline_shapes])
    print('FIGURES',json.dumps(images,ensure_ascii=False))
    print('HEADINGS')
    for i,p in enumerate(d.paragraphs):
        if p.style.name.startswith('Heading'):
            print(i,p.style.name,p.text,etree.tostring(p._p.find(qn('w:pPr')),encoding='unicode'))

font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
for start in range(0,len(images),6):
    group=images[start:start+6]
    sheet=Image.new('RGB',(1800,1900),'#e5e9ec')
    draw=ImageDraw.Draw(sheet)
    for j,item in enumerate(group):
        x=(j%2)*900; y=(j//2)*630
        draw.rectangle((x+8,y+8,x+892,y+622),fill='white')
        draw.text((x+20,y+16),f'P{item["p"]}  '+item['caption'][:70],font=font,fill='black')
        try:
            with Image.open(item['path']) as im:
                im=im.convert('RGB'); im.thumbnail((850,550),Image.Resampling.LANCZOS)
                sheet.paste(im,(x+(900-im.width)//2,y+65+(550-im.height)//2))
        except Exception as e: print('IMAGE_ERROR',e)
    sheet.save(OUT/f'images_{start+1:02d}_{start+len(group):02d}.jpg',quality=90)

assert sha256(SOURCE.read_bytes()).hexdigest()==digest
(OUT/'audit.json').write_text(json.dumps({'sha256':digest,'images':images},ensure_ascii=False,indent=2),encoding='utf8')
print('SOURCE_UNCHANGED_SHA256',digest)
