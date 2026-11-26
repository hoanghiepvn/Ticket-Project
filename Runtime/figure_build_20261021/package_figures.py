from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from PIL import Image, ImageDraw, ImageFont

root=Path(__file__).resolve().parents[2]
out=root/'Reports'/'Figures_Thesis'
names=sorted(p for p in out.glob('*.png') if not p.stem.endswith('_preview'))
assert len(names)==6
for p in names:
    with Image.open(p) as im:
        im.verify()
    assert p.with_suffix('.svg').is_file()

sheet=Image.new('RGB',(1800,1550),'#EEF2F5')
draw=ImageDraw.Draw(sheet)
font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',25)
labels=['2.1 · Nguyên tắc Medallion','3.1 · Kiến trúc tổng thể','3.2 · Quan hệ dữ liệu nguồn',
        '3.3 · Mô hình dữ liệu Gold','3.4 · Cập nhật tăng dần','3.5 · Điều phối Dataset']
for i,(p,label) in enumerate(zip(names,labels)):
    x=20+(i%3)*595; y=20+(i//3)*760
    draw.rounded_rectangle((x,y,x+575,y+735),radius=10,fill='white')
    draw.text((x+22,y+18),label,fill='#203D54',font=font)
    with Image.open(p) as im:
        im=im.convert('RGB'); im.thumbnail((545,650),Image.Resampling.LANCZOS)
        sheet.paste(im,(x+(575-im.width)//2,y+65+(650-im.height)//2))
sheet.save(out/'Xem_nhanh_6_so_do.jpg',quality=94)

archive=root/'Reports'/'Bo_hinh_Khoa_luan_Medallion.zip'
with ZipFile(archive,'w',ZIP_DEFLATED) as z:
    for p in sorted(out.iterdir()):
        if p.suffix.lower() in {'.svg','.png','.md','.jpg'} and not p.stem.endswith('_preview'):
            z.write(p,'Figures_Thesis/'+p.name)
with ZipFile(archive) as z:
    assert z.testzip() is None
print(archive)
print('Verified: 6 PNG, 6 SVG, guide, contact sheet.')
