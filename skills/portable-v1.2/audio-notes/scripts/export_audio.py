"""Local, resumable audio transcription. No API, model download or speaker guessing."""
from pathlib import Path
import argparse, hashlib, json, math, os, re, shutil, subprocess, sys, uuid, time
from datetime import datetime, timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import local_runtime
VERSION='1.1.0'
FLAGS=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0

def now():return datetime.now(timezone.utc).isoformat()
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def save(path,data):
    path=Path(path);temp=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
    temp.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8')
    for attempt in range(10):
        try:temp.replace(path);break
        except PermissionError:
            if attempt==9:raise
            time.sleep(.2*(attempt+1))
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def command(args):return subprocess.run(list(map(str,args)),capture_output=True,check=True,creationflags=FLAGS)
def stamp(t):
    n=max(0,round(t*1000));h,n=divmod(n,3600000);m,n=divmod(n,60000);s,n=divmod(n,1000)
    return f'{h:02}:{m:02}:{s:02}.{n:03}'
def device_report(requested='auto',minimum_gb=3):
    import torch
    report=dict(requested=requested,torch_version=torch.__version__,cuda_build=torch.version.cuda,
                cuda_available=torch.cuda.is_available(),selected='cpu',reason='CPU requested')
    if requested=='cpu':return report
    if not report['cuda_available']:
        report['reason']='Installed PyTorch cannot use CUDA. Existing CuPy rendering support does not enable PyTorch CUDA.'
        if requested=='cuda':raise RuntimeError(report['reason'])
        return report
    free,total=torch.cuda.mem_get_info()
    report.update(gpu=torch.cuda.get_device_name(0),free_gb=free/1024**3,total_gb=total/1024**3)
    if free<minimum_gb*1024**3:
        report['reason']='Available GPU memory is below the configured reserve.'
        if requested=='cuda':raise RuntimeError(report['reason'])
        return report
    try:
        a=torch.tensor([1.,2.],device='cuda'); value=(a*a).sum().item();torch.cuda.synchronize()
        if value!=5:raise RuntimeError('GPU calculation failed.')
    except RuntimeError as exc:
        if requested=='cuda':raise
        report['reason']='GPU calculation probe failed: '+str(exc);return report
    report.update(selected='cuda',reason='CUDA calculation verified; free memory meets reserve.')
    return report

def outputs(root,result):
    save(root/'transcript.json',result)
    segments=sorted(result['segments'],key=lambda s:(s['start'],s['track']))
    text=f'# Audio transcript\n\nStatus: {result["state"]}. Speaker identities were not inferred.\n\n'
    if result['state']=='silent':text+='All audio tracks measured at or below -90 dBFS. No speech was inferred.\n'
    text+='\n\n'.join(f'[{stamp(s["start"])} / track {s["track"]}] {s["text"]}' for s in segments)
    (root/'transcript.md').write_text(text,encoding='utf-8')
    (root/'transcript.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(s["start"]).replace(".",",")} --> {stamp(s["end"]).replace(".",",")}\n{s["text"]}' for i,s in enumerate(segments)),encoding='utf-8')

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source',nargs='?',type=Path);p.add_argument('--output',type=Path)
    p.add_argument('--model',default=None,help='Local .pt path, cached model name, or auto (default). Never downloads.')
    p.add_argument('--device',choices=['auto','cpu','cuda'],default='auto')
    p.add_argument('--gpu-reserve-gb',type=float,default=3);p.add_argument('--threads',type=int,default=None)
    p.add_argument('--chunk-seconds',type=int,default=300);p.add_argument('--overlap-seconds',type=float,default=2)
    p.add_argument('--language',default='en');p.add_argument('--check-device',action='store_true')
    p.add_argument('--ffmpeg');p.add_argument('--ffprobe')
    local_runtime.add_options(p)
    a=p.parse_args(argv)
    try:runtime=local_runtime.resolve(a,__file__)
    except (ValueError,FileNotFoundError) as exc:p.error(str(exc))
    if a.check_runtime:
        print(json.dumps(runtime,indent=2));return
    if a.check_device:
        print(json.dumps(device_report(a.device,a.gpu_reserve_gb),indent=2));return
    if not a.source or not a.output:p.error('A source and --output are required.')
    if a.chunk_seconds<5 or not 0<=a.overlap_seconds<min(a.chunk_seconds/2,30) or not 1<=a.threads<=32 or not math.isfinite(a.gpu_reserve_gb) or a.gpu_reserve_gb<=0:p.error('Invalid resource or chunk settings.')
    source=a.source.resolve();root=a.output.resolve()
    if not source.is_file():p.error('Source does not exist.')
    if root==source or source.is_relative_to(root):p.error('Output cannot contain the source.')
    root.mkdir(parents=True,exist_ok=True);lock=root/'.export.lock'
    os.environ.setdefault('NUMBA_CACHE_DIR',str(root/'.runtime-cache'))
    try:
        with lock.open('x') as f:f.write(json.dumps(dict(pid=os.getpid(),at=now())))
    except FileExistsError:p.error('Export lock exists. Check the recorded process before resuming.')
    try:
        ffmpeg=a.ffmpeg;ffprobe=a.ffprobe
        if not ffmpeg or not ffprobe:raise FileNotFoundError('FFmpeg and ffprobe must be available.')
        source_hash=sha(source)
        probe=json.loads(command([ffprobe,'-v','error','-show_streams','-show_format','-of','json',source]).stdout)
        tracks=[s for s in probe['streams'] if s['codec_type']=='audio']
        settings=dict(source=str(source),source_sha256=source_hash,exporter_sha256=sha(__file__),
                      model_sha256=sha(a.model) if a.model and a.model.is_file() else None,device=a.device,
                      runtime_helper_sha256=sha(Path(local_runtime.__file__)),
                      gpu_reserve_gb=a.gpu_reserve_gb,chunk_seconds=a.chunk_seconds,
                      overlap_seconds=a.overlap_seconds,language=a.language)
        if (root/'settings.json').exists() and read(root/'settings.json')!=settings:raise ValueError('Settings changed. Use a new output version.')
        save(root/'settings.json',settings);save(root/'probe.json',probe);save(root/'runtime.json',runtime)
        result=dict(schema=1,version=VERSION,source=str(source),source_sha256=source_hash,
                    state='running',device=None,tracks=[],segments=[],chunks=[])
        for track in tracks:
            log=command([ffmpeg,'-hide_banner','-nostats','-i',source,'-map',f'0:{track["index"]}',
                         '-vn','-af','volumedetect','-f','null','-']).stderr.decode(errors='replace')
            found=re.search(r'max_volume: ([\-\d.]+) dB',log)
            if not found:raise RuntimeError('Audio peak measurement failed.')
            peak=float(found.group(1));result['tracks'].append(dict(index=track['index'],peak_dbfs=peak,silent=peak<=-90))
        audible=[x for x in result['tracks'] if not x['silent']]
        if not audible:
            result['state']='silent' if tracks else 'no_audio'
            outputs(root,result);save(root/'progress.json',dict(phase=result['state'],at=now()));return
        if not a.model or not a.model.is_file():raise FileNotFoundError(runtime['model_reason'])
        import torch,whisper
        torch.set_num_threads(a.threads)
        report=device_report(a.device,a.gpu_reserve_gb);result['device']=report
        save(root/'device.json',report)
        selected=report['selected']
        try:model=whisper.load_model(str(a.model),device=selected)
        except (torch.cuda.OutOfMemoryError,RuntimeError) as exc:
            if selected!='cuda' or a.device!='auto':raise
            torch.cuda.empty_cache();selected='cpu'
            report.update(selected='cpu',reason='CUDA model loading failed: '+str(exc))
            save(root/'device.json',report);model=whisper.load_model(str(a.model),device='cpu')
        duration=float(probe['format']['duration']);chunkdir=root/'chunks';chunkdir.mkdir(exist_ok=True)
        result['state']='running'
        for track in audible:
            for index,start in enumerate(range(0,math.ceil(duration),a.chunk_seconds)):
                if (root/'STOP').exists():result['state']='stopped';break
                end=min(start+a.chunk_seconds,duration)
                decode_start=max(0,start-a.overlap_seconds);decode_end=min(duration,end+a.overlap_seconds)
                basename=f't{track["index"]}-c{index:05}'
                raw=chunkdir/(basename+'.json');wav=chunkdir/(basename+'.wav')
                save(root/'progress.json',dict(phase='transcribing',track=track['index'],start_seconds=start,
                     duration_seconds=duration,percent=round(100*start/duration,1),device=selected,at=now()))
                if not raw.exists():
                    command([ffmpeg,'-v','error','-ss',decode_start,'-i',source,'-map',f'0:{track["index"]}',
                             '-t',decode_end-decode_start,'-ar','16000','-ac','1','-y',wav])
                    try:
                        decoded=model.transcribe(str(wav),language=a.language,fp16=selected=='cuda',
                             verbose=None,word_timestamps=True,condition_on_previous_text=False,temperature=0)
                    except torch.cuda.OutOfMemoryError as exc:
                        if selected!='cuda' or a.device!='auto':raise
                        model=model.to('cpu');torch.cuda.empty_cache();selected='cpu'
                        report.update(selected='cpu',reason='CUDA ran out of memory; remaining chunks use CPU.')
                        save(root/'device.json',report)
                        decoded=model.transcribe(str(wav),language=a.language,fp16=False,verbose=None,
                                                word_timestamps=True,condition_on_previous_text=False,temperature=0)
                    save(raw,dict(decode_start=decode_start,decode_end=decode_end,device=selected,
                                  wav_sha256=sha(wav),result=decoded))
                cached=read(raw)
                if not wav.is_file() or sha(wav)!=cached['wav_sha256']:raise ValueError('Cached audio chunk changed or is missing.')
                for seg in cached['result']['segments']:
                    words=[dict(text=w['word'],start=w['start']+decode_start,end=w['end']+decode_start,
                                probability=w.get('probability')) for w in seg.get('words',[])
                           if start <= (w['start']+w['end'])/2+decode_start < end]
                    if words:
                        result['segments'].append(dict(start=words[0]['start'],end=words[-1]['end'],
                            text=''.join(w['text'] for w in words).strip(),words=words,speaker=None,
                            track=track['index'],chunk=index,no_speech_probability=seg.get('no_speech_prob'),
                            average_logprob=seg.get('avg_logprob')))
                result['chunks'].append(dict(track=track['index'],chunk=index,start=start,end=end,
                    decode_start=decode_start,decode_end=decode_end,raw=str(raw.relative_to(root)),sha256=sha(raw)))
                outputs(root,result)
            if result['state']=='stopped':break
        if sha(source)!=source_hash:raise ValueError('Source changed during transcription.')
        if result['state']!='stopped':
            result['state']='completed';result['completed_at']=now()
        else:result['stopped_at']=now()
        outputs(root,result)
        save(root/'progress.json',dict(phase=result['state'],at=now(),chunks=len(result['chunks']),device=selected))
    except BaseException as exc:
        save(root/'progress.json',dict(phase='failed',error=str(exc),at=now()));raise
    finally:lock.unlink(missing_ok=True)
if __name__=='__main__':main()
