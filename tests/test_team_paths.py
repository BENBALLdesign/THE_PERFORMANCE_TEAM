"""The checkout resolves its own registries and brand assets; the installation is a local record, never a code path."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import team_paths  # noqa: E402


class TeamPathsTests(unittest.TestCase):
    def test_checkout_layout(self):
        self.assertEqual(team_paths.CHECKOUT, ROOT)
        self.assertTrue(team_paths.registry('STUDY-GUIDE-EDITIONS.json').is_file())
        self.assertTrue(team_paths.registry('APPENDIX-VERSIONS.json').is_file())
        self.assertTrue(team_paths.registry('recordings-catalog.json').is_file())
        self.assertTrue(team_paths.registry('Library/CURRENT.json').is_file())

    def test_brand_assets_present_and_shaped(self):
        palette = json.loads(team_paths.brand('tokens/palette.json').read_text(encoding='utf-8-sig'))
        self.assertIn('navy', palette['color'])
        self.assertTrue(team_paths.brand('logos/BENBALL_A_CANONICAL.svg').is_file())
        for name in ['typography.json', 'spacing.json']:
            self.assertTrue(team_paths.brand('tokens/' + name).is_file(), name)

    def test_unconfigured_installation_is_explicit(self):
        with patch.object(team_paths, 'SETTINGS', ROOT / 'tests/no-such-installation.json'), \
             patch.dict(os.environ, {team_paths.ENV_INSTALLATION: ''}):
            self.assertIsNone(team_paths.installation(strict=False))
            with self.assertRaises(FileNotFoundError):
                team_paths.installation()

    def test_environment_names_an_installation(self):
        with tempfile.TemporaryDirectory() as tmp, \
             patch.object(team_paths, 'SETTINGS', ROOT / 'tests/no-such-installation.json'), \
             patch.dict(os.environ, {team_paths.ENV_INSTALLATION: tmp, team_paths.ENV_SEED_BANK: 'X:/BANK'}):
            self.assertEqual(team_paths.installation(), Path(tmp))
            self.assertEqual(team_paths.seed_bank(), Path('X:/BANK'))

    def test_no_bbdf_in_tracked_code(self):
        """The separation's point: no tracked module imports or names the BBDF code tree."""
        offenders = []
        for folder in ['tools', 'production', 'builder']:
            for p in (ROOT / folder).rglob('*.py'):
                text = p.read_text(encoding='utf-8', errors='replace')
                for needle in ['bbdf_core', 'BEN_BALL/BB_CODE', 'BEN_BALL\\\\BB_CODE', "Path('C:/Users/", '.cache/home-inspection-pdf-tools']:
                    if needle in text:
                        offenders.append(f'{p.relative_to(ROOT)}: {needle}')
        self.assertEqual(offenders, [])


if __name__ == '__main__':
    unittest.main()
