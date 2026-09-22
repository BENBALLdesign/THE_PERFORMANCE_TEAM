"""Portable local dependency/resource discovery. Standard library only; no downloads."""
from pathlib import Path
import ctypes,importlib.util,json,os,shutil,sys

VERSION='1.0.0'
PROFILES={'low-memory':(2,2),'balanced':(3,3),'throughput':(4,4)}
CONFIG_KEYS={'tool_dirs','model_dirs','python_packages','model','profile','tools','memory_reserve_gb'}

def memory_info():
    try:
        if os.name=='nt':
            from ctypes import wintypes
            class Memory(ctypes.Structure):
                _fields_=[('length',wintypes.DWORD),('load',wintypes.DWORD)]+[(n,ctypes.c_ulonglong) for n in ('total','available','total_page','available_page','total_virtual','available_virtual','extended')]
            m=Memory();m.length=ctypes.sizeof(m)
            if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):raise OSError('Memory query failed')
            return dict(total_gb=m.total/2**30,available_gb=m.available/2**30,method='GlobalMemoryStatusEx')
        if sys.platform.startswith('linux'):
            values={k:int(v.split()[0])*1024 for k,v in (line.split(':',1) for line in Path('/proc/meminfo').read_text().splitlines())}
            return dict(total_gb=values['MemTotal']/2**30,available_gb=values['MemAvailable']/2**30,method='/proc/meminfo')
        total=os.sysconf('SC_PAGE_SIZE')*os.sysconf('SC_PHYS_PAGES')/2**30
        return dict(total_gb=total,available_gb=None,method='sysconf; available memory unknown')
    except (OSError,ValueError,KeyError,AttributeError):
        return dict(total_gb=None,available_gb=None,method='unknown; conservative defaults')

def expanded(value,base=None):
    p=Path(os.path.expandvars(str(value))).expanduser()
    return ((base/p) if base and not p.is_absolute() else p).resolve()

def add_options(parser,ocr=False):
    parser.add_argument('--config',type=Path,help='Local JSON settings; relative paths inside it resolve from that file.')
    parser.add_argument('--tool-dir',action='append',default=[],help='Directory containing local binaries; repeatable.')
    parser.add_argument('--model-dir',action='append',default=[],help='Directory containing cached Whisper .pt files; repeatable.')
    parser.add_argument('--python-packages',type=Path,help='Optional compatible local Python package directory.')
    parser.add_argument('--profile',choices=['auto',*PROFILES],default=None,help='Automatic or explicit resource preset. Sources/audio jobs remain serial.')
    parser.add_argument('--memory-reserve-gb',type=float,default=None,help='Memory to leave free when automatically choosing a cached model (default 1.5).')
    parser.add_argument('--check-runtime',action='store_true',help='Print local tools, cached model, resources and dependency availability; do not process sources.')

def read_config(path):
    data=json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data,dict) or set(data)-CONFIG_KEYS:raise ValueError('Unsupported local settings keys: '+str(set(data)-CONFIG_KEYS if isinstance(data,dict) else 'expected an object'))
    for key in ('tool_dirs','model_dirs'):
        if key in data and (not isinstance(data[key],list) or not all(isinstance(v,str) for v in data[key])):raise ValueError(key+' must be a list of paths')
    if 'tools' in data and (not isinstance(data['tools'],dict) or set(data['tools'])-{'ffmpeg','ffprobe','tesseract'}):raise ValueError('tools must map ffmpeg, ffprobe and/or tesseract to local paths')
    return data

def find_tool(name,explicit,dirs):
    if explicit:
        p=expanded(explicit)
        if not p.is_file():raise FileNotFoundError(f'Explicit {name} path does not exist: {p}')
        return str(p)
    executable=name+('.exe' if os.name=='nt' else '')
    for directory in dirs:
        candidates=[directory/executable,directory/'bin'/executable,directory/name/executable]
        candidates+=sorted(directory.glob('*/bin/'+executable))+sorted(directory.glob('*/*/bin/'+executable))
        for p in candidates:
            if p.is_file():return str(p.resolve())
    found=shutil.which(name)
    if found:return str(Path(found).resolve())
    if name=='tesseract' and os.name=='nt':
        for var in ('ProgramFiles','ProgramFiles(x86)'):
            if os.environ.get(var):
                p=Path(os.environ[var])/'Tesseract-OCR'/executable
                if p.is_file():return str(p.resolve())
    return None

def choose_model(request,dirs,profile,memory,reserve):
    request=str(request or 'auto')
    if request!='auto':
        if '/' in request or '\\' in request or request.endswith('.pt'):
            p=expanded(request)
            if not p.is_file():raise FileNotFoundError('Requested local model is missing: '+str(p))
            return p,'explicit local checkpoint'
        for directory in dirs:
            p=directory/(request+'.pt')
            if p.is_file():return p.resolve(),'explicit cached model name'
        raise FileNotFoundError('Cached model '+request+' not found. Use --model PATH or --model-dir DIR. No download was attempted.')
    available=memory.get('available_gb')
    # Estimates are selection heuristics, not hard limits or performance guarantees.
    estimates={'tiny.en':.65,'base.en':1.0,'small.en':2.5}
    order=['base.en','tiny.en','small.en'] if profile=='low-memory' else ['small.en','base.en','tiny.en']
    for name in order:
        if available is not None and available-estimates[name]<reserve:continue
        for directory in dirs:
            p=directory/(name+'.pt')
            if p.is_file():return p.resolve(),f'automatic cached {name}; profile={profile}; reserve={reserve:g} GiB'
    return None,'No suitable cached checkpoint found within the memory estimate. Supply --model/--model-dir, free memory, or explicitly adjust the reserve. No download was attempted.'

def resolve(args,script,ocr=False):
    skills=Path(script).resolve().parents[2]
    config=expanded(args.config) if args.config else skills/'local-settings.json'
    cfg=read_config(config) if config.exists() else {}
    if args.config and not config.exists():raise FileNotFoundError('Settings file not found: '+str(config))
    anchor=config.parent
    pkg=args.python_packages or (expanded(cfg['python_packages'],anchor) if cfg.get('python_packages') else None)
    if pkg:
        pkg=expanded(pkg)
        if not pkg.is_dir():raise FileNotFoundError('Python package directory not found: '+str(pkg))
        sys.path.insert(0,str(pkg));os.environ['PYTHONPATH']=str(pkg)+(os.pathsep+os.environ['PYTHONPATH'] if os.environ.get('PYTHONPATH') else '')
    dirs=[expanded(p) for p in args.tool_dir]+[expanded(p,anchor) for p in cfg.get('tool_dirs',[])]+[skills/'tools']
    modeldirs=[expanded(p) for p in args.model_dir]+[expanded(p,anchor) for p in cfg.get('model_dirs',[])]+[skills/'models',skills/'tools']+dirs
    if os.environ.get('WHISPER_MODEL_DIR'):modeldirs.append(expanded(os.environ['WHISPER_MODEL_DIR']))
    modeldirs.append(Path.home()/'.cache/whisper')
    memory=memory_info();requested=args.profile or cfg.get('profile','auto')
    if requested not in ['auto',*PROFILES]:raise ValueError('Unknown resource profile: '+str(requested))
    profile=requested
    if profile=='auto':profile='low-memory' if memory['total_gb'] is None or memory['total_gb']<12 or (memory['available_gb'] is not None and memory['available_gb']<4) else 'balanced'
    reserve=args.memory_reserve_gb if args.memory_reserve_gb is not None else cfg.get('memory_reserve_gb',1.5)
    if not isinstance(reserve,(int,float)) or not 0<=reserve<1024:raise ValueError('memory-reserve-gb must be finite and between 0 and 1024')
    requested_model=args.model or cfg.get('model','auto')
    if args.model is None and requested_model!='auto' and ('/' in str(requested_model) or '\\' in str(requested_model) or str(requested_model).endswith('.pt')):requested_model=str(expanded(requested_model,anchor))
    model,reason=choose_model(requested_model,modeldirs,profile,memory,reserve)
    args.model=model
    tools={}
    for name in ['ffmpeg','ffprobe']+(['tesseract'] if ocr else []):
        explicit=getattr(args,name,None)
        if not explicit and cfg.get('tools',{}).get(name):explicit=expanded(cfg['tools'][name],anchor)
        tools[name]=find_tool(name,explicit,dirs);setattr(args,name,tools[name])
    # Whisper internally invokes ffmpeg by name when loading a WAV file.
    if tools.get('ffmpeg'):
        os.environ['PATH']=str(Path(tools['ffmpeg']).parent)+os.pathsep+os.environ.get('PATH','')
    workers,threads=PROFILES[profile];cpus=os.cpu_count() or 2
    if ocr:
        args.workers=args.workers if args.workers is not None else min(workers,cpus)
        args.speech_threads=args.speech_threads if args.speech_threads is not None else min(threads,cpus)
    else:args.threads=args.threads if args.threads is not None else min(threads,cpus)
    runtime=dict(schema=1,helper_version=VERSION,profile=profile,requested_profile=requested,memory=memory,memory_reserve_gb=reserve,tools=tools,model=str(model) if model else None,model_reason=reason,model_search_dirs=[str(p) for p in modeldirs],python=sys.executable,python_packages=str(pkg) if pkg else None,audio_jobs=1,ocr_workers=getattr(args,'workers',None),speech_threads=getattr(args,'speech_threads',getattr(args,'threads',None)),downloads=False)
    runtime['dependencies']={name:bool((spec:=importlib.util.find_spec(name)) and spec.origin) for name in (['PIL','numpy','torch','whisper'] if ocr else ['torch','whisper'])}
    if not args.check_runtime and not getattr(args,'check_device',False):
        missing=[n for n,p in tools.items() if not p]
        if missing:raise FileNotFoundError('Missing local tools: '+', '.join(missing)+'. Use PATH, --tool-dir or explicit tool paths; --check-runtime shows the search result.')
    args.runtime=runtime
    return runtime
