"""Field Card Concordance: deterministic source -> expression -> field use.

Derived catalog, not another authoritative glossary or a live RTS registration.
Rendering consumes compile_cards(); stale source or editorial text fails closed.
"""
from pathlib import Path
import copy,hashlib,html,json,re
from collections import defaultdict
from field_card_bindings import ALIASES,BINDINGS,NOTES,TERMS

HERE=Path(__file__).resolve().parent
import sys;sys.path.insert(0,str(HERE.parent/'tools'))
import team_paths
LIBRARY=team_paths.installation()/'Home Inspection Training/Study Guide Editions'
from prepare import OUT
SOURCE=OUT/'study-guide.json'
LONG=OUT/'study-guide-L1.json'
APP=OUT/'Appendices'
LOCK=HERE/'field-card-review-lock.json'
NAME='Field Card Concordance'

def read(p):return json.loads(p.read_text(encoding='utf-8'))
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def slug(s):return re.sub('[^a-z0-9]+','-',s.lower()).strip('-')
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def source_catalog():
    guide=read(SOURCE);long=read(LONG);gloss=read(APP/'APP-D-v1.3.json')
    facts={};by_code={};topic_nodes={};refs={}
    page_lookup={p['id']:p for p in guide['pages']}
    for alias,tid in ALIASES.items():
        p=page_lookup[tid];pi=guide['pages'].index(p)
        for i,row in enumerate(p['rows']):
            fid='SG-010:'+tid+':'+slug(row[0])
            facts[fid]=dict(id=fid,edition='SG-010',topic_id=tid,label=row[0],
                retained=row[1],qualification=row[2],source_sha256=digest(row),
                source_file=str(SOURCE),json_pointer=f'/pages/{pi}/rows/{i}',
                selector=dict(topic_id=tid,row_label=row[0]),
                link='../../STUDY GUIDE.html#'+tid,printed_page=p['printed_page'])
            by_code[alias+str(i)]=fid
    for p in long['pages']:
        tid=p['id'];node='SG-010-L1:'+tid
        topic_refs=[]
        for r in p.get('refs',[]):
            rid='reference:'+digest(r)[:18]
            refs[rid]=dict(id=rid,**r,scope='L1 topic-level reference; exact claim span not asserted')
            topic_refs.append(rid)
        topic_nodes[node]=dict(id=node,title=p['title'],topic_id=tid,
            compact_topic=guide['long_cut_topic_map'].get(tid),
            link='../../../SG-010-L1/STUDY GUIDE.html#'+tid,reference_ids=topic_refs)
    terms={}
    for i,t in enumerate(gloss['terms']):
        terms[t['term']]=dict(id='APP-D:term:'+slug(t['term']),**t,
            source_sha256=digest(t),json_pointer=f'/terms/{i}',
            source_file=str(APP/'APP-D-v1.3.json'),link='../APP-D-v1.3.html')
    notes={r[0]:dict(id='APP-D:'+r[0],label=r[1],text=r[2],source_sha256=digest(r),
            json_pointer=f'/notes/{i}',link='../APP-D-v1.3.html') for i,r in enumerate(gloss['notes'])}
    return guide,facts,by_code,topic_nodes,refs,terms,notes

def expression(path,text,fids,relation,facts):
    # A source row is indivisible: retained statement AND qualification travel.
    return dict(path=path,text=text,relationship=relation,fact_ids=fids,
        qualification_ids=[f+':qualification' for f in fids],
        exact_phrase_in_source=any(text.casefold() in (facts[f]['retained']+' '+facts[f]['qualification']).casefold() for f in fids),
        emphasis_origin='editorial' if path.endswith('/0') or path.startswith('/title') else 'none')

def timeline_relevance(c):
    # Relevance is navigation, never severity, defect probability or compliance.
    history={1,30,32,35,41,42,61}
    reference={3,12,15,16,19,21,27,28,34,36,38,39,46,53,58,59,60,63,64}
    if c['card_number'] in history:return 'history'
    if c['card_number'] in reference:return 'reference'
    return 'observe'

def compile_cards(raw,*,establish_review=False):
    guide,facts,codes,topics,refs,terms,notes=source_catalog()
    cards=copy.deepcopy(raw);used=set();used_terms=set();used_notes=set();reverse=defaultdict(set)
    signatures={};bindings=[]
    for c,spec,ns in zip(cards,BINDINGS,NOTES):
        groups=[[codes[k] for k in group.split()] for group in spec.split(';')]
        assert len(groups)==len(c['rows'])+1,(c['id'],len(groups))
        expressions=[]
        for i,row in enumerate(c['rows']):
            for j,text in enumerate(row):
                relation='derived_math' if c['kind']=='slope' else 'condensed'
                if c['kind']=='record':relation='editorial_prompt'
                expressions.append(expression(f'/rows/{i}/{j}',text,groups[i],relation,facts))
        expressions.append(expression('/note',c['note'],groups[-1],'condensed',facts))
        if c['kind']=='pipes':
            c['diagram_labels']=['SUMP','Groundwater','EJECTOR','Wastewater']
            for j,text in enumerate(c['diagram_labels']):
                expressions.append(expression(f'/diagram_labels/{j}',text,[codes['d4']],'condensed',facts))
        all_facts=sorted({x for group in groups for x in group})
        for path,text in [('/cue',c['cue']),('/write',c['write'])]+[(f'/title/{i}',v) for i,v in enumerate(c['title'])]:
            expressions.append(expression(path,text,all_facts,'editorial_prompt',facts))
        for f in all_facts:used.add(f);reverse[f].add(c['id'])
        note_ids=['N'+x for x in ns.split()]
        for n in note_ids:
            assert n in notes;used_notes.add(n);reverse[notes[n]['id']].add(c['id'])
        term_names=TERMS.get(c['card_number'],[])
        for t in term_names:
            assert t in terms;used_terms.add(t);reverse[terms[t]['id']].add(c['id'])
        tids=sorted({facts[f]['topic_id'] for f in all_facts})
        related=[n for n,t in topics.items() if t['compact_topic'] in tids]
        rids=sorted({r for n in related for r in topics[n]['reference_ids']})
        for r in rids:reverse[r].add(c['id'])
        pages=sorted({facts[f]['printed_page'] for f in all_facts})
        c['refs']=tids
        c['source']='SG-010 '+','.join(map(str,pages))+' / '+','.join(note_ids)
        c['concordance_id']=NAME
        c['concordance_anchor']='concordance.html#'+c['id']
        c['relevance']=timeline_relevance(c)
        step_ids=['identify','observe','disposition']
        if c['kind'] in ('route','evidence','bearing','pipes','heat'):step_ids.insert(2,'connect')
        if c['card_number'] in (20,21,22,23,31,33,47,50):step_ids.insert(2,'operate')
        task_ids=['inspect-area']
        if c['card_number']==1:task_ids=['prepare-visit','establish-access'];step_ids=['prepare','access','identify']
        if c['card_number'] in (8,48):task_ids=['inspect-area','close-visit'];step_ids=['disposition','review']
        if c['card_number'] in (25,57):step_ids.insert(0,'access')
        c['field_use']=dict(task_ids=task_ids,step_ids=step_ids,
            relationship='reference for human field work; does not execute or complete a Step',
            area_number=c['area_number'])
        binding=dict(card_id=c['id'],expressions=expressions,footnote_ids=[notes[n]['id'] for n in note_ids],
            term_ids=[terms[t]['id'] for t in term_names],related_l1_topic_ids=related,
            related_reference_ids=rids,reference_scope='related L1 topics, not fact-level recording proof',
            relevance=c['relevance'],relevance_basis='editorial navigation; does not alter technical meaning',
            field_use=c['field_use'])
        if c['kind']=='slope':
            binding['calculation']=dict(formula='100 * rise_inches / run_inches',run_inches=12,
                rise_inches=[.125,.25,.5,1],display_percent=[1.0,2.1,4.2,8.3],round_decimals=1,
                acceptance_threshold=False)
        bindings.append(binding)
        signatures[c['id']]=digest(dict(expressions=expressions,footnotes=binding['footnote_ids'],terms=binding['term_ids'],relevance=c['relevance']))
    signature=dict(facts={f:facts[f]['source_sha256'] for f in sorted(used)},cards=signatures,
        terms={t:terms[t]['source_sha256'] for t in sorted(used_terms)},
        footnotes={n:notes[n]['source_sha256'] for n in sorted(used_notes)},
        related_references=digest(refs),l1_routes=digest(topics))
    if establish_review:
        if LOCK.exists():raise ValueError('Review lock already exists. Review the delta explicitly before replacing it.')
        save(LOCK,dict(design=NAME,review_date='2026-09-20',basis='editorial mappings checked against existing edition rows; not a new technical/code audit',signature=signature))
    if not LOCK.exists():raise ValueError('No reviewed source lock. Rendering is withheld.')
    if read(LOCK)['signature']!=signature:raise ValueError('Concordance is stale: a fact, qualification, term, source reference or card expression changed. Review affected bindings before rendering.')
    data=dict(schema='field-card-concordance/0.1',name=NAME,status='experimental design; no canonical RTS or vocabulary admission',
        purpose='Resolve printed expressions to edition facts, qualifications, footnotes, terms and source context, then attach field-use references.',
        source_authority='existing published SG-010 and SG-010-L1; APP-D owns definitions and footnotes',
        source_snapshots={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (SOURCE,LONG,APP/'APP-D-v1.3.json')},
        facts={f:facts[f] for f in sorted(used)},terms={terms[t]['id']:terms[t] for t in sorted(used_terms)},
        footnotes={notes[n]['id']:notes[n] for n in sorted(used_notes)},l1_topics=topics,references=refs,
        cards=bindings,reverse_index={k:sorted(v) for k,v in sorted(reverse.items())},
        source_emphasis_policy='Card bolding/capitalization is editorial. Exact phrase matches are lexical evidence only, not inherited source emphasis.',
        review_lock_sha256=hashlib.sha256(LOCK.read_bytes()).hexdigest())
    return cards,data

def html_catalog(data,cards,out):
    esc=html.escape;by_id={c['id']:c for c in cards};parts=[]
    for b in data['cards']:
        c=by_id[b['card_id']];parts.append('<article id="'+c['id']+'"><h2>'+c['display_id']+' / '+esc(' - '.join(c['title']))+'</h2><p><a href="index.html">Card packs</a> · '+esc(NAME)+'</p>')
        if b.get('safety',{}).get('marked'):
            flag=b['safety']
            parts.append('<p style="color:#B3262E"><strong>+ SAFETY / '+esc(flag['focus'])+'</strong><br>'+esc(flag['meaning'])+'</p><p>Safety-emphasis sources: '+', '.join('<a href="'+data['facts'][fid]['link']+'">'+esc(data['facts'][fid]['label'])+'</a>' for fid in flag['fact_ids'])+'. Qualifications travel with these statements.</p>')
        if b.get('inspection_sketch'):
            parts.append('<p><strong>Inspection sketch:</strong> '+esc('; '.join(b['inspection_sketch']['targets']))+'. '+esc(b['inspection_sketch']['meaning'])+'</p>')
        for e in b['expressions']:
            if e['relationship']=='editorial_prompt':continue
            parts.append('<details><summary>'+esc(e['text'])+' <small>'+e['relationship']+'</small></summary>')
            for fid in e['fact_ids']:
                f=data['facts'][fid]
                parts.append('<p><a href="'+f['link']+'">SG-010 p. '+str(f['printed_page'])+' / '+esc(f['label'])+'</a><br>'+esc(f['retained'])+'<br><strong>Qualification:</strong> '+esc(f['qualification'])+'</p>')
            parts.append('</details>')
        parts.append('<h3>Terms · <span class="icon '+c['relevance']+'"></span> '+{'history':'History','observe':'Observe now','reference':'Check reference'}[c['relevance']]+'</h3><p class="quiet">Icon describes the use here, not every use of the term.</p>')
        for tid in b['term_ids']:
            t=data['terms'][tid]
            parts.append('<details><summary><span class="icon '+c['relevance']+'"></span> '+esc(t['term'])+'</summary><p>'+esc(t['expansion'])+' — '+esc(t['definition'])+'</p><a href="'+t['link']+'">APP-D: authoritative definition and source pointer</a><p>'+esc(t.get('source_pointer',''))+'</p></details>')
        parts.append('<details><summary>Footnotes and source context</summary>')
        for nid in b['footnote_ids']:
            n=data['footnotes'][nid];parts.append('<p><strong>'+nid.split(':')[-1]+' '+esc(n['label'])+'</strong>: '+esc(n['text'])+'</p>')
        parts.append('<p>These L1 links and their recording references are topic context. They do not assert that a particular recording time proves every card statement.</p>')
        for tid in b['related_l1_topic_ids']:
            t=data['l1_topics'][tid];parts.append('<p><a href="'+t['link']+'">'+esc(t['title'])+'</a></p>')
        parts.append('</details></article>')
    page='''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Field Card Concordance</title><style>body{font:17px system-ui;max-width:880px;margin:35px auto;padding:0 20px;color:#111}h1,h2,a{color:#1a1a5e}article{border-top:3px solid #1a1a5e;margin-top:45px;padding-top:15px}details{border-bottom:1px solid #ccc;padding:12px 0}summary{cursor:pointer}p{line-height:1.5}small,.quiet{font-size:14px;color:#555}.icon{display:inline-block;width:12px;height:12px;border:2px solid #1a1a5e;margin-right:5px;vertical-align:middle}.history{border-radius:50%;background:linear-gradient(90deg,transparent 50%,#1a1a5e 50%,#1a1a5e 60%,transparent 60%)}.observe{border-radius:70% 5%;transform:rotate(45deg);background:radial-gradient(circle,#1a1a5e 0 2px,transparent 3px)}.reference{border-radius:1px;box-shadow:inset 5px 0 white,inset 7px 0 #1a1a5e}input{font:inherit;padding:12px;width:90%}[hidden]{display:none}</style><h1>Field Card Concordance</h1><p>One translation layer connects a printed expression to its source statement and qualification, existing glossary definition, footnotes, and related recording context. Open any statement to follow it back.</p><p><a href="index.html">64 cards</a> · <a href="field-use.html">Routine / Tasks / Steps and timeline</a> · <a href="concordance.json">Portable data</a></p><p><span class="icon history"></span>History &nbsp; <span class="icon observe"></span>Observe now &nbsp; <span class="icon reference"></span>Check reference. These are navigation cues, not severity ratings or defect predictions.</p><input id="search" aria-label="Find a card or term" placeholder="Find a card, phrase or term">'''+''.join(parts)+'''<script>document.querySelector('input').oninput=e=>document.querySelectorAll('article').forEach(a=>a.hidden=!a.textContent.toLowerCase().includes(e.target.value.toLowerCase()));</script>'''
    (out/'concordance.html').write_text(page,encoding='utf-8')

def export(data,cards,out):
    save(out/'concordance.json',data)
    html_catalog(data,cards,out)
    save(out/'review-lock.json',read(LOCK))

if __name__=='__main__':
    import sys
    from field_cards_64_content import catalog
    cards,data=compile_cards(catalog(),establish_review='--establish-review' in sys.argv)
    print(json.dumps(dict(name=NAME,cards=len(cards),facts=len(data['facts']),expressions=sum(len(c['expressions']) for c in data['cards']),terms=len(data['terms']),footnotes=len(data['footnotes']))))
