"""Resolve home-inspection backup/evidence locations in the established Seed Bank.

Dropbox contains published reading material and small location records. Missing
or wrong bank volumes raise errors; bulk writes never fall back into Dropbox.
"""
from pathlib import Path
import argparse
import json

import team_paths

BANK = team_paths.seed_bank()
VAULT_ID = '435ce95c-afa2-475a-b8d8-afc8db7656fe'
POINTER = 'SEED BANK LOCATION.json'


def bank_root():
    registration = BANK / '_REGISTRY/vault.json'
    if not registration.is_file():
        raise FileNotFoundError('Seed Bank is unavailable; reconnect it before writing bulk files')
    value = json.loads(registration.read_text(encoding='utf-8-sig'))
    if value.get('vault_id') != VAULT_ID:
        raise ValueError('Wrong Seed Bank volume; refusing a fallback location')
    return BANK.resolve()


def domain_root():
    return bank_root() / 'DATA_ARCHIVE/HOME_INSPECTION'


def backup_root():
    return domain_root() / 'Backups/Current Set History'


def work_root(label):
    if not label or Path(label).name != label or label in ('.', '..') or '/' in label or '\\' in label:
        raise ValueError('Use one directory name for a work area')
    return domain_root() / 'Working Evidence' / label


def resolve(path):
    """Follow the nearest JSON location pointer; no NTFS junction or cloud traversal."""
    path = Path(path).resolve()
    if not path.exists():
        recording = resolve_recording_alias(path)
        if recording is not None:
            return recording
    for ancestor in [path, *path.parents]:
        pointer = ancestor / POINTER
        if pointer.is_file():
            data = json.loads(pointer.read_text(encoding='utf-8-sig'))
            if data.get('vault_id') != VAULT_ID or Path(data['original_root']).resolve() != ancestor.resolve():
                raise ValueError('Location pointer ownership does not match: ' + str(pointer))
            root = bank_root()
            destination = Path(data['bank_root']).resolve()
            if not destination.is_relative_to(root) or destination == root:
                raise ValueError('Location pointer escapes the Seed Bank')
            target = (destination / path.relative_to(ancestor)).resolve()
            if not target.is_relative_to(destination):
                raise ValueError('Resolved evidence path escapes its bank location')
            if not target.exists():
                raise FileNotFoundError(target)
            return target
    if not path.exists():
        raise FileNotFoundError(path)
    return path


def resolve_recording_alias(value):
    """Resolve a content ID or old absolute recording path without rewriting history.

    The small Dropbox catalog remains available while the bank is disconnected;
    the bank-volume check still fails closed before returning a bulk-file path.
    """
    mirror = team_paths.registry('recordings-catalog.json')
    if not mirror.is_file():
        return None
    data = json.loads(mirror.read_text(encoding='utf-8-sig'))
    if data.get('vault_id') != VAULT_ID:
        raise ValueError('Recording catalog belongs to another vault')
    needle = str(value).replace('\\', '/').casefold()
    matches = []
    for record in data.get('records', []):
        keys = [record['recording_id'], *record.get('source_ids', []), record['canonical_path']]
        keys.extend(alias['path'] for alias in record.get('aliases', []))
        if needle in {key.replace('\\', '/').casefold() for key in keys}:
            matches.append(record)
    if not matches:
        return None
    if len(matches) != 1:
        raise ValueError('Ambiguous recording catalog alias: ' + str(value))
    root = bank_root() / 'RECORDINGS'
    target = (root / matches[0]['bank_relative_path']).resolve()
    if target == root or not target.is_relative_to(root):
        raise ValueError('Recording catalog destination escapes the recordings archive')
    if not target.is_file():
        raise FileNotFoundError(target)
    return target


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', nargs='?')
    parser.add_argument('--backup-root', action='store_true')
    parser.add_argument('--recording', help='Recording content ID, study source ID, or old absolute path')
    args = parser.parse_args()
    print(resolve_recording_alias(args.recording) if args.recording else backup_root() if args.backup_root else resolve(args.path))
