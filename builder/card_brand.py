"""Place the approved BEN-Ball vector artwork without redrawing its geometry."""
from pathlib import Path
import copy
import hashlib
import re
import xml.etree.ElementTree as ET
from reportlab.graphics.shapes import Group
from reportlab.graphics.svgpath import SvgPath
from reportlab.lib.colors import HexColor
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
import team_paths

LOGO = team_paths.brand('logos/BENBALL_A_CANONICAL.svg')

def _read():
    root = ET.parse(LOGO).getroot()
    assert root.attrib['viewBox'] == '0 0 289 655'
    def node(element):
        kind = element.tag.split('}')[-1]
        if kind in ('title', 'desc'):
            return None
        group = Group()
        if kind == 'path':
            style = dict(part.split(':',1) for part in element.attrib['style'].split(';') if part)
            group.add(SvgPath(element.attrib['d'], strokeColor=None,
                fillColor=HexColor(style['fill']), fillMode=0 if style.get('fill-rule')=='evenodd' else 1))
        else:
            assert kind in ('svg','g'), kind
            for child in element:
                shape=node(child)
                if shape is not None: group.add(shape)
        transform=element.attrib.get('transform','')
        for operation,args in re.findall(r'(\w+)\(([^)]+)\)',transform):
            values=[float(x) for x in re.split(r'[,\s]+',args.strip())]
            assert operation in ('translate','scale'),operation
            if operation=='translate':group.translate(values[0],values[1] if len(values)>1 else 0)
            else:group.scale(values[0],values[1] if len(values)>1 else values[0])
        return group
    return node(root)

ART=_read()
SHA256=hashlib.sha256(LOGO.read_bytes()).hexdigest()

def mark(drawing,x,y,width=22):
    height=width*655/289
    group=Group(copy.deepcopy(ART))
    group.transform=(width/289,0,0,-width/289,x,y+height)
    drawing.add(group)
    return (x,y,x+width,y+height)
