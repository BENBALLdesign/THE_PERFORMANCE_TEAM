from pathlib import Path
import argparse,json,os,sys,tempfile,unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import local_runtime as R

class RuntimeTests(unittest.TestCase):
    def setUp(self):
        temp=ROOT/'tests/tmp';temp.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=temp);self.root=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()
    def touch(self,path):path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(b'test');return path
    def test_low_memory_prefers_cached_base(self):
        self.touch(self.root/'base.en.pt');self.touch(self.root/'small.en.pt')
        model,_=R.choose_model('auto',[self.root],'low-memory',{'available_gb':4},1.5)
        self.assertEqual(model.name,'base.en.pt')
    def test_reserve_prevents_large_automatic_model(self):
        self.touch(self.root/'small.en.pt');self.touch(self.root/'base.en.pt')
        model,_=R.choose_model('auto',[self.root],'balanced',{'available_gb':3},1.5)
        self.assertEqual(model.name,'base.en.pt')
    def test_missing_explicit_model_never_falls_back(self):
        self.touch(self.root/'base.en.pt')
        with self.assertRaises(FileNotFoundError):R.choose_model('small.en',[self.root],'low-memory',{},1.5)
    def test_no_model_reports_no_download(self):
        model,reason=R.choose_model('auto',[self.root],'balanced',{},1.5)
        self.assertIsNone(model);self.assertIn('No download',reason)
    def test_explicit_tool_wins_over_search_directory(self):
        a=self.touch(self.root/'explicit tool.exe');self.touch(self.root/'ffmpeg.exe')
        self.assertEqual(R.find_tool('ffmpeg',a,[self.root]),str(a.resolve()))
    def test_config_relative_paths_are_independent_of_cwd(self):
        tool=self.touch(self.root/'portable/bin/ffmpeg.exe')
        model=self.touch(self.root/'models/base.en.pt')
        cfg=self.root/'settings.json';cfg.write_text(json.dumps(dict(tools={'ffmpeg':'portable/bin/ffmpeg.exe'},model='models/base.en.pt',profile='low-memory')))
        parser=argparse.ArgumentParser();parser.add_argument('--model');parser.add_argument('--threads',type=int);parser.add_argument('--ffmpeg');parser.add_argument('--ffprobe');R.add_options(parser)
        args=parser.parse_args(['--config',str(cfg),'--check-runtime'])
        with patch.object(R,'memory_info',return_value=dict(total_gb=8,available_gb=4,method='test')):report=R.resolve(args,ROOT/'audio-notes/scripts/export_audio.py')
        self.assertEqual(report['tools']['ffmpeg'],str(tool.resolve()));self.assertEqual(report['model'],str(model.resolve()));self.assertEqual(args.threads,2)
    def test_command_line_model_overrides_config(self):
        model=self.touch(self.root/'override.pt');cfg=self.root/'settings.json';cfg.write_text(json.dumps(dict(model='missing-model.pt')))
        parser=argparse.ArgumentParser();parser.add_argument('--model');parser.add_argument('--threads',type=int);parser.add_argument('--ffmpeg');parser.add_argument('--ffprobe');R.add_options(parser)
        args=parser.parse_args(['--config',str(cfg),'--model',str(model),'--check-runtime'])
        report=R.resolve(args,ROOT/'audio-notes/scripts/export_audio.py');self.assertEqual(report['model'],str(model.resolve()))
    def test_invalid_config_fails_clearly(self):
        p=self.root/'bad.json';p.write_text('{"model_dris": []}')
        with self.assertRaises(ValueError):R.read_config(p)

if __name__=='__main__':unittest.main(verbosity=2)
