from prepare import read,WORK
# Each result was checked visually against the original recorded result screen.
SCORES=[
 ('S16',60,'Garage unit',89,8,9),('S17',1522,'Roof unit 1',89,16,18),
 ('S18',542,'Roof unit 3: first recorded attempt',67,6,9),('S18',724,'Roof unit 3: later attempt',89,8,9),
 ('S18',1261,'Roof unit 4: first recorded attempt',60,3,5),('S18',1424,'Roof unit 4: later attempt',100,5,5),
 ('S18',1678,'Roof unit 5: first recorded attempt',33,1,3),('S18',1787,'Roof unit 5: later attempt',100,3,3),
 ('S20',1494,'Plumbing unit 2',90,18,20),('S20',2972,'Plumbing unit 3',75,12,16),
 ('S24',1730,'Plumbing unit 4: first recorded attempt',61,11,18),('S24',2040,'Plumbing unit 4: later attempt',100,18,18),
 ('S24',2945,'Plumbing unit 5',89,8,9),('S24',4151,'Electrical unit 1',87,13,15),
 ('S26',1045,'Electrical unit 5',89,8,9),('S27',1837,'Electrical unit 6',92,12,13),
 ('S28',95,'Heating unit 1: first recorded attempt',29,2,7),('S28',302,'Heating unit 1: second recorded attempt',71,5,7),('S28',459,'Heating unit 1: third recorded attempt',100,7,7),
 ('S28',1353,'Heating unit 2',100,3,3),('S28',3307,'Heating unit 3',91,10,11),
 ('S29',1182,'Heating unit 4: first recorded oil attempt',67,8,12),('S29',1449,'Heating unit 4: later oil attempt',83,10,12),('S29',1879,'Heating unit 5: gravity/distribution',100,5,5)]
def records():
 result=[]
 for sid,ix,unit,score,correct,total in SCORES:
  root=next(p for p in (WORK/('Visual-'+sid)).glob('R*') if p.is_dir());f=read(root/f'ocr/{ix:07}.json')['frame']
  result.append(dict(source=sid,frame=ix,seconds=f['time_seconds'],timestamp=f['timestamp'],unit=unit,score=score,correct=correct,total=total,asset=f'Evidence/SG008/{sid}-F{ix}.jpg',cache_asset=str(root/f['image']),frame_sha256=f['sha256'],review='Visually confirmed result; selected corrections reviewed separately. Not a complete question-by-question audit.'))
 return result
