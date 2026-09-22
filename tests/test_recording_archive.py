"""Safety checks for the archive's destructive boundary, using tiny fixtures."""
import importlib.util,json,tempfile,unittest,hashlib,sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import recording_archive as ra

class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name).resolve()
        self.bank=self.root/'bank';self.media=self.root/'media';self.media.mkdir();(self.bank/'RECORDINGS').mkdir(parents=True)
        self.a=self.media/'original.mp4';self.b=self.bank/'RECORDINGS/duplicate.mp4'
        self.data=b'controlled fixture bytes';self.a.write_bytes(self.data);self.b.write_bytes(self.data)
        h=hashlib.sha256(self.data).hexdigest();self.dest=self.bank/'RECORDINGS/Named/record.mp4'
        self.record=dict(recording_id='R'+h[:12],source_sha256=h,size=len(self.data),canonical_path=str(self.dest),bank_relative_path='Named/record.mp4',observed_paths=[str(self.a),str(self.b)],title='fixture',role='original')
        self.plan=dict(vault_id=ra.VAULT_ID,bank_root=str(self.bank/'RECORDINGS'),records=[self.record],summary={})
        self.p=self.root/'plan.json';ra.save(self.p,self.plan)
        self.patch1=patch.object(ra,'bank_root',return_value=self.bank);self.patch1.start();self.patch2=patch.object(ra,'MEDIA',self.media);self.patch2.start()
        self.patch3=patch.object(ra,'MIRROR',self.root/'registries/recordings-catalog.json');self.patch3.start()
    def tearDown(self):self.patch1.stop();self.patch2.stop();self.patch3.stop();self.tmp.cleanup()
    def test_verified_move_and_resume(self):
        ra.apply(self.p);self.assertEqual(self.dest.read_bytes(),self.data);self.assertFalse(self.a.exists());self.assertFalse(self.b.exists())
        ra.apply(self.p);self.assertEqual(self.dest.read_bytes(),self.data)
    def test_wrong_source_retained(self):
        self.b.write_bytes(b'x'*len(self.data))
        with self.assertRaises(ValueError):ra.apply(self.p)
        self.assertTrue(self.a.exists());self.assertTrue(self.b.exists());self.assertFalse(self.dest.exists())
    def test_escape_refused(self):
        self.record['canonical_path']=str(self.root/'outside.mp4')
        with self.assertRaises(ValueError):ra.validate(self.plan)
        self.assertTrue(self.a.exists())
    def test_busy_extraction_refused(self):
        lock=self.root/'busy';lock.write_text('busy')
        with self.assertRaises(RuntimeError):ra.apply(self.p,lock)
        self.assertTrue(self.a.exists());self.assertTrue(self.b.exists())
if __name__=='__main__':unittest.main()
