"""SG-010 compact appendices: carry the SG-009 compact companions forward to the current long-cut versions.

Counts, ID ranges and recorded results are read from the current long appendices. Each compact
appendix must still print on its planned pages (asserted by the renderer).
"""
from prepare import *
import re

def carry(aid,src):
    return read(OUT/f'Appendices/Compact/{aid}-v{src}-C1.json')

def text_replace(obj,old,new):
    if isinstance(obj,str):return obj.replace(old,new)
    if isinstance(obj,list):return [text_replace(x,old,new) for x in obj]
    if isinstance(obj,tuple):return tuple(text_replace(x,old,new) for x in obj)
    if isinstance(obj,dict):return {k:text_replace(v,old,new) for k,v in obj.items()}
    return obj

def page_named(book,prefix):return next(p for p in book['pages'] if p['title'].startswith(prefix))

def books(L1,long):
    sources=L1['sources'];last=sources[-1]['id']
    src={'APP-A':'1.7','APP-B':'1.6','APP-C':'1.8','APP-D':'1.2','APP-E':'1.3','APP-F':'1.2','APP-G':'1.2','APP-H':'1.1'}
    out={}
    for aid,old in src.items():
        bk=text_replace(carry(aid,old),'SG-009','SG-010');v=long[aid]['version']
        bk.update(version=v+'-C1',based_on_version=v,edition='SG-010',long_cut='../'+aid+'-v'+v+'.html',presentation_revision=REV)
        for k in ['page_count','page_index']:bk.pop(k,None)
        out[aid]=bk
    a=out['APP-A'];p=page_named(a,'Choose tools')
    p['items']=[list(x) for x in p['items']]
    p['note']='T025 wire samples belong to training, away from energized equipment. T027 sink stoppers / microwave-safe vessel support a supervised primary-function check only. Detailed checks: APP-A long cut.'
    out['APP-B']['pages'][0]['note']=f"The complete {len(long['APP-B']['items'])}-entry register, the NHIE scope-coverage check with its open gaps, and item-specific limits remain in APP-B long cut."
    c=out['APP-C'];ids=[x['id'] for x in long['APP-C']['items']]
    page_named(c,'Turn an observation')['note']=f'Full report-mention entries {ids[0]}-{ids[-1]}, retained in append order: APP-C long cut.'
    grp=page_named(c,'Keep different');grp['items']=[list(x) for x in grp['items']]
    for it in grp['items']:
        if it[0].startswith('Heating / cooling / interior'):it[1]=it[1].rstrip()+' Keep glazing marks, escape release, stair geometry and fireplace identification as separate observations.'
    d=out['APP-D'];notes=page_named(d,'Notes used throughout')
    notes['items']=[[h,re.sub(r'S01-S\d\d','S01-'+last,t)] for h,t in notes['items']]
    later=[n for n in long['APP-D']['notes'] if n[0]>'N09']
    notes['note']='N10-N'+later[-1][0][1:]+' (final-course reviews: '+'; '.join(n[1] for n in later)+') are in APP-D long cut. '+notes['note']
    e=out['APP-E'];pg=e['pages'][0]
    pg['intro']=f'The edition covers {len(sources)} source recordings through {last}. S38 adds hydronic, steam, electric heat and cooling lessons; S39 is a repaired recording of interior lessons that ends at fireplace screen 13/15.'
    pg['note']='S32 remains a 61-second reference bookmark (CC-S32-01). S37 is a practice-assessment result screen. S39 was repaired from an interrupted file; its recovery receipt and damaged parent remain in the recording archive.'
    refs=[x['id'] for x in long['APP-H']['references']]
    pg['items']=[[h,re.sub(r'S01-S\d\d','S01-'+last,re.sub(r'H01–H\d\d','H01–'+refs[-1],t))] for h,t in pg['items']]
    g=out['APP-G'];pg=g['pages'][0];pg['title']=pg['title'].replace('/ S31 review','/ SG-010 review')
    res=long['APP-G']['recorded_results']
    pick=[r for r in res if r['source'] in ('S37','S39')]
    pg['note']='Recorded results since S31 include '+'; '.join(f"{r['source']} {r['unit'].replace('Initial practice assessment - recorded result','initial practice assessment')} {r['score']}% ({r['correct']}/{r['total']})" for r in pick)+'. A practice result is not the course certificate or a licensing result. Full attempts and corrections remain in the long cut.'
    return out

def render(b,L1):
    from design_language import compact_pages,compact_html
    long={a['id']:read(OUT/a['path'].replace('.html','.json')) for a in L1['appendices']}
    dest=OUT/'Appendices/Compact';manifest=[]
    for aid,data in books(L1,long).items():
        stem=aid+'-v'+data['version'];flow=compact_pages(data,b);body=compact_html(data,b)
        # The shared template labels every compact page 'experimental R1'; SG-010 names its issue instead.
        flow=[b.para(f.getPlainText().replace('| experimental R1','| SG-010'),b.SMALL) if isinstance(f,b.Paragraph) and f.getPlainText().endswith('| experimental R1') else f for f in flow]
        doc=b.Doc(dest/(stem+'.pdf'),aid+' compact appendix - SG-010');doc.edition_label='SG-010 · COMPACT APPENDIX';doc.build(flow)
        actual=len(b.PdfReader(dest/(stem+'.pdf')).pages)
        assert actual==len(data['pages']),(aid,actual,len(data['pages']),doc.positions)
        data['page_count']=actual;data['page_index']=doc.positions
        save(dest/(stem+'.json'),data);(dest/(stem+'.html')).write_text(b.doc_html(aid+' · '+data['title']+' · compact',body),encoding='utf-8')
        manifest.append(dict(id=aid,version=data['version'],based_on_version=data['based_on_version'],title=data['title'],pages=actual,path='Appendices/Compact/'+stem+'.html',pdf='Appendices/Compact/'+stem+'.pdf'))
    save(OUT/'compact-appendices.json',manifest)
    print('compact appendices',[(m['id'],m['pages']) for m in manifest],'total',sum(m['pages'] for m in manifest))
