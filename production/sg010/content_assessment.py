"""Preserve the observed practice result without inventing an answer audit."""
from prepare import *

def apply(d,compact,apps,walk):
    result=dict(source='S37',seconds=14.809596,timestamp='00:00:14.810',unit='Initial practice assessment - recorded result',score=72,correct=36,total=50,asset='Evidence/S37-initial-assessment-result.jpg',cache_asset=str(WORK/'incoming-preview/S37-0.jpg'),frame_sha256=sha(WORK/'incoming-preview/S37-0.jpg'),review='Visually confirmed result screen. Separate from reported course completion and any licensing examination. Question-level correction audit remains unverified.')
    apps['APP-G']['recorded_results'].append(result)
    apps['APP-G']['pages'].append(dict(id='initial_practice_assessment',title='Practice result: use the evidence at the right scale',blocks=[dict(kind='table',headers=['Evidence','What it supports','What remains separate'],widths=[110,212,182],rows=[
        ['S37 / 36 of 50 / 72%','A recorded initial-assessment result. Retain the screen, attempt label and date with the score.','The user reported passing the course. This practice score is not the course certificate or a state/national licensing result.'],
        ['S36 / opening role outline','A structured coverage check for technical systems, reporting, agreements and professional conduct.','Exam weighting is not local defect frequency, field urgency or a property risk score.'],
        ['Recorded question screens','Review exact wording, selected answer and any visible correct-answer feedback together.','The result alone does not identify which 14 questions were missed. Do not infer strengths or weaknesses from the aggregate score.'],
        ['Study priority','Use repeated course-review issues, verified corrections and the field consequences of an error to choose the next review topic.','A repeated successful attempt preserves learning history; it does not erase earlier attempts or prove readiness in an unobserved topic.']])],refs=[dict(source='S37',seconds=14.809596,label='Initial assessment result screen'),dict(source='S36',seconds=0,label='Inspector-role outline and recorded initial assessment')]))
    evidence=OUT/'Evidence/S37-initial-assessment-result.jpg';evidence.parent.mkdir(exist_ok=True);shutil.copy2(WORK/'incoming-preview/S37-0.jpg',evidence)
    save(OUT/'assessment-review.json',dict(edition='SG-010',result=result,question_level_audit='not established from result screen',course_completion='user reported passing; separate from this practice attempt'))
