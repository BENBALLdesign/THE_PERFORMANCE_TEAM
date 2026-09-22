"""Deterministic, read-only lookup and portable exports from existing SG owners.

No media scan, model call, Seed database mutation, or vocabulary admission.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import team_paths

TRAINING = Path('Home Inspection Training')
EDITION = TRAINING / 'Study Guide Editions/SG-009'
CURRENT = TRAINING / 'CURRENT EDITION'
PROPERTY = Path('Property Reviews/505 Walker Ave')
CARDS = EDITION / 'Appendices/Quick Charts - 64 Cards'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write(path, value, lines=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = ('\n'.join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in value)
            if lines else json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))
    path.write_text(text + '\n', encoding='utf-8')


def pointer_part(value):
    return str(value).replace('~', '~0').replace('/', '~1')


def select(value, pointer):
    for item in pointer.lstrip('/').split('/') if pointer else []:
        item = item.replace('~1', '/').replace('~0', '~')
        value = value[int(item)] if isinstance(value, list) else value[item]
    return value


def build(team, output, overlay=None, edition=None, glossary=None, current=None):
    """Overlay is a staged TEAM tree; original structured owners stay authoritative.

    edition / glossary / current select the edition folder, its APP-D file name and the shelf folder.
    Defaults reproduce the SG-009 package; a later edition passes its own (e.g. SG-010, APP-D-v1.3.json).
    """
    team, output = Path(team), Path(output)
    overlay = Path(overlay) if overlay else None
    if output.exists():
        raise ValueError('Use a new output directory; preserve previous packages')
    edition_id = edition or EDITION.name
    EDITION_DIR = TRAINING / 'Study Guide Editions' / edition_id
    CARDS_DIR = EDITION_DIR / 'Appendices/Quick Charts - 64 Cards'
    CURRENT_DIR = TRAINING / (current or CURRENT.name)
    GLOSSARY = EDITION_DIR / 'Appendices' / (glossary or 'APP-D-v1.2.json')
    pins, owners, records, edges = {}, {}, {}, set()

    def resolve(rel):
        p = overlay / rel if overlay else team / rel
        return p if p.exists() else team / rel

    def owner(rel):
        key = Path(rel).as_posix()
        if key not in owners:
            owners[key] = read(resolve(rel))
            pins[key] = digest(resolve(rel))
        return owners[key]

    def add(ident, kind, label, rel, pointer, payload, routes=None):
        if ident in records:
            raise ValueError('Duplicate ID: ' + ident)
        select(owner(rel), pointer)
        records[ident] = dict(id=ident, kind=kind, label=label,
                             source_path=Path(rel).as_posix(), json_pointer=pointer,
                             source_sha256=pins[Path(rel).as_posix()],
                             routes=routes or [], payload=payload)

    def edge(source, relation, target):
        edges.add((source, relation, target))

    nav = owner(EDITION_DIR / 'navigation.json')
    nav_counts = Counter(item['id'] for item in nav['entries'])
    for i, item in enumerate(nav['entries']):
        ident = item['id'] if nav_counts[item['id']] == 1 else 'navigation:' + item['kind'] + ':' + item['id']
        add(ident, item['kind'], item['title'], EDITION_DIR / 'navigation.json',
            f'/entries/{i}', item, item.get('routes'))
    graph = owner(CARDS_DIR / 'concordance.json')
    guide = owner(EDITION_DIR / 'study-guide.json')
    prop = owner(PROPERTY / 'concordance.json')

    def guide_for(fact_id):
        # A fact is pinned to the edition in its own ID; an older property fact checks against that frozen guide.
        prefix = fact_id.split(':')[0]
        return guide if prefix == edition_id else owner(TRAINING / 'Study Guide Editions' / prefix / 'study-guide.json')

    for ident, fact in graph['facts'].items():
        add(ident, 'qualified fact', fact['label'], CARDS_DIR / 'concordance.json',
            '/facts/' + pointer_part(ident), fact,
            [dict(edition=fact.get('edition', edition_id), page=fact['printed_page'])])
    for ident, fact in prop['facts'].items():
        if ident in records:
            old = records[ident]['payload']
            if old['retained'] != fact['statement'] or old['qualification'] != fact['qualification']:
                raise ValueError('Conflicting shared fact: ' + ident)
        else:
            add(ident, 'qualified fact', fact['label'], PROPERTY / 'concordance.json',
                '/facts/' + pointer_part(ident), fact)
    # Prove current fact text and qualifier against the content owner, not old copied hashes.
    for item in list(records.values()):
        if item['kind'] != 'qualified fact':
            continue
        fact = item['payload']
        topic = item['id'].split(':')[1]
        page = next(p for p in guide_for(item['id'])['pages'] if p['id'] == topic)
        row = next(r for r in page['rows'] if r[0] == fact['label'])
        if row[1] != fact.get('retained', fact.get('statement')) or row[2] != fact['qualification']:
            raise ValueError('Fact changed in guide: ' + item['id'])
    for ident, ref in graph['references'].items():
        add(ident, 'source locator', ref.get('label', ident), CARDS_DIR / 'concordance.json',
            '/references/' + pointer_part(ident), ref)
    for ident, topic in graph['l1_topics'].items():
        for target in topic['reference_ids']:
            edge(ident, 'topic-level source; exact claim span not asserted', target)
    cards = owner(CARDS_DIR / 'cards.json')
    for i, card in enumerate(cards['cards']):
        records[card['id']]['card'] = card
        records[card['id']]['card_owner'] = dict(path=CARDS_DIR.as_posix() + '/cards.json', pointer=f'/cards/{i}')
    for card in graph['cards']:
        ident = card['card_id']
        records[ident]['concordance'] = card
        for exp in card['expressions']:
            for target in exp.get('fact_ids', []):
                edge(ident, 'qualified study fact', target)
        for key, relation in [('term_ids', 'definition'), ('footnote_ids', 'numbered note'),
                              ('related_l1_topic_ids', 'long-cut context'),
                              ('related_reference_ids', 'reference context')]:
            for target in card.get(key, []):
                edge(ident, relation, target)
    # All glossary definitions and notes, including those not selected by a card.
    glossary_path = GLOSSARY
    glossary = owner(glossary_path)
    by_label = {r['label']: r for r in records.values() if r['kind'] == 'definition'}
    for i, term in enumerate(glossary['terms']):
        record = by_label[term['term']]
        if record['payload']['meaning'] != term['definition']:
            raise ValueError('Definition mismatch: ' + term['term'])
        record.update(source_path=glossary_path.as_posix(), json_pointer=f'/terms/{i}',
                      source_sha256=pins[glossary_path.as_posix()], definition=term)
    for i, note in enumerate(glossary['notes']):
        record = records['APP-D:' + note[0]]
        if record['payload']['meaning'] != note[2]:
            raise ValueError('Note mismatch: ' + note[0])
        record.update(source_path=glossary_path.as_posix(), json_pointer=f'/notes/{i}',
                      source_sha256=pins[glossary_path.as_posix()])
    for i, card in enumerate(prop['cards']):
        add(card['id'], 'property card', card['title'].replace('\n', ' / '),
            PROPERTY / 'concordance.json', f'/cards/{i}', card,
            [dict(file='Property Review/505 WALKER - FIELD CARDS - 5x7.pdf', page=card['n']),
             dict(file='Property Review/505 WALKER - FIELD CARDS - LETTER PRINT.pdf', page=(card['n']+1)//2)])
        for target in card['fact_ids']:
            edge(card['id'], 'field question context; not a property finding', target)
        for target in card['source_card_ids']:
            edge(card['id'], 'general field card', target)
        for target in card['glossary']:
            edge(card['id'], 'definition', target['id'])
        for target in card['notes']:
            edge(card['id'], 'numbered note', 'APP-D:' + target)
        for target in card['findings']:
            edge(card['id'], 'retained property evidence', 'P505:' + target)
    evidence = owner(PROPERTY / 'property-evidence.json')
    for i, finding in enumerate(evidence['findings']):
        add('P505:' + finding['id'], 'property evidence statement', finding['claim'],
            PROPERTY / 'property-evidence.json', f'/findings/{i}', finding)
    # Package-level property/visual scope, unresolved issues and chronology stay explicit.
    for rel in [PROPERTY / 'property-evidence.json', PROPERTY / 'visual-evidence-manifest.json',
                PROPERTY / 'manifest.json', EDITION_DIR / 'visual-language.json',
                CURRENT_DIR / '_Maintenance/issue.json']:
        owner(rel)
    shelf = owner(CURRENT_DIR / '_Maintenance/manifest.json')
    files = []
    # A staged shelf may not have its Start Here directory yet; the contract records that explicitly.
    directory = [dict(shelf['directory'], kind='directory', title='Start here')] if shelf.get('directory') else []
    for row in shelf['files'] + directory:
        rel = CURRENT_DIR / row['file']
        actual = digest(resolve(rel))
        if actual != row['sha256']:
            raise ValueError('PDF shelf hash mismatch: ' + row['file'])
        pins[rel.as_posix()] = actual
        files.append(dict(id='file:' + row['file'], label=row.get('title', row['file']),
                          path=rel.as_posix(), shelf_file=row['file'], sha256=actual,
                          pages=row.get('pages'), kind=row['kind'], bytes=resolve(rel).stat().st_size))
    files.sort(key=lambda r: r['id'])
    file_names = {r['shelf_file'] for r in files}
    for record in records.values():
        for route in record['routes']:
            if route.get('edition'):
                route.setdefault('file', 'STUDY GUIDE - ' + route['edition'] + '.pdf')
            # Navigation deliberately includes H14's unavailable reference.
            if route.get('file') not in file_names:
                route['availability'] = 'unavailable in current reading set'
            else:
                file = next(f for f in files if f['shelf_file'] == route['file'])
                if file['pages'] and not 1 <= route.get('page', 1) <= file['pages']:
                    raise ValueError('Page outside document: ' + record['id'])
                route['availability'] = 'available'
    for source, relation, target in edges:
        if source not in records or target not in records:
            raise ValueError('Unresolved relationship: ' + str((source, relation, target)))
    issue = shelf['issue_id']
    output.mkdir(parents=True)
    write(output / 'records.jsonl', sorted(records.values(), key=lambda r: r['id']), True)
    write(output / 'relations.jsonl', [dict(source=a, relation=b, target=c) for a,b,c in sorted(edges)], True)
    write(output / 'files.jsonl', files, True)
    terms = [dict(id=r['id'], label=r['label'], namespace='home-inspection',
                  definition=r['definition']['definition'], aliases=[], listed=False,
                  sources=[dict(path=r['source_path'], json_pointer=r['json_pointer'], sha256=r['source_sha256'])],
                  routes=r['routes'], relations=[], usage_kind='term')
             for r in sorted(records.values(), key=lambda r: r['id']) if r['kind']=='definition']
    write(output / 'seed-terms-candidate.json', dict(terms=terms, status='Derived candidate; not imported, reviewed or admitted'))
    resources = [dict(id=f['id'], label=f['label'], path=f['path'], type='reference',
                      kind=f['kind'], state='reference', sha256=f['sha256']) for f in files]
    write(output / 'seed-arrangement-candidate.json', dict(resources=resources, order=[r['id'] for r in resources],
          status='Candidate collection to merge deliberately; never replace the full Seed arrangement'))
    for rel, data in owners.items():
        # Raw source bytes preserve pins; no PDF or bulk recording duplication.
        dest = output / 'owners' / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(resolve(rel).read_bytes())
    contract = dict(schema='home-inspection-library/1', issue=issue, root='THE PERFORMANCE TEAM',
                    authority='Derived index; the named source documents own their content and meanings',
                    source_pins=pins, records=len(records), relations=len(edges), pdfs=len(files),
                    course_progress=dict(percent=98, basis='user reported', source_completeness_verified=False,
                                         full_course_review='pending remaining recordings and incorporation'),
                    coverage='Current published S01-S32 context; S32a bookmark is not a complete lesson; H14 remains unavailable',
                    semantics=['Qualified study fact is not a property finding', 'Topic reference is not an exact claim citation',
                               'Colour means area, hatch means qualification, dots mean source context',
                               'Retain red safety cross and blue Maryland crab separately',
                               'Local RTS links do not execute, register or complete a Step'],
                    seed_integration='Separate files, definitions and relationships. Candidate files only; no database write.',
                    files={p.relative_to(output).as_posix(): digest(p) for p in sorted(output.rglob('*')) if p.is_file()})
    if not directory:
        contract['directory'] = 'absent: shelf manifest has no Start Here row (staged build)'
    if edition_id != EDITION.name:
        contract.update(edition=edition_id, glossary=GLOSSARY.as_posix(), shelf=CURRENT_DIR.as_posix())
    write(output / 'manifest.json', contract)
    return dict(issue=issue, records=len(records), relations=len(edges), pdfs=len(files), definitions=len(terms))


def verify(package, team=None, overlay=None):
    package = Path(package)
    manifest = read(package / 'manifest.json')
    changed = []
    for rel, expected in manifest['files'].items():
        path = package / rel
        if not path.exists() or digest(path) != expected:
            changed.append('package:' + rel)
    if team:
        for rel, expected in manifest['source_pins'].items():
            path = Path(overlay) / rel if overlay else Path(team) / rel
            if not path.exists():
                path = Path(team) / rel
            if not path.exists() or digest(path) != expected:
                changed.append('source:' + rel)
    return dict(status='stale' if changed else ('current' if team else 'snapshot integrity verified; current sources not checked'),
                issue=manifest['issue'], changed=changed)


def lookup(package, query, team=None, limit=5):
    status = verify(package, team)
    if status['changed']:
        return dict(status, results=[])
    rows = [json.loads(line) for line in (Path(package)/'records.jsonl').read_text(encoding='utf8').splitlines()]
    edges = [json.loads(line) for line in (Path(package)/'relations.jsonl').read_text(encoding='utf8').splitlines()]
    tokens = re.findall(r'\w+', query.casefold())
    ranked = []
    for row in rows:
        exact = query.casefold() in (row['id'].casefold(), row['label'].casefold())
        haystack = json.dumps(row, ensure_ascii=False).casefold()
        if exact or (tokens and all(t in haystack for t in tokens)):
            ranked.append((0 if exact else 1, row['id'], row))
    results = []
    by_id = {r['id']: r for r in rows}
    for _, ident, row in sorted(ranked)[:limit]:
        related = [dict(e, record=by_id[e['target']]) for e in edges if e['source']==ident]
        results.append(dict(record=row, related=related))
    return dict(status, query=query, results=results)


def recording(query, team=None, limit=8):
    """Find originals through the mutable archive catalog without editing editions.

    The catalog is a tracked registry of the checkout; team is accepted for call compatibility only.
    """
    catalog_path=team_paths.registry('recordings-catalog.json')
    if not catalog_path.is_file():
        return dict(status='recording catalog unavailable',results=[])
    catalog=read(catalog_path)
    tokens=re.findall(r'\w+',query.casefold())
    ranked=[]
    for row in catalog.get('records',[]):
        exact=query.casefold() in {str(x).casefold() for x in [row['recording_id'],*row.get('source_ids',[]),*row.get('original_names',[])]}
        haystack=json.dumps(row,ensure_ascii=False).casefold()
        if exact or (tokens and all(t in haystack for t in tokens)):
            ranked.append((not exact,row['recording_id'],row))
    return dict(status=catalog['status'],catalog=str(catalog_path),query=query,results=[r for _,_,r in sorted(ranked)[:limit]],note='Storage lookup; incorporation_status remains separate from archive_status. Connect the verified Seed Bank before opening media.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    p = sub.add_parser('build'); p.add_argument('--team', required=True); p.add_argument('--output', required=True); p.add_argument('--overlay')
    p.add_argument('--edition', help='edition folder name under Study Guide Editions (default SG-009)')
    p.add_argument('--glossary', help='APP-D file name inside that edition (default APP-D-v1.2.json)')
    p.add_argument('--current', help='shelf folder name under Home Inspection Training (default CURRENT EDITION)')
    for action in ('verify', 'lookup'):
        p = sub.add_parser(action); p.add_argument('--package', required=True); p.add_argument('--team')
        if action == 'lookup':
            p.add_argument('query'); p.add_argument('--limit', type=int, default=5)
    p=sub.add_parser('recording');p.add_argument('query');p.add_argument('--team',default=None);p.add_argument('--limit',type=int,default=8)
    args = vars(parser.parse_args()); action = args.pop('action')
    result = globals()[action](**args)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 2 if result.get('status') == 'stale' else 0


if __name__ == '__main__':
    sys.exit(main())
