"""505 Walker Ave / SG-010 staged update (handoff item 8).

Retains the P1 18-page combined packet body, frame and evidence. Changes:
  - printed "SG-009" references -> "SG-010" (width-neutral digit swaps, same font/position);
  - two new P1-framed pages after the findings: SG-010 routes, and conditional course prompts;
  - footers renumbered 1..20 with the shared P1 frame function.
New course knowledge enters only as PROMPTS / cross-references. No observed condition is added.
Stage only: writes to the Seed Bank work folder; never publishes to Property Reviews or CURRENT.
"""
from pathlib import Path
import sys, json, hashlib, shutil, re, html, datetime

CODE = Path(__file__).resolve().parents[2]   # THE_PERFORMANCE_TEAM checkout root (__file__ is in production/sg010: parents[0]=sg010, [1]=production, [2]=root)
sys.path[:0] = [str(CODE/'tools'), str(CODE/'builder/property-505-r2')]
import team_paths
team_paths.ensure_pymupdf()
import home_inspection_storage as storage
import pymupdf as fitz
from home_inspection_page_frame import frame, print_palette
import atlas_brand
from maryland_marker import crab
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle, Flowable

PROP = team_paths.installation()/'Property Reviews/505 Walker Ave'
SG = storage.work_root('sg010-20260921')
OUTSRC = SG/'output'
WORK = SG/'walker-sg010'
NAME = '505 WALKER - COMBINED PROPERTY REVIEW.pdf'
BASE_SHA = '612e244f5ce0136907c095c4cfd73175d69b5177a9eac6449b23fad70fb6eedd'
NAVY = print_palette()['navy']; TEAL = '#007A9E'; RED = '#B12C3B'; GRAY = '#555860'; RULE = '#CBD4D7'
NEW_AT = 4          # 0-based insertion index: new pages become 5 and 6
NEW_PAGES = 2
SECTION_NEW = 'SG-010 routes'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p, d):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
def slug(s): return re.sub('[^a-z0-9]+', '-', s.lower()).strip('-')

# Retained desktop evidence. Windows stay windows; nothing here is a completion date.
EVIDENCE = [
    ('RECORD', 'City YEAR_BUILD 1895', 'F01 / tax-derived field; not original documentation'),
    ('RECORD', 'Addition permit COM2017-15221 issued 5 March 2018', 'F02 / issuance, not completion'),
    ('IMAGE WINDOW', 'Overhead (aerial) roof change bracketed 2017-2018', 'Visual R2 / capture dates bound the change'),
    ('IMAGE WINDOW', 'Facade dormer absent 2013, visible 2019', 'F03 / dormer not named in the permit'),
    ('UNVERIFIED', 'Approved plans, final inspections, completion', 'F04 / unresolved; no completion date established'),
]

# Conditional review prompts. basis = retained finding IDs only. No prompt asserts a condition.
PROMPTS = [
    dict(card='P505-01', flags=['md'], session='S33', charts=['life_safety'], l1=['interior_life_safety'],
         basis=['F01', 'F02'], trigger='1895 core year (record); 2018 work records.',
         prompt='Record smoke and CO alarms as two functions: location, type, power, date. Maryland existing-occupancy '
                'smoke-alarm duties do not follow the 1895 core date, and later work can change applicability. Ask; do not assume.',
         appc=['smoke', 'carbon monoxide']),
    dict(card='P505-03', flags=[], session='S39', charts=['interior_routes'], l1=['floor_finishes'],
         basis=['F02', 'F04'], trigger='One-story addition over an existing basement (permit).',
         prompt='Where old and new floors meet, name each finish layer; note soft, lifted or stained areas and what '
                'coverings hide. Leave suspect older resilient tile undisturbed.',
         appc=['floor']),
    dict(card='P505-04', flags=[], session='S34', charts=['insulation'], l1=['air_vapor_thermal', 'interior_moisture'],
         basis=['F06'], trigger='Several roof-to-wall interfaces (Sept 2022 image).',
         prompt='Below each junction, compare ceiling, sheathing and exhaust paths. Stain distribution suggests '
                'questions; it does not prove cause or identify mold.',
         appc=['stain', 'moisture']),
    dict(card='P505-05', flags=['safety'], session='S34', charts=['insulation'], l1=['insulation_materials', 'ventilation_exhaust'],
         basis=['F03', 'F04'], trigger='Front dormer inside the 2013-2019 image window.',
         prompt='If the attic is safely accessible at the dormer: identify the thermal boundary, insulation product and '
                'continuity, air paths and baffles. Leave suspect vermiculite undisturbed.',
         appc=['insulation', 'vermiculite']),
    dict(card='P505-06', flags=['safety'], session='S39', charts=['interior_routes'], l1=['fireplace_masonry', 'fireplace_factory_gas'],
         basis=['F06'], trigger='Front brick chimney visible; interior route unseen.',
         prompt='Establish what the flue serves. Masonry fireplace: hearth extension, firebox, damper, visible flue. '
                'Gas logs or insert: read the label; damper held open for gas logs. Do not light fires.',
         appc=['fireplace', 'hearth']),
    dict(card='P505-09', flags=['safety'], session='S38', charts=['hydronic_electric'], l1=['hydronic_systems', 'steam_systems'],
         basis=['F01', 'F05'], trigger='1895 core; 2018 fuel-equipment records.',
         prompt='Ask whether hot-water or steam heat was ever present or remains. If a boiler exists: expansion, relief, '
                'low-water cutoff and condensate return are separate checks; record pressure as read.',
         appc=['boiler', 'steam']),
    dict(card='P505-09', flags=['safety'], session='S38', charts=['cooling', 'heatpumps'], l1=['cooling_types', 'heatpump_inspection'],
         basis=['F05'], trigger='2018 record: 24,000 BTU AC / heat pump, 800 CFM.',
         prompt='Sort cooling by heat path; operate by normal controls only; record mode, conditions and condensate '
                'route. A temperature split alone does not diagnose charge.',
         appc=['cooling', 'condensate']),
    dict(card='P505-09', flags=['safety'], session='S33', charts=['appliances'], l1=['kitchen_appliances', 'kitchen_waste', 'bath_laundry'],
         basis=['F05'], trigger='2018 records: seven fixtures and fuel equipment.',
         prompt='Operate the kitchen, bath and laundry appliances in scope: dryer duct and termination, dishwasher '
                'loop / air gap, range-restraint evidence; return below fixtures. No self-clean or improvised tip test.',
         appc=['dryer', 'dishwasher', 'range']),
    dict(card='P505-07', flags=['safety'], session='S39', charts=['interior_routes'], l1=['safety_glazing', 'interior_doors'],
         basis=['F06'], trigger='Entry within changed massing (image).',
         prompt='Any glazing in or beside doors, stairs or tubs: hazardous location first, then the permanent mark; no '
                'mark = unverified. Operate each accessible interior door; a key needed to exit is a safety concern.',
         appc=['glazing', 'door']),
    dict(card='P505-11', flags=['safety'], session='S39', charts=['interior_routes'], l1=['egress_openings', 'interior_stairs'],
         basis=['F03'], trigger='Dormer level (image window); room use unknown.',
         prompt='If the dormer level holds a sleeping room, operate its escape opening fully. Stairs to it: uniform '
                'risers, graspable continuous rail, guard at the open side, headroom.',
         appc=['escape', 'stair']),
]

class Flags(Flowable):
    def __init__(self, flags): super().__init__(); self.flags = flags; self.width = 22; self.height = 14
    def wrap(self, aw, ah): return self.width, self.height
    def draw(self):
        c = self.canv; x = 7
        for f in self.flags:
            if f == 'safety':
                s = 11; c.setFillColor(HexColor(RED))
                c.rect(x-s/6, 7-s/2, s/3, s, fill=1, stroke=0); c.rect(x-s/2, 7-s/6, s, s/3, fill=1, stroke=0)
            elif f == 'md':
                crab(c, x, 7, 12)
            x += 14

def st(size=9, bold=False, color=NAVY, leading=None):
    return ParagraphStyle('s', fontName='Helvetica-Bold' if bold else 'Helvetica', fontSize=size,
                          leading=leading or size*1.2, textColor=HexColor(color))

def table(c, rows, widths, y, head=True, pad=3):
    t = Table(rows, colWidths=widths)
    style = [('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), pad),
             ('RIGHTPADDING', (0, 0), (-1, -1), pad), ('TOPPADDING', (0, 0), (-1, -1), 3.5),
             ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
             ('LINEBELOW', (0, 0), (-1, -1), .6, HexColor(RULE))]
    if head: style.append(('LINEBELOW', (0, 0), (-1, 0), 1, HexColor(NAVY)))
    t.setStyle(TableStyle(style))
    _, h = t.wrapOn(c, 540, 2000); t.drawOn(c, 36, y-h); return y-h

def new_pages(data, total):
    """Two portrait bodies drawn by ReportLab; P1 frame overlaid by the shared frame function."""
    from io import BytesIO
    buf = BytesIO(); c = Canvas(buf, pagesize=(612, 792), invariant=1)
    # Page A: routes
    y = 660
    c.setFillColor(HexColor(NAVY)); c.setFont('Helvetica-Bold', 10)
    c.drawString(36, y, 'RETAINED DESKTOP EVIDENCE / dated windows, not completion dates'); y -= 6
    rows = [[Paragraph(k, st(8, True, TEAL)), Paragraph(v, st(9, True)), Paragraph(n, st(8.5, color=GRAY))] for k, v, n in EVIDENCE]
    y = table(c, rows, [78, 232, 230], y, head=False) - 14
    c.setFillColor(HexColor(NAVY)); c.setFont('Helvetica-Bold', 10)
    c.drawString(36, y, 'CARD ROUTES / SG-009 references resolved to SG-010'); y -= 6
    rows = [[Paragraph(h, st(8, True)) for h in ['CARD', 'SG-010 COMPACT CHART / PAGE', 'L1 PAGES', 'CHANGE FROM SG-009']]]
    for cd in data['cards']:
        charts = ' / '.join(f"{r['chart_no']} p{r['sg010_page']}" for r in cd['topic_routes'])
        parts = {x.strip() for r in cd['topic_routes'] for x in str(r['l1_pages']).split(',') if x.strip()}
        l1 = ', '.join(sorted(parts, key=lambda x: int(x.split('-')[0])))
        moved = [f"{r['chart_no']} p{r['sg009_page']}->{r['sg010_page']}" for r in cd['topic_routes'] if r['sg009_page'] != r['sg010_page']]
        n = len([p for p in data['prompts'] if p['card'] == cd['card_id']])
        change = 'Footer SG-010. ' + ('Moved: ' + ', '.join(moved) + '. ' if moved else 'Pages unchanged. ') + \
                 (f'{n} new prompt{"s" if n > 1 else ""} (p. {NEW_AT+2}).' if n else 'No new prompt.')
        rows.append([Paragraph(f"<b>{cd['card_id']}</b><br/>{html.escape(cd['title'])}", st(8.3, leading=9.6)),
                     Paragraph(charts, st(8.5)), Paragraph(l1, st(8.5)), Paragraph(change, st(8.3, color=GRAY))])
    y = table(c, rows, [120, 158, 82, 180], y) - 12
    note = ('Fact IDs alias one-to-one, SG-009:&lt;chart&gt;:&lt;row&gt; -> SG-010:&lt;chart&gt;:&lt;row&gt;; '
            f"{data['summary']['facts_aliased']} facts, {data['summary']['facts_statement_changed']} with revised wording. "
            'QC card and note numbers printed on the cards are unchanged. Full routes: concordance-SG010-crosswalk.json.')
    Paragraph(note, st(8.5, color=GRAY)).wrapOn(c, 540, 100)
    p = Paragraph(note, st(8.5, color=GRAY)); _, h = p.wrap(540, 100); p.drawOn(c, 36, y-h); assert y-h > 46, y-h
    c.showPage()
    # Page B: prompts
    y = 660
    rows = [[Paragraph(h, st(8, True)) for h in ['', 'CARD', 'RETAINED EVIDENCE', 'PROMPT / IF PRESENT, IF ACCESSIBLE', 'SG-010 ROUTE']]]
    for pr in data['prompts']:
        route = ' / '.join(f"{r['chart_no']} p{r['page']}" for r in pr['compact']) + '<br/>L1 ' + ', '.join(dict.fromkeys(str(x['page']) for x in pr['l1']))
        rows.append([Flags(pr['flags']), Paragraph(f"<b>{pr['card']}</b><br/>{pr['session']}", st(8.3, leading=9.6)),
                     Paragraph(pr['trigger'] + '<br/>' + ' '.join(pr['basis']), st(8.3, color=GRAY, leading=9.8)),
                     Paragraph(pr['prompt'], st(8.6, leading=10.3)), Paragraph(route, st(8.3, leading=9.8))])
    y = table(c, rows, [26, 50, 112, 272, 80], y) - 14
    x0 = 44
    s = 11; c.setFillColor(HexColor(RED)); c.rect(x0-s/6, y-4-s/2, s/3, s, fill=1, stroke=0); c.rect(x0-s/2, y-4-s/6, s, s/3, fill=1, stroke=0)
    p = Paragraph('Red cross: safety attention. It does not mean a hazard was confirmed at this property.', st(9)); _, h = p.wrap(510, 40); p.drawOn(c, 63, y-h); y -= h+8
    crab(c, x0, y-5, 13)
    p = Paragraph('Blue crab / MD: Maryland-specific detail. It is not a compliance verdict.', st(9)); _, h = p.wrap(510, 40); p.drawOn(c, 63, y-h); y -= h+10
    p = Paragraph('Course content from S33, S34, S38 and S39 informs these questions only. Property evidence, findings F01-F07 '
                  'and the dated windows are unchanged. Fireplace prompts rest on S39 screens 1-13; screens 14-15 and the Unit 6 '
                  'exam are missing from the recording (N14). APP-C v1.9 mention links are in the crosswalk JSON.', st(9, color=GRAY, leading=11.5))
    _, h = p.wrap(540, 80); p.drawOn(c, 36, y-h); assert y-h > 46, y-h
    c.showPage(); c.save()
    body = fitz.open(stream=buf.getvalue(), filetype='pdf')
    titles = [('SG-010 routes for the field cards',
               'The 12 cards resolved to SG-010 compact charts and L1 pages. Evidence and findings unchanged.'),
              ('New course prompts, conditional',
               'S33, S34, S38 and S39 add questions to carry into the visit. None records a condition observed at 505 Walker Ave.')]
    for i, pg in enumerate(body):
        ov = fitz.open(stream=frame(612, 792, address='505 Walker Ave', section=SECTION_NEW, page=NEW_AT+1+i, total=total,
                                    title=titles[i][0], subtitle=html.escape(titles[i][1]), logo=atlas_brand.mark, crab=crab), filetype='pdf')
        pg.show_pdf_page(pg.rect, ov, 0)
    return body

def crosswalk():
    g = read(OUTSRC/'study-guide.json'); P = {p['id']: p for p in g['pages']}
    pi = read(OUTSRC/'page-index.json'); pl = read(OUTSRC/'page-index-L1.json')
    old = read(PROP/'concordance-SG009-crosswalk.json'); conc = read(PROP/'concordance.json')
    appc = read(OUTSRC/'Appendices/APP-C-v1.9.json')['items']
    ev = read(PROP/'property-evidence.json')
    titles = {c['id']: c['title'].replace('\n', ' ').capitalize() for c in conc['cards']}
    oldfacts = old.get('facts', {})
    if isinstance(oldfacts, list): oldfacts = {f['current_id']: f for f in oldfacts}
    rowsby = {f'{k}:{slug(r[0])}': r for k, p in P.items() for r in p['rows']}
    cards = []; aliased = changed = unknown = 0; aliases = {}
    for cd in old['cards']:
        routes = []
        for t, oldpage in cd['current_topic_pages'].items():
            p = P[t]; assert pi[t] == p['printed_page']
            routes.append(dict(topic=t, chart_no=p['title'][:2], title=p['title'][2:].strip(), sg009_page=oldpage,
                               sg010_page=p['printed_page'], l1_pages=p['long_pages'], source_sessions=p['source_sessions']))
        facts = []
        for fid in cd['current_fact_ids']:
            key = fid.split(':', 1)[1]; r = rowsby[key]; new = 'SG-010:'+key
            prev = oldfacts.get(fid, {}); stmt_changed = (prev.get('statement') != r[1] or prev.get('qualification') != r[2]) if prev else None
            aliased += 1; changed += bool(stmt_changed); unknown += stmt_changed is None; aliases[fid] = new
            facts.append(dict(previous=fid, current=new, statement_changed=stmt_changed))
        cards.append(dict(card_id=cd['card_id'], title=titles.get(cd['card_id'], cd['card_id']), topic_routes=routes,
                          facts=facts, terms=cd['terms'], notes=cd['notes'], standard_card_ids=cd['standard_card_ids']))
    prompts = []
    for n, pr in enumerate(PROMPTS, 1):
        assert set(pr['basis']) <= {f['id'] for f in ev['findings']}
        mentions = [m['id'] for m in appc if any(k in (m['mention']+' '+m.get('note', '')).lower() for k in pr['appc'])][:4]
        prompts.append(dict(id=f"{pr['card']}-SG010-{n:02}", card=pr['card'], flags=pr['flags'], session=pr['session'],
                            trigger=pr['trigger'], basis=pr['basis'], prompt=pr['prompt'],
                            compact=[dict(topic=t, chart_no=P[t]['title'][:2], page=P[t]['printed_page']) for t in pr['charts']],
                            l1=[dict(topic=t, page=pl[t]) for t in pr['l1']], app_c_mentions=mentions,
                            relationship='review prompt from SG-010 course content; conditional; not an observed property condition'))
    return dict(name='Field Card Concordance / SG-010 crosswalk', property_review='PR-505-WALKER-S31', edition='SG-010',
                previous_edition='SG-009', prior_crosswalk_sha256=sha(PROP/'concordance-SG009-crosswalk.json'),
                guide_sha256=sha(OUTSRC/'study-guide.json'), l1_sha256=sha(OUTSRC/'study-guide-L1.json'),
                page_index_sha256=sha(OUTSRC/'page-index.json'), page_index_l1_sha256=sha(OUTSRC/'page-index-L1.json'),
                meaning='SG-009 routes and fact IDs mapped to SG-010; new course prompts added separately. Property evidence, findings and Visual R2 unchanged.',
                evidence_windows=[dict(kind=k, statement=v, qualification=q) for k, v, q in EVIDENCE],
                findings=ev['findings'], new_observed_conditions=0, fact_aliases=aliases,
                summary=dict(cards=len(cards), facts_aliased=aliased, facts_statement_changed=changed, facts_not_in_prior_crosswalk=unknown, prompts=len(prompts)),
                cards=cards, prompts=prompts)

def swap(page, old, new):
    """Replace a printed token in place: same font, size, colour and origin (digit swaps are width-neutral)."""
    done = []
    for b in page.get_text('dict')['blocks']:
        for l in b.get('lines', []):
            for s in l['spans']:
                i = s['text'].find(old)
                while i >= 0:
                    # Span char boxes via rawdict are costlier; use search on the span line instead.
                    done.append((s, i)); i = s['text'].find(old, i+1)
    rects = page.search_for(old)
    assert len(rects) == len(done), (old, len(rects), len(done))
    for r, (s, _) in zip(sorted(rects, key=lambda r: (r.y0, r.x0)), sorted(done, key=lambda d: (d[0]['bbox'][1], d[0]['bbox'][0]))):
        rr = fitz.Rect(r.x0+.4, r.y0+1, r.x1-.4, r.y1-1)
        page.add_redact_annot(rr, fill=None)
        done_font = 'hebo' if 'Bold' in s['font'] else 'helv'
        yield rr, dict(size=s['size'], color=s['color'], font=done_font, origin=(r.x0, s['origin'][1]), new=new, old=old)

def build():
    base = PROP/NAME; assert sha(base) == BASE_SHA
    for d in ['baseline', 'output', 'qa']: (WORK/d).mkdir(parents=True, exist_ok=True)
    for n in [NAME, 'combined-packet.json', 'concordance-SG009-crosswalk.json', 'property-evidence.json']:
        shutil.copy2(PROP/n, WORK/'baseline'/n)
    data = crosswalk(); save(WORK/'output/concordance-SG010-crosswalk.json', data)
    total = 18 + NEW_PAGES
    doc = fitz.open(base); ref = fitz.open(base)
    sections = ['Findings']*4 + ['Dated imagery']*7 + ['Property outline'] + ['Field cards']*6
    edits = []
    for i, pg in enumerate(doc):
        pending = []
        for old, new in [('SG-009 through S31', 'SG-010 through S39'), ('SG-009 /', 'SG-010 /')]:
            pending += list(swap(pg, old, new))
        h, w = pg.rect.height, pg.rect.width
        pg.add_redact_annot(fitz.Rect(0, h-38, w, h), fill=(1, 1, 1))
        pg.apply_redactions(images=0, graphics=1, text=0)
        for rr, t in pending:
            pg.insert_text(t['origin'], t['new'], fontname=t['font'], fontsize=t['size'],
                           color=tuple(((t['color'] >> k) & 255)/255 for k in (16, 8, 0)))
            edits.append(dict(old_page=i+1, new_page=i+1+(NEW_PAGES if i >= NEW_AT else 0), old=t['old'], new=t['new'],
                              rect=[round(v, 2) for v in rr]))
        newno = i+1+(NEW_PAGES if i >= NEW_AT else 0)
        ov = fitz.open(stream=frame(w, h, address='505 Walker Ave', section=sections[i], page=newno, total=total,
                                    title='x' if i < 12 else None, subtitle='x' if i < 12 else None,
                                    logo=atlas_brand.mark, crab=crab, cards=i >= 12), filetype='pdf')
        foot = fitz.Rect(0, h-38, w, h); pg.show_pdf_page(foot, ov, 0, clip=foot)
    left = ''.join(p.get_text() for p in doc)
    kept = [dict(page=k+1+(NEW_PAGES if k >= NEW_AT else 0), text=m) for k, p in enumerate(doc)
            for m in re.findall(r'.{0,60}SG-009.{0,20}', p.get_text())]
    # Only the Visual R2 historical statement may keep SG-009 (it records what R2 linked to at the time).
    assert len(kept) == 1 and 'existing property cards and SG-009' in kept[0]['text'] and 5 <= kept[0]['page'] - NEW_PAGES <= 11, kept
    doc.insert_pdf(new_pages(data, total), start_at=NEW_AT)
    doc.set_page_labels([dict(startpage=0, prefix='', style='D', firstpagenum=1)])
    doc.set_toc([[1, 'Findings and timeline', 1], [1, 'SG-010 routes and review prompts', 5], [1, 'Dated images and evidence', 7],
                 [1, 'Property outline', 14], [1, 'Field cards - Letter sheets', 15]])
    m = doc.metadata
    m['subject'] = ('Current reviewed findings, imagery, outline and field cards. STAGED SG-010 update: routes and conditional '
                    'course prompts (S33/S34/S38/S39); no new property evidence or findings. Frame P1.')
    doc.set_metadata(m)
    out = WORK/'output'/NAME
    doc.save(out, garbage=4, deflate=True, no_new_id=True)
    # Body verification: every retained page vs baseline, outside footer and swapped tokens.
    import numpy as np
    new = fitz.open(out); checks = []
    for i in range(18):
        j = i+(NEW_PAGES if i >= NEW_AT else 0)
        a = ref[i].get_pixmap(dpi=72); b = new[j].get_pixmap(dpi=72)
        A = np.frombuffer(a.samples, np.uint8).reshape(a.h, a.w, a.n); B = np.frombuffer(b.samples, np.uint8).reshape(b.h, b.w, b.n)
        mask = np.ones(A.shape[:2], bool); mask[a.h-39:, :] = False
        for e in edits:
            if e['old_page'] == i+1:
                x0, y0, x1, y1 = e['rect']; mask[max(0, int(y0)-3):int(y1)+4, max(0, int(x0)-3):int(x1)+4] = False
        diff = int((np.abs(A.astype(int)-B.astype(int)).max(axis=2)[mask] > 24).sum())
        checks.append(dict(old_page=i+1, new_page=j+1, body_pixels_changed_72dpi=diff))
    assert all(c['body_pixels_changed_72dpi'] == 0 for c in checks), checks
    manifest = dict(schema='home-inspection-property-sg010-change/1', property='505 Walker Ave', status='STAGED - not published',
                    built_at=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
                    baseline=dict(pdf=str(base), pages=18, sha256=BASE_SHA, frame='P1'),
                    staged=dict(pdf=str(out), pages=len(new), sha256=sha(out), frame='P1 (shared frame function, unchanged)'),
                    page_map=[dict(old=c['old_page'], new=c['new_page']) for c in checks],
                    inserted_pages=[dict(page=5, title='SG-010 routes for the field cards'), dict(page=6, title='New course prompts, conditional')],
                    text_edits=edits, footers='All footers regenerated by home_inspection_page_frame.frame with n / 20',
                    body_verification=checks, crosswalk=str(WORK/'output/concordance-SG010-crosswalk.json'),
                    crosswalk_sha256=sha(WORK/'output/concordance-SG010-crosswalk.json'),
                    unchanged=['Findings F01-F07 and property-evidence.json', 'Pages 1-4 bodies except the one SG line on p4',
                               'Dated imagery 7 pages and vector outline', 'Card bodies, diagrams, QC/N numbers, crosses and crabs',
                               'Standalone 5x7, Letter, findings, image and outline PDFs in Property Reviews'],
                    new_observed_conditions=0, prompts=len(data['prompts']),
                    sg009_text_retained=[dict(k, reason='Visual R2 historical statement of its linkage at issue; evidence page body retained') for k in kept])
    save(WORK/'output/change-manifest.json', manifest)
    print(json.dumps(dict(pdf=str(out), pages=len(new), sha=manifest['staged']['sha256'], edits=len(edits), summary=data['summary'])))

if __name__ == '__main__': build()
