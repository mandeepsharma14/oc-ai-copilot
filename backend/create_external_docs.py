from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
import os

os.makedirs("sample_docs/external", exist_ok=True)
styles = getSampleStyleSheet()
title_style = ParagraphStyle("title", parent=styles["Heading1"], fontSize=16, spaceAfter=12)
heading_style = ParagraphStyle("heading", parent=styles["Heading2"], fontSize=13, spaceAfter=8)
body_style = ParagraphStyle("body", parent=styles["Normal"], fontSize=11, spaceAfter=6, leading=16)

def make_pdf(filename, title, sections):
    doc = SimpleDocTemplate("sample_docs/external/" + filename, pagesize=letter,
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
    print("Created: sample_docs/external/" + filename)

make_pdf("Duration-Premium-Shingles-Spec.pdf",
    "Duration Premium Shingles - Product Specification Sheet - Rev 9 - Approved Feb 2025",
    [
        ("1. Product Overview", [
            "Duration Premium shingles are Owens Corning flagship roofing shingles featuring SureNail Technology for superior wind resistance and nail placement accuracy.",
            "Duration Premium shingles are available in 45 colors and carry a Limited Lifetime warranty for the original owner."
        ]),
        ("2. Wind Resistance Rating", [
            "Duration Premium shingles are rated to 110 mph wind resistance per ASTM D3161 Class F.",
            "Duration STORM shingles are rated to 130 mph wind resistance and carry a UL 2218 Class 4 impact rating.",
            "SureNail Technology provides a triple layer of reinforcement at the nail zone for superior holding power.",
            "Both products qualify for insurance premium discounts in 38 states due to their wind and impact ratings."
        ]),
        ("3. R-Value and Energy Performance", [
            "Duration Premium shingles are ENERGY STAR rated when installed with Owens Corning starter strips.",
            "The reflective granule option reduces rooftop temperatures by up to 20 degrees F compared to standard shingles.",
            "Duration Cool shingles meet California Title 24 energy requirements for steep-slope roofing."
        ]),
        ("4. Installation Requirements", [
            "Minimum roof slope: 2 in 12 for standard installation, 4 in 12 recommended for optimal performance.",
            "Nail placement must be within the SureNail fabric strip — 6 nails per shingle in high wind zones above 90 mph.",
            "Starter strip is required at eaves and rakes. Use Owens Corning Starter Strip Plus for warranty compliance.",
            "Underlayment requirement: minimum 30-pound felt or synthetic equivalent. WeatherLock self-sealing underlayment recommended in valleys and around penetrations.",
            "Always consult local building codes and a licensed roofing contractor before installation."
        ]),
        ("5. Pricing Guidance", [
            "Duration Premium MSRP: 98 to 118 dollars per square (100 square feet of coverage) depending on color and region.",
            "Duration STORM MSRP: 112 to 136 dollars per square.",
            "Lowe's Pro contractor accounts receive 5 to 8 percent below street pricing on qualifying orders.",
            "Volume pricing activates at 50 square orders. Contact your OC territory representative for details.",
            "Pricing shown is MSRP guidance only. Final pricing is subject to your account agreement with your retailer or OC representative."
        ]),
        ("6. Warranty", [
            "Limited Lifetime warranty for the original owner on Duration Premium shingles.",
            "110 mph wind warranty standard. 130 mph wind warranty on Duration STORM.",
            "Algae resistance warranty: 10 years on Duration Tru-Def series.",
            "Warranty is transferable once to a subsequent owner within the first 5 years.",
            "Contact Owens Corning at 1-800-GET-PINK or visit owenscorning.com for complete warranty terms."
        ]),
        ("7. Availability", [
            "Duration Premium is a national stocking item at all Lowe's and Home Depot distribution centers.",
            "Standard lead time: 3 to 5 days for DC-to-store replenishment.",
            "Direct-to-jobsite shipping available for orders of 100 squares or more via OC distribution network.",
            "Special order colors: 7 to 10 business days."
        ])
    ]
)

make_pdf("EcoTouch-PINK-FIBERGLAS-Spec.pdf",
    "EcoTouch PINK FIBERGLAS Insulation - Product Data Sheet - Rev 14 - Approved Jan 2025",
    [
        ("1. Product Overview", [
            "EcoTouch PINK FIBERGLAS insulation is Owens Corning flagship residential and light commercial insulation product.",
            "Made with a minimum of 50 percent recycled content. GREENGUARD Gold certified for low VOC emissions.",
            "Available in faced (kraft) and unfaced versions for walls, floors, attics, and crawl spaces."
        ]),
        ("2. R-Value by Product and Thickness", [
            "R-11: 3.5 inch thickness — standard 2x4 wall cavity.",
            "R-13: 3.5 inch thickness — high-density version for 2x4 wall cavity.",
            "R-15: 3.5 inch thickness — premium high-density for 2x4 wall cavity.",
            "R-19: 6.25 inch thickness — standard 2x6 wall cavity or floor.",
            "R-21: 5.5 inch thickness — high-density for 2x6 wall cavity. Most popular for exterior walls.",
            "R-30: 10 inch thickness — attic floor insulation.",
            "R-38: 12 inch thickness — attic floor insulation for Climate Zones 4 and above.",
            "R-49: 16 inch thickness — attic floor insulation for Climate Zones 6 and 7.",
            "ProPink blown-in insulation: R-60 achievable at 16.25 inch depth."
        ]),
        ("3. Climate Zone Recommendations", [
            "Climate Zone 1 and 2 (South Florida, Hawaii): R-30 attic, R-13 walls minimum.",
            "Climate Zone 3 (Southeast US): R-38 attic, R-13 walls minimum.",
            "Climate Zone 4 (Mid-Atlantic, Pacific Northwest): R-49 attic, R-13 plus R-5 continuous walls.",
            "Climate Zone 5 (Ohio, Indiana, Pennsylvania, New York, Oregon): R-49 attic, R-20 walls or R-13 plus R-5 continuous. R-21 high-density batt recommended.",
            "Climate Zone 6 (Minnesota, Wisconsin, Montana): R-60 attic, R-20 plus R-5 continuous walls.",
            "Climate Zone 7 (Northern Minnesota, Alaska): R-60 attic, R-20 plus R-10 continuous walls.",
            "Always verify with local building codes as requirements may exceed IECC minimums."
        ]),
        ("4. Attic Installation Guide", [
            "Step 1: Air seal all penetrations before installing insulation. Seal around electrical boxes, plumbing, and recessed lights.",
            "Step 2: Install ventilation baffles at every rafter bay at the eave. Maintain minimum 1 inch air channel from soffit to ridge.",
            "Step 3: Lay first layer of batts between joists with kraft facing down toward the heated space.",
            "Step 4: For R-49 or higher, install second layer of unfaced batts perpendicular across the top of joists to eliminate thermal bridging.",
            "Step 5: Keep batts away from recessed light fixtures unless IC-rated. Maintain 3 inch clearance minimum.",
            "Step 6: Insulate the attic hatch separately to match attic R-value.",
            "Never compress insulation — compression reduces R-value proportionally.",
            "Always consult local building codes and a licensed contractor before installation."
        ]),
        ("5. Pricing Guidance", [
            "EcoTouch R-13 (15 inch wide, 40 square feet per bag): approximately 18 to 22 dollars at retail.",
            "EcoTouch R-21 (15 inch wide, 40 square feet per bag): approximately 28 to 34 dollars at retail.",
            "EcoTouch R-38 (16 inch wide, 40 square feet per bag): approximately 42 to 50 dollars at retail.",
            "Contractor and builder pricing available through OC Pro program. Contact your OC representative.",
            "Pricing shown is MSRP guidance only. Final pricing subject to your account agreement."
        ]),
        ("6. Certifications", [
            "GREENGUARD Gold certified — tested for over 10000 chemical emissions.",
            "ENERGY STAR partner product.",
            "Complies with California Title 24 requirements.",
            "Meets ASHRAE 90.1 requirements for commercial applications."
        ])
    ]
)

make_pdf("Thermafiber-Mineral-Wool-Fire-Rating.pdf",
    "Thermafiber Mineral Wool Insulation - Fire Rating and Technical Specification - Rev 8 - Approved Jan 2025",
    [
        ("1. Product Overview", [
            "Thermafiber mineral wool insulation is manufactured from natural basalt rock and recycled slag.",
            "Non-combustible with a melting point above 2000 degrees F. Will not burn, smolder, or contribute to flame spread.",
            "Available in UltraBatt for wall cavities and RainBarrier for continuous exterior insulation applications."
        ]),
        ("2. Fire Performance Ratings", [
            "ASTM E84: Flame spread index 0, Smoke developed index 0. Non-combustible classification.",
            "UL Classified: Fire Classification R13950.",
            "NFPA 285 compliant in tested wall assemblies with steel stud framing.",
            "ASTM E136 non-combustibility verified for all Thermafiber products.",
            "Suitable for Type I, II, III, IV, and V construction per IBC 2021.",
            "FM Approved for use in FM-compliant wall and roof systems."
        ]),
        ("3. Assembly Fire Ratings", [
            "1-hour rated wall assembly: 3.5 inch Thermafiber UltraBatt plus 5/8 inch Type X gypsum each side, per ASTM E119.",
            "2-hour rated wall assembly: 3.5 inch Thermafiber UltraBatt plus two layers 5/8 inch Type X gypsum each side.",
            "Fire ratings are assembly-specific. Always verify the complete wall assembly against tested UL or FM listings.",
            "The insulation rating alone does not certify the full assembly. Consult your OC commercial technical representative for project-specific documentation."
        ]),
        ("4. Acoustic Performance", [
            "Thermafiber UltraBatt STC 45 to 52 depending on wall assembly.",
            "Thermafiber SafeSound for interior partition walls: STC 39 to 52.",
            "Effective at reducing both airborne and structure-borne sound transmission.",
            "Ideal for hotels, multi-family residential, healthcare facilities, and offices."
        ]),
        ("5. R-Value and Thermal Performance", [
            "Thermafiber UltraBatt R-15: 3.5 inch thickness for 2x4 wall cavity.",
            "Thermafiber UltraBatt R-23: 5.5 inch thickness for 2x6 wall cavity.",
            "Thermafiber RainBarrier continuous insulation: R-4 per inch, available in 1 to 4 inch thickness.",
            "Combining R-21 fiberglass cavity with R-5 RainBarrier continuous achieves effective wall R-26 eliminating thermal bridging at studs."
        ]),
        ("6. Commercial Applications and Pricing", [
            "Thermafiber is suitable for exterior walls, curtain walls, cavity walls, roofing, and mechanical systems.",
            "Thermafiber UltraBatt pricing: approximately 0.80 to 1.20 dollars per square foot installed depending on thickness and region.",
            "Thermafiber RainBarrier CI pricing: approximately 1.20 to 1.80 dollars per square foot installed.",
            "For commercial specifications, Thermafiber offers a free wall assembly specification service.",
            "Contact your OC commercial representative or visit owenscorning.com/thermafiber for project support.",
            "Pricing shown is guidance only. Final pricing subject to project scope and account agreement."
        ])
    ]
)

print("All 3 external product documents created in sample_docs/external/")
