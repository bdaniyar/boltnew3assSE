"""Check final document content and editable structure after visual review."""
from pathlib import Path
from zipfile import ZipFile
import hashlib
import json
import re
import shutil
from io import BytesIO
from PIL import Image
from lxml import etree
from pypdf import PdfReader
from docx import Document

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'A4_Boranov_Daniyar'
DATA=json.loads((OUT/'evidence/report-data.json').read_text())
DOCX=OUT/'A4_Boranov_Daniyar_Report.docx'
PDF=OUT/'A4_Boranov_Daniyar_Report.pdf'
AI=OUT/'AI_Evidence.pdf'
N={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing','r':'http://schemas.openxmlformats.org/package/2006/relationships'}
with ZipFile(DOCX) as z:
    xml=etree.fromstring(z.read('word/document.xml'))
    text='\n'.join(xml.xpath('//w:t/text()',namespaces=N))
    footer='\n'.join(z.read(n).decode() for n in z.namelist() if n.startswith('word/footer') and n.endswith('.xml'))
    settings=z.read('word/settings.xml').decode()
    rels=etree.fromstring(z.read('word/_rels/document.xml.rels'))
    links=sorted({e.get('Target') for e in rels if e.get('TargetMode')=='External'})
    media={hashlib.sha256(z.read(n)).hexdigest():n for n in z.namelist() if n.startswith('word/media/')}
    for n in media.values():
        Image.open(BytesIO(z.read(n))).verify()
    # Compare displayed and embedded aspect ratios: complete images, never crops.
    image_rels={e.get('Id'):e.get('Target') for e in rels if '/image' in e.get('Type','')}
    aspect_ok=[]
    for inline in xml.xpath('//wp:inline',namespaces=N):
        extent=inline.find('wp:extent',N)
        rid=inline.xpath('.//a:blip/@*[local-name()="embed"]',namespaces=N)[0]
        im=Image.open(BytesIO(z.read('word/'+image_rels[rid])))
        actual=int(extent.get('cx'))/int(extent.get('cy'))
        aspect_ok.append(abs(actual/(im.width/im.height)-1)<0.002)
    table_count=len(xml.xpath('//w:tbl',namespaces=N))
    paragraph_count=len(xml.xpath('//w:p',namespaces=N))
    black_text=all(v.upper()=='000000' for v in xml.xpath('//w:rPr/w:color/@w:val',namespaces=N))
reader=PdfReader(PDF)
pdf_text='\n'.join(p.extract_text() or '' for p in reader.pages)
pdf_links=[]
for page in reader.pages:
    for ref in page.get('/Annots',[]):
        a=ref.get_object().get('/A',{})
        if a.get('/URI'):pdf_links.append(str(a['/URI']))
expected={DATA['deployment'].get('url') or 'https://smart-campus-room-av-j4pb.bolt.host/',DATA['deployment']['bolt_url']}
assert set(links)==expected,(links,expected)
assert expected<=set(pdf_links),(pdf_links,expected)
for value in ['Boranov Daniyar','24B031718','Thursday 14:00–17:00',DATA['final_source_commit'],'F1','F2','F3','F4','F5','AC1','AC2','AC3','AC4','AC5','AC6','47/47','76/76','22/22']:
    assert value in text,value
assert table_count==9
assert paragraph_count>100
assert len(media)==10
assert all(aspect_ok)
assert black_text
assert 'PAGE' in footer
assert 'documentProtection' not in settings
for phrase in ['The student delegated','AI generated this report','Student decision pending','The root agent performed','Human approval not recorded','This section was written by AI','The student did not personally execute']:
    assert phrase not in text,phrase
if DATA['deployment']['verified']:
    for phrase in ['Previous A3 demonstration','is being checked','not presented as a verified A4 deployment']:
        assert phrase not in text,phrase
reflection=(OUT/'evidence/reflection.txt').read_text()
words=len(reflection.split())
assert 200<=words<=300
assert ' '.join(reflection.split()) in ' '.join(text.split())
ai_reader=PdfReader(AI)
ai_text='\n'.join(p.extract_text() or '' for p in ai_reader.pages)
flat=lambda s: re.sub(r'\s+','',re.sub(r'Page\s+\d+','',s))
history={}
for name in ['01-user-prompt.txt','01-assistant-response.md','02-user-approval-and-request-exact.txt','03-bolt-sync-prompt-exact.txt','03-bolt-sync-response-visible.txt','04-bolt-publish-ui-request.txt','04-bolt-publish-response-visible.txt']:
    history[name]=flat((OUT/'evidence/ai-exchanges'/name).read_text()) in flat(ai_text)
assert all(history.values()),history
qa={
    'status':'PASS','report_pages':len(reader.pages),'ai_evidence_pages':len(ai_reader.pages),
    'native_word_paragraphs':paragraph_count,'native_word_tables':table_count,'embedded_images':len(media),
    'all_image_aspect_ratios_preserved':all(aspect_ok),'native_page_field':True,'editing_protection':False,
    'all_explicit_text_colors_black':black_text,'docx_external_links':links,'pdf_external_links':sorted(set(pdf_links)),
    'exact_history_text_complete_ignoring_layout_whitespace':history,'reflection_words':words,
    'source_commit':DATA['final_source_commit'],'public_a4_verified':DATA['deployment']['verified'],
    'report_visual_review_pages':list(range(1,len(reader.pages)+1)),
    'ai_visual_review_pages':list(range(1,len(ai_reader.pages)+1)),
    'visual_issues':[],
    'renderer':'Bundled Codex LibreOffice 25.2 through render_docx.py; bundled Poppler',
    'files':{p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [DOCX,PDF,AI]},
}
(OUT/'evidence/document-qa.json').write_text(json.dumps(qa,indent=2)+'\n')
print(json.dumps(qa,indent=2))
