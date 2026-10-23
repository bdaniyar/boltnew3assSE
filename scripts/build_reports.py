"""Build Assignment 03 reports from preserved, real evidence.

Run after evidence/prototype-access.json is present. The PDF operation marker
was already executed once by the root agent before this authoring task.
"""

from __future__ import annotations

from datetime import date
from html import escape
from io import BytesIO
import json
from pathlib import Path
import re
import shutil
import fitz

from PIL import Image as PILImage
from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Flowable, Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate,
    Spacer, Table, TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "A3_Boranov_Daniyar"
EVIDENCE = PACKAGE / "evidence"
SHOTS = EVIDENCE / "screenshots"
RESULTS = EVIDENCE / "test-results"
OUTPUT = ROOT / "output" / "pdf"
QA = EVIDENCE / "report-qa"
W = A4[0] - 96

FONT_DIR = Path("/System/Library/Fonts/Supplemental")
for family, filename in (
    ("Academic", "Arial.ttf"), ("AcademicBold", "Arial Bold.ttf"),
    ("AcademicItalic", "Arial Italic.ttf"), ("Code", "Courier New.ttf"),
):
    pdfmetrics.registerFont(TTFont(family, str(FONT_DIR / filename)))
pdfmetrics.registerFontFamily(
    "Academic", normal="Academic", bold="AcademicBold", italic="AcademicItalic",
    boldItalic="AcademicBold",
)

STYLES = {
    "title": ParagraphStyle("Title", fontName="AcademicBold", fontSize=19,
                            leading=23, spaceAfter=10),
    "subtitle": ParagraphStyle("Subtitle", fontName="Academic", fontSize=12,
                               leading=16, spaceAfter=10),
    "h1": ParagraphStyle("Heading", fontName="AcademicBold", fontSize=13,
                         leading=17, spaceBefore=8, spaceAfter=7, keepWithNext=True),
    "h2": ParagraphStyle("Subheading", fontName="AcademicBold", fontSize=10.5,
                         leading=14, spaceBefore=7, spaceAfter=5, keepWithNext=True),
    "body": ParagraphStyle("Body", fontName="Academic", fontSize=10.5,
                           leading=14.1, spaceAfter=7, splitLongWords=True),
    "small": ParagraphStyle("Small", fontName="Academic", fontSize=9.1,
                            leading=12, spaceAfter=5, splitLongWords=True),
    "caption": ParagraphStyle("Caption", fontName="Academic", fontSize=8.5,
                              leading=11.2, spaceAfter=7, splitLongWords=True),
    "cell": ParagraphStyle("Cell", fontName="Academic", fontSize=8.4,
                           leading=11.1, spaceAfter=0, splitLongWords=True),
    "cellsmall": ParagraphStyle("CellSmall", fontName="Academic", fontSize=7.9,
                                leading=10.5, spaceAfter=0, splitLongWords=True),
    "cellhead": ParagraphStyle("CellHead", fontName="AcademicBold", fontSize=8.2,
                               leading=10.7, spaceAfter=0, splitLongWords=True),
    "raw": ParagraphStyle("RawEvidence", fontName="Academic", fontSize=9.2,
                          leading=12.4, spaceAfter=6, splitLongWords=True),
    "code": ParagraphStyle("Code", fontName="Code", fontSize=8.7,
                           leading=11, spaceAfter=7),
}


def p(text, style="body", markup=False):
    return Paragraph(text if markup else escape(text).replace("\n", "<br/>"), STYLES[style])


def h(text):
    return p(text, "h1")


def sub(text):
    return p(text, "h2")


def paragraphs(text, style="body"):
    return [p(block.strip(), style) for block in text.strip().split("\n\n") if block.strip()]


def table(headers, rows, widths, small=False):
    cell_style = "cellsmall" if small else "cell"
    data = [[p(x, "cellhead") for x in headers]]
    data += [[p(str(x), cell_style) for x in row] for row in rows]
    result = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    result.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eeeeee")),
        ("LINEABOVE", (0, 0), (-1, 0), 0.6, colors.black),
        ("LINEBELOW", (0, 0), (-1, 0), 0.6, colors.black),
        ("LINEBELOW", (0, 1), (-1, -1), 0.35, colors.HexColor("#aaaaaa")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return result


def image(name, width, crop=None):
    source = PILImage.open(SHOTS / name)
    if crop:
        source = source.crop(crop)
    buf = BytesIO()
    source.save(buf, format="PNG")
    buf.seek(0)
    return Image(buf, width=width, height=width * source.height / source.width)


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.black)
    canvas.setLineWidth(0.35)
    canvas.line(48, 36, A4[0] - 48, 36)
    canvas.setFont("Academic", 8)
    canvas.setFillColor(colors.black)
    canvas.drawString(48, 23, "Software Engineering Assignment 03 | Boranov Daniyar | 24B031718")
    canvas.drawRightString(A4[0] - 48, 23, str(doc.page))
    canvas.restoreState()


class AgentLoop(Flowable):
    def __init__(self):
        super().__init__()
        self.width = W
        self.height = 68

    def draw(self):
        labels = ["User goal", "Model/Plan", "Tool call", "Observation", "Next step", "Human review"]
        box_w = 72
        gap = (W - 6 * box_w) / 5
        c = self.canv
        c.setStrokeColor(colors.black)
        c.setFillColor(colors.white)
        c.setLineWidth(0.6)
        for i, label in enumerate(labels):
            x = i * (box_w + gap)
            c.setFillColor(colors.white)
            c.rect(x, 20, box_w, 30, stroke=1, fill=1)
            c.setFillColor(colors.black)
            c.setFont("Academic", 8.2)
            c.drawCentredString(x + box_w / 2, 31, label)
            if i < 5:
                a, b = x + box_w + 2, x + box_w + gap - 2
                c.line(a, 35, b, 35)
                c.line(b - 3, 38, b, 35)
                c.line(b - 3, 32, b, 35)


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def approved_blocks():
    request = (EVIDENCE / "ai-exchanges" / "user-request-exact.txt").read_text(encoding="utf-8")
    def between(first, last):
        return request.split(first, 1)[1].split(last, 1)[0].strip()
    return {
        "scope": between("### Scope Statement", "### Initial Assumptions"),
        "assumptions": between("### Initial Assumptions", "### Possible Failure Points"),
        "failure_points": between("### Possible Failure Points", "### Function Contract"),
        "contract": between("### Function Contract", "### Initial Manual Verification Plan"),
        "manual": between("### Initial Manual Verification Plan", "Preserve this baseline"),
    }


def access_items(access, style="small"):
    result = []
    for label, key in (
        ("Bolt.new project", "bolt_project_url"),
        ("Public live demo", "public_demo_url"),
        ("GitHub repository", "github_repository_url"),
    ):
        url = access.get(key)
        if url:
            result.append(p(f'<b>{label}:</b> <link href="{escape(url, quote=True)}" color="black"><u>{escape(url)}</u></link>', style, True))
        else:
            result.append(p(f"{label}: no verified public deployment is recorded.", style))
    return result


def publication_summary(access):
    if access.get("public_access_verified") and access.get("latest_version_verified"):
        count = access.get("mandatory_cases_passed")
        if isinstance(count, bool):
            count = "all six" if count else "not established"
        return f"Public access and the latest version were verified. Mandatory published-page cases passed: {count}. Checked: {access.get('checked_at', 'see access record')}."
    return "The final source is tested locally. Public access to the latest deployed version is not fully verified; the exact remaining publication action is recorded in Final verification."


REFLECTION = (
    "I see AI-assisted coding as a careful process: plan the rules, review the proposed code, and test real results. "
    "Vibe coding can produce a useful first page quickly, but a good-looking page can still break a requirement. "
    "In this project, the generated add and delete controls were removed because AC5 requires availability checking only. "
    "A reliability risk was the old Available result remaining visible after the room became blocked. "
    "A usability risk was offering an invalid start hour, while a security risk comes from vulnerable dependencies and broad tool permissions. "
    "I understand why code review remains a human responsibility: AI statements about correctness need evidence. "
    "Tools should have only the access needed for the task, and changes should be recoverable. "
    "The executed tests give stronger support than a successful build alone. "
    "I would next improve keyboard and screen-reader testing and address the remaining dependency advisories, while keeping the same one-room scope."
)


def build_main(access, audit):
    blocks = approved_blocks()
    vulns = audit.get("metadata", {}).get("vulnerabilities", {})
    audit_text = ", ".join(f"{vulns.get(k, 0)} {k}" for k in ("low", "moderate", "high", "critical"))
    source_commit = access.get("source_commit", "7864b494c4cd2aecbad3725c1ef34c3aa82af097")
    story = []
    def page(items):
        if story:
            story.append(PageBreak())
        story.extend(items)

    # 1: Academic front page with actual access links and the complete scope.
    page([
        p("Software Engineering Assignment #03", "title"),
        p("Smart Campus Room Availability Checker", "subtitle"),
        p("Boranov Daniyar  |  Student ID: 24B031718\nClass: Thursday 14:00–17:00  |  23 October 2026", "body"),
        h("1. Prototype Access"),
        *access_items(access),
        p(publication_summary(access), "small"),
        p("The GitHub repository is private; the complete source is included in the submission package.", "small"),
        h("2. Project overview and approved scope"),
        *paragraphs(blocks["scope"]),
        sub("Project baseline"),
        p("This Assignment #03 continues the existing Bolt.new project. The original React and TypeScript application was preserved before cleanup. The fixed demonstration data is room A-102, now=540 (09:00), blocked=False and one existing interval 600–660 (10:00–11:00)."),
        p("Original commit: 687c5f7bbcb29590ad3030cf5e596431be5971b7. Recoverable tag: prototype-v1. The source archive and original files are retained under evidence/original-v1/.", "small"),
        p("The project has no login, database, backend, external API, payments or booking confirmation. All room and booking data is fictional.", "small"),
    ])

    assumptions = [line[2:] for line in blocks["assumptions"].splitlines() if line.startswith("- ")]
    failures = blocks["failure_points"].replace("**", "")
    contract = blocks["contract"].replace("`", "")
    page([
        h("3. Initial assumptions and failure points"),
        sub("Initial assumptions"),
        *[p("• " + line, "small") for line in assumptions],
        sub("Possible failure points"),
        *paragraphs(failures, "small"),
        h("4. Function contract and initial manual plan"),
        *paragraphs(contract, "small"),
        sub("Initial manual verification plan"),
        *paragraphs(blocks["manual"], "small"),
        sub("Plan review"),
        p('The cleanup plan preserves v1, keeps AC1–AC6 fixed, removes booking editing, clears stale results, fixes the Start picker and verifies Python, frontend and mobile behavior. The recorded response to this plan was: “Approve this plan”.', "small"),
        p("The requirements above retain the supplied baseline. The exact plan-review question and reply are preserved in evidence/ai-exchanges/personal-plan-review.json.", "caption"),
    ])

    page([
        h("5. Acceptance criteria"),
        table(["ID", "Fixed requirement"], [
            ["AC1", "Integer start/end; 0 <= start < end <= 1440; start > now. Assume now is valid in 0–1439."],
            ["AC2", "Maximum duration 120 minutes. Exactly 120 is valid; 121 is invalid."],
            ["AC3", "Reject every request when the selected room is blocked."],
            ["AC4", "Reject overlap with any existing booking. Half-open intervals may touch at either endpoint."],
            ["AC5", "Return/display Available or Unavailable; do not create, confirm, delete, modify or mutate bookings."],
            ["AC6", "Give clear validation feedback and a usable narrow/mobile layout without horizontal overflow."],
        ], [43, W - 43]),
        h("6. Python implementation overview"),
        p("booking.py defines can_book(start, end, now, blocked, existing). It returns a built-in Boolean and uses only Python 3 features. The first generated file was saved as booking-v1.py before testing. All 47 test methods passed for v1 and final; no Python repair was needed."),
        table(["Check", "Reason and boundary"], [
            ["Exact integer types", "AC1: reject float, string, None and bool before arithmetic."],
            ["Bounds and ordering", "AC1: reject negative, equal, reversed and out-of-day intervals; permit end=1440."],
            ["start <= now", "AC1: reject the past and equality; a start one minute later can pass."],
            ["end - start > 120", "AC2: reject 121; permit 120 when other rules pass."],
            ["blocked", "AC3: reject a blocked room."],
            ["Loop and strict overlap", "AC4: start < booked_end and end > booked_start; check later bookings too."],
            ["Final True", "AC5: only reached after every check; read arguments without changing them."],
        ], [118, W - 118]),
        p("The complete branch review is in evidence/python-review.md. Valid now, Boolean blocked and well-formed existing intervals are contract assumptions; malformed existing data is outside the required scope.", "caption"),
    ])

    page([
        h("7. Existing Bolt.new prototype"),
        p("The existing stack was retained: React 18, TypeScript, Vite, Tailwind CSS and Lucide icons. No replacement application or broad redesign was created. The one-room fixture, component structure and six examples remain."),
        table(["File or component", "Role in the final prototype"], [
            ["src/main.tsx / App.tsx", "Mount React and coordinate selected times, blocked state and the latest result."],
            ["src/utils/availability.ts", "Validate AC1–AC4 and return a clear status/message without changing inputs."],
            ["src/utils/time.ts", "Format integer minutes as HH:MM; preserve the 24:00 end boundary."],
            ["src/data/sampleData.ts", "Store the fixed fictional room, demo time, frozen bookings and example cases."],
            ["TimeControls / RoomCard", "Hour/minute selects; blocked-room toggle. Start 00–23; End may use 24:00."],
            ["BookingsSection", "Display the fictional booking list as read-only."],
            ["ResultPanel / ExampleCases", "Present Available/Unavailable and reasons; load the six fixture scenarios."],
            ["Header / CurrentTimeBadge", "Identify the tool and clearly label 09:00 as a fixed demo time."],
        ], [156, W - 156]),
        h("8. Workflow, preservation and cleanup"),
        p("Plan: retain the supplied scope and boundary checks. Generate: preserve Python v1 and the original Bolt source. Critique: compare every rule with source and browser behavior. Repair: make focused changes for three reproduced issues. Verify: rerun the complete tests and inspect real desktop/mobile output."),
        p("Before editing, the original Git hash was recorded, the prototype-v1 tag was created, and the source was archived. No original screenshots were present in the repository, so v1 was served from the preserved version and genuine before screenshots were captured. The original Bolt prompt and rendered response were recovered from the project chat."),
        p("Cleanup removed add/delete booking paths, cleared stale results on time/status changes, fixed Start hour choices and added polite status semantics. Unused Supabase and a missing favicon reference were removed. Compatible lockfile updates reduced dependency advisories without changing the application rules."),
        p("The independent archive check compared all 28 archived files with the original tag and found no mismatch. The first Python implementation also remains byte-identical to final.", "small"),
    ])

    page([
        h("9. Executed testing results"),
        p("Both implementations were executed, not only read. The same Python suite and the same frontend validator suite were used for v1 and final. Browser checks exercised the actual rendered controls and status panels."),
        table(["Test group", "Original v1", "Final"], [
            ["Python unittest", "47/47; exit 0", "47/47; exit 0"],
            ["Actual frontend validator", "37/37; exit 0", "37/37; exit 0"],
            ["Browser mandatory fixtures", "6/6", "6/6"],
            ["Browser additional boundaries", "10/10", "10/10"],
            ["Browser repair checks", "3 defects reproduced", "8/8 checks pass"],
            ["Responsive layout", "320 px: no overflow", "320/375/768/1440 px: 4/4"],
            ["Lint / typecheck / build", "All exited 0", "All exited 0"],
        ], [231, 134, W - 365]),
        sub("Six mandatory scenarios"),
        p("Base: now=540, blocked=False, existing=[(600,660)]. Case 3 sets blocked=True. True means Available; False means Unavailable.", "small"),
        table(["Request", "Expected", "Python v1 / final", "Browser v1 / final"], [
            ["660–720", "True", "True / True", "Available / Available"],
            ["630–690", "False", "False / False", "Unavailable / Unavailable"],
            ["660–720, blocked", "False", "False / False", "Unavailable / Unavailable"],
            ["720–840 (120 min)", "True", "True / True", "Available / Available"],
            ["720–841 (121 min)", "False", "False / False", "Unavailable / Unavailable"],
            ["540–570 (starts now)", "False", "False / False", "Unavailable / Unavailable"],
        ], [133, 64, 127, W - 324]),
        sub("Boundary and preservation checks"),
        p("Additional cases covered reversed/equal times, negative and out-of-day values, invalid types, both touching endpoints, containment, overlap in later/unsorted bookings, the last day minute and end=1440. Frozen or nested input data remained unchanged. Browser checks confirmed invalid-time reasons and no controls outside the viewport."),
        p("The 37 frontend logic cases also passed after each of the three focused repairs and after compatible dependency updates. A separate review reran Python 47/47 and frontend 37/37. These results do not claim screen-reader testing or live-site deployment unless listed separately.", "small"),
    ])

    page([
        h("10. Acceptance traceability"),
        p("V1 and final actual columns use executed evidence. Passing validator cases in v1 did not establish that the whole original page met AC5 or AC6.", "small"),
        table(["AC ID", "Implementation/file", "Test input", "Expected", "V1 actual", "Final actual"], [
            ["AC1", "booking.py; availability.ts", "540–570; reversed/equal; bad type/day bound", "Reject", "Reject; suites pass", "Reject; suites pass"],
            ["AC1", "TimeControls.tsx", "11:30, then Start hour 24", "No invalid Start option", "1470 min; label 24:00", "Start only 00–23"],
            ["AC2", "booking.py; availability.ts", "720–840 / 720–841", "True / False", "True / False", "True / False"],
            ["AC3", "Both validators; RoomCard", "660–720; blocked=True", "Unavailable", "Fresh check rejects", "Rejects; old result clears"],
            ["AC4", "Both validators", "660–720 and 550–600; existing 600–660", "Both Available", "Both Available", "Both Available"],
            ["AC4", "Both validators", "630–690; later-booking overlap", "Reject all overlap", "Rejected", "Rejected"],
            ["AC5", "App; BookingsSection; data", "Delete base booking; repeat checks", "Read-only bookings", "Delete changes list", "No edit controls; unchanged"],
            ["AC5", "Both validators", "Available/rejected calls; frozen/nested inputs", "Boolean/status; no mutation", "No validator mutation", "No validator mutation"],
            ["AC6", "App; ResultPanel", "Check Available, toggle blocked; invalid start", "Clear, current feedback", "Stale Available remains", "Clears; reason on check"],
            ["AC6", "Responsive layout", "V1:320; final:320,375,768,1440 px", "No overflow; usable controls", "320 px passes", "All 4 widths pass"],
        ], [34, 90, 112, 81, 88, W - 405], small=True),
        sub("Evidence map"),
        p("Python: python-v1.* / python-final.* and python-review.md. Validator: frontend-v1-logic.tap / frontend-final-test.tap and after-*-repair.tap. Browser: browser-{v1,final}-{mandatory,boundaries}.json, browser-v1-issues.json, browser-v1-picker.txt, browser-final-repair-checks.json and browser-final-layout.json. All are under evidence/test-results/ except the review note.", "small"),
        p("Screenshots document the visible state; JSON/TAP/unittest records provide the full executed cases and raw output. The original source remains available for reproducing the before behavior.", "small"),
    ])

    before_after = Table([
        [p("BEFORE: v1 room blocked", "caption"), p("AFTER: final room blocked", "caption")],
        [image("v1-blocked-badge-detail.jpg", 238), image("final-blocked-badge-detail.jpg", 238)],
        [image("v1-stale-result-detail.jpg", 238), image("final-stale-result-detail.jpg", 238)],
    ], colWidths=[W / 2, W / 2], hAlign="LEFT")
    before_after.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    page([
        h("11. Issue log"),
        table(["Issue", "Reproduction", "Priority", "Prompt/change", "Retest result"], [
            ["F01: AC5 booking editing", "V1: remove 10:00–11:00; list becomes empty. Add/remove controls exist.", "High", "Keep fixture read-only; remove controls/handlers; freeze data and use readonly types.", "No management buttons; list unchanged across cases; logic 37/37."],
            ["F02: stale result", "Check 11:00–12:00, then mark room blocked. Old Available remains.", "High", "Clear result after either time or blocked status changes; add polite live status.", "All 3 changes clear result; blocked recheck rejects; logic 37/37."],
            ["F03: Start hour 24", "Set Start 11:30, then hour 24. State=1470; display=24:00.", "Medium", "Start 00–23 only; End 24:00 forces minute zero; retain validator.", "Start option fixed; End minute 0; 23:59–24:00 valid; logic 37/37."],
        ], [72, 118, 44, 142, W - 376], small=True),
        p("Focused prompt text and complete repair response are preserved in exchange 04; source critique and browser reproduction records establish the original findings. No defect was introduced to create evidence.", "caption"),
        h("12. Before and after: stale blocked result"),
        before_after,
        p("Figure 1. Genuine browser detail captures at the same 1440 px viewport. After an Available check, the room is marked blocked. V1 retains Available; final clears the previous result and asks for a new check. Full original screenshots and native detail captures are retained in evidence/screenshots/.", "caption"),
        p("Preventive cleanup removed an unused dependency and a missing favicon reference. Compatible lockfile repairs reduced the recorded audit from 13 advisories to the final count reported in section 16; application rules and layout were retained.", "small"),
    ])

    # Readable result details accompany a desktop overview and narrow viewport.
    desktop = image("final-desktop.jpg", 340, crop=(230, 100, 1210, 920))
    mobile = image("final-mobile-320.jpg", 119, crop=(0, 0, 320, 1350))
    left_gallery = [
        desktop, p("Figure 2. Final desktop interface; original 1440 px capture.", "caption"),
        image("final-available.jpg", 340, crop=(728, 735, 1208, 849)),
        p("Figure 3. Available: endpoint touch, 660–720.", "caption"),
        image("final-overlap.jpg", 340, crop=(728, 735, 1208, 865)),
        p("Figure 4. Unavailable: overlap, 630–690.", "caption"),
    ]
    right_gallery = [mobile, p("Figure 5. 320 px layout detail. Full-height capture is included in evidence.", "caption")]
    gallery = Table([[left_gallery, right_gallery]], colWidths=[363, W - 363], hAlign="LEFT")
    gallery.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    small_results = Table([
        [image("final-blocked.jpg", 238, crop=(728, 735, 1208, 849)),
         image("final-invalid-start-now.jpg", 238, crop=(728, 735, 1208, 865))],
        [p("Figure 6. Blocked request is Unavailable.", "caption"),
         p("Figure 7. Starts-now validation explains the strict future rule.", "caption")],
    ], colWidths=[W / 2, W / 2])
    small_results.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    page([
        h("13. Final prototype evidence"),
        p("These are genuine browser captures. Details show only selected original screenshot regions; full files preserve the complete context.", "caption"),
        gallery,
        small_results,
        p("All final tested widths (320, 375, 768 and 1440 px) had no horizontal overflow or controls outside the viewport. The availability flow worked at each width. Full Available, overlap, blocked, invalid, 120/121-minute, desktop and mobile screenshots are included in the evidence directory.", "caption"),
    ])

    page([
        h("14. Coding-agent analysis"),
        AgentLoop(),
        p("Figure 8. Observable coding-agent loop. An observation may lead to another tool call and test before the result is accepted.", "caption"),
        sub("Context, tools and permissions"),
        p("The assistants used the assignment PDF, supplied requirements, existing repository, Bolt chat, source code, tests and browser observations. Observed tools included shell and file operations, Git, Python unittest, Node's test runner, npm quality checks, browser controls and PDF generation/rendering. The workspace permitted file changes, process execution and network access. Git and GitHub REST published the build using the existing repository credential helper. The Bolt browser workspace was blocked by a startup failure."),
        sub("Observed behavior and limits"),
        p("The evidence shows files read and written, commands executed, returned output, screenshots and recorded results. It does not show hidden model reasoning or internal Bolt architecture. Bolt displayed Standard mode, not a model identifier. The exact model names were not displayed for the recorded exchanges."),
        sub("Safety checkpoint and responsibility"),
        p("Before generated changes were accepted, the baseline source was preserved. The approved plan was checked against the fixed criteria, and execution records support acceptance. Read-only source review and real tests separated predictions from observed behavior."),
        p("Recovery through the original tag supports reliability. Clear current feedback supports usability and availability. Limited permissions, no unnecessary service integration and dependency review reduce security risk. Human review remains responsible for accepting the scope, checking the evidence and deciding what to submit."),
        h("15. Reflection"),
        p(REFLECTION),
        p(f"Reflection length: {len(REFLECTION.split())} words.", "caption"),
    ])

    remaining = [str(x) for x in access.get("notes", [])]
    publication_rows = [
        ["Source committed", str(source_commit)],
        ["Original recovery point", "prototype-v1 at 687c5f7bbcb29590ad3030cf5e596431be5971b7"],
        ["Public sign-in-free access", "Verified" if access.get("public_access_verified") else "Not fully verified"],
        ["Latest deployed version", "Verified" if access.get("latest_version_verified") else "Not fully verified"],
        ["Published mandatory flow", f"{access['mandatory_cases_passed']}/6 passed" if access.get("mandatory_cases_passed") == 6 else str(access.get("mandatory_cases_passed", "Not verified"))],
        ["Access check time", str(access.get("checked_at", "See prototype-access.json"))],
    ]
    page([
        h("16. Final verification and limitations"),
        table(["Check", "Recorded result"], publication_rows, [157, W - 157]),
        *[p(note, "small") for note in remaining],
        sub("Quality and remaining limits"),
        p("The final Python suite, frontend logic suite, lint, TypeScript check and production build passed. Source, original v1 evidence, actual test logs, screenshots, AI exchanges and the access record are included. The final documents were rendered and inspected for layout; the QA record is under evidence/report-qa/.", "small"),
        p(f"The last recorded dependency audit contains {vulns.get('total', sum(vulns.get(k, 0) for k in ('low', 'moderate', 'high', 'critical')))} advisories ({audit_text}). Compatible transitive updates were applied. The remaining Tailwind/PostCSS chain proposes a Tailwind major-version migration; other residual advisories also remain for later review. A broad upgrade was not forced during this focused cleanup. These counts describe the recorded audit, not a vulnerability-free project.", "small"),
        p("Keyboard and screen-reader behavior was not fully tested. Polite live-status attributes were verified, but no screen-reader outcome is claimed. The application uses a fixed demo clock and fictional data; it does not check real campus room availability.", "small"),
        sub("References"),
        p("[1] Software Engineering Assignment #03, supplied 30-page PDF. Scope and criteria: pp. 8–10; planning/Python/prototype/tests: pp. 11–14; cleanup/agent analysis: pp. 15–19; evidence/reflection: pp. 20–23; submission: pp. 28–29.", "small"),
        p("[2] Lesson #05 and Lesson #06 references listed in the assignment, pp. 25–26. Lecture materials were not separately provided; no additional claims are attributed to them.", "small"),
        p("[3] Existing Bolt.new project, preserved Git tag prototype-v1, final repository source, and original chat. Access links are on page 1 and repeated in README.md.", "small"),
        p("[4] Local evidence: Python unittest logs; frontend TAP/quality/audit logs; browser JSON and screenshots; independent integrity review; prototype-access.json; AI_Evidence.pdf and exact exchange text files.", "small"),
        sub("Reproduction"),
        p("Python: python3 -m unittest -v test_booking. Frontend: npm ci; npm test; npm run lint; npm run typecheck; npm run build. Serve the existing source with npm run dev. Full setup, source recovery and exact access notes are in README.md.", "small"),
    ])
    path = OUTPUT / "A3_Boranov_Daniyar_Report.pdf"
    doc = SimpleDocTemplate(str(path), pagesize=A4, leftMargin=48, rightMargin=48,
                            topMargin=39, bottomMargin=48, title="Software Engineering Assignment 03 - Boranov Daniyar",
                            author="Boranov Daniyar", subject="Smart Campus Room Availability Checker")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return path, blocks


def build_ai(access):
    story = [
        p("AI Evidence", "title"),
        p("Software Engineering Assignment #03\nBoranov Daniyar | 24B031718\n23 October 2026", "subtitle"),
        h("Evidence scope and tool record"),
        p("This document preserves genuine observed Bolt.new material and actual delegated Codex exchanges from the implementation, critique, repair and verification workflow. Sub-agent tasks are labeled as delegated exchanges, not separate historical user conversations. Complete raw text files remain under evidence/ai-exchanges/."),
        p("Bolt.new displayed Standard mode; its exact model was not displayed. The exact model identifier for the recorded Codex exchanges was not displayed. Date of use: 23 October 2026, Asia/Almaty. The original Bolt prompt contains 4036 characters and its complete rendered final response contains 2632 characters. Tool output, source changes, tests and screenshots are preserved separately."),
        p("Original Bolt correctness statements below are historical claims. Later source and browser checks established add/delete controls, a stale result and a Start-hour inconsistency. Those claims were reviewed and corrected rather than accepted automatically."),
        sub("Real plan review"),
    ]
    review = load_json(EVIDENCE / "ai-exchanges" / "personal-plan-review.json")
    story.extend([p("Exact question", "h2"), *paragraphs(review["question"], "raw"),
                  p("Exact user response", "h2"), *paragraphs(review["answer"], "raw")])
    story.extend([
        sub("Workflow and decisions"),
        p("A. Plan: retain supplied AC1–AC6 and record boundary checks. B. Generate: preserve original Bolt v1 and first Python implementation. C. Critique: inspect each branch and reproduce three UI issues. D. Repair: remove booking management, clear stale feedback and correct the picker; then apply compatible dependency updates. E. Verify: rerun tests and inspect browser/PDF output."),
        p("The generated recommendation to support adding/removing demo bookings was rejected in cleanup because it conflicts with fixed AC5. Python v1 passed its full suite and required no repair. A later dependency pass supersedes the earlier 13-advisory snapshot; the earlier response is retained unchanged as historical evidence."),
    ])
    exchange_info = [
        ("01", "Original Bolt.new generation", "01-bolt-prompt.txt", "01-bolt-response.txt",
         "Original project chat exported from the Pasted Content dialog and complete rendered final response. The opening/tool-status transcript is also included after this response."),
        ("02", "Codex delegated Python implementation", "02-python-prompt.txt", "02-python-response.txt",
         "Actual root-agent task and complete sub-agent final response. The pre-generation plan and branch review are separate evidence files."),
        ("03", "Codex delegated original-source critique", "03-critique-prompt.txt", "03-critique-response.txt",
         "Actual source-review exchange. Predictions in the response were explicitly separated from later browser execution."),
        ("04", "Codex delegated focused frontend repair", "04-repair-prompt.txt", "04-repair-response.txt",
         "Actual repair exchange. The root agent captured v1 before application changes and performed the rendered checks."),
        ("05", "Codex delegated independent final verification", "05-verify-prompt.txt", "05-verify-response.txt",
         "Actual verification exchange. This review independently executed Python and frontend logic tests; it reviewed rather than reran browser operations."),
    ]
    if (EVIDENCE / "ai-exchanges" / "06-dependencies-response.txt").exists():
        exchange_info.append(("06", "Codex delegated compatible dependency repair", "06-dependencies-prompt.txt", "06-dependencies-response.txt",
                              "Actual targeted dependency exchange after the earlier audit snapshot. Final audit results and test logs are retained."))
    for num, name, prompt_name, response_name, note in exchange_info:
        story.extend([PageBreak(), h(f"Exchange {num}. {name}"), p(note, "small"),
                      sub("Exact prompt"), *paragraphs((EVIDENCE / "ai-exchanges" / prompt_name).read_text(encoding="utf-8"), "raw"),
                      sub("Complete response"), *paragraphs((EVIDENCE / "ai-exchanges" / response_name).read_text(encoding="utf-8"), "raw")])
        if num == "01":
            story.extend([sub("Original opening text and observed tool statuses"),
                          *paragraphs((EVIDENCE / "ai-exchanges" / "01-bolt-observed-chat.txt").read_text(encoding="utf-8"), "raw")])
    story.extend([PageBreak(), h("Review and evidence index"),
                  p("The exact user task is preserved in user-request-exact.txt. The initial requirements, assumptions and manual plan are reproduced in the main report. No claim is made about when that baseline was independently written."),
                  table(["Stage", "Evidence and outcome"], [
                      ["Plan", "python-plan.md; supplied baseline; exact plan-review approval JSON."],
                      ["Generate", "Original Bolt source/tag/archive; original prompt and response; booking-v1.py."],
                      ["Critique", "original-v1/source-review.md; browser-v1-issues.json; browser-v1-picker.txt."],
                      ["Repair", "Final source diff; 04 repair exchange; frontend-after-*-repair.tap; screenshots."],
                      ["Verify", "Python 47/47; frontend 37/37; independent reruns; browser 6+10+8 checks and four widths."],
                      ["Access", "prototype-access.json records exact URLs and publication checks; do not infer deployment from Git commits."],
                  ], [80, W - 80]),
                  p("Tests and tool actions were executed by the assistants, with the exact observed user plan approval preserved above. Hidden internal model reasoning and unobserved screen-reader behavior are not claimed."),
                  *access_items(access),
                  p(publication_summary(access), "small")])
    path = OUTPUT / "AI_Evidence.pdf"
    doc = SimpleDocTemplate(str(path), pagesize=A4, leftMargin=48, rightMargin=48,
                            topMargin=42, bottomMargin=48, title="AI Evidence - Assignment 03",
                            author="Boranov Daniyar", subject="Genuine Bolt and delegated Codex exchanges")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return path, exchange_info


def write_readme(access, audit):
    vulns = audit.get("metadata", {}).get("vulnerabilities", {})
    rows = []
    for label, key in (("Bolt.new project/editor", "bolt_project_url"), ("Public live demo", "public_demo_url"), ("GitHub repository", "github_repository_url")):
        url = access.get(key)
        rows.append(f"- {label}: [{url}]({url})" if url else f"- {label}: no verified deployment URL is available; see access notes below.")
    notes = "\n".join(f"- {note}" for note in access.get("notes", []))
    text = f"""# Software Engineering Assignment #03

**Boranov Daniyar** · **24B031718** · **Thursday 14:00–17:00** · **23 October 2026**

Smart Campus Room Availability Checker. This package continues the original Bolt.new React/TypeScript/Vite project. It checks one fictional room and never creates, confirms, changes or deletes bookings.

## Prototype access

{chr(10).join(rows)}

{publication_summary(access)}

{notes}

The exact access record is `evidence/prototype-access.json`. GitHub source updates alone do not establish that Bolt has deployed the same version.

## Submission files

- `A3_Boranov_Daniyar_Report.pdf`: academic report, criteria, traceability, issues, evidence, agent analysis and reflection.
- `AI_Evidence.pdf`: exact genuine prompts and complete responses, actual approval record and review chain.
- `booking.py`, `test_booking.py`: Python implementation and 47 runnable unittest methods.
- `prototype/`: final existing React/Vite application source and frontend test harness.
- `evidence/original-v1/`: preserved source, ZIP archive, baseline metadata and the first Python implementation.
- `evidence/screenshots/`: genuine original/final browser captures and native detail captures.
- `evidence/test-results/`: actual stdout/stderr, TAP, JSON, quality checks, audit and browser records.
- `evidence/report-qa/`: final document render and layout-check metadata.

## Run Python checks

Use Python 3, standard library only, from this directory:

```sh
python3 -m unittest -v test_booking
```

The same full suite passed against v1 and final: **47/47**, exit 0, with no failures, errors or skips. Python v1 and final are byte-identical. `now` is valid in 0–1439; `blocked` is Boolean; existing intervals are well-formed integer-minute pairs. Start/end reject bool and other non-integer types.

## Run the prototype

Use Node.js and npm. From `prototype/`:

```sh
npm ci
npm run dev
```

Open the local URL printed by Vite. The fictional base fixture is room A-102, now 540 (09:00), blocked false and booking 600–660 (10:00–11:00).

```sh
npm test
npm run lint
npm run typecheck
npm run build
npm run preview
```

The frontend validator suite passed **37/37** for v1, after each focused repair and final. Lint, typecheck and production build exited 0. Browser tests passed the mandatory **6/6**, additional boundaries **10/10**, repair checks **8/8**, and all four layout widths **320, 375, 768, 1440 px** without horizontal overflow or outside controls. A separate review reran Python 47/47 and frontend 37/37.

## Recover original v1

The original commit is `687c5f7bbcb29590ad3030cf5e596431be5971b7`; tag `prototype-v1`. In a repository checkout, inspect without replacing current files:

```sh
git show prototype-v1:src/App.tsx
git worktree add ../prototype-v1-review prototype-v1
```

An archived copy is also in `evidence/original-v1/prototype-v1-source.zip`. Independent integrity review checked all 28 archive files against the tag with no mismatches. The current source commit is recorded in `evidence/prototype-access.json`; later documentation/package commits may follow it.

## Focused changes

1. Removed booking add/delete controls and state paths; frozen, readonly fictional data.
2. Cleared stale outcomes after either time or blocked-status changes; polite live status semantics.
3. Limited Start to 00–23; End supports 24:00 only with minute zero.
4. Removed unused Supabase and missing favicon reference; compatible transitive lockfile updates.

## Limitations and final checks

- Fixed fictional data and a supplied demo clock; no real campus data or booking service.
- Latest recorded dependency audit: {vulns.get('total', 0)} advisories ({vulns.get('low', 0)} low, {vulns.get('moderate', 0)} moderate, {vulns.get('high', 0)} high, {vulns.get('critical', 0)} critical). The remaining Tailwind/PostCSS chain proposes a Tailwind major migration; other residual advisories also need later review. A broad upgrade was not forced.
- Screen-reader and complete keyboard behavior were not executed; live-region attributes were checked.
- Publication and latest-version status are stated explicitly above. Follow the exact remaining action in the access notes if either is unverified.

All reported PASS results are supported by actual execution records. Original AI correctness statements are retained as historical evidence and are not substituted for the observed tests.
"""
    (PACKAGE / "README.md").write_text(text, encoding="utf-8")


def render_for_qa(paths):
    """Render every page, with contact sheets for complete-page layout review."""
    render_root = Path("/tmp/a3-pdf-render")
    render_root.mkdir(parents=True, exist_ok=True)
    rendered = {}
    for path in paths:
        doc = fitz.open(path)
        images = []
        folder = render_root / path.stem
        folder.mkdir(parents=True, exist_ok=True)
        for i, page in enumerate(doc):
            pix = page.get_pixmap(matrix=fitz.Matrix(110 / 72, 110 / 72), alpha=False)
            target = folder / f"page-{i + 1:02d}.png"
            pix.save(target)
            thumb = PILImage.open(target).convert("RGB")
            thumb.thumbnail((298, 421))
            images.append(thumb.copy())
        columns = 2
        for start in range(0, len(images), 6):
            subset = images[start:start + 6]
            rows = (len(subset) + columns - 1) // columns
            contact = PILImage.new("RGB", (columns * 308, rows * 431), "#cccccc")
            for j, im in enumerate(subset):
                contact.paste(im, ((j % columns) * 308 + 5, (j // columns) * 431 + 5))
            contact.save(folder / f"contact-{start // 6 + 1}.jpg")
        rendered[path.name] = {"renderer": "PyMuPDF", "dpi": 110, "pages_rendered": len(images), "folder": str(folder)}
    return rendered


def main():
    access_path = EVIDENCE / "prototype-access.json"
    if not access_path.exists():
        raise SystemExit("Waiting for evidence/prototype-access.json; refusing to invent access links.")
    access = load_json(access_path)
    audit_path = RESULTS / "frontend-post-dependency-audit.json"
    if not audit_path.exists():
        audit_path = RESULTS / "frontend-final-dependency-audit.json"
    audit = load_json(audit_path)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    QA.mkdir(parents=True, exist_ok=True)
    main_path, blocks = build_main(access, audit)
    ai_path, exchanges = build_ai(access)
    metadata = {"date": "2026-10-23", "reflection_word_count": len(REFLECTION.split()),
                "audit_source": str(audit_path.relative_to(ROOT)), "files": {},
                "exchange_count": len(exchanges), "approved_baseline": blocks,
                "render_review": "Pending visual inspection of latest rendered pages"}
    for path in (main_path, ai_path):
        reader = PdfReader(path)
        metadata["files"][path.name] = {
            "pages": len(reader.pages),
            "page_text_lengths": [len(pg.extract_text() or "") for pg in reader.pages],
            "link_uris": [str(annot.get_object().get("/A", {}).get("/URI"))
                          for pg in reader.pages for annot in pg.get("/Annots", [])
                          if annot.get_object().get("/A", {}).get("/URI")],
        }
        shutil.copy2(path, PACKAGE / path.name)
    if len(PdfReader(main_path).pages) != 10:
        raise SystemExit(f"Main report has {len(PdfReader(main_path).pages)} pages; expected exactly 10. Inspect overflow.")
    assert 100 <= len(REFLECTION.split()) <= 200
    write_readme(access, audit)
    metadata["renders"] = render_for_qa((main_path, ai_path))
    (QA / "report-build.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"report_pages": len(PdfReader(main_path).pages),
                      "ai_evidence_pages": len(PdfReader(ai_path).pages),
                      "reflection_words": len(REFLECTION.split()), "exchanges": len(exchanges)}, indent=2))


if __name__ == "__main__":
    main()
