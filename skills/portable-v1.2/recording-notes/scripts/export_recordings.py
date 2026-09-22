"""Versioned, local recording exports. Sources are opened read-only.
Python 3.11+, Pillow, numpy, FFmpeg and Tesseract; optional cached Whisper.
"""
from __future__ import annotations
import argparse, concurrent.futures, csv, hashlib, html, io, json, math, os
from pathlib import Path
import re, shutil, subprocess, sys, time, uuid
from datetime import datetime, timezone

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import local_runtime
VERSION = '1.2.0'
FLAGS = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0

def now(): return datetime.now(timezone.utc).isoformat()
def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''): h.update(block)
    return h.hexdigest()
def write_json(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding='utf-8')
    for attempt in range(10):
        try: temp.replace(path); break
        except PermissionError:
            if attempt == 9: raise
            time.sleep(.2 * (attempt + 1))
def read_json(path): return json.loads(Path(path).read_text(encoding='utf-8'))
def stamp(seconds):
    ms = max(0, round(seconds * 1000)); h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f'{h:02}:{m:02}:{s:02}.{ms:03}'
def run(command, **kwargs):
    return subprocess.run(list(map(str, command)), check=True, capture_output=True,
                          creationflags=FLAGS, **kwargs)
def tool(name, explicit=None):
    p = explicit or shutil.which(name)
    if not p and name == 'tesseract':
        p = local_runtime.find_tool(name,None,[])
    if not p or not Path(p).is_file(): raise FileNotFoundError(f'{name} is required; supply its path.')
    return str(Path(p).resolve())
def status(root, phase, **kw):
    event = dict(at=now(), phase=phase, **kw)
    write_json(Path(root) / 'progress.json', event)
    with (Path(root) / 'events.jsonl').open('a', encoding='utf-8') as f:
        f.write(json.dumps(event, ensure_ascii=False) + '\n')
    print(json.dumps(event, ensure_ascii=True), flush=True)
def normal(text): return re.sub(r'\s+', ' ', text).strip().casefold()
def reference_tokens(text):
    # Capture candidates only. Digits in URLs, headings and question numbers are not automatically rules.
    return re.findall(r'(?:[A-Z]{1,5}\s*)?\d+(?:\s*/\s*\d+|\.\d+)*(?:\s*(?:%|inches|inch|feet|foot|mm|cm|psi|psf|degrees|[\"\u2033\u00b0]))?', text)
def audio_analysis(source, ffmpeg, streams):
    tracks = [x for x in streams if x['codec_type'] == 'audio']
    result = []
    for stream in tracks:
        p = run([ffmpeg, '-hide_banner', '-nostats', '-i', source,
                 '-map', f'0:{stream["index"]}', '-vn', '-af', 'volumedetect', '-f', 'null', '-'])
        log = p.stderr.decode('utf-8', errors='replace')
        peak = re.search(r'max_volume: ([\-\d.]+) dB', log)
        if not peak: raise RuntimeError('Audio level measurement did not return a peak.')
        db = float(peak.group(1))
        result.append(dict(stream=stream['index'], channels=stream.get('channels'), peak_dbfs=db,
                           silent=db <= -90, method='FFmpeg volumedetect on all channels, full stream'))
    return dict(state='absent' if not tracks else ('silent' if all(x['silent'] for x in result) else 'present'),
                tracks=result, threshold_dbfs=-90)
def extract_frames(source, folder, ffmpeg, interval, scene):
    folder.mkdir(parents=True, exist_ok=True)
    select = '1' if interval == 0 else f'isnan(prev_selected_t)+gte(t-prev_selected_t,{interval})+gt(scene,{scene})'
    logpath = folder.parent / 'frame-extraction.log'
    with logpath.open('wb') as log:
        subprocess.run([ffmpeg, '-hide_banner', '-nostats', '-i', str(source), '-map', '0:v:0',
                        '-vf', f"select='{select}',showinfo", '-fps_mode', 'vfr', '-q:v', '2',
                        '-y', str(folder / 'frame-%07d.jpg')], stdout=subprocess.DEVNULL,
                       stderr=log, check=True, creationflags=FLAGS)
    times = [float(x) for x in re.findall(r'\bn:\s*\d+\s+pts:\s*[-\d]+\s+pts_time:([\d.eE+\-]+)',
                                        logpath.read_text(encoding='utf-8', errors='replace'))]
    files = sorted(folder.glob('frame-*.jpg'))
    if len(files) != len(times): raise RuntimeError(f'Frame/timestamp mismatch: {len(files)} / {len(times)}')
    return [dict(index=i+1, time_seconds=t, timestamp=stamp(t), image=str(p.relative_to(folder.parent)),
                 sha256=digest(p)) for i, (p,t) in enumerate(zip(files, times))]
def ocr_frame(path, executable, language, scale):
    from PIL import Image, ImageOps
    with Image.open(path) as im:
        im = ImageOps.grayscale(im)
        if scale != 1: im = im.resize((round(im.width*scale), round(im.height*scale)), Image.Resampling.LANCZOS)
        data = io.BytesIO(); im.save(data, format='PNG')
    env = dict(os.environ, OMP_THREAD_LIMIT='1')
    p = run([executable, 'stdin', 'stdout', '-l', language, '--psm', '3', 'tsv'], input=data.getvalue(), env=env)
    words = []
    for row in csv.DictReader(io.StringIO(p.stdout.decode('utf-8', errors='replace')), delimiter='\t', quoting=csv.QUOTE_NONE):
        if row.get('level') != '5' or not row.get('text', '').strip(): continue
        words.append(dict(text=row['text'], confidence=float(row['conf']),
                          line=[int(row[x]) for x in ('block_num','par_num','line_num')],
                          box=[int(row[x])/scale for x in ('left','top','width','height')]))
    lines = []
    for w in words:
        if not lines or lines[-1]['key'] != w['line']:
            lines.append(dict(key=w['line'], words=[]))
        lines[-1]['words'].append(w)
    for line in lines:
        line['text'] = ' '.join(x['text'] for x in line['words'])
        line['confidence'] = sum(x['confidence'] for x in line['words']) / len(line['words'])
    return dict(text='\n'.join(x['text'] for x in lines), lines=lines,
                confidence=sum(x['confidence'] for x in words)/len(words) if words else None)
def transcribe(source, output, audio, args, ffmpeg):
    path = output / 'transcript.json'
    if path.exists(): return read_json(path)
    result = dict(schema=1, status=audio['state'], segments=[], speaker_identification='not performed')
    if audio['state'] == 'present' and not args.skip_speech:
        if not args.model:raise FileNotFoundError(args.runtime['model_reason'])
        engine = Path(__file__).parents[2] / 'audio-notes/scripts/export_audio.py'
        if not engine.is_file(): raise FileNotFoundError('The sibling audio-notes exporter is required for audible recordings.')
        child = output / 'audio-export'
        run([sys.executable, '-B', engine, source, '--output', child,
             '--model', args.model, '--language', args.language, '--device', args.device,
             '--chunk-seconds', args.chunk_seconds, '--threads', args.speech_threads,
             '--ffmpeg',ffmpeg,'--ffprobe',args.ffprobe])
        decoded = read_json(child / 'transcript.json')
        result.update(status=decoded['state'], segments=decoded['segments'], device=decoded.get('device'),
                      audio_export='audio-export/transcript.json')
    elif audio['state'] == 'present':
        result.update(status='needs_transcription', reason='Speech extraction explicitly skipped.')
    write_json(path, result)
    text = f'# Audio transcript\n\nStatus: {result["status"]}.\n\n'
    if audio['state'] == 'silent': text += 'The entire audio track measured at or below -90 dBFS. No spoken transcript was inferred.\n'
    for s in result['segments']: text += f'[{stamp(s["start"])}] {s["text"]}\n\n'
    (output / 'transcript.md').write_text(text, encoding='utf-8')
    (output / 'transcript.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(s["start"]).replace(".",",")} --> {stamp(s["end"]).replace(".",",")}\n{s["text"]}' for i,s in enumerate(result['segments'])), encoding='utf-8')
    return result

def export_source(source, root, args, tools):
    ffmpeg, ffprobe, tesseract = tools
    source = Path(source).resolve(); source_hash = digest(source)
    sid = 'R' + source_hash[:12]; folder = root / sid; folder.mkdir(exist_ok=True)
    settings = dict(version=VERSION, exporter_sha256=digest(__file__), interval=args.interval,
                    runtime_helper_sha256=digest(Path(local_runtime.__file__)),
                    scene=args.scene, ocr_language=args.ocr_language, scale=args.scale,
                    tesseract_version=run([tesseract,'--version']).stdout.decode().splitlines()[0],
                    ffmpeg_version=run([ffmpeg,'-version']).stdout.decode().splitlines()[0],
                    skip_speech=args.skip_speech, model=str(args.model), language=args.language, device=args.device,
                    audio_exporter_sha256=digest(Path(__file__).parents[2]/'audio-notes/scripts/export_audio.py'),
                    chunk_seconds=args.chunk_seconds)
    config = dict(source_sha256=source_hash, settings=settings)
    if (folder/'config.json').exists() and read_json(folder/'config.json') != config:
        raise ValueError('Source/export settings changed. Select a new output folder to preserve the earlier version.')
    write_json(folder/'config.json',config)
    status(root,'metadata',source=source.name)
    probe = json.loads(run([ffprobe,'-v','error','-show_format','-show_streams','-of','json',source]).stdout)
    write_json(folder/'probe.json', probe)
    metadata = dict(id=sid,path=str(source),sha256=source_hash,size=source.stat().st_size,
                    modified_ns=source.stat().st_mtime_ns, duration_seconds=float(probe['format']['duration']),
                    creation_time=probe['format'].get('tags',{}).get('creation_time'),name=source.name)
    audio = audio_analysis(source,ffmpeg,probe['streams']); write_json(folder/'audio.json',audio)
    status(root,'audio',source=source.name,state=audio['state'])
    transcript=transcribe(source,folder,audio,args,ffmpeg)
    videos = [s for s in probe['streams'] if s['codec_type']=='video' and not s.get('disposition',{}).get('attached_pic')]
    if (folder/'frames.json').exists():
        frames=read_json(folder/'frames.json')
        if any(not (folder/f['image']).exists() or digest(folder/f['image'])!=f['sha256'] for f in frames):
            raise ValueError('A cached frame changed or is missing; use a new output version.')
    else:
        status(root,'frames',source=source.name,interval=args.interval,scene_threshold=args.scene)
        frames=extract_frames(source,folder/'frames',ffmpeg,args.interval,args.scene) if videos else []
        write_json(folder/'frames.json',frames)
    ocrdir=folder/'ocr'; ocrdir.mkdir(exist_ok=True)
    pending=[f for f in frames if not (ocrdir/f'{f["index"]:07}.json').exists()]
    completed=len(frames)-len(pending)
    status(root,'screen_text',source=source.name,completed=completed,total=len(frames))
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        future_map={pool.submit(ocr_frame,folder/f['image'],tesseract,args.ocr_language,args.scale):f for f in pending}
        for future in concurrent.futures.as_completed(future_map):
            frame=future_map[future]; data=dict(frame=frame, **future.result())
            write_json(ocrdir/f'{frame["index"]:07}.json',data)
            completed+=1
            if completed%20==0 or completed==len(frames):
                status(root,'screen_text',source=source.name,completed=completed,total=len(frames),percent=round(100*completed/max(len(frames),1),1))
    evidence=[]; seen={}; screen_md=[]; references=[]
    for frame in frames:
        data=read_json(ocrdir/f'{frame["index"]:07}.json')
        new=[]
        for ln,line in enumerate(data['lines']):
            key=normal(line['text'])
            if not key: continue
            occurrence=dict(frame=frame['index'],time_seconds=frame['time_seconds'],timestamp=frame['timestamp'],
                            image=f'{sid}/{frame["image"]}',line=ln,confidence=line['confidence'])
            if key in seen:
                seen[key]['occurrences'].append(occurrence)
                continue
            eid=f'{sid}-F{frame["index"]:07}-L{ln+1:03}'
            row=dict(id=eid,source=sid,kind='screen_ocr',text=line['text'],confidence=line['confidence'],
                     reference_candidates=reference_tokens(line['text']),occurrences=[occurrence],review='unverified_ocr')
            seen[key]=row; evidence.append(row); new.append(row)
            for token in row['reference_candidates']:
                references.append(dict(evidence_id=eid,token=token,source=sid,timestamp=frame['timestamp'],
                                       context=line['text'],confidence=line['confidence']))
        if new:
            screen_md.append(f'## {frame["timestamp"]} (frame {frame["index"]})\n\n'+ '\n'.join(f'- [{r["id"]}] {r["text"]}' for r in new))
    for i,s in enumerate(transcript['segments']):
        evidence.append(dict(id=f'{sid}-A{i+1:05}',source=sid,kind='speech_machine',text=s['text'],
            occurrences=[dict(time_seconds=s['start'],timestamp=stamp(s['start']),end_seconds=s['end'],track=s['track'])],review='unverified_transcript'))
    if digest(source)!=source_hash: raise ValueError('Source changed while extraction was running. Results cannot be finalized.')
    write_json(folder/'evidence.json',evidence)
    (folder/'screen-text.md').write_text('# Screen text: newly encountered lines\n\nMachine extraction. Repeated exact lines are indexed once; all occurrences remain in evidence.json.\n\n'+'\n\n'.join(screen_md),encoding='utf-8')
    summary=dict(schema=1, source=metadata,audio=audio,transcript_status=transcript['status'],
                 sampled_frames=len(frames),unique_text_lines=len(seen),exported_at=now(),settings=settings)
    write_json(folder/'manifest.json',summary)
    return summary,evidence,references

STYLE='''body{font:16px system-ui;margin:0;background:#f3f5f5;color:#17252a}header{background:#172d32;color:white;padding:24px 5vw}main{max-width:1280px;margin:auto;padding:24px}h1{margin:0 0 8px}a{color:#0b6262}input{padding:12px;width:90%;font:inherit}article{background:white;padding:18px;margin:12px 0;border:1px solid #d4dede;border-radius:8px}summary{cursor:pointer;font-weight:600}.muted{color:#56666b;font-size:14px}img{max-width:100%;max-height:820px;object-fit:contain}table{border-collapse:collapse;width:100%}td,th{padding:10px;border:1px solid #ccd5d5;text-align:left}pre{white-space:pre-wrap;font:14px ui-monospace}button{padding:8px 14px;cursor:pointer}nav{padding:12px 0} @media print{header{background:white;color:black}nav,input,button{display:none}article{break-inside:avoid}}'''
def index_html(root,summaries,evidence):
    esc=html.escape; cards=[]
    for s in summaries:
        m=s['source']; cards.append(f'<article><b>{esc(m["name"])}</b><p>{stamp(m["duration_seconds"])} | {s["sampled_frames"]} sampled frames | audio: {s["audio"]["state"]}</p><a href="{m["id"]}/screen-text.md">Extracted text</a> | <a href="{m["id"]}/manifest.json">Source record</a></article>')
    for e in evidence:
        o=e['occurrences'][0]; image=o.get('image')
        detail=f'<img loading="lazy" src="{esc(image)}" alt="Recorded screen at {o["timestamp"]}">' if image else ''
        cards.append(f'<article class="evidence" id="{e["id"]}"><div class="muted">{e["id"]} | {o["timestamp"]} | {len(e["occurrences"])} observations | {e["review"]}</div><p>{esc(e["text"])}</p><details><summary>Inspect recorded screen</summary>{detail}</details></article>')
    (root/'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Recording evidence</title><style>'+STYLE+'</style><header><h1>Recording evidence</h1>Searchable screen text and source timestamps</header><main><nav><a href="study-notes.html">Study notes</a> | <a href="reference-candidates.csv">Number/reference candidates</a></nav><input id="search" placeholder="Find a term, reference number, or evidence ID">'+''.join(cards)+'''</main><script>document.querySelector('#search').addEventListener('input',e=>{let q=e.target.value.toLowerCase();document.querySelectorAll('.evidence').forEach(a=>a.hidden=!a.textContent.toLowerCase().includes(q))})</script></html>''',encoding='utf-8')

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('sources',nargs='*',type=Path);p.add_argument('--output',type=Path)
    p.add_argument('--interval',type=float,default=1,help='Seconds between sampled frames; 0 processes every frame.')
    p.add_argument('--scene',type=float,default=.035,help='Also sample intervening scene changes.')
    p.add_argument('--workers',type=int,default=None);p.add_argument('--scale',type=float,default=2)
    p.add_argument('--ocr-language',default='eng');p.add_argument('--language',default='en')
    p.add_argument('--model',default=None,help='Local .pt path, cached model name, or auto (default). Never downloads.')
    p.add_argument('--speech-threads',type=int,default=None);p.add_argument('--chunk-seconds',type=int,default=300)
    p.add_argument('--device',choices=['auto','cpu','cuda'],default='auto');p.add_argument('--skip-speech',action='store_true');p.add_argument('--ffmpeg');p.add_argument('--ffprobe');p.add_argument('--tesseract')
    local_runtime.add_options(p,ocr=True)
    args=p.parse_args(argv)
    try:runtime=local_runtime.resolve(args,__file__,ocr=True)
    except (ValueError,FileNotFoundError) as exc:p.error(str(exc))
    if args.check_runtime:
        print(json.dumps(runtime,indent=2));return
    if not args.sources or not args.output:p.error('Sources and --output are required unless --check-runtime is used.')
    if not math.isfinite(args.interval) or args.interval<0 or not 0<=args.scene<=1 or not 1<=args.workers<=16 or not 1<=args.speech_threads<=32 or not 1<=args.scale<=4 or args.chunk_seconds<1:
        p.error('Invalid sampling, scale, worker or chunk parameters.')
    root=args.output.resolve()
    for source in args.sources:
        source=source.resolve()
        if not source.is_file(): p.error(f'Source does not exist: {source}')
        if root==source or source.is_relative_to(root): p.error('Output must not contain or replace source files.')
    root.mkdir(parents=True,exist_ok=True)
    lock=root/'.export.lock'
    try:
        with lock.open('x') as f: f.write(json.dumps(dict(pid=os.getpid(),at=now())))
    except FileExistsError: p.error('An export lock exists. Check its process before resuming; do not run two exporters in the same folder.')
    try:
        write_json(root/'runtime.json',runtime)
        executable=tuple(tool(n,getattr(args,n)) for n in ('ffmpeg','ffprobe','tesseract'))
        summaries=[]; evidence=[]; references=[]; known=set()
        for source in args.sources:
            h=digest(source)
            if h in known: continue
            known.add(h); s,e,r=export_source(source,root,args,executable)
            summaries.append(s); evidence.extend(e); references.extend(r)
        write_json(root/'evidence.json',evidence)
        with (root/'reference-candidates.csv').open('w',encoding='utf-8-sig',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=['evidence_id','token','source','timestamp','context','confidence'])
            writer.writeheader();writer.writerows(references)
        write_json(root/'manifest.json',dict(schema=1,version=VERSION,sources=summaries,exported_at=now(),
                   evidence_count=len(evidence),reference_candidates=len(references),interpretation='pending'))
        index_html(root,summaries,evidence)
        status(root,'complete',sources=len(summaries),evidence=len(evidence),reference_candidates=len(references))
    except BaseException as exc:
        status(root,'failed',error=str(exc)); raise
    finally:
        lock.unlink(missing_ok=True)
if __name__=='__main__':main()
