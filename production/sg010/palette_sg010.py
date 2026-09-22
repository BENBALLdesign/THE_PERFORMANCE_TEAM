"""SG-010 P1 area palette: the eight house-area hues of the SG-009 C1 language, re-tuned in lightness so that every
band separates in grayscale (Ben ruling 2026-09-22: "retune tones").

Hue and saturation are kept from the C1 colours; only lightness moves, to a fixed luma ladder (Rec. 601 luma, 0-255)
with a uniform step. Area 5 (Systems, navy) stays the darkest ink; area 8 (Attic / roof, olive) becomes the lightest
band. Bands lighter than INK_SWITCH take navy labels instead of white. Card header text keeps the original C1 ink
colours (field_cards_64.AREA_COLORS): identity by hue, separation by band tone.
"""
import colorsys
from reportlab.lib.colors import HexColor
C1={0:('#424956','Throughout'),1:('#43624E','Site'),2:('#8C523A','Exterior'),3:('#655673','Garage'),4:('#245B70','Lowest'),5:('#1A1A5E','Systems'),6:('#775238','Rooms'),7:('#216865','Wet rooms'),8:('#635B26','Attic / roof')}
TARGET={5:30,4:44,7:58,0:72,3:86,1:100,6:114,2:128,8:142}   # luma ladder, step 14
INK_SWITCH=118                                              # band luma at or above this: navy label, not white
def luma(hexcolour):
    r,g,b=HexColor(hexcolour).rgb();return 255*(.299*r+.587*g+.114*b)
def _retune(hexcolour,target):
    r,g,b=HexColor(hexcolour).rgb();h,l,s=colorsys.rgb_to_hls(r,g,b)
    lo,hi=0.0,1.0
    for _ in range(40):
        mid=(lo+hi)/2;rr,gg,bb=colorsys.hls_to_rgb(h,mid,s)
        if 255*(.299*rr+.587*gg+.114*bb)<target:lo=mid
        else:hi=mid
    rr,gg,bb=colorsys.hls_to_rgb(h,(lo+hi)/2,s)
    return '#%02X%02X%02X'%(round(rr*255),round(gg*255),round(bb*255))
AREA={a:(_retune(C1[a][0],TARGET[a]),C1[a][1]) for a in C1}
LUMA={a:round(luma(AREA[a][0]),1) for a in AREA}
_sorted=sorted(LUMA.values());MIN_STEP=min(b-a for a,b in zip(_sorted,_sorted[1:]))
assert MIN_STEP>=12,LUMA
def label_ink(a):
    """Label colour on a band of area a: white on dark bands, navy on light ones."""
    return 'white' if LUMA[a]<INK_SWITCH else '#1A1A5E'
def palette_record():
    return {str(a):dict(hex=v[0],label=v[1],luma=LUMA[a],c1_hex=C1[a][0],label_ink=label_ink(a),meaning='House area, never urgency, pass/fail or construction era') for a,v in AREA.items()}
if __name__=='__main__':
    for a in sorted(AREA,key=lambda k:LUMA[k]):print(a,AREA[a][1].ljust(12),C1[a][0],'->',AREA[a][0],'luma',round(luma(C1[a][0])),'->',LUMA[a],'label',label_ink(a))
    print('min grayscale step',MIN_STEP)
