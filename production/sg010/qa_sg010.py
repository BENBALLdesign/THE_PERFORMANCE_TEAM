"""SG-010 visual verification proofs (Part B step 9): render every staged reading page into contact sheets.

Reads the staged shelf (shelf_sg010.SHELF) and writes PNG contact sheets to the Seed Bank work folder `qa-final`.
Original source PDFs (carried byte-exact) are not re-proofed. Colour sheets cover every page of every guide, appendix,
card deck, property PDF and the Start Here directory; grayscale sheets cover the pages where colour carries meaning
(compact charts, contents leaves, cards, APP-F/APP-H). Card proofs at 100 % add a 5 x 7 legibility check.
Usage: python -X utf8 -B qa_sg010.py   -> prints the sheet index (qa-final/index.json)
"""
from prepare import *
import re
team_paths.ensure_pymupdf()
import pymupdf as fitz
from PIL import Image,ImageDraw,ImageOps
from shelf_sg010 import SHELF
QA=WORK/'qa-final'
DPI=62;COLS=4;ROWS=2
def render(pdf,i,dpi=DPI,gray=False):
    p=fitz.open(pdf)[i];pm=p.get_pixmap(dpi=dpi,colorspace='gray' if gray else 'rgb');im=Image.frombytes('L' if gray else 'RGB',(pm.w,pm.h),pm.samples)
    return im
def sheet(label,pdf,pages,dest,gray=False,cols=COLS,rows=ROWS,dpi=DPI):
    ims=[render(pdf,i,dpi,gray) for i in pages];w=max(i.width for i in ims);h=max(i.height for i in ims);pad=14
    out=Image.new('RGB',(cols*(w+pad)+pad,rows*(h+pad+18)+pad),(120,120,120));d=ImageDraw.Draw(out)
    for k,(i,im) in enumerate(zip(pages,ims)):
        x=pad+(k%cols)*(w+pad);y=pad+(k//cols)*(h+pad+18)
        out.paste(im.convert('RGB'),(x,y+18));d.text((x,y+3),f'{label} p.{i+1}',fill=(255,255,255))
    out.save(dest,optimize=True);return dest
def main():
    if QA.exists():shutil.rmtree(QA)
    QA.mkdir(parents=True);m=read(SHELF/'_Maintenance/manifest.json');index=[]
    docs=[('START HERE','00 - START HERE.pdf')]+[(r['title'] if r['kind'] in ('guide',) else Path(r['file']).stem,r['file']) for r in m['files'] if r['kind'] in ('guide','compact','long','cards','property','diagram')]
    for label,rel in docs:
        pdf=SHELF/rel;n=len(fitz.open(pdf));per=COLS*ROWS;slug=re.sub(r'[^A-Za-z0-9]+','-',Path(rel).stem).strip('-')
        for s in range(0,n,per):
            pages=list(range(s,min(n,s+per)));dest=QA/f'{slug}-{s+1:03}-{pages[-1]+1:03}.png'
            sheet(label,pdf,pages,dest);index.append(dict(sheet=dest.name,file=rel,pages=[p+1 for p in pages],mode='colour'))
    # Grayscale where colour carries meaning.
    gray=[('STUDY GUIDE - SG-010.pdf',[0,1,2,3,4,5,6,7]),('STUDY GUIDE - SG-010.pdf',[24,25,26,27,28,29,30,31]),('STUDY GUIDE - SG-010-L1.pdf',[1,2,3,4,5,6,7,8]),
          ('Field Cards/QUICK CHARTS - 64 CARDS - 5x7.pdf',[0,5,7,17,22,24,26,32]),('Field Cards/QUICK CHARTS - 64 CARDS - 5x7.pdf',[43,44,45,46,47,49,52,53]),('Field Cards/QUICK CHARTS - 64 CARDS - 5x7.pdf',[55,56,59,62,63,48,33,41]),
          ('Compact Appendices/APP-H-v1.2-C1.pdf',[0,1,2,3]),('Compact Appendices/APP-F-v1.3-C1.pdf',[0,1,2,3]),('00 - START HERE.pdf',[0,1,2]),('Property Review/505 WALKER - COMBINED PROPERTY REVIEW.pdf',[4,5,14,15])]
    for k,(rel,pages) in enumerate(gray):
        dest=QA/f'gray-{k+1:02}-{re.sub(r"[^A-Za-z0-9]+","-",Path(rel).stem).strip("-")}.png';sheet(Path(rel).stem,SHELF/rel,pages,dest,gray=True,rows=(len(pages)+COLS-1)//COLS);index.append(dict(sheet=dest.name,file=rel,pages=[p+1 for p in pages],mode='grayscale'))
    # 5 x 7 legibility: changed cards at 100 % (72 dpi = actual size).
    for i in [0,5,7,17,22,24,26,32,43,44,45,46,47,48,49,52,53,55,56,59,62,63]:
        dest=QA/f'card-100pct-QC-{i+1:03}.png';render(SHELF/'Field Cards/QUICK CHARTS - 64 CARDS - 5x7.pdf',i,110).save(dest);index.append(dict(sheet=dest.name,file='Field Cards/QUICK CHARTS - 64 CARDS - 5x7.pdf',pages=[i+1],mode='card 110 dpi'))
    save(QA/'index.json',index);print(json.dumps(dict(sheets=len(index),folder=str(QA))))
if __name__=='__main__':main()
