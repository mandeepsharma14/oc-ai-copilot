from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
import os

os.makedirs("sample_docs", exist_ok=True)
styles = getSampleStyleSheet()
title_style = ParagraphStyle("title", parent=styles["Heading1"], fontSize=16, spaceAfter=12)
heading_style = ParagraphStyle("heading", parent=styles["Heading2"], fontSize=13, spaceAfter=8)
body_style = ParagraphStyle("body", parent=styles["Normal"], fontSize=11, spaceAfter=6, leading=16)

def make_pdf(filename, title, sections):
    doc = SimpleDocTemplate("sample_docs/" + filename, pagesize=letter,
                            rightMargin=inch, leftMargin=inch,
                            topMargin=inch, bottomMargin=inch)
    story = []
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 0.2*inch))
    for heading, paragraphs in sections:
        story.append(Paragraph(heading, heading_style))
        for p in paragraphs:
            story.append(Paragraph(p, body_style))
        story.append(Spacer(1, 0.15*inch))
    doc.build(story)
    print("Created: sample_docs/" + filename)

make_pdf("EHS-LOTO-003-SC.pdf",
    "LOTO Procedure - South Carolina Doors Assembly Line - Rev 4 - Approved Mar 2025",
    [
        ("1. Purpose and Scope", [
            "This procedure establishes the Lockout/Tagout LOTO requirements for the South Carolina Doors assembly line at the Aiken SC facility.",
            "Owner: SC Site EHS Manager. Applies to all maintenance technicians, operators, and contractors on the SC Doors assembly line."
        ]),
        ("2. Energy Sources", [
            "480V main electrical disconnect at Panel E-08.",
            "Pneumatic supply valves PV-201 through PV-206 operating at 120 PSI.",
            "Hydraulic press unit HP-01 operating at 3000 PSI.",
            "Foam injection heater circuit HT-04 operating at 350 degrees F."
        ]),
        ("3. Required PPE", [
            "Safety glasses with side shields at all times.",
            "Leather gloves for electrical components.",
            "Heat-resistant gloves near heater circuit HT-04.",
            "Steel-toed boots in all assembly areas."
        ]),
        ("4. LOTO Procedure Steps", [
            "Step 1: Notify all affected employees. Post IN-PROGRESS signage at all four entry points to the assembly zone.",
            "Step 2: Identify all energy sources. Review the energy isolation map at Station 1A.",
            "Step 3: De-energize the 480V disconnect at Panel E-08. Apply personal hasp lock with name tag. Verify with E-08 maintenance tag.",
            "Step 4: Close all pneumatic valves PV-201 through PV-206. Bleed lines to zero. All gauges DP-201 through DP-206 must read 0 PSI.",
            "Step 5: Release hydraulic energy in HP-01 by cycling dump valve DV-HP-01 twice. Verify gauge reads zero.",
            "Step 6: Allow heater HT-04 to cool below 120F using infrared thermometer at Station 4B. Cooldown takes 15 to 20 minutes.",
            "Step 7: Attempt to start line from local panel to verify zero energy state. Line must not start.",
            "Step 8: Document in SC LOTO logbook at Station 1A. Supervisor sign-off required for work exceeding 4 hours."
        ]),
        ("5. Restoring Equipment", [
            "Ensure all tools and personnel are clear of equipment.",
            "Remove all locks in reverse order. Each person removes only their own lock.",
            "Restore pneumatic supply by opening valves slowly.",
            "Re-energize Panel E-08 only after all locks removed and area is clear.",
            "Test at low speed before resuming production.",
            "Sign off LOTO logbook and notify all affected employees."
        ]),
        ("6. Emergency Contacts", [
            "Site EHS Manager: ext 4401",
            "Maintenance Supervisor: ext 4215",
            "Plant Emergency: ext 911 or site radio Channel 1"
        ])
    ]
)

make_pdf("OC-HR-ONBOARD-ENG-003.pdf",
    "New Automation Engineer Onboarding Guide - Rev 2 - Approved Jan 2025",
    [
        ("1. Purpose", [
            "This guide provides a structured 90-day onboarding plan for new automation engineers joining Owens Corning.",
            "Owner: HR Engineering Talent. Applies to all new automation engineers at North America manufacturing sites."
        ]),
        ("2. Week 1 - Foundation", [
            "Day 1: IT setup - laptop, SSO activation, OC AI Copilot access, Teams onboarding, and badge access.",
            "Day 2 to 3: Safety orientation - LOTO fundamentals, confined space awareness, PPE requirements.",
            "Day 4 to 5: OC Automation Standards review OC-AUTO-STD-001 and PLC platform introduction with mentor."
        ]),
        ("3. Weeks 2 to 4 - Technical Onboarding", [
            "Shadow a senior automation engineer on at least two active projects.",
            "Complete Studio 5000 Logix Designer training through OC-approved Rockwell Automation vendor within 30 days.",
            "Complete OT cybersecurity awareness training IT-SEC-OT-001 mandatory before any OT system access.",
            "Review the three most recent FAT and SAT reports for your assigned site."
        ]),
        ("4. Days 31 to 60 - Active Engagement", [
            "Assigned to one live capital project as supporting engineer.",
            "Complete OC Engineering Standards assessment. Passing score is 80 percent. Two attempts permitted.",
            "First 30-day performance check-in with hiring manager in Workday."
        ]),
        ("5. Days 61 to 90 - Independent Contribution", [
            "Lead one engineering deliverable - scope document, FAT checklist, or design review.",
            "Complete 30-60-90 day self-assessment in Workday.",
            "Mentor assignment finalized for ongoing development.",
            "Full engineering document system access granted upon 90-day review completion."
        ]),
        ("6. Required Certifications", [
            "LOTO certification required within 14 days before independent maintenance work.",
            "Confined space entry awareness required within 30 days.",
            "OT cybersecurity awareness IT-SEC-OT-001 required before OT access.",
            "Studio 5000 Logix Designer required within 30 days.",
            "OC Engineering Standards assessment required within 60 days."
        ])
    ]
)

make_pdf("OC-MAINT-PM-004.pdf",
    "Injection Molding Machine PM Schedule - Rev 4 - Approved Feb 2025",
    [
        ("1. Purpose and Scope", [
            "This document defines the preventive maintenance schedule for all injection molding machines at Owens Corning sites.",
            "Owner: Reliability Engineering. All PM records must be entered in SAP PM within 24 hours of completion."
        ]),
        ("2. Daily Checks - Operator", [
            "Hydraulic oil level and temperature. Target 40 to 50 degrees Celsius. Record in shift log.",
            "Tie bar lubrication - one grease shot per tie bar per shift using OC-approved lithium-based grease.",
            "Hopper and feed throat inspection - verify no bridging or contamination.",
            "Cooling water flow indicator - verify green status on all circuits.",
            "Visual inspection of all safety guards and door interlocks."
        ]),
        ("3. Weekly PM - Maintenance Technician", [
            "Full hydraulic system pressure test at operating pressure. Document in SAP PM work order.",
            "Screw and barrel wear measurement. Record and trend against baseline.",
            "Heater band resistance check on all zones. Tolerance is plus or minus 5 percent of rated.",
            "Ejector pin lubrication and inspection for wear.",
            "Check and tighten all hydraulic fittings. Inspect for leaks."
        ]),
        ("4. Monthly PM", [
            "Full hydraulic oil sample analysis. Send to OC-approved lab within 24 hours.",
            "Clamping force calibration to machine tonnage spec plus or minus 2 percent.",
            "Safety circuit and door interlock functional test - mandatory two-person procedure.",
            "Mold cooling circuit flush with approved descaling solution.",
            "Electrical panel inspection for loose connections and overheating signs."
        ]),
        ("5. Annual PM", [
            "Full screw and barrel replacement assessment based on wear trend.",
            "Hydraulic pump overhaul or replacement per decision tree in Appendix B.",
            "Load cell and pressure transducer calibration by certified vendor.",
            "Complete electrical system audit including motor insulation resistance testing.",
            "Update machine history card in SAP PM with all annual findings."
        ]),
        ("6. SAP PM Requirements", [
            "All PM activities recorded in SAP PM within 24 hours of completion.",
            "Work order must include technician name, date, measurements, parts used, and abnormal findings.",
            "Abnormal findings escalated to Reliability Engineer within 4 hours.",
            "Failed PM completion reported to Maintenance Supervisor immediately."
        ])
    ]
)

print("All 3 sample documents created in sample_docs/")
