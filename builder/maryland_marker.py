"""Local vector crab: Maryland relevance, never a safety or compliance verdict."""
from reportlab.lib.colors import HexColor
COLOR=HexColor('#007A9E')
MEANING='Blue crab / MD = Maryland-specific detail. It does not establish applicability or compliance.'
def crab(c,x,y,size=14):
    c.saveState();c.translate(x,y);c.scale(size/20,size/20)
    c.setFillColor(COLOR);c.setStrokeColor(COLOR);c.setLineWidth(1.3)
    c.ellipse(-5,-3,5,3,fill=1,stroke=0)
    for s in [-1,1]:
        for yy,tip in [(1,3),(0,0),(-1,-3),(-2,-5)]:
            p=c.beginPath();p.moveTo(s*4,yy);p.lineTo(s*8,tip);p.lineTo(s*10,tip-1);c.drawPath(p)
        p=c.beginPath();p.moveTo(s*4,2);p.lineTo(s*7,6);p.lineTo(s*6,8);c.drawPath(p)
        p=c.beginPath();p.moveTo(s*6,6);p.lineTo(s*3.5,8.5);p.lineTo(s*4,11);p.lineTo(s*5.7,8.6);p.lineTo(s*7.7,10.2);p.lineTo(s*8,7.6);p.close();c.drawPath(p,fill=1,stroke=0)
        c.line(s*2,2,s*2.5,4.5);c.circle(s*2.5,4.5,.7,fill=1,stroke=0)
    c.restoreState()

def drawing(x,y,size=14):
    from reportlab.graphics.shapes import Group,Ellipse,Line,Polygon,Circle
    g=Group();g.add(Ellipse(0,0,5,3,fillColor=COLOR,strokeColor=None))
    for s in [-1,1]:
        for yy,tip in [(1,3),(0,0),(-1,-3),(-2,-5)]:
            g.add(Line(s*4,yy,s*8,tip,strokeColor=COLOR,strokeWidth=1.3));g.add(Line(s*8,tip,s*10,tip-1,strokeColor=COLOR,strokeWidth=1.3))
        g.add(Line(s*4,2,s*7,6,strokeColor=COLOR,strokeWidth=1.3))
        g.add(Polygon([s*6,6,s*3.5,8.5,s*4,11,s*5.7,8.6,s*7.7,10.2,s*8,7.6],fillColor=COLOR,strokeColor=None))
        g.add(Line(s*2,2,s*2.5,4.5,strokeColor=COLOR,strokeWidth=1.3));g.add(Circle(s*2.5,4.5,.7,fillColor=COLOR,strokeColor=None))
    g.scale(size/20,size/20);g.translate(x*20/size,y*20/size)
    return g
