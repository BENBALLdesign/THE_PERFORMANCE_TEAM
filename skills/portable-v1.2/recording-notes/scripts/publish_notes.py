"""Publish supplied notes locally; never generate or submit model prompts.
JSON fields: title, context, scope, numbers[{reference,value,meaning,status,refs}],
topics[{title,items:[{text,refs}]}], trees[{title,start,nodes:[{id,text,refs,branches:[{label,to}]}]}],
questions[{text,refs}]. Each ref: {source: source ID from manifest, frame: integer, label: lesson/page}.
"""
from pathlib import Path
import argparse,csv,hashlib,html,json
from datetime import datetime,timezone
from export_recordings import STYLE,read_json,write_json,digest

def publish(root,notes_path):
    root=Path(root).resolve();data=read_json(notes_path);manifest=read_json(root/'manifest.json')
    sources={s['source']['id']:s['source'] for s in manifest['sources']}
    frames={sid:{f['index']:f for f in read_json(root/sid/'frames.json')} for sid in sources}
    refs={}
    def collect(value):
        if isinstance(value,dict):
            for ref in value.get('refs',[]):
                key=(ref['source'],ref['frame'])
                if key[0] not in frames or key[1] not in frames[key[0]]:raise ValueError(f'Unknown evidence frame: {key}')
                frame=frames[key[0]][key[1]];p=root/key[0]/frame['image']
                if key not in refs and digest(p)!=frame['sha256']:raise ValueError('Evidence frame has changed.')
                refs.setdefault(key,dict(id=f'S{len(refs)+1:03}',**ref,**frame))
            for k,v in value.items():
                if k!='refs':collect(v)
        elif isinstance(value,list):
            for v in value:collect(v)
    collect(data)
    for row in data.get('numbers',[]):
        if not row.get('refs'):raise ValueError('Every number needs evidence.')
    for tree in data.get('trees',[]):
        ids=[n['id'] for n in tree['nodes']];nodes={n['id']:n for n in tree['nodes']}
        if len(ids)!=len(set(ids)):raise ValueError('Duplicate decision node.')
        reached=set()
        def walk(ident,trail):
            if ident not in nodes:raise ValueError('Unknown decision target.')
            if ident in trail:raise ValueError('Decision tree has a cycle.')
            reached.add(ident)
            for b in nodes[ident].get('branches',[]):walk(b['to'],trail|{ident})
        walk(tree['start'],set())
        if reached!=set(ids):raise ValueError('Unreachable decision node.')
    esc=html.escape
    def citation(items,markdown=False):
        out=[]
        for r in items:
            x=refs[(r['source'],r['frame'])];label=f'{x["id"]} · {r.get("label","")} · {x["timestamp"]}'
            image=f'{r["source"]}/{x["image"]}'
            if markdown:out.append(f'[{label}]({image})')
            else:out.append(f'<a class="source" href="{esc(image)}" data-image="{esc(image)}" data-caption="{esc(label)}">{esc(label)}</a>')
        return ' '.join(out)
    sections=[];md=[f'# {data["title"]}',data.get('context',''),data.get('scope','')]
    rows=[]
    for r in data.get('numbers',[]):
        rows.append('<tr>'+''.join(f'<td>{esc(str(r.get(k,"")))}</td>' for k in ('reference','value','meaning','status'))+f'<td>{citation(r["refs"])}</td></tr>')
    sections.append('<section id="numbers"><h2>Numbers and references</h2><div class="table-wrap"><table><thead><tr><th>Reference</th><th>Value</th><th>What to remember</th><th>Evidence status</th><th>Source</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div></section>')
    md+=['## Numbers and references','| Reference | Value | Meaning | Status / source |','|---|---|---|---|']
    for r in data.get('numbers',[]):md.append('| '+' | '.join(str(r.get(k,'')).replace('|','/') for k in ('reference','value','meaning'))+' | '+r.get('status','')+' '+citation(r['refs'],True)+' |')
    treedata=[]
    for i,t in enumerate(data.get('trees',[])):
        nodes={n['id']:n for n in t['nodes']};md+=['## '+t['title'],'Interpretation of the recorded material; see the linked sources.']
        for n in t['nodes']:
            md.append(f'- **{n["id"]}** {n["text"]} '+citation(n.get('refs',[]),True))
            for b in n.get('branches',[]):md.append(f'  - {b["label"]} → {b["to"]}')
        treedata.append(dict(start=t['start'],nodes={n['id']:dict(text=n['text'],branches=n.get('branches',[]),refs=citation(n.get('refs',[]))) for n in t['nodes']}))
        full=''.join(f'<p><b>{esc(n["id"])}.</b> {esc(n["text"])} '+citation(n.get('refs',[]))+''.join(f'<br><span class="branch">{esc(b["label"])} → {esc(b["to"])}</span>' for b in n.get('branches',[]))+'</p>' for n in t['nodes'])
        sections.append(f'<section class="tree" id="tree-{i}"><h2>{esc(t["title"])}</h2><p class="muted">Study decision tree derived from the recorded pages.</p><div class="walk" data-tree="{i}"></div><details class="full-tree"><summary>Show every branch</summary>{full}</details></section>')
    for i,t in enumerate(data.get('topics',[])):
        parts=[];md+=['## '+t['title']]
        for item in t['items']:
            parts.append(f'<li>{esc(item["text"])}<div>{citation(item.get("refs",[]))}</div></li>')
            md.append('- '+item['text']+' '+citation(item.get('refs',[]),True))
        sections.append(f'<section id="topic-{i}"><h2>{esc(t["title"])}</h2><ul>'+''.join(parts)+'</ul></section>')
    questions=data.get('questions',[])
    sections.append('<section class="questions" id="questions"><h2>Questions to resolve</h2>'+''.join(f'<p>{esc(q["text"])}<br>{citation(q.get("refs",[]))}</p>' for q in questions)+'</section>')
    md+=['## Questions to resolve']+[q['text']+' '+citation(q.get('refs',[]),True) for q in questions]
    sections.append('<section id="sources"><h2>Recording map</h2>'+''.join(f'<p><b>{esc(s["name"])}</b><br><span class="muted">{sid} | {s["duration_seconds"]:.2f} seconds</span><br><a href="{esc(Path(s["path"]).as_uri())}">Open original recording</a></p>' for sid,s in sources.items())+'<a href="index.html">Search all extracted evidence</a></section>')
    extra='''html{scroll-behavior:smooth}header .kicker{color:#b8d9b8;text-transform:uppercase;letter-spacing:2px;font-size:12px}main{padding-top:10px}section{background:white;border:1px solid #d5dddd;border-radius:10px;padding:22px;margin:18px 0}h2{font-size:23px;color:#183e42;margin:0 0 16px}nav{position:sticky;top:0;background:#f3f5f5;z-index:2;display:flex;gap:8px;flex-wrap:wrap}nav a,button{border:1px solid #c8d6d6;border-radius:6px;padding:9px 13px;background:white;text-decoration:none;color:#17575b}button:hover,nav a:hover{background:#e0eeeb}button:active{background:#bfd8d1}.source{display:inline-block;font-size:12px;padding:4px 6px;margin:4px 3px 0 0;background:#eaf2ef;border-radius:4px}.table-wrap{overflow:auto}th{background:#edf3f2}td{font-size:14px;vertical-align:top}td:nth-child(2){font-weight:700;min-width:120px}li{margin:12px 0;line-height:1.5}.questions{border-left:6px solid #b57b26;background:#fff9ec}.walk{border:1px solid #c8d9d2;border-radius:8px;padding:18px;background:#f5faf7}.walk p{font-size:19px}.walk button{margin:6px}.branch{display:inline-block;padding-left:22px;color:#31635e}.full-tree{margin-top:16px}dialog{max-width:95vw;max-height:95vh;border:0;border-radius:10px;padding:14px}dialog img{display:block;max-height:78vh}dialog::backdrop{background:#12272cbb}.count{font-size:14px;color:#d5e9e8;margin-top:12px}@media print{section{break-inside:auto}table{font-size:11px}.source{font-size:10px}.walk{display:none}.full-tree{display:block}dialog{display:none}header{padding:0}}'''
    js='''const trees=TREEDATA;function draw(i,id){let t=trees[i],n=t.nodes[id],box=document.querySelector('[data-tree="'+i+'"]');box.replaceChildren();let p=document.createElement('p');p.textContent=n.text;box.append(p);let refs=document.createElement('div');refs.innerHTML=n.refs;box.append(refs);for(let b of n.branches){let bt=document.createElement('button');bt.textContent=b.label;bt.onclick=()=>draw(i,b.to);box.append(bt)}let reset=document.createElement('button');reset.textContent='Start again';reset.onclick=()=>draw(i,t.start);box.append(reset)}trees.forEach((t,i)=>draw(i,t.start));document.addEventListener('click',e=>{let a=e.target.closest('a[data-image]');if(a){e.preventDefault();let d=document.querySelector('dialog');d.querySelector('img').src=a.dataset.image;d.querySelector('p').textContent=a.dataset.caption;d.showModal()}});document.querySelector('dialog button').onclick=()=>document.querySelector('dialog').close();window.addEventListener('beforeprint',()=>document.querySelectorAll('.full-tree').forEach(x=>x.open=true));'''.replace('TREEDATA',json.dumps(treedata,ensure_ascii=False).replace('<','\\u003c'))
    content='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>'+esc(data['title'])+'</title><style>'+STYLE+extra+'</style><header><div class="kicker">Class reference / recorded evidence</div><h1>'+esc(data['title'])+'</h1><p>'+esc(data.get('context',''))+'</p><div class="count">'+f'{len(sources)} recordings · {sum(s["sampled_frames"] for s in manifest["sources"])} sampled frames · {len(data.get("numbers",[]))} reference rows · {len(treedata)} decision trees</div></header><main><nav><a href="#numbers">Numbers</a><a href="#tree-0">Decisions</a><a href="#topic-0">Study notes</a><a href="#questions">Open questions</a><a href="index.html">Search evidence</a><button onclick="window.print()">Print / save PDF</button></nav><p class="muted">'+esc(data.get('scope',''))+'</p>'+''.join(sections)+'</main><dialog><button>Close</button><p></p><img alt="Recorded source evidence"></dialog><script>'+js+'</script></html>'
    (root/'study-notes.html').write_text(content,encoding='utf-8')
    (root/'study-notes.md').write_text('\n\n'.join(md),encoding='utf-8')
    write_json(root/'study-notes.json',data);write_json(root/'decision-trees.json',data.get('trees',[]))
    with (root/'reference-table.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=['reference','value','meaning','status','sources']);writer.writeheader()
        writer.writerows({**{k:r.get(k,'') for k in ('reference','value','meaning','status')},'sources':citation(r['refs'],True)} for r in data.get('numbers',[]))
    report=dict(schema=1,at=datetime.now(timezone.utc).isoformat(),source_frames_checked=len(refs),
                note_sha256=digest(root/'study-notes.json'),renderer_sha256=digest(__file__),
                evidence_manifest_sha256=digest(root/'manifest.json'),numbers=len(data.get('numbers',[])),trees=len(treedata),
                boundary='Supplied interpretations rendered locally; citations verified for existence and file integrity, not semantic correctness.')
    write_json(root/'publication.json',report);print(json.dumps(report,indent=2));return report

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--export',dest='root',required=True,type=Path);p.add_argument('--notes',required=True,type=Path);a=p.parse_args();publish(a.root,a.notes)
if __name__=='__main__':main()