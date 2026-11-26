from pathlib import Path
import os
import pypdfium2 as pdfium

root=Path(os.environ['TEMP'])/'ticketing_chapter4_revision_20261013'
out=root/'pages'
out.mkdir(exist_ok=True)
pdf=pdfium.PdfDocument(str(root/'chapter4.pdf'))
for n in range(len(pdf)):
    page=pdf[n]
    page.render(scale=1.4).to_pil().save(out/f'page-{n+1}.png')
    print(f'Page {n+1}: '+page.get_textpage().get_text_range().replace('\r\n',' / ')[:140])
print('Pages:',len(pdf))
