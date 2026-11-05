import os
HERE = os.path.dirname(os.path.abspath(__file__))
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

ACC = RGBColor(0x1F, 0x4E, 0x79)
SOFT = RGBColor(0xEA, 0xF1, 0xF8)
WARN = RGBColor(0xFF, 0xF4, 0xE0)
WARNLINE = RGBColor(0xC7, 0x77, 0x00)
DARK = RGBColor(0x22, 0x22, 0x22)
GREY = RGBColor(0x66, 0x66, 0x66)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
FONT = "Calibri"

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
s = prs.slides.add_slide(prs.slide_layouts[6])


def textbox(x, y, w, h, runs_list, size, color=DARK, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.05)
    tf.margin_top = tf.margin_bottom = Inches(0.02)
    p = tf.paragraphs[0]
    p.alignment = align
    for text, b, c in runs_list:
        r = p.add_run()
        r.text = text
        r.font.size = Pt(size)
        r.font.name = FONT
        r.font.bold = b if b is not None else bold
        r.font.color.rgb = c or color
    return tb


# title + question
textbox(0.5, 0.3, 12.3, 0.7, [("The paper in one table", True, ACC)], 34)
textbox(0.5, 1.0, 12.3, 0.9,
        [("Stranski–Totomanow conjecture: ", True, DARK),
         ("the first crystal to nucleate is the one with the lowest barrier. "
          "Oppositely charged colloids (T* = 1, κσ = 6) are used to test it.", False, DARK)], 16)

rows = [
    ("#", "Experiment", "What forms", "Barrier / rate", "What it tells us"),
    ("1", "Brute-force MC, p* = 15", "nothing in 3×10⁶ cycles", "nucleation far too rare",
     "a rare-event method (FFS) is needed"),
    ("2", "FFS, MC without swaps, p* = 15\n(dr 0.01 for the initial flux, 0.04 for branching)",
     "disordered fcc\ncritical nucleus ≈ 120", "high barrier (≈ 31–32 kT)\nlow rate",
     "the nucleus that forms is not the cheapest one"),
    ("3", "FFS with 20% swaps, p* = 15", "CsCl\ncritical nucleus ≈ 65",
     "low barrier (≈ 20–22 kT)\nhigh rate", "with swaps the lowest-barrier crystal wins"),
    ("4", "Brute-force MC, p* = 18, no swaps", "disordered fcc", "no numbers given",
     "same outcome as row 2, without FFS"),
    ("5", "Brute-force MC, p* = 18, with swaps", "CsCl", "no numbers given",
     "same swap effect as row 3"),
]
widths = [0.5, 3.8, 2.6, 2.7, 2.7]  # = 12.3
row_h = [0.42, 0.55, 0.85, 0.75, 0.75, 0.55]
x0, y0 = 0.5, 1.85
gt = s.shapes.add_table(len(rows), 5, Inches(x0), Inches(y0), Inches(sum(widths)), Inches(sum(row_h)))
tbl = gt.table
# drop the built-in style banding
tblPr = tbl._tbl.tblPr
tblPr.set("firstRow", "0"); tblPr.set("bandRow", "0")
for j, w in enumerate(widths):
    tbl.columns[j].width = Inches(w)
for i, h in enumerate(row_h):
    tbl.rows[i].height = Inches(h)

for i, row in enumerate(rows):
    for j, text in enumerate(row):
        c = tbl.cell(i, j)
        c.vertical_anchor = MSO_ANCHOR.MIDDLE
        c.margin_left = c.margin_right = Inches(0.08)
        c.margin_top = c.margin_bottom = Inches(0.03)
        c.fill.solid()
        if i == 0:
            c.fill.fore_color.rgb = ACC
        elif i == 4:
            c.fill.fore_color.rgb = WARN
        else:
            c.fill.fore_color.rgb = SOFT if i % 2 == 1 else WHITE
        tf = c.text_frame
        tf.word_wrap = True
        lines = text.split("\n")
        for k, line in enumerate(lines):
            p = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
            p.alignment = PP_ALIGN.CENTER if j == 0 else PP_ALIGN.LEFT
            r = p.add_run()
            r.text = line
            r.font.name = FONT
            if i == 0:
                r.font.size, r.font.bold, r.font.color.rgb = Pt(15), True, WHITE
            else:
                small = (j == 1 and k == 1)
                r.font.size = Pt(11 if small else 14)
                r.font.bold = (j == 2) and k == 0
                r.font.color.rgb = GREY if small else DARK
        if i == 4 and j == 1:
            p = tf.add_paragraph()
            r = p.add_run()
            r.text = "THIS WORK"
            r.font.name, r.font.size, r.font.bold = FONT, Pt(12), True
            r.font.color.rgb = WARNLINE

# take-home bar
by = y0 + sum(row_h) + 0.3
bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), Inches(by), Inches(12.3), Inches(0.8))
bar.fill.solid(); bar.fill.fore_color.rgb = SOFT
bar.line.color.rgb = ACC; bar.line.width = Pt(1.25)
tf = bar.text_frame
tf.word_wrap = True
tf.vertical_anchor = MSO_ANCHOR.MIDDLE
tf.margin_left = tf.margin_right = Inches(0.15)
p = tf.paragraphs[0]
p.alignment = PP_ALIGN.LEFT
for text, b in [("Take-home: ", True),
                ("without swaps, small nuclei cannot rearrange their charge arrangement, so they are not in local "
                 "equilibrium and the conjecture fails. Swaps restore that equilibrium and CsCl appears.", False)]:
    r = p.add_run(); r.text = text
    r.font.name, r.font.size, r.font.bold, r.font.color.rgb = FONT, Pt(15), b, ACC if b else DARK

textbox(0.5, 7.0, 12.3, 0.4,
        [("Barriers are read from the paper’s umbrella-sampling figure (N = 8000), approximate. "
          "Source: Sanz, Valeriani, Frenkel, Dijkstra, Phys. Rev. Lett. 99, 055501 (2007).", False, GREY)], 10)

out = os.path.join(HERE, "../../docs/reports/07_meeting_slides.pptx")


# ======================= slide 2 =======================
s = prs.slides.add_slide(prs.slide_layouts[6])
textbox(0.5, 0.3, 12.3, 0.7, [("What I built, and why p* = 18", True, ACC)], 34)
textbox(0.5, 1.0, 12.3, 0.7,
        [("The paper gives no numbers at p* = 18, so this is a test of a new working code ", False, DARK),
         ("and a qualitative comparison.", False, DARK)], 16)


def panel(x, y, w, h, title, paras, size=13, fill=SOFT, line=ACC):
    box = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    box.fill.solid(); box.fill.fore_color.rgb = fill
    box.line.color.rgb = line; box.line.width = Pt(1.25)
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.margin_left = tf.margin_right = Inches(0.15)
    tf.margin_top = Inches(0.08)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    r = p.add_run(); r.text = title
    r.font.name, r.font.size, r.font.bold, r.font.color.rgb = FONT, Pt(size + 2), True, line
    p.space_after = Pt(4)
    for text in paras:
        p = tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(3)
        r = p.add_run(); r.text = text
        r.font.name, r.font.size, r.font.color.rgb = FONT, Pt(size), DARK


# left: code history
panel(0.5, 1.85, 4.3, 3.35, "The code",
      ["1.  No working code at the start.",
       "2.  Found the NpT Monte Carlo case study of Frenkel and Smit, Understanding Molecular "
       "Simulation (Lennard-Jones).",
       "3.  Changed it to signed hard-core Yukawa colloids: two charge types, hard-core rejection.",
       "4.  Added trajectory output, so runs can be viewed in OVITO."], size=15)

# right: setup table
rows2 = [
    ("", "Value", "Why"),
    ("System", "N = 1000 (500 +, 500 −), T* = 1, p* = 18, κσ = 6, rc = 3.5σ",
     "paper’s system size and state point; p* = 18 is the paper’s brute-force case"),
    ("Run", "3×10⁶ cycles, no swaps; 1 cycle = 1000 displacement + 1 volume move",
     "same length as the paper’s p* = 15 brute-force test"),
    ("Step size dr", "0.01 and 0.04 (two separate runs)", "the two values the paper uses in its FFS runs at p* = 15"),
    ("Volume step", "vmax = 0.0005", "not given in the paper; tuned to about 20% volume acceptance"),
    ("Start", "validated liquid (density 1.037, no crystal by PTM or CNA)",
     "a brute-force run needs a clean liquid start"),
]
w2 = [1.45, 3.35, 3.0]
rh2 = [0.36, 0.7, 0.7, 0.55, 0.55, 0.55]
gt2 = s.shapes.add_table(len(rows2), 3, Inches(5.0), Inches(1.85), Inches(sum(w2)), Inches(sum(rh2)))
t2 = gt2.table
t2._tbl.tblPr.set("firstRow", "0"); t2._tbl.tblPr.set("bandRow", "0")
for j, w in enumerate(w2):
    t2.columns[j].width = Inches(w)
for i, h in enumerate(rh2):
    t2.rows[i].height = Inches(h)
for i, row in enumerate(rows2):
    for j, text in enumerate(row):
        c = t2.cell(i, j)
        c.vertical_anchor = MSO_ANCHOR.MIDDLE
        c.margin_left = c.margin_right = Inches(0.08)
        c.margin_top = c.margin_bottom = Inches(0.03)
        c.fill.solid()
        c.fill.fore_color.rgb = ACC if i == 0 else (SOFT if i % 2 == 1 else WHITE)
        tf = c.text_frame; tf.word_wrap = True
        r = tf.paragraphs[0].add_run(); r.text = text
        r.font.name = FONT
        if i == 0:
            r.font.size, r.font.bold, r.font.color.rgb = Pt(14), True, WHITE
        else:
            r.font.size, r.font.bold, r.font.color.rgb = Pt(12), (j == 0), DARK

# bottom: why p*=18, contributions
panel(0.5, 5.45, 6.05, 1.75, "Why brute force at p* = 18",
      ["The paper says nucleation is likely enough there that no FFS is needed, so a plain run is a "
       "direct test of the new code. The paper gives no cluster size, time or step size at p* = 18."],
      size=15)
panel(6.75, 5.45, 6.05, 1.75, "What I contributed",
      ["•  working Yukawa NpT Monte Carlo code with trajectory output",
       "•  validated liquid starting point (500:500, no overlaps, no crystal)",
       "•  tuned volume step; frozen, reproducible run workflow"],
      size=14, fill=WARN, line=WARNLINE)



# ======================= slide 3 =======================
FIGD = os.path.join(HERE, "../../docs/reports/figs") + os.sep
s = prs.slides.add_slide(prs.slide_layouts[6])
textbox(0.5, 0.25, 12.3, 0.7, [("What came out at p* = 18", True, ACC)], 34)

# left: plot + numbers
s.shapes.add_picture(FIGD + "cna_largest_cluster.png", Inches(0.5), Inches(1.1), width=Inches(5.7))
panel(0.5, 4.2, 5.7, 1.25, "At 3.0×10⁶ cycles (dr = 0.04)",
      ["146 fcc, 294 hcp, 8 bcc, 552 other. No CsCl signal.",
       "Opposite-charge neighbours: 0.58 in the crystal, 0.60 in the liquid (random mixing: 0.50)."],
      size=12)

# right: three columns
cols = [("Liquid start", "no crystalline particles", "ovito_cna_liquid_seg001_f0.png", "ovito_gr_liquid_seg001_f0.png"),
        ("2.1×10⁶ cycles", "largest cluster: 193", "ovito_cna_seg009_f100.png", "ovito_gr_seg009_f100.png"),
        ("3.0×10⁶ cycles", "largest cluster: 440", "ovito_cna_seg012_f250.png", "ovito_gr_seg012_f250.png")]
cw, step, x0c = 2.05, 2.17, 6.45
for k, (head, sub, cna, gr) in enumerate(cols):
    x = x0c + k * step
    textbox(x, 1.05, cw, 0.3, [(head, True, ACC)], 15, align=PP_ALIGN.CENTER)
    textbox(x, 1.35, cw, 0.3, [(sub, False, GREY)], 12, align=PP_ALIGN.CENTER)
    s.shapes.add_picture(FIGD + cna, Inches(x), Inches(1.7), width=Inches(cw))
textbox(x0c, 3.78, 6.4, 0.3,
        [("CNA colours: green fcc, red hcp, blue bcc, white other. dr = 0.04 run.", False, GREY)], 11)
s.shapes.add_picture(FIGD + "gr_three_frames.png", Inches(x0c), Inches(4.1), width=Inches(6.4))

panel(0.5, 5.65, 6.05, 1.65, "Reading",
      ["Close-packed crystal (fcc and hcp, almost no bcc) with no extra charge order, in line with "
       "the paper’s no-swap result. dr = 0.01 stayed liquid. The crystal fills the 1000-particle box, "
       "so quote the nucleation time (about 2×10⁶ cycles), not the size."],
      size=13)
panel(6.75, 5.65, 6.05, 1.65, "Next",
      ["•  add a swap move: CsCl is expected",
       "•  more seeds and a larger system, to see an isolated nucleus",
       "•  compare g(r) with the paper’s cluster g(r)",
       "•  FFS at p* = 15, the link to infRETIS"],
      size=13, fill=WARN, line=WARNLINE)

prs.save(out)
print(out)
