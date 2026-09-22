"""SG-010 render orchestrator. Renders staged data in the Seed Bank output; never publishes.

Reuses the established builder renderers (build, design_language, edition, short, walking) with
SG-010 globals set here. Counts come from the data, not from earlier editions.
Stages: appendices -> terms (APP-D page locator) -> l1 -> compact -> walking.
Usage: python -X utf8 -B render_sg010.py [stage ...]
"""
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import prepare
from prepare import *
sys.path.insert(1,str(BUILDER));sys.path.insert(2,str(REPO))
import build as b,design_language as dl,edition,glossary
import re,unicodedata
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus.tableofcontents import TableOfContents,SimpleIndex
dl.install(b)
b.DATE='21 September 2026'

def L1():return read(OUT/'study-guide-L1.json')
def app(aid):
    a=next(x for x in L1()['appendices'] if x['id']==aid);return read(OUT/a['path'].replace('.html','.json'))
def terms():return [(t['term'],t['expansion'],t['definition'],t['topic']) for t in app('APP-D')['terms']]
def set_terms():b.TERMS=glossary.TERMS=terms()

# Section headings keyed by the first topic of each section, in guide order.
def domains(data):
    out=[];last=None
    for p in data['pages']:
        if p['section']!=last:out.append((p['id'],p['section']));last=p['section']
    return out

def add_pages(flow,pages,data,b):
    """edition.add_pages with P1 pagination control: no empty 'Source notes:' label, short tables kept whole,
    and the source line kept with the flowable it annotates (no orphan source line at a page top)."""
    body=''
    for p in pages:
        h=b.heading(p['title'],p['id']);h.style=copy.copy(h.style);h.style.keepWithNext=False
        flow+=[b.CondPageBreak(180),b.Spacer(1,12),h];body+=f'<section id="{b.e(p["id"])}"><h2>{b.e(p["title"])}</h2>';items=[]
        for block in p['blocks']:
            if block['kind']=='text':items.append(b.para(block['text']));body+='<p>'+b.e(block['text'])+'</p>'
            elif block['kind']=='table':
                t=b.table(block);th=t.wrap(524,704)[1];items+=[b.KeepTogether([t]) if th<170 else t,b.Spacer(1,8)];body+=b.html_table(block)
            elif block['kind']=='figures':
                items.append(b.figure_flow(block['ids'],data['figures'],min(block.get('height',160),140)))
                for fid in block['ids']:
                    f=data['figures'][fid];body+=f'<figure><img loading="lazy" src="../{b.e(f["asset"])}" alt="{b.e(f.get("caption",""))}"><figcaption>{b.e(f.get("caption",""))}</figcaption></figure>'
        if p.get('refs'):
            refs='Source notes: '+' | '.join(b.reference_text(r) for r in p['refs']);ref=b.para(refs,b.SMALL);body+='<p class="refs">'+b.e(refs)+'</p>'
            i=len(items)-1
            while i>0 and isinstance(items[i],b.Spacer):i-=1
            if items and isinstance(items[i],(b.KeepTogether,b.Paragraph)):items[i]=b.KeepTogether([items[i],ref])
            else:items.append(ref)
        body+='</section>';flow+=items
    return body

def long_appendix(r,d):
    aid=r['id'];v=r['version']
    flow=[b.heading(aid+' v'+v+' / '+r['title'],aid),dl.appendix_map(aid),b.Spacer(1,12)]
    body='<p>SG-010 cumulative edition; stable entry IDs and historical evidence retained.</p>'
    def block(title,headers,rows,widths=None):
        nonlocal body
        table=b.table(dict(headers=headers,rows=rows,widths=widths));th=table.wrap(524,704)[1]
        head=b.para(title,ParagraphStyle('RegisterHeading',parent=b.H2,keepWithNext=False))
        need=head.wrap(524,704)[1]+head.getSpaceAfter()+sum(table._rowHeights[:2])+4
        # P1: a short table travels whole with its heading (no orphan rows); a long table still splits with a repeated header.
        flow.extend([b.CondPageBreak(min(680,need))]+([b.KeepTogether([head,table])] if th<170 else [head,table])+[b.Spacer(1,10)])
        body+='<h2>'+b.e(title)+'</h2>'+b.html_table(dict(headers=headers,rows=rows))
    if aid in ['APP-A','APP-B','APP-C']:
        flow.append(b.para('Select for the actual service and evidence. Entry IDs persist. This register does not establish ownership, training, completion or a property finding.',b.SMALL))
        rows=[]
        for x in r['items']:
            if aid=='APP-C':rows.append([x['id']+' / '+x['mention'],x['note'],x.get('source','')])
            else:rows.append([x['id']+' / '+x['name'],x.get('purpose','')+'\nLimit: '+x.get('limit','')+'\nCheck: '+x.get('pre_use_check',''),x.get('basis','')])
        block('Preserved register + SG-010 review',['ID / item','Use / qualification','Basis'],rows,[115,275,134])
        if aid=='APP-B' and r.get('scope_coverage'):
            flow.append(b.para('Coverage check against the NHIE content outline task families. Exam weighting is not field risk. A listed gap means no guide topic covers that knowledge item.',b.SMALL))
            titles={p['id']:p['title'] for p in d['pages']}
            block('Scope coverage / NHIE task families',['Family','Guide topics','Open gaps'],[[f['id']+' / '+f['task_family'],'; '.join(titles[t] for t in f['topic_ids']),'\n'.join(f.get('gaps',[])) or 'None found'] for f in r['scope_coverage']],[118,256,130])
    elif aid=='APP-D':
        block('Terms and distinctions',['Term','Definition / source pointer'],[[t['term'],t['expansion']+'. '+t['definition']+'\n'+t['source_pointer']] for t in r['terms']],[120,384])
        block('Numbered notes',['ID / meaning','Qualification'],[[n+' / '+label,text] for n,label,text in r['notes']],[140,364])
        from supplements import NUMBERS
        block('S15-S29 numerical reference chart (retained)',['Value / application','Basis / qualification'],[[a+' / '+c,basis+' / '+source+' / '+note] for a,c,basis,source,note in NUMBERS])
        body+=add_pages(flow,r['pages'],d,b)
    elif aid=='APP-E':
        flow.append(b.para(r.get('coverage_note',''),b.SMALL))
        block('Original recordings / full hashes in source data',['ID / duration','Recording / status','SHA-256 prefix'],[[s['id']+' / '+b.ts(s.get('duration_seconds',0) or 0),s.get('name',Path(s.get('source_path','')).name)+('\n'+s['status'] if s.get('status') else ''),s.get('source_sha256',s.get('sha256',''))[:16]] for s in r['sources']],[83,300,121])
        for x in r['external_references']:
            flow.append(b.KeepTogether([b.para(x['id']+' / '+x['title'],b.H2),b.para(x['note']),b.Paragraph('<link href="'+b.e(x['url'])+'">'+b.e(x['url'])+'</link>',b.SMALL)]))
            body+='<h3 id="'+x['id']+'">'+b.e(x['title'])+'</h3><p>'+b.e(x['note'])+' <a href="'+b.e(x['url'])+'">Primary source</a></p>'
    elif aid=='APP-F':
        tools={x['id']:x for x in app('APP-A')['items']};refs={x['id']:x for x in app('APP-B')['items']}
        block('Common kit / all seven eras',['Pack / ID','Use'],[['[  ] '+id,tools[id]['name']+' / '+tools[id]['purpose']] for id in r['common_kit']])
        block('System and scope modules',['Module / tools','Selection condition'],[[m+' / '+c,e] for m,c,e in r['modules']])
        flow.append(b.para('Select by original construction year, then add for later alterations and installed equipment. These are packing groups, not code eras. Ownership and competence remain unrecorded.'))
        for era in r['eras']:
            flow.extend([b.CondPageBreak(250),b.heading(era['id']+' / '+era['years'],era['id']),b.para(era['focus'])])
            block('Beyond the common kit',['Field tools','Records'],[['\n'.join('[  ] '+x+' '+tools[x]['name'] for x in era['tool_ids']),'\n'.join('[  ] '+x+' '+refs[x]['name'] for x in era['reference_ids'])]],[252,252])
            flow.append(b.para(era['note']))
        flow.append(b.para('Property / year / source: __________________\nAlterations / systems: __________________\nPacked / unavailable / referral: __________________'))
    elif aid=='APP-H':
        for title,headers,rows in r['sections']:block(title,headers,rows)
        block('References',['ID / source','Use / checked'],[[x['id']+' / '+x['title'],x.get('note','')+(' Reviewed '+x['reviewed_on']+'.' if x.get('reviewed_on') else '')+'\n'+x.get('url','')] for x in r['references']],[190,314])
        if r.get('unresolved'):
            flow.append(b.para('Unresolved: '+'; '.join(u if isinstance(u,str) else ' / '.join(str(v) for v in (u.values() if isinstance(u,dict) else u)) for u in r['unresolved']),b.SMALL))
    else:
        block('Recorded attempts through SG-010',['Source / time','Unit','Result'],[[x['source']+' / '+x['timestamp'],x['unit'],str(x['score'])+'% / '+str(x['correct'])+'/'+str(x['total'])] for x in r['recorded_results']],[118,310,76])
        flow.append(b.para('Separate attempts remain separate. Match questions by wording; a course answer and a current field requirement can differ. Screens are evidence of the recorded result, not professional certification.',b.SMALL))
        body+=add_pages(flow,r['pages'],d,b)
    dest=OUT/f'Appendices/{aid}-v{v}';pdf=Path(str(dest)+'.pdf')
    doc=b.Doc(pdf,aid+' / '+r['title']);doc.build(flow)
    r['page_index']=doc.positions;save(Path(str(dest)+'.json'),r)
    Path(str(dest)+'.html').write_text(b.doc_html(aid+' / '+r['title'],body),encoding='utf-8')
    return dict(id=aid,version=v,title=r['title'],path=f'Appendices/{aid}-v{v}.html',pdf=f'Appendices/{aid}-v{v}.pdf',pages=len(b.PdfReader(pdf).pages))

def stage_appendices():
    d=L1();set_terms();done=[]
    for a in d['appendices']:
        done.append(long_appendix(read(OUT/a['path'].replace('.html','.json')),d));print(done[-1]['id'],done[-1]['pages'],'pages')
    d['appendices']=done;save(OUT/'study-guide-L1.json',d)

def norm(s):return re.sub(r'[^a-z0-9]+',' ',unicodedata.normalize('NFKD',s).casefold()).strip()
def stage_terms():
    import pdfplumber
    a=next(x for x in L1()['appendices'] if x['id']=='APP-D');found={}
    ts=app('APP-D')['terms']
    with pdfplumber.open(OUT/a['pdf']) as pdf:
        for pn,p in enumerate(pdf.pages,1):
            text=norm(p.crop((40,40,172,750)).extract_text() or '')
            for t in ts:
                if t['term'] not in found and re.search(r'\b'+re.escape(norm(t['term']))+r'\b',text):found[t['term']]=pn
    missing=[t['term'] for t in ts if t['term'] not in found];assert not missing,missing
    nav=read(HERE/'navigation.json') if (HERE/'navigation.json').exists() else dict(schema='study-guide-navigation/1',issue=REV,derived=True)
    nav['glossary_pages']=found;nav['glossary_source']=a['pdf'];save(HERE/'navigation.json',nav)
    print('located',len(found),'terms across',len(set(found.values())),'APP-D pages')

def cover(data):
    from design_language import reference_cover
    flow=reference_cover(b)
    n=len({s['id'] for s in data['sources']})
    flow[6]=b.para(f"{n} source recordings through {data['sources'][-1]['id']} | {len(data['pages'])} component topics | {len(data['appendices'])} long-cut appendices",b.BODY)
    return flow

def render_l1(data):
    flow=cover(data)+[b.PageBreak(),b.para('Contents',b.H1)]
    toc=TableOfContents();toc.levelStyles=[ParagraphStyle('TOC',fontName='Helvetica-Bold',fontSize=9.4,leading=12.2,spaceBefore=6,leftIndent=0,rightIndent=28),ParagraphStyle('TOC-sub',fontName='Helvetica',fontSize=8.6,leading=11,spaceBefore=2,leftIndent=12,rightIndent=28)];flow+=[toc]
    import housing
    flow+=[b.PageBreak()]+housing.frontmatter(b)
    index=SimpleIndex(style=ParagraphStyle('Index',fontName='Helvetica',fontSize=9,leading=12),headers=True,dot=' . ')
    starts=dict(domains(data))
    for p in data['pages']:
        if p['id'] in starts:flow+=[b.PageBreak(),b.heading(starts[p['id']],'section_'+p['id'])]
        else:flow+=[b.CondPageBreak(150),b.Spacer(1,12)]
        names=[p['id'].replace('_',' ').capitalize()]+[alias.strip() for t in b.TERMS if t[3]==p['id'] for alias in t[0].split(' / ')]
        h=b.Paragraph(''.join('<index item="'+b.e(x)+'"/>' for x in names)+b.e(p['title']),b.H2);h.topic_id=p['id'];h.toc_level=1;flow.append(h)
        for blk in p['blocks']:
            if blk['kind']=='text':flow.append(b.para(blk['text']))
            elif blk['kind']=='table':
                if blk.get('title'):flow.append(b.para(blk['title'],b.H2))
                flow+=[b.table(blk),b.Spacer(1,8)]
            elif blk['kind']=='figures':flow+=[b.figure_flow(blk['ids'],data['figures'],blk.get('height',200)),b.Spacer(1,8)]
        if p.get('refs'):
            ref=b.para('Source notes [N01-N04]: '+' | '.join(b.reference_text(r) for r in p['refs']),b.SMALL)
            i=len(flow)-1
            while i>0 and isinstance(flow[i],b.Spacer):i-=1
            while i>0 and getattr(flow[i-1],'getKeepWithNext',lambda:False)():i-=1
            flow[i:]=[b.KeepTogether(flow[i:]+[ref])]
    flow+=[b.PageBreak(),b.heading('Subject index','subject_index'),b.para('L1 = page in this volume. D = page in the APP-D long glossary: "12 / D4" means topic page 12, definition page 4. Sources: APP-E; packing: APP-F; corrections: APP-G; local history: APP-H.',b.SMALL),index]
    second=b.copy.deepcopy(flow)
    name='STUDY GUIDE - SG-010-L1.pdf'
    doc=b.Doc(OUT/name,'Home Inspection Study Guide - SG-010-L1');doc.multiBuild(flow,maxPasses=8,canvasmaker=index.getCanvasMaker())
    subjects={}
    for p in data['pages']:
        for x in [p['id'].replace('_',' ').capitalize()]+[alias.strip() for t in b.TERMS if t[3]==p['id'] for alias in t[0].split(' / ')]:subjects.setdefault(x,set()).add(doc.positions[p['id']])
    from navigation import ALIASES
    for label,tid in ALIASES.items():subjects.setdefault(label,set()).add(doc.positions[tid])
    merged={}
    for label,pages in subjects.items():merged.setdefault(label.casefold(),[label,set()])[1].update(pages)
    subjects={v[0]:v[1] for v in merged.values()}
    defs={part.casefold():pn for label,pn in read(HERE/'navigation.json')['glossary_pages'].items() for part in label.split(' / ')}
    def locator(x):
        pn=defs.get(x.casefold());return ', '.join(map(str,sorted(subjects[x])))+(' / D'+str(pn) if pn else '')
    names=sorted(subjects,key=str.casefold);style=ParagraphStyle('IndexCell',parent=b.SMALL,fontSize=8.7,leading=10.8,spaceAfter=0);out=[]
    for start in range(0,len(names),68):
        sub=names[start:start+68];half=(len(sub)+1)//2;rows=[]
        for j in range(half):
            row=[]
            for k in [j,j+half]:row.extend([sub[k],locator(sub[k])] if k<len(sub) else ['',''])
            rows.append(row)
        t=b.Table([[b.para(x,b.HEAD) for x in ['Subject','L1 / D','Subject','L1 / D']]]+[[b.para(x,style) for x in row] for row in rows],colWidths=[196,56,196,56],repeatRows=1,hAlign='LEFT')
        t.setStyle(b.TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),('BACKGROUND',(0,0),(-1,0),b.H1.textColor),('LINEBELOW',(0,0),(-1,-1),.25,b.colors.HexColor('#DDDDDD'))]))
        if start:out+=[b.PageBreak(),b.para('Subject index (continued)',b.H1)]
        out.append(t)
    flow=second;flow[-1:]=out
    doc=b.Doc(OUT/name,'Home Inspection Study Guide - SG-010-L1');doc.multiBuild(flow,maxPasses=8,canvasmaker=index.getCanvasMaker())
    save(OUT/'page-index-L1.json',doc.positions)
    return doc

def stage_l1():
    d=L1();set_terms();b.DOMAINS=domains(d)
    for p in d['pages']:
        for blk in p['blocks']:
            if blk['kind']=='paragraph':blk['kind']='text'
    doc=render_l1(d)
    pages=len(b.PdfReader(OUT/'STUDY GUIDE - SG-010-L1.pdf').pages)
    d['page_count']=pages;save(OUT/'study-guide-L1.json',d)
    print('L1',len(d['pages']),'topics',pages,'pages')

def ranges(nums):
    nums=sorted(set(nums));out=[];start=last=nums[0]
    for n in nums[1:]+[None]:
        if n is not None and n==last+1:last=n;continue
        out.append(str(start) if start==last else str(start)+'-'+str(last));start=last=n
    return ', '.join(out)

# Finder: defined APP-D terms (must exist) plus familiar labels routed to a chart by id.
FINDER_TERMS={'AFCI','AFUE','CO','CSST','DWV','EIFS','GFCI','MWBC','T&P / TPR','Rake / eave','Grounding / bonding','Load path','Differential movement','Efflorescence','Notch / bored hole','Post-tensioned slab','Collar tie / rafter tie','WRB','U-factor / SHGC','Ledger / guard / handrail','Cross-connection / air gap','Dielectric connection','Heat exchanger','IC / IC-AT','Safety glazing','Hearth extension','Winder / walkline'}
FINDER_LABELS=[('Aluminum wiring','circuits'),('Basement','foundation_water'),('Heat pump','heatpumps'),('Light switches','devices'),('Plaster / cracks','movement'),('Sump pump','dwv'),('Water stains','movement'),('3-way / 4-way switches','devices'),('Appliances','appliances'),('Smoke / CO','life_safety'),('Insulation','insulation'),('Scope / referrals','scope'),('Boiler / steam','hydronic_electric'),('Egress window','interior_routes'),('Fireplace / gas logs','interior_routes'),('Stairs / handrails','interior_routes')]

def render_compact(d,PAGES):
    from reportlab.platypus import Table,TableStyle
    import housing
    SMALL0=b.SMALL;b.SMALL=ParagraphStyle('ReadableNotes',parent=b.SMALL,fontSize=9,leading=11.4,spaceAfter=5)
    longpos=read(OUT/'page-index-L1.json');topics={p['id']:p for p in d['pages']}
    mapped={tid:p['id'] for p in PAGES for tid in p['topics']}
    assert len(mapped)==sum(len(p['topics']) for p in PAGES),'Duplicate compact mapping'
    assert set(mapped)==set(topics),(set(topics)-set(mapped),set(mapped)-set(topics))
    first=4;index_page=first+len(PAGES);total=index_page
    shelf=read(OUT/'compact-appendices.json');shelf_pages=sum(a['pages'] for a in shelf)
    cover=[b.heading('HOME INSPECTION · SG-010','cover'),b.para('Field comparisons and colleague discussions',b.H2),b.para('For an experienced construction professional working in Baltimore City and Anne Arundel, Baltimore, Carroll, Harford and Howard counties. Start with the local stock on pp. 2-3; use the component charts to sharpen an observation, comparison or conversation.'),b.para(f'{total} pages / {(total+1)//2} sheets duplex. Print at actual size. Each topic stays on one page. SG-010-L1 holds the complete topic treatment; the eight appendices are separately printable.',b.SMALL)]
    routes=[[p['title'],str(j+first)] for j,p in enumerate(PAGES)];half=(len(routes)+1)//2
    cover+=[b.table(dict(headers=['Quick route','Page','Quick route','Page'],rows=[routes[j]+(routes[j+half] if j+half<len(routes) else ['','']) for j in range(half)],widths=[220,42,220,42])),b.para(f'Subject finder and appendix routes: p. {index_page}. COURSE / EXAM / NOTE / LOCAL distinguish source basis. The charts are reviewed syntheses; local and product requirements retain their qualifications. Definitions and numbered notes are in APP-D; source register in APP-E.',b.SMALL)]
    flow=cover+[b.PageBreak()]+housing.frontmatter(b)
    body=f'<nav><a href="STUDY GUIDE - SG-010.pdf">Print SG-010 ({total} pages)</a><a href="STUDY GUIDE - SG-010-L1.html">Open the long cut</a><a href="index.html">Edition library</a><a href="regional-field-focus.html">Local housing chart</a></nav><p>Compact reference for an experienced construction professional. Every topic below has one printed page. Full explanations, source images and detailed qualifications remain in SG-010-L1; the appendices print independently.</p>'
    body+='<input id="search" placeholder="Find a component, term or distinction"><details><summary>Contents</summary><ol>'+''.join('<li><a href="#'+p['id']+'">'+b.e(p['title'])+'</a></li>' for p in PAGES)+'</ol></details>'
    CELL0=b.CELL;b.CELL=ParagraphStyle('CompactPrintCell',parent=CELL0,fontSize=11,leading=14.2)
    from design_language import topic_chart,topic_html
    for j,p in enumerate(PAGES):
        refs=[r for tid in p['topics'] for r in topics[tid].get('refs',[])];sids=sorted(set(r['source'] for r in refs if r.get('source') and re.fullmatch(r'S\d\d',r['source'])))
        p.update(printed_page=j+first,long_pages=ranges([longpos[t] for t in p['topics']]),source_sessions=sids)
        flow+=[b.PageBreak(),b.heading(p['title'],p['id']),b.para(p['route'],b.H2)]+topic_chart(p)+[b.Spacer(1,9)]
        if p.get('figure'):
            f=d['figures'][p['figure']];im=b.PILImage.open(OUT/f['asset']);w,h=im.size;scale=min(330/w,(125 if w/h<1.2 else 95)/h)  # P1: a near-square figure gets more height than a wide one
            flow+=[b.Image(str(OUT/f['asset']),w*scale,h*scale),b.para(f['caption']+' Source: '+f.get('source','')+' '+f.get('timestamp',''),b.SMALL)]
        flow+=[b.para('Discuss: '+p['discuss'],b.BODY),b.para(p['note'],b.SMALL),b.para('L1 pp. '+p['long_pages']+'; sources '+', '.join(sids)+'. Full records: APP-E long cut.',b.SMALL)]
        body+='<section class="topic" id="'+p['id']+'">'+''.join('<span id="'+tid+'"></span>' for tid in p['topics'] if tid!=p['id'])+'<h2>'+b.e(p['title'])+'</h2><p>'+b.e(p['route'])+'</p>'+topic_html(p,b)
        if p.get('figure'):
            f=d['figures'][p['figure']];body+='<figure><img src="'+f['asset']+'" alt="'+b.e(f['caption'])+'"><figcaption>'+b.e(f['caption'])+'</figcaption></figure>'
        body+='<p><strong>Discuss:</strong> '+b.e(p['discuss'])+'</p><p class="refs">'+b.e(p['note'])+'</p><details><summary>Long-cut topics and sources (pp. '+p['long_pages']+')</summary><ul>'+''.join('<li><a href="STUDY GUIDE - SG-010-L1.html#'+tid+'">'+b.e(topics[tid]['title'])+' - L1 p. '+str(longpos[tid])+'</a></li>' for tid in p['topics'])+'</ul></details></section>'
    b.CELL=CELL0
    page_of={p['id']:p['printed_page'] for p in PAGES}
    chosen=[(t,page_of[mapped[tid]]) for t,exp,dfn,tid in b.TERMS if t in FINDER_TERMS and tid in mapped]
    assert len(chosen)==len(FINDER_TERMS),FINDER_TERMS-{c[0] for c in chosen}
    chosen+=[(label,page_of[cid]) for label,cid in FINDER_LABELS];chosen.sort(key=lambda x:x[0].casefold())
    flow+=[b.PageBreak(),b.heading('Quick finder and appendix shelf','subject_index'),b.para('Pages below refer to SG-010. More subjects: the subject index at the back of L1. Meanings: APP-D long cut; selected terms and numbered notes: APP-D compact. Switching illustration: Source Diagrams, sheet 1.',b.SMALL)]
    small=ParagraphStyle('Finder',parent=b.SMALL,fontSize=10.5,leading=13.5,spaceAfter=0);cols=[];n=(len(chosen)+1)//2
    for subset in [chosen[:n],chosen[n:]]:
        t=Table([[b.para(a,small),b.para(str(pg),small)] for a,pg in subset],colWidths=[210,33]);t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),3),('TOPPADDING',(0,0),(-1,-1),2),('LINEBELOW',(0,0),(-1,-1),.2,b.colors.HexColor('#DDDDDD'))]));cols.append(t)
    outer=Table([cols],colWidths=[252,252]);outer.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),8)]));flow+=[outer,b.Spacer(1,12)]
    by={a['id']:a for a in shelf};label=dict(A='Field tools',B='Reference and record tools',C='Reporting prompts',D='Selected terms and notes',E='Source routes',F='Seven-era packing cards',G='Selected corrections',H='Local timeline')
    rows=[[x+' / '+y,label[x]+' / '+label[y],f"{by['APP-'+x]['pages']} / {by['APP-'+y]['pages']} pages"] for x,y in ['AB','CD','EF','GH']]
    flow+=[b.table(dict(headers=['Compact appendix','Contents','Length'],rows=rows,widths=[85,320,119])),b.para(f'Eight compact appendices: {shelf_pages} pages total, each an optional print job. L1 holds the complete registers, numerical references and source history. Print only selected pages useful to the visit or conversation.',b.SMALL)]
    body+='<section><h2>Reference and exam routes</h2><ul>'+''.join('<li id="'+p['id']+'"><a href="STUDY GUIDE - SG-010-L1.html#'+p['id']+'">'+b.e(p['title'])+'</a></li>' for key in ['reference_pages','exam_pages'] for p in d[key])+'</ul></section>'
    body+='''<script>document.getElementById('search').addEventListener('input',function(){let q=this.value.toLowerCase();document.querySelectorAll('.topic').forEach(s=>s.hidden=!s.textContent.toLowerCase().includes(q));});</script>'''
    doc=b.Doc(OUT/'STUDY GUIDE - SG-010.pdf','Home Inspection Study Guide - SG-010');doc.edition_label='SG-010';doc.build(flow)
    count=len(b.PdfReader(OUT/'STUDY GUIDE - SG-010.pdf').pages);b.SMALL=SMALL0
    assert count==total,(count,total)
    assert all(doc.positions[p['id']]==p['printed_page'] for p in PAGES),'a chart overflowed its page'
    assert doc.positions['subject_index']==index_page
    save(OUT/'page-index.json',doc.positions)
    record=dict(schema=2,edition='SG-010',date=b.DATE,title='Home Inspection Study Guide - Field comparisons and colleague discussions',pages=PAGES,sources=d['sources'],appendices=shelf,figures={k:v for k,v in d['figures'].items() if k in {p.get('figure') for p in PAGES}},companion='SG-010-L1',long_cut_topic_map=mapped,source_coverage=d['source_coverage'],presentation_revision=REV,print_policy=dict(pages=count,duplex_sheets=(count+1)//2,reference_appendices_separate=True,target='One chart per page; compact working reference',audience='Experienced construction professional; field review and colleague discussion',page_test='Every page supports an observation, distinction, decision, lookup or discussion.',compact_appendix_pages=shelf_pages,appendix_long_cut_separate=True,main_table_type_points=11,notes_type_points=9))
    save(OUT/'study-guide.json',record)
    (OUT/'STUDY GUIDE.html').write_text(b.doc_html('SG-010 - Field comparisons and colleague discussions',body),encoding='utf-8')
    print('compact',len(PAGES),'charts',count,'pages; finder',len(chosen))

def stage_compact():
    set_terms();render_compact(L1(),read(OUT/'compact-editorial.json')['pages'])

# W1 path tags per step: W = WATER, L = LOAD, C = COMBUSTION (energy route incl. electrical).
PATHS={'before':['','WLC','WLC','',''],'arrive':['','','','WC','LC'],'outside':['W','W','WL','L','WC','LC'],'lowest':['','W','L','L','W',''],
 'systems':['C','W','WC','C','C','WC'],'rooms':['WL','L','C','W','WC','C'],'upper':['','LW','W','W','WLC',''],'close':['','','','','']}
PATH_COLOR=dict(W='#2F6FA3',L='#8A6A2E',C='#B5542B')
NAMING='Paths: W = WATER, L = LOAD, C = COMBUSTION. COMBUSTION names the energy route: fuel, electricity, heat delivery and venting. It includes the full electrical inspection; the name does not mean every system burns fuel.'

def stage_walking():
    import walking
    from reportlab.platypus import Table,TableStyle
    from reportlab.graphics.shapes import Drawing,Rect,String
    from reportlab.lib.colors import HexColor
    PAGES=read(OUT/'walking-editorial.json')['pages'];idx=read(OUT/'page-index.json');short=read(OUT/'study-guide.json');byid={p['id']:p for p in short['pages']}
    for p in PAGES:
        assert set(p['refs'])<=set(byid),(p['id'],set(p['refs'])-set(byid));assert len(PATHS[p['id']])==len(p['steps']),p['id']
    body=ParagraphStyle('WalkingBody',parent=b.BODY,fontSize=11,leading=13.6,spaceAfter=4)
    head=ParagraphStyle('WalkingStep',parent=body,fontName='Helvetica-Bold',spaceAfter=5)
    note=ParagraphStyle('WalkingNote',parent=b.SMALL,fontSize=9,leading=11.5)
    def marker(tags):
        d=Drawing(16,40);d.add(Rect(3,26,9,9,fillColor=None,strokeColor=dl.N,strokeWidth=.7))
        for k,t in enumerate(tags):d.add(String(7.5,15-k*8.5,t,fontName='Helvetica-Bold',fontSize=7.5,fillColor=HexColor(PATH_COLOR[t]),textAnchor='middle'))
        return d
    flow=[];html='<nav><a href="STUDY GUIDE - SG-010-W1.pdf">Print W1 (8 pages / 4 sheets duplex)</a><a href="index.html">Edition library</a></nav><p>Route companion. T = arrival; D = departure. Site work follows the property, with no imposed inspection duration.</p><p>'+b.e(NAMING)+'</p>'
    for k,p in enumerate(PAGES):
        if k:flow.append(b.PageBreak())
        flow+=[walking.strip(k),b.heading(p['title'],p['id']),b.para(p['where']+' / '+p['route'],note)]
        if k==0:flow.append(b.para(NAMING,note))
        rows=[[marker(PATHS[p['id']][j]),[b.para(title,head),b.para(act,body)],b.para(capture,body)] for j,(title,act,capture) in enumerate(p['steps'])]
        t=Table([[b.para('',b.HEAD),b.para('DO / OBSERVE',b.HEAD),b.para('CAPTURE / RESOLVE',b.HEAD)]]+rows,colWidths=[22,298,184])
        t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),dl.N),('BACKGROUND',(-1,1),(-1,-1),dl.TINT),('LINEBELOW',(0,1),(-1,-1),.6,dl.GRAY),('LEFTPADDING',(0,0),(-1,-1),7),('LEFTPADDING',(0,1),(0,-1),3),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
        flow+=[t,b.Spacer(1,9),b.para(p['gate'],head),b.para(p['note'],note)]
        refs='; '.join(byid[r]['title'].split('  ',1)[-1]+' p. '+str(idx[r]) for r in p['refs'])
        flow.append(b.para('SG-010: '+refs+'. MD: COMAR 09.36.07 '+p['md']+'.',note))
        html+='<section id="'+p['id']+'"><h2>'+str(k+1)+' / '+b.e(p['title'])+'</h2><p>'+b.e(p['route'])+'</p>'+b.html_table(dict(headers=['Path','Step','Do / observe','Capture / resolve'],rows=[[PATHS[p['id']][j]]+list(st) for j,st in enumerate(p['steps'])]))+'<p><strong>'+b.e(p['gate'])+'</strong></p><p>'+b.e(p['note'])+'</p><p>'+''.join('<a href="STUDY GUIDE.html#'+r+'">'+b.e(byid[r]['title'])+'</a> / ' for r in p['refs'])+'<a href="'+walking.MD+'">MD '+p['md']+'</a></p></section>'
        if k==len(PAGES)-1:flow.append(b.para('MD source: Maryland Department of Labor, Minimum Standards of Practice; chapter revised 22 Dec 2025, checked 20 Sep 2026. Digital W1 provides the live link.',note))
    doc=b.Doc(OUT/'STUDY GUIDE - SG-010-W1.pdf','SG-010-W1 - Walking Cut');doc.build(flow)
    n=len(b.PdfReader(OUT/'STUDY GUIDE - SG-010-W1.pdf').pages);assert n==len(PAGES),(n,doc.positions)
    assert all(doc.positions[p['id']]==i+1 for i,p in enumerate(PAGES)),doc.positions
    save(OUT/'walking-cut.json',dict(edition='SG-010-W1',status='Route aid',presentation_revision=REV,pages=PAGES,paths=PATHS,path_naming=NAMING,page_index=doc.positions,print_pages=n,duplex_sheets=(n+1)//2,source_coverage=L1()['source_coverage'],timing='T is arrival; D is actual departure. Preparation and closeout are suggested windows; inspection duration is unrestricted.',sources=[dict(id='MD',url=walking.MD,checked='2026-09-20',revision_effective='2025-12-22'),dict(id='SG-010',path='study-guide.json'),dict(id='SG-010-L1',path='study-guide-L1.json')],limits='Not an exhaustive checklist. Apply current standards and agreed scope.'))
    (OUT/'STUDY GUIDE - SG-010-W1.html').write_text(b.doc_html('SG-010-W1 / Walking Cut',html),encoding='utf-8')
    print('W1',n,'pages')

def stage_compact_appendices():
    import compact_sg010
    set_terms();compact_sg010.render(b,L1())

STAGES=dict(appendices=stage_appendices,terms=stage_terms,l1=stage_l1,compact_appendices=stage_compact_appendices,compact=stage_compact,walking=stage_walking)
if __name__=='__main__':
    for s in sys.argv[1:] or list(STAGES):STAGES[s]()
