"""Reproducible county housing-stock comparison and professional study routing."""
from prepare import read,save,HERE,OUT
from reportlab.graphics.shapes import Drawing,Rect,String
from reportlab.graphics import renderSVG
from reportlab.lib.colors import HexColor,white
import csv,html
LABELS=['Before 1940','1940-1959','1960-1979','1980-1999','2000-2009','2010-2019','2020 onward']
BINS=[(9,),(7,8),(5,6),(3,4),(2,),(1,),(0,)]
COLORS=['#193b42','#30606b','#517b80','#769c97','#a3b9a1','#c5ceaf','#e3e6cc']
PRIORITIES=[
 ['Baltimore City','68% pre-1960; 50% attached single units','Older masonry, roof/parapet drainage, concealed interfaces, accumulated alterations and legacy services. Trace water and load paths across changed assemblies.','What is original, what changed, and what evidence supports that sequence?'],
 ['Baltimore County','29% built 1960-1979; 24% built 1940-1959','Material identification, branch wiring, supply/DWV transitions, equipment replacement and envelope repairs. Keep the actual installation generation separate from house age.','Do the conductor, piping and equipment observations fit the claimed renovation history?'],
 ['Anne Arundel','29% built 1980-1999; 26% built 1960-1979','Mixed original/replacement systems, roof-wall/deck interfaces and water management. Establish public/private services and site exposure for the address.','Which interface or replacement most changes the inspection route?'],
 ['Carroll','32% built 1980-1999; 28% built 1960-1979; 81% detached','Envelope/accessory structures and altered systems; establish actual service type before adding well/septic modules. Older pockets remain significant.','What does the actual site require beyond the core visit scope?'],
 ['Harford','34% built 1980-1999; 25% built 1960-1979','Original-versus-replacement components, concealed water paths, decks and equipment installation. Date the altered system before applying a rule.','Is this deterioration, an installation defect, or an unresolved concealed condition?'],
 ['Howard','41% built 1980-1999; 31% built 2000-2019','Repair interfaces, original/replacement equipment, controls, drainage and installation records. Recent local code changes matter for newer work.','Which record or observed detail would resolve the installation question?']]

def dataset():
 d=read(HERE/'housing-data.json')
 for c in d['counties']:
  assert sum(a['estimate'] for a in c['ages'])==c['total']['estimate']
  c['groups']=[dict(label=label,estimate=sum(c['ages'][i]['estimate'] for i in ix),percent=100*sum(c['ages'][i]['estimate'] for i in ix)/c['total']['estimate']) for label,ix in zip(LABELS,BINS)]
 d.update(grouping=LABELS,method='Sum published count estimates within each band, then divide by the jurisdiction total. Percentages are rounded for display; source-row margins of error are retained. No interpolation at 2015 or 2024.',inference='Study priorities are editorial judgments based on housing age and form, not measured defect rates or the distribution of future inspection jobs.')
 return d

def chart():
 d=dataset();g=Drawing(524,244)
 for j,c in enumerate(d['counties']):
  y=212-j*27;name=c['name'].replace(' County','').replace('city','City');g.add(String(0,y+7,name,fontName='Arial',fontSize=8.8));x=105
  for k,a in enumerate(c['groups']):
   w=a['percent']*4.16;g.add(Rect(x,y,w,21,fillColor=HexColor(COLORS[k]),strokeColor=white,strokeWidth=.5))
   if a['percent']>=7:g.add(String(x+w/2,y+7,str(round(a['percent']))+'%',textAnchor='middle',fontName='Arial',fontSize=8,fillColor=white if k<3 else HexColor('#193b42')))
   x+=w
 for k,label in enumerate(LABELS):
  x=k%4*131;y=30-(k//4)*18;g.add(Rect(x,y,10,10,fillColor=HexColor(COLORS[k]),strokeWidth=0));g.add(String(x+14,y+2,label,fontName='Arial',fontSize=8.1))
 return g

def table_rows():
 return [[c['name'].replace(' County','').replace('city','City')]+[str(round(a['percent']))+'%' for a in c['groups']] for c in dataset()['counties']]

NOTE='Source: 2024 ACS 1-year housing estimates (DP04), Maryland Department of Planning; six county/city profiles. Universe: all housing units, occupied and vacant, including multifamily units. Percentages are rounded and estimates carry sampling error; source values and margins are retained in housing-data.json/CSV. These are not counts of buildings, defect rates or predicted inspection bookings. The 2020-onward estimate covers the 2024 survey vintage, not construction through 2026.'

def publish_data(b):
 d=dataset();save(OUT/'housing-data.json',d)
 with (OUT/'housing-data.csv').open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.writer(f);w.writerow(['FIPS','Jurisdiction','Year-built category','Estimated housing units','Estimate margin of error','Published percent','Percent margin of error','Source URL'])
  for c in d['counties']:
   for a in c['ages']:w.writerow([c['fips'],c['name'],a['label'],a['estimate'],a['moe'],a['percent'],a['percent_moe'],c['source_url']])
 renderSVG.drawToFile(chart(),str(OUT/'figures/housing-age-by-county.svg'))
 body='<p>'+b.e(NOTE)+'</p><img style="width:100%" src="figures/housing-age-by-county.svg" alt="Housing age distribution by jurisdiction">'+b.html_table(dict(headers=['Jurisdiction']+LABELS,rows=table_rows()))
 body+='<h2>Use the mix to select study topics</h2><p>The routes below are editorial inferences. Actual construction, alterations, services and observed condition set the visit priorities.</p>'+b.html_table(dict(headers=['Jurisdiction','Housing-stock cue','Study emphasis','Colleague discussion'],rows=PRIORITIES))
 body+='<h2>Official data and address-level checks</h2><ul>'+''.join('<li><a href="'+c['source_url']+'">'+b.e(c['name'])+' - 2024 ACS profile</a></li>' for c in d['counties'])+'</ul><p><a href="housing-data.csv">Source values and margins (CSV)</a> | <a href="https://dat.maryland.gov/realproperty/Pages/Finding-Your-Property-Information-Online.aspx">Maryland SDAT property-record lookup</a></p><p>County averages can conceal neighborhood differences. Confirm the property record, original year, permit/alteration history and visible assemblies. A ZIP code is not a code jurisdiction.</p>'
 (OUT/'regional-field-focus.html').write_text(b.doc_html('SG-010 - Regional housing and field focus',body),encoding='utf-8')

def frontmatter(b):
 if getattr(b,'design_installed',False):
  from design_language import housing_chart,stock_routes
  return [b.heading('Where the housing stock changes','regional_focus'),b.para('Six jurisdictions. Seven age bands. Use the mix to choose what to review.'),housing_chart(),b.para(NOTE,b.SMALL),b.PageBreak(),b.heading('From local stock to field questions','field_routes'),b.para('Statistics establish the context. The dashed connections below are study priorities to verify against the actual property.'),stock_routes(),b.para('Sources: 2024 ACS 1-year DP04, Maryland Department of Planning. Age and structure-form percentages are separate county measures; their joint distribution and defect rates are not established. Detailed values and margins: housing-data.csv. Packing cards: APP-F. Exact local dates: APP-H.',b.SMALL)]
 flow=[b.heading('Regional housing: where to focus','regional_focus'),b.para('Use local housing age and form to choose review topics before the visit. Then let the property evidence change the plan. The same charts support a focused discussion with a colleague.'),chart(),b.table(dict(headers=['Jurisdiction','Pre-1940','1940-59','1960-79','1980-99','2000-09','2010-19','2020+'],rows=table_rows(),widths=[111,59,59,59,59,59,59,59])),b.para(NOTE,b.SMALL),b.PageBreak(),b.heading('Field and colleague discussion routes','field_routes')]
 rows=[[x[0]+'\n'+x[1],x[2]+'\nDiscuss: '+x[3]] for x in PRIORITIES]
 flow +=[b.table(dict(headers=['Local stock cue','Review emphasis / discussion question'],rows=rows,widths=[140,384])),b.para('Topic route: structure/masonry/moisture; exterior/deck/drainage; plumbing/materials; electrical/legacy wiring; heating/venting. APP-F selects the kit; APP-H resolves code chronology. Source figures remain at the relevant topic. These priorities supplement the full agreed inspection scope.',b.SMALL)]
 return flow
