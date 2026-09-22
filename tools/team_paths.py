"""Where THE PERFORMANCE TEAM checkout, its installation, its registries, its brand assets and the Seed Bank are.

The checkout (this repository) owns code, contracts, registries and the small brand assets the renderers
read. The installation (the Dropbox folder "THE PERFORMANCE TEAM") owns published reading material and
is named only by the ignored local file installation.json. Bulk media and history live in the Seed Bank,
named there as well. Nothing here consults a BBDF package, path or database.
"""
from pathlib import Path
import json
import os
import sys

CHECKOUT = Path(__file__).resolve().parents[1]
REGISTRIES = CHECKOUT / 'registries'
ASSETS = CHECKOUT / 'assets'
SETTINGS = CHECKOUT / 'installation.json'
EXAMPLE = CHECKOUT / 'installation.example.json'
DEFAULT_SEED_BANK = 'F:/SEED BANK'

ENV_INSTALLATION = 'PERFORMANCE_TEAM_INSTALLATION'
ENV_SEED_BANK = 'PERFORMANCE_TEAM_SEED_BANK'
ENV_PYMUPDF = 'PERFORMANCE_TEAM_PYMUPDF'


def settings():
    """The local installation record, or an empty mapping in a fresh clone."""
    if not SETTINGS.is_file():
        return {}
    return json.loads(SETTINGS.read_text(encoding='utf-8-sig'))


def installation(strict=True):
    """Root of the Dropbox installation (published reading material). Never a code location."""
    value = settings().get('installation_root') or os.environ.get(ENV_INSTALLATION)
    if not value:
        if strict:
            raise FileNotFoundError(
                f'No installation configured: copy {EXAMPLE.name} to {SETTINGS.name} beside the checkout root '
                f'and set installation_root (or set {ENV_INSTALLATION})')
        return None
    root = Path(value)
    if strict and not root.is_dir():
        raise FileNotFoundError(f'Installation root does not exist: {root}')
    return root


def seed_bank():
    """Seed Bank volume root. home_inspection_storage still checks the vault registration before any bulk write."""
    return Path(settings().get('seed_bank') or os.environ.get(ENV_SEED_BANK) or DEFAULT_SEED_BANK)


def registry(name):
    """A tracked registry file (STUDY-GUIDE-EDITIONS.json, recordings-catalog.json, Library/CURRENT.json ...)."""
    return REGISTRIES / name


def brand(rel=''):
    """Vendored brand assets: tokens/palette.json, tokens/typography.json, tokens/spacing.json, logos/BENBALL_A_CANONICAL.svg."""
    root = ASSETS / 'brand'
    return root / rel if rel else root


def ensure_pymupdf():
    """Import PyMuPDF from the environment, or from the side path named in installation.json.

    requirements.txt lists pymupdf; the side path only bridges an environment that has not installed it yet.
    """
    try:
        import pymupdf  # noqa: F401
        return pymupdf
    except ImportError:
        pass
    extra = settings().get('pymupdf_path') or os.environ.get(ENV_PYMUPDF)
    if extra and extra not in sys.path:
        sys.path.insert(0, extra)
    import pymupdf
    return pymupdf


if __name__ == '__main__':
    print(json.dumps(dict(checkout=str(CHECKOUT), registries=str(REGISTRIES), brand=str(brand()),
                          installation=str(installation(strict=False)), seed_bank=str(seed_bank())), indent=2))
