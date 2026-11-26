from pathlib import Path
import os
import re
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(__file__).parent
OUT = Path(os.environ['TEMP']) / 'ticketing_chapter4_revision_20261013'
OUT.mkdir(parents=True, exist_ok=True)
doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
sec.left_margin, sec.right_margin = Cm(3), Cm(2)
sec.top_margin = sec.bottom_margin = Cm(2.5)
sec.footer_distance = Cm(1.2)
for name, size in [('Normal', 13), ('Title', 16), ('Heading 1', 14), ('Heading 2', 13)]:
    s = doc.styles[name]
    s.font.name = 'Times New Roman'
    s.font.size = Pt(size)
    s.font.color.rgb = RGBColor(0,0,0)
    s.element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'), 'Times New Roman')
    s.paragraph_format.space_after = Pt(6)
    s.paragraph_format.widow_control = True
    if name == 'Normal':
        s.paragraph_format.line_spacing = 1.5
        s.paragraph_format.first_line_indent = Cm(.75)
    else:
        s.font.bold = True
        s.paragraph_format.keep_with_next = True
        s.paragraph_format.space_before = Pt(12)
doc.core_properties.title = 'Chương 4 Triển khai và đánh giá hệ thống'
doc.core_properties.author = 'Nguyễn Hoàng Hiệp'

def inline(p, text, changed=False, code=False):
    parts = [text] if code else re.split(r'(`[^`]+`)', text)
    for part in parts:
        mono = code or (part.startswith('`') and part.endswith('`'))
        value = part if code or not mono else part[1:-1]
        r = p.add_run(value)
        if mono:
            r.font.name = 'Consolas'
            r.font.size = Pt(10.5 if code else 11.5)
        if changed:
            r.font.highlight_color = WD_COLOR_INDEX.YELLOW
    return p

def body(text, changed):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT if text.startswith('[') else WD_ALIGN_PARAGRAPH.JUSTIFY
    if text.startswith('['):
        p.paragraph_format.first_line_indent = Cm(0)
    return inline(p, text, changed)

def xml(tag, **attrs):
    x = OxmlElement('w:' + tag)
    for k,v in attrs.items(): x.set(qn('w:'+k), str(v))
    return x

table_count = 0
def add_table(lines, changed):
    global table_count
    rows = [[x.strip() for x in ln.strip().strip('|').split('|')] for ln in lines]
    rows.pop(1)
    table_count += 1
    titles = ['Môi trường triển khai', 'Các trang báo cáo Power BI', 'Kết quả thực thi mô hình dbt', 'Quy mô nguồn ngày 04 tháng 10 năm 2026', 'Chỉ tiêu bán vé ngày 04 tháng 10 năm 2026']
    cp = doc.add_paragraph()
    cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cp.paragraph_format.first_line_indent = Cm(0)
    cp.paragraph_format.keep_with_next = True
    cp.paragraph_format.space_before = Pt(6)
    inline(cp, f'Bảng 4.{table_count} {titles[table_count-1]}', changed)
    for r in cp.runs: r.bold = True; r.font.size = Pt(12)
    t = doc.add_table(rows=0, cols=len(rows[0]))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    widths = {1:[8.5,7.5],2:[6,10],3:[7.5,3.5,5],4:[9,7],5:[3.5,3.2,3.8,5.5]}[table_count]
    for col,w in zip(t.columns,widths): col.width = Cm(w)
    borders=xml('tblBorders')
    for name in ['top','left','bottom','right','insideH','insideV']:
        borders.append(xml(name,val='single',sz='4',color='D9D9D9'))
    t._tbl.tblPr.append(borders)
    for i, vals in enumerate(rows):
        row=t.add_row()
        row._tr.get_or_add_trPr().append(xml('cantSplit'))
        if i == 0: row._tr.get_or_add_trPr().append(xml('tblHeader'))
        for j,(cell,value,w) in enumerate(zip(row.cells,vals,widths)):
            cell.width=Cm(w)
            cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            pr=cell._tc.get_or_add_tcPr()
            margins=xml('tcMar')
            for side in ['top','bottom','left','right']: margins.append(xml(side,w='85',type='dxa'))
            pr.append(margins)
            if i==0: pr.append(xml('shd',fill='E8EDF1',val='clear'))
            p=cell.paragraphs[0]
            p.paragraph_format.first_line_indent=Cm(0)
            p.paragraph_format.line_spacing=1.1
            p.paragraph_format.space_after=Pt(3)
            p.paragraph_format.space_before=Pt(3)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j==0 or table_count==2 else WD_ALIGN_PARAGRAPH.CENTER
            if i>0 and table_count in (3,4,5) and j>0: p.alignment=WD_ALIGN_PARAGRAPH.RIGHT if j>1 or table_count!=3 else WD_ALIGN_PARAGRAPH.CENTER
            inline(p,value,changed)
            for r in p.runs:
                r.font.size=Pt(11.5)
                if i==0: r.bold=True
    p=doc.add_paragraph()
    p.paragraph_format.first_line_indent=Cm(0)
    p.paragraph_format.space_after=Pt(3)
    p.paragraph_format.line_spacing=1
    p.add_run().font.size=Pt(3)

lines=(ROOT/'chapter4.md').read_text(encoding='utf-8').splitlines()
i=0; changed=False; changed_paragraphs=0
while i<len(lines):
    line=lines[i]
    if line==':::changed': changed=True; i+=1; continue
    if line==':::': changed=False; i+=1; continue
    if not line.strip(): i+=1; continue
    if line.startswith('```'):
        code=[]; i+=1
        while i<len(lines) and not lines[i].startswith('```'): code.append(lines[i]); i+=1
        p=doc.add_paragraph()
        p.paragraph_format.first_line_indent=Cm(0)
        p.paragraph_format.line_spacing=1
        p.paragraph_format.space_before=Pt(4)
        p.paragraph_format.space_after=Pt(8)
        p.paragraph_format.keep_together=True
        inline(p,'\n'.join(code),changed,True)
        changed_paragraphs+=int(changed)
        i+=1; continue
    if line.startswith('|'):
        table_lines=[]
        while i<len(lines) and lines[i].startswith('|'): table_lines.append(lines[i]); i+=1
        add_table(table_lines,changed); continue
    if line.startswith('#'):
        level=len(line)-len(line.lstrip('#'))
        title=line[level:].strip()
        p=doc.add_paragraph(style='Title' if level==1 else f'Heading {level-1}')
        p.paragraph_format.first_line_indent=Cm(0)
        if level==1:
            p.alignment=WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before=Pt(0)
            p.paragraph_format.space_after=Pt(16)
        inline(p,title,changed)
        changed_paragraphs+=int(changed)
        i+=1; continue
    parts=[line]; i+=1
    while i<len(lines) and lines[i].strip() and not lines[i].startswith(('#','|','```',':::')):
        parts.append(lines[i]); i+=1
    body(' '.join(parts),changed)
    changed_paragraphs+=int(changed)

footer=sec.footer.paragraphs[0]
footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
footer.paragraph_format.first_line_indent=Cm(0)
fld=xml('fldSimple',instr='PAGE')
footer._p.append(fld)
for root in [doc.element,doc.styles.element]:
    for b in list(root.iter(qn('w:pBdr'))): b.getparent().remove(b)
doc.save(OUT/'chapter4.docx')
print(f'Created {len(doc.paragraphs)} paragraphs, {table_count} tables, {changed_paragraphs} highlighted blocks.')
print(OUT/'chapter4.docx')
