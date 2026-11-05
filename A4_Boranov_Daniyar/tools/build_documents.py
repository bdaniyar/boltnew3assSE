"""Build the A4 submission documents from actual recorded evidence.

Run with the bundled Codex Python runtime. The required DOCX renderer then
exports the main PDF; it never calls desktop LibreOffice.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from xml.sax.saxutils import escape
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'A4_Boranov_Daniyar'
BASELINE = '55cab2a186df4107ab7189f509c259006af28f3f'
BOLT = 'https://bolt.new/~/sb1-bskzikuu'
OLD_DEMO = 'https://smart-campus-room-av-j4pb.bolt.host/'
BLACK = RGBColor(0, 0, 0)


def xml_child(tag, **attrs):
    e = OxmlElement(tag)
    for key, value in attrs.items():
        e.set(qn(key), str(value))
    return e


def font_run(r, size=None, bold=None):
    r.font.name = 'Calibri'
    r.font.color.rgb = BLACK
    if bold is not None:
        r.font.bold = bold
    if size is not None:
        r.font.size = Pt(size)
    r._element.get_or_add_rPr().rFonts.set(qn('w:ascii'), 'Calibri')
    r._element.rPr.rFonts.set(qn('w:hAnsi'), 'Calibri')
    return r


def setup():
    doc = Document()
    sec = doc.sections[0]
    sec.page_width = Inches(8.5)
    sec.page_height = Inches(11)
    sec.top_margin = Inches(.62)
    sec.bottom_margin = Inches(.62)
    sec.left_margin = Inches(.68)
    sec.right_margin = Inches(.68)
    sec.footer_distance = Inches(.28)
    for name in ['Normal', 'Title', 'Subtitle', 'Heading 1', 'Heading 2', 'Caption']:
        s = doc.styles[name]
        s.font.name = 'Calibri'
        s.font.color.rgb = BLACK
        s._element.get_or_add_rPr().rFonts.set(qn('w:ascii'), 'Calibri')
        s._element.rPr.rFonts.set(qn('w:hAnsi'), 'Calibri')
        borders=s._element.find(qn('w:pPr'))
        if borders is not None:
            for el in list(borders):
                if el.tag == qn('w:pBdr'):
                    borders.remove(el)
    normal=doc.styles['Normal']
    normal.font.size=Pt(11)
    normal.paragraph_format.space_after=Pt(6)
    normal.paragraph_format.line_spacing=1.08
    doc.styles['Title'].font.size=Pt(24)
    doc.styles['Title'].font.bold=True
    doc.styles['Title'].paragraph_format.space_after=Pt(10)
    doc.styles['Heading 1'].font.size=Pt(15)
    doc.styles['Heading 1'].font.bold=True
    doc.styles['Heading 1'].paragraph_format.space_before=Pt(10)
    doc.styles['Heading 1'].paragraph_format.space_after=Pt(7)
    doc.styles['Heading 2'].font.size=Pt(12)
    doc.styles['Heading 2'].font.bold=True
    doc.styles['Heading 2'].paragraph_format.space_before=Pt(7)
    doc.styles['Heading 2'].paragraph_format.space_after=Pt(5)
    doc.styles['Caption'].font.size=Pt(9)
    doc.styles['Caption'].font.italic=False
    doc.styles['Caption'].paragraph_format.space_after=Pt(6)
    foot=sec.footer.paragraphs[0]
    foot.alignment=WD_ALIGN_PARAGRAPH.CENTER
    font_run(foot.add_run('Page '), 9)
    r=foot.add_run()
    r._r.append(xml_child('w:fldChar', **{'w:fldCharType':'begin'}))
    instr=xml_child('w:instrText', **{'xml:space':'preserve'})
    instr.text=' PAGE '
    r._r.append(instr)
    r._r.append(xml_child('w:fldChar', **{'w:fldCharType':'end'}))
    doc.core_properties.title='Software Engineering Assignment 04'
    doc.core_properties.subject='Smart Campus Room Availability Checker'
    doc.core_properties.author='Boranov Daniyar'
    return doc


def p(doc, text, *, style=None, size=None, bold=None):
    para=doc.add_paragraph(style=style)
    font_run(para.add_run(str(text)),size,bold)
    return para


def h(doc, text, level=1):
    return p(doc,text,style=f'Heading {level}')


def link(doc,label,url):
    para=doc.add_paragraph()
    font_run(para.add_run(label+' '),11,True)
    rel=doc.part.relate_to(url,'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink',is_external=True)
    hyper=OxmlElement('w:hyperlink');hyper.set(qn('r:id'),rel)
    run=OxmlElement('w:r');prop=OxmlElement('w:rPr')
    prop.append(xml_child('w:color',**{'w:val':'000000'}))
    prop.append(xml_child('w:u',**{'w:val':'single'}))
    prop.append(xml_child('w:sz',**{'w:val':'22'}))
    run.append(prop);txt=OxmlElement('w:t');txt.text=url;run.append(txt);hyper.append(run);para._p.append(hyper)
    return para


def table(doc, headers, rows, widths, *, font=9.5, centered=()):
    t=doc.add_table(rows=1, cols=len(headers))
    t.alignment=WD_TABLE_ALIGNMENT.CENTER
    t.autofit=False
    pr=t._tbl.tblPr
    borders=xml_child('w:tblBorders')
    for edge in ['top','left','bottom','right','insideH','insideV']:
        borders.append(xml_child('w:'+edge,**{'w:val':'single','w:sz':'5','w:color':'D9D9D9'}))
    pr.append(borders)
    layout=xml_child('w:tblLayout',**{'w:type':'fixed'});pr.append(layout)
    for grid,width in zip(t._tbl.tblGrid.gridCol_lst,widths):
        grid.set(qn('w:w'),str(int(width*1440)))
    allrows=[headers]+list(rows)
    for n,data in enumerate(allrows):
        row=t.rows[0] if n==0 else t.add_row()
        row._tr.get_or_add_trPr().append(xml_child('w:cantSplit'))
        if n==0:
            row._tr.get_or_add_trPr().append(xml_child('w:tblHeader'))
        for j,(cell,text,width) in enumerate(zip(row.cells,data,widths)):
            cell.width=Inches(width)
            cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            cp=cell._tc.get_or_add_tcPr()
            margins=xml_child('w:tcMar')
            for edge,value in [('top',75),('bottom',75),('left',90),('right',90)]:
                margins.append(xml_child('w:'+edge,**{'w:w':str(value),'w:type':'dxa'}))
            cp.append(margins)
            if n==0:
                cp.append(xml_child('w:shd',**{'w:fill':'E7E6E6'}))
            para=cell.paragraphs[0]
            para.paragraph_format.space_after=Pt(0)
            para.paragraph_format.line_spacing=1.04
            para.alignment=WD_ALIGN_PARAGRAPH.CENTER if j in centered else WD_ALIGN_PARAGRAPH.LEFT
            font_run(para.add_run(str(text)),font,n==0)
    space=doc.add_paragraph()
    space.paragraph_format.space_after=Pt(2)
    space.paragraph_format.space_before=Pt(0)
    space.paragraph_format.line_spacing=Pt(3)
    font_run(space.add_run(''),3)
    return t


def page(doc):
    doc.add_page_break()


def image(doc,path,caption,max_w=7.1,max_h=3.0):
    from PIL import Image
    path=Path(path)
    if not path.is_absolute():
        path=OUT/path
    if not path.is_file():
        raise FileNotFoundError(path)
    with Image.open(path) as im:
        w,h=im.size
    width=min(max_w,max_h*w/h)
    para=doc.add_paragraph()
    para.alignment=WD_ALIGN_PARAGRAPH.CENTER
    para.paragraph_format.space_after=Pt(4)
    run=para.add_run()
    shape=run.add_picture(str(path),width=Inches(width))
    shape._inline.docPr.set('descr',caption)
    p(doc,caption,style='Caption')


def paired_images(doc, records, caption, max_h=4.4):
    from PIL import Image
    para=doc.add_paragraph()
    para.alignment=WD_ALIGN_PARAGRAPH.CENTER
    para.paragraph_format.space_after=Pt(5)
    for index, record in enumerate(records):
        path=Path(record['file'])
        if not path.is_absolute():path=OUT/path
        with Image.open(path) as im:w,h=im.size
        width=min(3.25,max_h*w/h)
        if index:font_run(para.add_run('    '),11)
        shape=para.add_run().add_picture(str(path),width=Inches(width))
        shape._inline.docPr.set('descr',record['caption'])
    p(doc,caption,style='Caption')


def count_result(data, kind):
    for c in data['checks']:
        name=c['name'].lower()
        if (kind=='python' and 'python' in name) or (kind=='frontend' and 'frontend' in name) or (kind=='ui' and ('chromium' in name or name=='ui')):
            return f"{c['passed']}/{c['total']}"
    return 'See final results'


def check_results(data):
    aliases={'python':'Python regression','frontend':'Frontend logic','ui':'Chromium UI','lint':'Lint','typecheck':'Type checking','build':'Production build'}
    rows=[]
    for c in data['checks']:
        passed=c.get('passed',c.get('tests_passed',c.get('pass')))
        total=c.get('total',c.get('tests_total',c.get('tests')))
        result=f'{passed}/{total} passed' if passed is not None and total is not None else f"Exit {c['exit_code']}"
        command=c['command']
        if isinstance(command,list):command=' '.join(command)
        rows.append([aliases.get(c['name'],c['name']),result,command])
    return rows


def source_count(data,name,default):
    return data.get('metrics',{}).get(name,default)


def make_reflection():
    return '''For Assignment 04, I chose to extend the existing Smart Campus prototype. I provided the previous source, the original acceptance criteria, the assignment PDF and clear limits. I approved a small plan that kept the current framework, fixed demo time and booking rules.

The most useful AI suggestion was to separate room matching from availability checking. This made the new filters easier to understand and test. Keeping the selected room ID also reduced the risk of showing one room while checking another room's bookings. A shared result panel made the status messages more consistent.

One recommendation was modified for a technical reason. A normal production build would overwrite the tracked deployment folder. The verification build therefore used a separate ignored output folder. I also kept the original overlap comparison because touching booking endpoints must remain valid. A backend, live clock and booking creation were outside the agreed scope.

The verification evidence includes real Python and frontend regression results, new filtering and state tests, and browser checks. Room switching and empty-state tests were especially useful. A correct validation function alone cannot prove that the interface passes the right room data. These tests supported the decision to clear old results whenever the room or requirements change. One keyboard check initially used an unreliable key sequence. It was corrected to native type-ahead after a focused browser check; the application did not need a change.

I would next improve keyboard and screen-reader testing. A larger catalog would also need clearer data validation and more equipment combinations. For this assignment, a small fictional catalog keeps the behavior reproducible and the design easy to inspect.'''


def build_report(data):
    doc=setup()
    p(doc,'Software Engineering Assignment 04',style='Title')
    p(doc,'Smart Campus Room Availability Checker',style='Subtitle')
    p(doc,'Boranov Daniyar',bold=True)
    p(doc,'Student ID 24B031718')
    p(doc,'Thursday 14:00–17:00')
    h(doc,'1 Project overview and prototype access')
    p(doc,'The Smart Campus prototype now supports four fictional university rooms. Capacity and equipment filters help users choose a suitable room. The availability check then uses only that room\'s blocked status and existing bookings. The original time rules and read-only booking behavior are preserved.')
    dep=data['deployment']
    if dep.get('verified'):
        link(doc,'Live A4 demonstration',dep['url'])
        p(doc,dep.get('summary','The published A4 version was checked without signing in.'))
    else:
        p(doc,dep.get('summary','The A4 version was verified locally. Publication of the updated version remains to be completed.'))
        link(doc,'Previous A3 demonstration',dep.get('url') or OLD_DEMO)
        p(doc,'This address is the previous published prototype and is not presented as a verified A4 deployment.')
    link(doc,'Existing Bolt project',dep.get('bolt_url',BOLT))
    h(doc,'2 Original implementation and recoverable source')
    p(doc,'The original A3 implementation is preserved at commit '+BASELINE+'. The annotated tag a4-baseline-2026-11-05 and the verified recovery bundle keep the starting version recoverable. The earlier prototype-v1 tag and historical A3 evidence are also unchanged.')
    p(doc,'Final A4 source commit '+data['final_source_commit']+'. The package contains source references, test files, command logs and recovery instructions in README.md.')
    table(doc,['Scope','Implementation'],[
        ['Original rules','Integer minutes, fixed now 540, maximum 120 minutes, blocked rejection, touching endpoints allowed'],
        ['New behavior','Four rooms; capacity and ALL-equipment filters; empty state; room switching'],
        ['Data boundary','Fictional data only; no booking creation or changes'],
    ],[1.15,5.95],font=10)
    page(doc)
    h(doc,'3 Codebase map and maintainability risks')
    p(doc,'The analysis used real source and function references from the preserved baseline. The risks affect the extension of a working one-room application.')
    table(doc,['Source','Responsibility'],[
        ['src/App.tsx App and handleCheck','Application state, checking and component composition'],
        ['src/types.ts and data/sampleData.ts','Original domain types, A-102, fixed time and examples'],
        ['src/utils/availability.ts checkAvailability','Pure AC1–AC5 validation and booking overlap checks'],
        ['src/components','Time controls, room details, bookings and result feedback'],
        ['scripts/frontend-test.mjs','Actual TypeScript availability function tested with 37 fixtures'],
        ['booking.py can_book and test_booking.py','Python reference implementation and 47 tests'],
    ],[3.05,4.05],font=9.5)
    table(doc,['Risk','Baseline evidence','Change'],[
        ['Global booking coupling','App.tsx lines 27–35 and 95 use SAMPLE_BOOKINGS.','Check and display derive data from the selected room.'],
        ['Small room model','types.ts lines 8–12 lacks capacity, equipment and bookings.','Readonly room catalog stores all required fields.'],
        ['Repeated invalidation','Five handlers clear results at App.tsx lines 42, 47, 52, 57 and 64.','One state transition path invalidates prior results.'],
        ['No executable UI events','frontend-test.mjs lines 17–49 tests pure rules only.','Real Chromium tests exercise filtering and switching.'],
        ['Repeated feedback wrapper','ResultPanel.tsx has three repeated status sections.','A shared accessible wrapper presents conditional feedback.'],
    ],[1.35,2.7,3.05],font=9.5)
    h(doc,'4 Prioritized improvement plan')
    p(doc,'P1 added the room model and fictional catalog. P2 extracted pure filtering and connected the selected room to checking and booking display. P3 added the controls, selection handling and shared feedback. P4 ran the final regression and UI checks and collected evidence. Each step kept changes small enough to inspect in the Git diff.')
    page(doc)
    h(doc,'5 Preservation of AC1 to AC6')
    p(doc,'The availability function retains the original validation contract. Room selection changes its input data, while the meaning of valid and invalid requests stays the same.')
    table(doc,['Criterion','Preserved behavior','Source and verification'],[
        ['AC1','Whole minutes; 0 ≤ start < end ≤ 1440; start > 540.','utils/availability.ts checkAvailability; invalid time and day-boundary fixtures'],
        ['AC2','Exactly 120 minutes allowed; 121 rejected.','Original duration guard and separate regression/UI boundary checks'],
        ['AC3','A blocked room cannot be available.','Existing blocked guard; catalog-blocked room and UI checks'],
        ['AC4','Overlaps rejected; touching endpoints allowed.','start < booking.end AND end > booking.start; boundary fixtures'],
        ['AC5','Only check availability; bookings never change.','Readonly/frozen catalog and deep equality checks'],
        ['AC6','Clear result/reason and responsive controls.','Shared ResultPanel, labelled controls and narrow-screen browser tests'],
    ],[.65,3.1,3.35],font=10)
    h(doc,'6 New room catalog')
    table(doc,['Room and capacity','Equipment','Blocked','Bookings'],[
        ['A-102 Study Room A-102\n4 people','Whiteboard, projector','No','10:00–11:00'],
        ['B-201 Team Room B-201\n8 people','Whiteboard, display','No','11:00–12:00'],
        ['C-303 Seminar Room C-303\n12 people','Projector, display, video conference','No','12:00–13:00'],
        ['D-404 Project Room D-404\n20 people','Whiteboard, projector, video conference','Yes','14:00–15:00'],
    ],[2.15,2.45,.65,1.85],font=10,centered=(2,))
    p(doc,'Each room has an ID, name, capacity, equipment list, blocked status and its own immutable bookings. A-102 keeps the original booking from 600 to 660 minutes. The current demo time remains 540 minutes, or 09:00.')
    page(doc)
    h(doc,'7 Filtering and room selection')
    table(doc,['Rule','Final behavior','Verification focus'],[
        ['F1','Capacity must be greater than or equal to attendees.','Exact, insufficient and larger capacity'],
        ['F2','Every required equipment item must be present. An empty selection adds no equipment restriction.','ALL matching, partial match and no equipment'],
        ['F3','A matching blocked room remains clearly marked and cannot become Available.','D-404 blocked guard and UI'],
        ['F4','No matching rooms produces a clear empty state. Old feedback and invalid selection are cleared.','Zero-match browser event'],
        ['F5','Room switching clears prior feedback; checking uses the new room\'s status and bookings.','A-102 available versus B-201 overlap for 11:00–12:00'],
    ],[.55,4.1,2.45],font=10)
    p(doc,'Capacity and equipment conditions are combined with AND. Attendee count must be a positive whole number. Selecting a room stores its ID and derives the current room record. If new filters exclude that room, selection and feedback are cleared, and checking is disabled until a visible room is selected.')
    p(doc,'The original example cases are scoped to A-102. They cannot silently check a room hidden by the current filters. Bookings remain read-only throughout filtering, switching and checking.')
    h(doc,'8 Refactoring design decisions')
    p(doc,'Room matching and availability are separate pure functions. This keeps capacity and equipment rules easy to test while preserving the original time and overlap validator. The trade-off is that the interface must explain that a matching room can still be blocked or have a booking conflict.')
    p(doc,'Selection uses a room ID rather than a second copy of room data. The booking list and availability check therefore use one derived record. A common state update path clears obsolete results. This introduces explicit state transitions, but makes F5 behavior testable without duplicating the validator.')
    p(doc,'The result panel uses one shared status wrapper. Available, unavailable and initial content keep different messages within the same labelled live region. This reduces repeated rendering code and keeps accessibility attributes consistent.')
    page(doc)
    h(doc,'9 Module and component diagrams')
    p(doc,'The BEFORE diagram reflects the original one-room source. The AFTER diagram reflects the final catalog, filter, state and presentation modules. Diagram source files and readable images are included in diagrams/.')
    image(doc,data['diagrams']['before'],'Figure 1  Original A3 module and component structure',max_h=2.8)
    image(doc,data['diagrams']['after'],'Figure 2  Final A4 module and component structure',max_h=3.5)
    page(doc)
    h(doc,'10 Automated testing and execution results')
    p(doc,'The existing Python and frontend regression tests were retained. New tests use the production catalog, filtering functions and state transitions. Chromium tests execute real interface events, including room switching, filtering, empty state and mobile layout.')
    table(doc,['Check','Actual result','Executed command'],check_results(data),[1.25,1.05,4.8],font=9.5)
    p(doc,'The original baseline passed Python 47/47 and frontend 37/37. These results were rerun and saved before source changes. Final counts come from the test runners, not from counting assertions or screenshots. Full commands, stdout/stderr, exit codes and reports are included in evidence/.')
    h(doc,'11 Test coverage and evidence')
    table(doc,['Coverage','Relevant behavior'],[
        ['AC1–AC4 regression','Invalid/equal/reversed times; 120/121 minutes; blocked room; touching and overlapping intervals; multiple bookings'],
        ['AC5 and room isolation','Frozen booking inputs unchanged; each room uses its own booking list'],
        ['F1 and F2','Exact and insufficient capacity; ALL equipment; missing item; empty equipment selection'],
        ['F3–F5 UI','Blocked room; no matches; switching rooms; filters invalidating selection; no stale result'],
        ['AC6 UI','Labelled controls, clear feedback and narrow/mobile layout'],
    ],[1.45,5.65],font=10)
    p(doc,'A normal verification build was changed to use an ignored output directory because dist/ already contains tracked deployment files. This preserves the previous snapshot during checks. Publication status is verified separately from local test results.')
    page(doc)
    h(doc,'12 Filtering and availability evidence')
    records={Path(s['file']).name:s for s in data['screenshots']}
    for name,label in [
        ('report-filter-controls.png','Figure 3  Capacity and equipment requirements'),
        ('report-matching-rooms.png','Figure 4  Only matching rooms are displayed'),
        ('report-empty-state.png','Figure 5  Clear empty state when no rooms match'),
    ]:
        s=records[name]
        image(doc,s['file'],label+'. '+s['caption'],max_h=2.0)
    paired_images(doc,[records['report-available-feedback.png'],records['report-overlap-feedback.png']],
        'Figure 6  The same 11:00–12:00 request is available in C-303 and unavailable in B-201. Each result uses that room\'s own bookings.',max_h=1.0)
    p(doc,'These are complete semantic-element captures from real browser checks. Their capture records, viewport sizes and original screenshots are included in the evidence folder.')
    page(doc)
    h(doc,'13 Selected room and responsive evidence')
    s=records['report-selected-room.png']
    image(doc,s['file'],'Figure 7  '+s['caption'],max_w=5.5,max_h=1.4)
    paired_images(doc,[records['report-mobile-filter-controls.png'],records['report-mobile-time-controls.png']],
        'Figure 8  At a 320-pixel viewport, the complete requirements and original time controls remain readable and usable. Both semantic-element screenshots are displayed without cropping.',max_h=3.8)
    p(doc,'Changing rooms removes the previous availability feedback. A later check uses the chosen room\'s existing bookings. On a narrow screen the controls remain usable without horizontal scrolling. The screenshots and UI assertions cover these behaviors separately.')
    page(doc)
    h(doc,'14 Measured quality evaluation')
    m=data.get('metrics',{})
    table(doc,['Measure','A3 baseline','Final A4','How measured'],[
        ['Python regression','47/47',count_result(data,'python'),'unittest runner totals in saved logs'],
        ['Frontend logic','37/37',count_result(data,'frontend'),'Node test runner totals; existing fixtures retained'],
        ['Executable UI coverage','No committed executable UI suite',count_result(data,'ui'),'Chromium test report, excluding screenshots from test count'],
        ['Repeated status wrappers','3',str(m.get('status_wrappers_after',1)),'ResultPanel source before/after; repeated wrapper locations removed'],
        ['Result invalidation locations','5',str(m.get('result_clear_after',1)),'Input handlers before versus common transition after'],
        ['Production modules',str(m.get('modules_before',13)),str(m.get('modules_after',18)),'TS/TSX production files, excluding declarations; saved file lists'],
        ['UI components',str(m.get('components_before',7)),str(m.get('components_after',9)),'Source files under src/components; module responsibilities shown in diagrams'],
    ],[1.4,1.2,2.05,2.45],font=9.5)
    p(doc,'Two repeated status-wrapper locations were removed (3 to 1), and four repeated input-result reset locations were removed (5 to 1). The final locations are ResultPanel.tsx and state/checker.ts updateInputs. The larger catalog and filtering controls are feature additions. Pure filtering, one selected-room state path and shared status presentation improve maintainability. Duplication measurements count active production locations only; preserved A3 source copies are not removed or counted as refactoring gains.')
    h(doc,'15 Remaining limitations')
    limits=data.get('limitations',[
        'The rooms, bookings and current time are fictional and fixed. The application does not create or save reservations.',
        'Automated Chromium and layout checks do not replace a complete keyboard and screen-reader accessibility audit.',
    ])
    for item in limits:
        p(doc,item)
    if not dep.get('verified'):
        p(doc,'The updated source must be synchronized and published in the existing Bolt project before this URL can be treated as a verified public A4 version.')
    page(doc)
    h(doc,'16 Reflection')
    reflection=make_reflection()
    count=len(reflection.split())
    assert 200<=count<=300,count
    for part in reflection.split('\n\n'):
        p(doc,part)
    h(doc,'17 AI use and references')
    p(doc,'Codex supported codebase analysis, implementation, test design and documentation. Bolt.new was used to synchronize and publish the existing project. Recommendations were checked against the assignment, source code, Git diffs and actual test output. The separate AI evidence appendix records prompts, outputs, review decisions and verification sources.')
    p(doc,'[1] Software Engineering Assignment 04, supplied 30-page PDF, especially pages 10–19 and 25–27.')
    p(doc,'[2] Smart Campus Room Availability Checker, preserved A3 baseline '+BASELINE+' and final A4 source '+data['final_source_commit']+'.')
    p(doc,'[3] Playwright documentation, Installation and Web server, used for the executable Chromium checks.')
    dest=OUT/'A4_Boranov_Daniyar_Report.docx'
    doc.save(dest)
    (OUT/'evidence'/'reflection.txt').write_text(reflection+'\n')
    (OUT/'evidence'/'report-content-checks.json').write_text(json.dumps({'reflection_words':count,'native_tables':len(doc.tables),'embedded_images':len(doc.inline_shapes),'final_source_commit':data['final_source_commit'],'public_a4_verified':bool(dep.get('verified')),'report_sections':17,'all_text_editable_except_screenshots_and_diagrams':True},indent=2)+'\n')
    return dest


def build_ai_evidence(data):
    fonts=Path('/Users/daniarboranov/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/libreoffice-headless/libreoffice/LibreOfficeDev.app/Contents/Resources/fonts/truetype')
    pdfmetrics.registerFont(TTFont('EvidenceSans',str(fonts/'DejaVuSans.ttf')))
    pdfmetrics.registerFont(TTFont('EvidenceSansBold',str(fonts/'DejaVuSans-Bold.ttf')))
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='EvidenceTitle',fontName='EvidenceSansBold',fontSize=20,leading=24,spaceAfter=14,textColor=colors.black))
    styles.add(ParagraphStyle(name='EvidenceHead',fontName='EvidenceSansBold',fontSize=13,leading=16,spaceBefore=12,spaceAfter=7,textColor=colors.black,keepWithNext=True))
    styles.add(ParagraphStyle(name='EvidenceBody',fontName='EvidenceSans',fontSize=9.5,leading=12,spaceAfter=6,textColor=colors.black))
    styles.add(ParagraphStyle(name='Transcript',fontName='EvidenceSans',fontSize=9,leading=12,spaceAfter=5,textColor=colors.black,wordWrap='CJK',splitLongWords=True))
    styles.add(ParagraphStyle(name='TranscriptHeading',parent=styles['Transcript'],keepWithNext=True))
    story=[]
    def a(text,sty='EvidenceBody'):
        story.append(Paragraph(escape(text).replace('\n','<br/>'),styles[sty]))
    a('Assignment 04 AI Evidence','EvidenceTitle')
    a('Boranov Daniyar | Student ID 24B031718 | Thursday 14:00–17:00')
    a('This appendix records actual prompts, preserved responses and technical verification for the existing Smart Campus application. It is separate from the main engineering report. The original Assignment 03 AI evidence is unchanged.')
    a('Tool and review record','EvidenceHead')
    a('Tool: Codex. Model family: GPT-6, as identified by the session instructions; the exact deployment identifier was not exposed. Work date: 5 November 2026, Asia/Almaty.')
    a('The Task 1 plan was explicitly approved in the full request reproduced below. No other personal review or independently executed student tests are inferred from that approval. The reflection is a first-person draft prepared for final review.')
    a('Output used and technical decisions','EvidenceHead')
    a('The approved plan guided the four-room catalog, pure capacity/equipment filtering, selected-room state and real UI tests. The existing time and overlap validator and Python reference were preserved. One actual AI recommendation was modified: verification builds use an ignored output path because the deployment folder is tracked. Equipment ALL matching and touching endpoints were checked against the assignment and original contract.')
    a('Verification sources include the complete assignment PDF, production source, preserved baseline bundle and hashes, Git diffs, actual regression/UI logs and screenshots. Final source commit: '+data['final_source_commit']+'.')
    a('Actual final command results','EvidenceHead')
    for row in check_results(data):
        a(row[0]+': '+row[1]+'. Command: '+row[2])
    hist=data.get('test_history',{})
    if hist:
        a('Test correction and preserved failures','EvidenceHead')
        a('The first UI run passed 20 of 21 tests. A native-select keyboard test assumed an unreliable ArrowDown and Enter sequence. A focused check supported native type-ahead; the corrected check passed 1 of 1. The final suite passed 22 of 22. No application fix was required. Original failing logs and the corrected-run evidence are retained in evidence/implementation-testing.')
    a('Public deployment record','EvidenceHead')
    a(data['deployment'].get('summary','See deployment evidence in the submission package.'))
    for file,label in [
        ('01-user-prompt.txt','Task 1 exact user prompt'),
        ('01-assistant-response.md','Task 1 complete assistant response'),
        ('02-user-approval-and-request-exact.txt','Exact approval and full implementation request'),
    ]:
        story.append(PageBreak())
        a(label,'EvidenceHead')
        a('The following text is preserved verbatim. Layout wrapping does not change the historical exchange.')
        text=(OUT/'evidence'/'ai-exchanges'/file).read_text()
        for line in text.splitlines():
            # Escape source exactly; blank paragraphs are retained as spacing.
            if line:
                a(line,'TranscriptHeading' if line.lstrip().startswith('#') else 'Transcript')
            else:
                story.append(Spacer(1,4))
    record_files=list(data.get('ai_additional_transcripts',[]))
    known={Path(item['file']).name for item in record_files}
    for filename,title in [
        ('03-bolt-sync-prompt-exact.txt','Existing Bolt project exact synchronization prompt'),
        ('03-bolt-sync-response-visible.txt','Existing Bolt project complete visible agent response'),
        ('04-bolt-publish-ui-request.txt','Existing Bolt publication UI generated request'),
        ('04-bolt-publish-response-visible.txt','Existing Bolt publication complete visible response'),
    ]:
        full=OUT/'evidence'/'ai-exchanges'/filename
        if full.is_file() and filename not in known:
            record_files.append({'file':str(full),'title':title})
    if record_files:
        a('Review of the Bolt synchronization recommendation','EvidenceHead')
        a('Tool: Bolt.new Standard agent; the exact model was not identified. The request concerned synchronization of the existing project, without code generation or publication. The complete visible response was preserved, including progress labels; hidden reasoning and unexpanded tool details are not claimed.')
        a('The Publish control later generated the exact publication request preserved below. The visible publication response and independent anonymous HTTP, build-asset and browser checks verify the actual result; a chat success statement alone is not treated as deployment proof.')
        a('The response treated unavailable shell Git commands as a synchronization blocker. That limitation was not accepted as proof that the built-in GitHub interface or publication was unavailable. The actual Code view and existing interface were checked separately. This modified recommendation and its verification sources are recorded in 03-bolt-sync-observation.json.')
        a('After publication, a managed repository synchronization removed an ignored tracked baseline log and deployment assets. The historical log was restored byte for byte, the verified A4 build was tracked, and narrow ignore exceptions protected these records. Production TypeScript, Python and test source remained identical to the tested version. The exact artifact-only change and preservation checks are recorded in evidence/refactoring/bolt-sync-preservation-fix.json.')
    for item in record_files:
        path=ROOT/item['file'] if not Path(item['file']).is_absolute() else Path(item['file'])
        if Path(item['file']).name == '03-bolt-sync-prompt-exact.txt':
            story.append(PageBreak())
        else:
            story.append(Spacer(1,12))
        a(item['title'],'EvidenceHead')
        for line in path.read_text().splitlines():
            a(line,'Transcript') if line else story.append(Spacer(1,4))
    def footer(canvas,doc):
        canvas.saveState();canvas.setFont('EvidenceSans',8);canvas.drawCentredString(letter[0]/2,26,f'Page {doc.page}');canvas.restoreState()
    dest=OUT/'AI_Evidence.pdf'
    SimpleDocTemplate(str(dest),pagesize=letter,rightMargin=44,leftMargin=44,topMargin=42,bottomMargin=44,title='Assignment 04 AI Evidence',author='Boranov Daniyar').build(story,onFirstPage=footer,onLaterPages=footer)
    return dest


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--data',type=Path,default=OUT/'evidence'/'report-data.json');parser.add_argument('--skip-evidence',action='store_true');parser.add_argument('--evidence-only',action='store_true');args=parser.parse_args()
    data=json.loads(args.data.read_text())
    assert data.get('final_source_commit') and re.fullmatch(r'[a-f0-9]{40}',data['final_source_commit'])
    assert data.get('checks') and all(c['exit_code']==0 for c in data['checks'])
    if not args.evidence_only:print(build_report(data))
    if not args.skip_evidence:print(build_ai_evidence(data))

if __name__=='__main__':
    main()
