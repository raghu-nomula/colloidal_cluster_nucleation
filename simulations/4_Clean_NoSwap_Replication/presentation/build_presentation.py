#!/usr/bin/env python3
"""Build the editable PowerPoint summary of the clean no-swap replication."""

from pathlib import Path
import csv
import math
import sys

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from ovito.io import import_file
from ovito.modifiers import PolyhedralTemplateMatchingModifier
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt


ROOT = Path(__file__).resolve().parents[2]
REP = ROOT / "4_Clean_NoSwap_Replication"
OUT = REP / "presentation"
ASSETS = OUT / "assets"
OUT.mkdir(exist_ok=True)
ASSETS.mkdir(exist_ok=True)

NAVY = RGBColor(20, 42, 66)
BLUE = RGBColor(36, 105, 168)
ORANGE = RGBColor(225, 120, 45)
TEAL = RGBColor(42, 142, 135)
GOLD = RGBColor(224, 172, 55)
INK = RGBColor(40, 48, 58)
MID = RGBColor(100, 112, 124)
LIGHT = RGBColor(238, 242, 246)
WHITE = RGBColor(255, 255, 255)
RED = RGBColor(184, 63, 63)


def read_numeric(path):
    rows = []
    with open(path) as handle:
        for line in handle:
            if not line.strip() or line.startswith("#"):
                continue
            rows.append([float(x) for x in line.split()])
    return np.asarray(rows)


def aggregate_moves(branch):
    total = np.zeros(4, dtype=np.int64)
    for seg in range(1, 13):
        p = REP / branch / f"production_3M_seg{seg:03d}" / "run_metrics.dat"
        row = read_numeric(p)[-1]
        total += np.array([row[6], row[7], row[9], row[10]], dtype=np.int64)
    return {
        "particle_attempts": int(total[0]), "particle_accepted": int(total[1]),
        "volume_attempts": int(total[2]), "volume_accepted": int(total[3]),
        "particle_rate": total[1] / total[0], "volume_rate": total[3] / total[2],
    }


def load_thermo(branch):
    a = read_numeric(REP / branch / "production_3M_control" / "cumulative_metrics.dat")
    return {"cycle": a[:, 0], "energy": a[:, 1], "density": a[:, 2], "eta": a[:, 3]}


def load_structure(branch):
    p = REP / "analysis" / "production_3M" / f"{branch}_structure_timeseries.csv"
    with open(p) as handle:
        rows = list(csv.DictReader(handle))
    def col(name): return np.asarray([float(r[name]) for r in rows])
    return {"cycle": col("cumulative_cycle"),
            "ptm": col("ptm_largest_fcc_hcp_cluster"),
            "cna": col("cna_largest_fcc_hcp_cluster"),
            "fcc": col("ptm_fcc"), "hcp": col("ptm_hcp")}


def mpl_style():
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 11,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.edgecolor": "#7a8794", "axes.labelcolor": "#28303a",
        "xtick.color": "#536170", "ytick.color": "#536170",
        "grid.color": "#d9e0e7", "grid.linewidth": 0.7,
    })


def make_charts(t1, t4, s1, s4, m1, m4):
    mpl_style()
    fmt_m = FuncFormatter(lambda x, pos: f"{x/1e6:g}M")
    fig, ax = plt.subplots(2, 1, figsize=(11, 6.5), sharex=True)
    for data, color, label in [(t1, "#2469a8", "dr = 0.01"), (t4, "#e1782d", "dr = 0.04")]:
        ax[0].plot(data["cycle"], data["density"], color=color, lw=1.8, label=label)
        ax[1].plot(data["cycle"], data["energy"], color=color, lw=1.5)
    ax[0].set_ylabel("Number density")
    ax[1].set_ylabel("Energy / particle")
    ax[1].set_xlabel("MC cycles")
    ax[0].legend(frameon=False, ncol=2)
    for a in ax: a.grid(True, alpha=.8); a.xaxis.set_major_formatter(fmt_m)
    fig.tight_layout()
    fig.savefig(ASSETS / "thermodynamics.png", dpi=220, transparent=False)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(11, 4.8))
    ax.plot(s1["cycle"], s1["ptm"], color="#2469a8", lw=1.7, label="dr = 0.01 · PTM")
    ax.plot(s4["cycle"], s4["ptm"], color="#e1782d", lw=2.2, label="dr = 0.04 · PTM")
    ax.plot(s4["cycle"], s4["cna"], color="#e1782d", lw=1.2, ls="--", alpha=.8, label="dr = 0.04 · CNA")
    for x, y, txt in [(2.049e6, 100, "100"), (2.112e6, 250, "250"), (2.285e6, 500, "500")]:
        ax.scatter([x], [y], s=45, color="#e1782d", zorder=5)
        ax.annotate(txt, (x, y), xytext=(7, 7), textcoords="offset points", color="#9b4d17", weight="bold")
    ax.axhline(100, color="#7a8794", lw=1, ls=":")
    ax.set(xlabel="MC cycles", ylabel="Largest connected FCC/HCP domain", ylim=(-8, 590))
    ax.xaxis.set_major_formatter(fmt_m); ax.grid(True, alpha=.8); ax.legend(frameon=False, ncol=3, loc="upper left")
    fig.tight_layout(); fig.savefig(ASSETS / "cluster_growth.png", dpi=220); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    labels = ["Particle moves", "Volume moves"]
    x = np.arange(2); width = .34
    ax.bar(x-width/2, [100*m1["particle_rate"],100*m1["volume_rate"]], width, color="#2469a8", label="dr = 0.01")
    ax.bar(x+width/2, [100*m4["particle_rate"],100*m4["volume_rate"]], width, color="#e1782d", label="dr = 0.04")
    ax.set_xticks(x, labels); ax.set_ylabel("Acceptance (%)"); ax.set_ylim(0, 100); ax.grid(axis="y")
    ax.legend(frameon=False, ncol=2)
    for c in ax.containers: ax.bar_label(c, fmt="%.1f%%", padding=3, fontsize=10)
    fig.tight_layout(); fig.savefig(ASSETS / "acceptance.png", dpi=220); plt.close(fig)


def largest_component(pos, st, box, cutoff=1.45):
    ids = np.where((st == 1) | (st == 2))[0]
    if len(ids) == 0: return np.zeros(len(st), dtype=bool)
    parent = np.arange(len(ids)); sizes = np.ones(len(ids), int)
    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]; i = parent[i]
        return i
    def union(i, j):
        a, b = find(i), find(j)
        if a == b: return
        if sizes[a] < sizes[b]: a, b = b, a
        parent[b] = a; sizes[a] += sizes[b]
    p = pos[ids]
    for i in range(len(ids)-1):
        d = p[i+1:] - p[i]; d -= box * np.rint(d / box)
        for k in np.where(np.einsum("ij,ij->i", d, d) < cutoff**2)[0]: union(i, i+1+int(k))
    roots = np.array([find(i) for i in range(len(ids))]); root = max(set(roots), key=lambda r: np.sum(roots == r))
    mask = np.zeros(len(st), bool); mask[ids[roots == root]] = True
    return mask


def render_frame(cycle, label):
    seg = min(int(cycle // 250000) + 1, 12)
    if cycle > 0 and cycle % 250000 == 0: seg = int(cycle // 250000)
    local = int(cycle - (seg-1)*250000)
    frame = local // 1000
    traj = REP / "dr_0.04" / f"production_3M_seg{seg:03d}" / "traj.lammpstrj"
    pipe = import_file(str(traj), multiple_frames=True)
    pipe.modifiers.append(PolyhedralTemplateMatchingModifier(rmsd_cutoff=.10))
    data = pipe.compute(frame)
    pos = np.asarray(data.particles.positions).copy()
    st = np.asarray(data.particles["Structure Type"]).copy()
    box = np.diag(np.asarray(data.cell.matrix)[:, :3]).copy()
    big = largest_component(pos, st, box)
    fig = plt.figure(figsize=(5.2, 5.2), facecolor="#f7f9fb")
    ax = fig.add_subplot(111, projection="3d", facecolor="#f7f9fb")
    other = ~big
    ax.scatter(pos[other,0], pos[other,1], pos[other,2], s=5, c="#aab5c0", alpha=.48 if not np.any(big) else .22, depthshade=False)
    fcc = big & (st == 1); hcp = big & (st == 2)
    ax.scatter(pos[fcc,0], pos[fcc,1], pos[fcc,2], s=19, c="#2469a8", alpha=.95, depthshade=False, label="FCC")
    ax.scatter(pos[hcp,0], pos[hcp,1], pos[hcp,2], s=19, c="#e5a62d", alpha=.95, depthshade=False, label="HCP")
    ax.view_init(elev=22, azim=38); ax.set_box_aspect((1,1,1)); ax.set_axis_off()
    ax.set_xlim(0,box[0]); ax.set_ylim(0,box[1]); ax.set_zlim(0,box[2])
    ax.set_title(label, color="#142a42", fontsize=12, weight="bold", pad=-2)
    fig.tight_layout(pad=.1)
    path = ASSETS / f"snapshot_{cycle:07d}.png"; fig.savefig(path, dpi=200, bbox_inches="tight"); plt.close(fig)
    return path, int(np.sum(big)), int(np.sum(fcc)), int(np.sum(hcp))


def set_bg(slide, color=WHITE): slide.background.fill.solid(); slide.background.fill.fore_color.rgb = color
def add_text(slide, text, x, y, w, h, size=20, color=INK, bold=False, align=PP_ALIGN.LEFT, font="Aptos", margin=.04):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tf = box.text_frame
    tf.clear(); tf.margin_left=tf.margin_right=Inches(margin); tf.margin_top=tf.margin_bottom=Inches(.02); tf.vertical_anchor=MSO_ANCHOR.MIDDLE
    p=tf.paragraphs[0]; p.text=text; p.alignment=align
    for r in p.runs: r.font.name=font; r.font.size=Pt(size); r.font.bold=bold; r.font.color.rgb=color
    return box
def add_rect(slide,x,y,w,h,fill=LIGHT,line=None,radius=False):
    shape=slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid(); shape.fill.fore_color.rgb=fill
    shape.line.color.rgb = line or fill
    return shape
def add_title(slide,title,kicker=None):
    if kicker: add_text(slide,kicker.upper(),.65,.30,12,.25,9,TEAL,True)
    add_text(slide,title,.65,.58,12,.55,28,NAVY,True)
    add_rect(slide,.65,1.18,.72,.05,TEAL)
def add_footer(slide,n,source=None):
    if source: add_text(slide,source,.68,7.14,11.7,.20,7,MID)
    add_text(slide,f"{n:02d}",12.25,7.10,.38,.22,8,MID,True,PP_ALIGN.RIGHT)
def add_bullets(slide,items,x,y,w,h,size=18,color=INK):
    box=slide.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h)); tf=box.text_frame; tf.clear(); tf.word_wrap=True
    tf.margin_left=Inches(.05); tf.margin_right=Inches(.03)
    for i,item in enumerate(items):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph(); p.text=item; p.level=0; p.font.size=Pt(size); p.font.name="Aptos"; p.font.color.rgb=color
        p.space_after=Pt(10); p.text="•  "+p.text
    return box
def add_picture(slide,path,x,y,w,h=None):
    return slide.shapes.add_picture(str(path), Inches(x), Inches(y), width=Inches(w), height=Inches(h) if h else None)
def add_pill(slide,text,x,y,w,color):
    add_rect(slide,x,y,w,.38,color,color,True); add_text(slide,text,x,y,w,.38,11,WHITE,True,PP_ALIGN.CENTER)


def build_deck():
    m1,m4=aggregate_moves("dr_0.01"),aggregate_moves("dr_0.04")
    t1,t4=load_thermo("dr_0.01"),load_thermo("dr_0.04")
    s1,s4=load_structure("dr_0.01"),load_structure("dr_0.04")
    make_charts(t1,t4,s1,s4,m1,m4)
    snaps=[]
    for cyc,lab in [(0,"Validated liquid"),(2049000,"First ≥100 domain"),(2112000,"Domain ≥250"),(2285000,"Domain ≥500"),(3000000,"Final state")]: snaps.append(render_frame(cyc,lab))

    prs=Presentation(); prs.slide_width=Inches(13.333); prs.slide_height=Inches(7.5); blank=prs.slide_layouts[6]
    slides=[]
    def new(title=None,kicker=None,bg=WHITE):
        s=prs.slides.add_slide(blank); set_bg(s,bg)
        if title: add_title(s,title,kicker)
        slides.append(s); return s

    # 1
    s=new(bg=NAVY); add_text(s,"RECONSTRUCTING\nCRYSTAL NUCLEATION",.72,.72,7.4,1.55,34,WHITE,True)
    add_text(s,"No-swap MC–NpT simulations\nof an oppositely charged Yukawa mixture",.78,2.30,6.45,.82,16,RGBColor(203,220,234))
    add_pill(s,"T* = 1",.78,3.33,1.25,TEAL); add_pill(s,"p* = 18",2.18,3.33,1.35,ORANGE); add_pill(s,"N = 1000",3.68,3.33,1.50,BLUE)
    add_picture(s,snaps[-1][0],7.95,.52,4.75,5.9); add_text(s,"Paper benchmark → controlled reconstruction → persistent close-packed growth",.78,6.55,7,.4,13,WHITE,False)
    add_footer(s,1)
    # 2
    s=new("The question is kinetic—not only thermodynamic","Scientific motivation")
    add_rect(s,.75,1.65,3.55,3.85,LIGHT,LIGHT,True); add_text(s,"LIQUID",1.02,1.91,3.0,.35,15,NAVY,True,PP_ALIGN.CENTER)
    add_text(s,"Local fluctuations\ncreate small ordered domains",1.10,2.55,2.85,.85,20,INK,False,PP_ALIGN.CENTER)
    add_text(s,"Which structure is reached\nwithin the available time?",1.05,3.75,2.95,.75,18,TEAL,True,PP_ALIGN.CENTER)
    add_text(s,"→",4.52,3.0,.65,.7,34,MID,True,PP_ALIGN.CENTER)
    add_rect(s,5.28,1.65,3.10,3.85,RGBColor(232,241,250),BLUE,True); add_text(s,"DISORDERED\nCLOSE-PACKED",5.52,2.00,2.62,.85,18,BLUE,True,PP_ALIGN.CENTER); add_text(s,"FCC/HCP-like packing\nfast local route",5.52,3.35,2.62,.75,17,INK,False,PP_ALIGN.CENTER)
    add_text(s,"or",8.55,3.15,.55,.4,16,MID,True,PP_ALIGN.CENTER)
    add_rect(s,9.28,1.65,3.10,3.85,RGBColor(252,241,228),ORANGE,True); add_text(s,"CHARGE-ORDERED\nCsCl-LIKE",9.52,2.00,2.62,.85,18,ORANGE,True,PP_ALIGN.CENTER); add_text(s,"requires structural +\ncharge reorganization",9.52,3.35,2.62,.75,17,INK,False,PP_ALIGN.CENTER)
    add_footer(s,2,"Conceptual summary based on Sanz et al., PRL 99, 055501 (2007).")
    # 3
    s=new("What the paper actually established","Paper benchmark")
    add_bullets(s,["Binary 50:50 mixture of oppositely charged hard-core Yukawa particles.","N = 1000, κσ = 6, T* = 1; disordered FCC competes with charge-ordered CsCl.","At p* = 15, no spontaneous event appeared in 3 × 10⁶ ordinary MC cycles.","Forward Flux Sampling generated rare reactive trajectories; the growing nuclei were compact and FCC-like.","Operational critical size at p* = 15: n ≈ 120 ± 15."],.78,1.55,7.0,4.9,18)
    add_rect(s,8.25,1.65,4.28,3.95,NAVY,NAVY,True); add_text(s,"IMPORTANT DISTINCTION",8.65,2.05,3.5,.35,13,TEAL,True,PP_ALIGN.CENTER)
    add_text(s,"3 million cycles without\nspontaneous nucleation",8.68,2.65,3.42,.85,23,WHITE,True,PP_ALIGN.CENTER)
    add_text(s,"applies to p* = 15",8.68,3.65,3.42,.45,18,GOLD,True,PP_ALIGN.CENTER)
    add_text(s,"FFS samples rare pathways; it does not prescribe their crystal structure.",8.70,4.45,3.38,.68,14,RGBColor(215,225,234),False,PP_ALIGN.CENTER)
    add_footer(s,3,"Sanz, Valeriani, Frenkel & Dijkstra, Phys. Rev. Lett. 99, 055501 (2007), DOI 10.1103/PhysRevLett.99.055501.")
    # 4
    s=new("Why move to p* = 18?","State-point choice")
    add_text(s,"p* = 15",1.05,1.75,2.1,.45,24,BLUE,True,PP_ALIGN.CENTER); add_text(s,"p* = 18",9.75,1.75,2.1,.45,24,ORANGE,True,PP_ALIGN.CENTER)
    add_rect(s,1.15,2.45,2.0,.16,BLUE); add_rect(s,3.15,2.49,6.55,.08,RGBColor(185,197,208)); add_rect(s,9.70,2.45,2.0,.16,ORANGE)
    add_text(s,"Rare event\nFFS needed",.95,3.05,2.45,.9,19,INK,True,PP_ALIGN.CENTER); add_text(s,"Higher postcritical probability\nDirect kinetic MC is feasible",9.25,3.05,2.95,.9,19,INK,True,PP_ALIGN.CENTER)
    add_rect(s,3.65,4.55,5.95,1.15,RGBColor(242,247,250),TEAL,True); add_text(s,"The paper reports the same no-swap phenomenology at p* = 18:\na substitutionally disordered FCC lattice forms.",3.95,4.70,5.35,.78,17,NAVY,True,PP_ALIGN.CENTER)
    add_footer(s,4,"The paper does not report the exact number of p* = 18 cycles or the brute-force displacement size.")
    # 5
    s=new("Our reconstruction isolates one controlled difference","Experimental design")
    add_bullets(s,["Reconstruct only the no-swap, brute-force p* = 18 experiment.","Preserve N, composition, T*, p*, interaction, cutoff, and MC–NpT ensemble.","Start both trajectories from one byte-identical validated liquid.","Compare dr = 0.01 and dr = 0.04 because the paper does not specify dr for its p* = 18 brute-force run."],.78,1.55,7.1,4.7,18)
    add_rect(s,8.25,1.72,4.25,1.55,RGBColor(232,241,250),BLUE,True); add_text(s,"TRIAL A",8.58,1.93,1.2,.3,12,BLUE,True); add_text(s,"dr = 0.01",8.58,2.35,3.55,.48,28,NAVY,True)
    add_rect(s,8.25,3.62,4.25,1.55,RGBColor(252,241,228),ORANGE,True); add_text(s,"TRIAL B",8.58,3.83,1.2,.3,12,ORANGE,True); add_text(s,"dr = 0.04",8.58,4.25,3.55,.48,28,NAVY,True)
    add_text(s,"Controlled comparison—not a claim that either dr is uniquely specified by the paper.",8.35,5.55,4.05,.7,13,MID,False,PP_ALIGN.CENTER)
    add_footer(s,5)
    # 6
    s=new("Production began from a validated metastable liquid","Parent-state validation")
    add_picture(s,snaps[0][0],.75,1.50,4.75,4.95)
    vals=[("ρ","1.03708"),("η","0.54301"),("overlaps","0"),("PTM crystal","0"),("CNA-BCC","1 isolated"),("max S(hkl)","2.03")]
    for i,(a,b) in enumerate(vals):
        x=5.85+(i%2)*3.15; y=1.62+(i//2)*1.35
        add_rect(s,x,y,2.78,1.02,LIGHT,LIGHT,True); add_text(s,a,x+.16,y+.12,2.42,.25,11,MID,True); add_text(s,b,x+.16,y+.43,2.42,.40,21,NAVY,True)
    add_rect(s,5.85,5.85,5.93,.60,TEAL,TEAL,True); add_text(s,"No single classifier carried the argument",5.92,5.88,5.80,.50,16,WHITE,True,PP_ALIGN.CENTER)
    add_footer(s,6,"Validated parent: common/validated_parent_N1000_T1_P18.res; SHA-256 begins 7e406f2b…")
    # 7
    s=new("From liquid preparation to structural evidence","Simulation protocol")
    stages=[("01","Prepare liquid","earlier p* = 18 history"),("02","Validate parent","geometry + PTM/CNA + S(k)"),("03","Tune & pilot","acceptance + volume moves"),("04","Smoke test","segment chaining + hashes"),("05","Production","12 × 250k cycles"),("06","Analyse","thermo + connected domains")]
    for i,(num,title,sub) in enumerate(stages):
        x=.72+i*2.08; add_rect(s,x,2.08,1.73,2.25,LIGHT,LIGHT,True); add_text(s,num,x+.12,2.20,.52,.34,14,TEAL,True); add_text(s,title,x+.12,2.77,1.50,.52,17,NAVY,True); add_text(s,sub,x+.12,3.42,1.50,.55,11,MID)
        if i<5: add_text(s,"→",x+1.75,2.92,.30,.45,20,MID,True,PP_ALIGN.CENTER)
    add_rect(s,1.38,5.20,10.55,.75,NAVY,NAVY,True); add_text(s,"Every segment records parameters, input lineage, seed, hashes, completion state, and move statistics.",1.58,5.29,10.15,.55,16,WHITE,True,PP_ALIGN.CENTER)
    add_footer(s,7)
    # 8
    s=new("Two trajectories; one deliberately changed parameter","Controlled trials")
    rows=[("Maximum displacement","0.01","0.04"),("Particles / composition","1000 / 50:50","1000 / 50:50"),("T* / p*","1 / 18","1 / 18"),("κσ / cutoff","6 / 3.5σ","6 / 3.5σ"),("Volume step vmax","0.0005","0.0005"),("Swap moves","none","none"),("Production","3M cycles","3M cycles")]
    add_text(s,"CONTROL",.92,1.46,3.5,.35,12,MID,True); add_text(s,"dr = 0.01",5.16,1.46,2.6,.35,14,BLUE,True,PP_ALIGN.CENTER); add_text(s,"dr = 0.04",9.03,1.46,2.6,.35,14,ORANGE,True,PP_ALIGN.CENTER)
    for i,(a,b,c) in enumerate(rows):
        y=1.94+i*.68; fill=LIGHT if i%2==0 else WHITE
        add_rect(s,.82,y,11.65,.60,fill,fill); add_text(s,a,1.00,y+.05,3.3,.48,14,INK,True); add_text(s,b,4.90,y+.05,3.1,.48,14,BLUE,False,PP_ALIGN.CENTER); add_text(s,c,8.78,y+.05,3.1,.48,14,ORANGE,False,PP_ALIGN.CENTER)
    add_footer(s,8,"The branches use different random-number sequences; replicate seeds are still needed for causal inference.")
    # 9
    s=new("The production campaign was large and auditable","Run scale")
    add_rect(s,.78,1.62,3.60,1.55,NAVY,NAVY,True); add_text(s,"3,000,000",.92,1.88,3.32,.56,31,WHITE,True,PP_ALIGN.CENTER); add_text(s,"MC cycles per trajectory",.92,2.48,3.32,.30,13,RGBColor(205,220,232),False,PP_ALIGN.CENTER)
    add_rect(s,4.85,1.62,3.60,1.55,TEAL,TEAL,True); add_text(s,"12 × 250,000",4.99,1.88,3.32,.56,27,WHITE,True,PP_ALIGN.CENTER); add_text(s,"chained production segments",4.99,2.48,3.32,.30,13,WHITE,False,PP_ALIGN.CENTER)
    add_rect(s,8.92,1.62,3.60,1.55,ORANGE,ORANGE,True); add_text(s,"1,000 + ~1",9.06,1.88,3.32,.56,27,WHITE,True,PP_ALIGN.CENTER); add_text(s,"particle + volume trials / cycle",9.06,2.48,3.32,.30,13,WHITE,False,PP_ALIGN.CENTER)
    for j,(name,m,col) in enumerate([("dr = 0.01",m1,BLUE),("dr = 0.04",m4,ORANGE)]):
        y=3.78+j*1.22; add_text(s,name,.95,y,1.35,.35,15,col,True)
        add_text(s,f"{m['particle_attempts']/1e9:.3f}B",2.55,y,1.65,.35,19,NAVY,True,PP_ALIGN.CENTER); add_text(s,"particle attempts",2.55,y+.38,1.65,.24,10,MID,False,PP_ALIGN.CENTER)
        add_text(s,f"{m['particle_accepted']/1e9:.3f}B",4.60,y,1.65,.35,19,NAVY,True,PP_ALIGN.CENTER); add_text(s,"accepted",4.60,y+.38,1.65,.24,10,MID,False,PP_ALIGN.CENTER)
        add_text(s,f"{m['volume_attempts']/1e6:.3f}M",6.70,y,1.65,.35,19,NAVY,True,PP_ALIGN.CENTER); add_text(s,"volume attempts",6.70,y+.38,1.65,.24,10,MID,False,PP_ALIGN.CENTER)
        add_text(s,f"{m['volume_accepted']/1e3:.1f}k",8.80,y,1.65,.35,19,NAVY,True,PP_ALIGN.CENTER); add_text(s,"accepted",8.80,y+.38,1.65,.24,10,MID,False,PP_ALIGN.CENTER)
        add_text(s,f"{100*m['particle_rate']:.2f}% / {100*m['volume_rate']:.2f}%",10.70,y,1.65,.35,17,col,True,PP_ALIGN.CENTER); add_text(s,"particle / volume",10.70,y+.38,1.65,.24,10,MID,False,PP_ALIGN.CENTER)
    add_footer(s,9,"Totals summed from the final accounting row of all 12 production segments in each branch.")
    # 10
    s=new("The larger displacement lowers particle acceptance","Move statistics")
    add_picture(s,ASSETS/"acceptance.png",.85,1.45,7.0,4.95)
    add_rect(s,8.28,1.72,4.08,1.25,RGBColor(232,241,250),BLUE,True); add_text(s,f"{100*m1['particle_rate']:.1f}%",8.55,1.89,1.45,.48,26,BLUE,True); add_text(s,"particle acceptance\ndr = 0.01",10.02,1.84,2.0,.72,14,INK,True)
    add_rect(s,8.28,3.22,4.08,1.25,RGBColor(252,241,228),ORANGE,True); add_text(s,f"{100*m4['particle_rate']:.1f}%",8.55,3.39,1.45,.48,26,ORANGE,True); add_text(s,"particle acceptance\ndr = 0.04",10.02,3.34,2.0,.72,14,INK,True)
    add_text(s,"Volume acceptance remains similar (~22%), so the later structural contrast is not explained by a frozen volume mover.",8.42,5.05,3.78,1.05,15,NAVY,True,PP_ALIGN.CENTER)
    add_footer(s,10)
    # 11
    s=new("Only dr = 0.04 enters a distinct late-time regime","Thermodynamic evolution")
    add_picture(s,ASSETS/"thermodynamics.png",.72,1.35,8.15,5.55)
    add_rect(s,9.08,1.64,3.65,1.55,RGBColor(232,241,250),BLUE,True); add_text(s,"dr = 0.01",9.35,1.83,3.10,.32,14,BLUE,True); add_text(s,"late 500k mean\nρ = 1.04468\nE/N = −0.94660",9.35,2.19,3.10,.78,16,NAVY,True)
    add_rect(s,9.08,3.48,3.65,1.55,RGBColor(252,241,228),ORANGE,True); add_text(s,"dr = 0.04",9.35,3.67,3.10,.32,14,ORANGE,True); add_text(s,"late 500k mean\nρ = 1.10217\nE/N = −0.80909",9.35,4.03,3.10,.78,16,NAVY,True)
    add_text(s,"Thermodynamics tells us something changed—not what structure formed.",9.20,5.65,3.40,.72,14,TEAL,True,PP_ALIGN.CENTER)
    add_footer(s,11)
    # 12
    s=new("Connected persistence turns labels into evidence","Structural analysis")
    steps=[("1","PTM","local FCC/HCP labels"),("2","Adaptive CNA","independent classifier"),("3","Connectivity","neighbors within 1.45σ"),("4","Persistence","track the largest domain")]
    for i,(n,a,b) in enumerate(steps):
        x=.82+i*3.10; add_rect(s,x,1.75,2.68,2.25,LIGHT,LIGHT,True); add_text(s,n,x+.16,1.92,.42,.38,16,TEAL,True); add_text(s,a,x+.18,2.52,2.30,.42,20,NAVY,True,PP_ALIGN.CENTER); add_text(s,b,x+.20,3.18,2.26,.52,13,MID,False,PP_ALIGN.CENTER)
    add_rect(s,1.35,4.78,10.65,1.05,NAVY,NAVY,True); add_text(s,"500 crystalline labels scattered through the box  ≠  one connected domain of 500 particles",1.60,4.98,10.15,.52,18,WHITE,True,PP_ALIGN.CENTER)
    add_text(s,"Agreement between PTM and CNA guards against a one-classifier artifact.",2.48,6.22,8.30,.38,15,TEAL,True,PP_ALIGN.CENTER)
    add_footer(s,12)
    # 13
    s=new("Persistent close-packed growth appears only for dr = 0.04","Cluster evolution")
    add_picture(s,ASSETS/"cluster_growth.png",.72,1.42,8.45,5.25)
    add_text(s,"dr = 0.01",9.50,1.65,2.7,.35,15,BLUE,True,PP_ALIGN.CENTER); add_text(s,"max PTM  13\nfinal PTM  4\nlate mean  2.6",9.50,2.12,2.7,1.13,20,NAVY,True,PP_ALIGN.CENTER)
    add_text(s,"dr = 0.04",9.50,3.58,2.7,.35,15,ORANGE,True,PP_ALIGN.CENTER); add_text(s,"max PTM  559\nfinal PTM  484\nlate mean  509",9.50,4.05,2.7,1.13,20,NAVY,True,PP_ALIGN.CENTER)
    add_footer(s,13,"Threshold crossings are first saved frames, not exact nucleation or commitment times.")
    # 14
    s=new("The domain grows, connects, and survives","Structural snapshots · dr = 0.04")
    xs=[.55,3.10,5.65,8.20,10.75]
    for x,(path,n,f,h) in zip(xs,snaps):
        add_picture(s,path,x,1.50,2.15,3.05); add_text(s,f"largest domain: {n}",x,4.72,2.15,.32,11,NAVY,True,PP_ALIGN.CENTER)
    add_text(s,"Gray: liquid/other     Blue: FCC in largest domain     Gold: HCP in largest domain",2.15,5.45,9.0,.40,14,INK,True,PP_ALIGN.CENTER)
    add_rect(s,2.00,6.18,9.30,.55,TEAL,TEAL,True); add_text(s,"Connectivity—not merely the number of colored particles—is the central visual test.",2.08,6.20,9.14,.48,15,WHITE,True,PP_ALIGN.CENTER)
    add_footer(s,14,"PTM classification with RMSD cutoff 0.10; connected FCC/HCP domain cutoff 1.45σ.")
    # 15
    s=new("The two independent classifiers tell the same story","Persistence & structure")
    add_rect(s,.82,1.62,5.62,3.78,RGBColor(252,241,228),ORANGE,True); add_text(s,"FINAL dr = 0.04 STATE",1.15,1.95,4.95,.35,13,ORANGE,True,PP_ALIGN.CENTER)
    add_text(s,"PTM connected domain  484\nCNA connected domain  440",1.15,2.55,4.95,1.12,24,NAVY,True,PP_ALIGN.CENTER)
    add_text(s,"PTM composition\n160 FCC + 324 HCP",1.15,3.95,4.95,.80,18,INK,True,PP_ALIGN.CENTER)
    add_rect(s,6.88,1.62,5.62,3.78,NAVY,NAVY,True); add_text(s,"PERSISTENCE TEST",7.18,1.95,5.02,.35,13,TEAL,True,PP_ALIGN.CENTER)
    add_text(s,"501 / 501",7.18,2.55,5.02,.62,34,WHITE,True,PP_ALIGN.CENTER); add_text(s,"frames in the final 500k window\nhave PTM and CNA domains > 100",7.18,3.28,5.02,.95,18,WHITE,True,PP_ALIGN.CENTER)
    add_text(s,"Interpretation: persistent close-packed crystalline growth, with FCC/HCP mixing consistent with stacking faults.",1.30,5.93,10.72,.58,16,TEAL,True,PP_ALIGN.CENTER)
    add_footer(s,15)
    # 16
    s=new("What we can say—and what comes next","Conclusion")
    add_rect(s,.78,1.50,7.22,3.88,NAVY,NAVY,True); add_text(s,"SUPPORTED",1.10,1.83,2.0,.35,13,TEAL,True)
    add_bullets(s,["Both branches began from the same validated liquid.","dr = 0.04 developed a large, persistent close-packed domain after ~2.05M cycles.","dr = 0.01 remained liquid-like through 3M cycles.","The no-swap outcome is qualitatively consistent with the paper’s FCC-like kinetic pathway."],1.05,2.30,6.55,2.70,17,WHITE)
    add_rect(s,8.38,1.50,4.18,3.88,LIGHT,LIGHT,True); add_text(s,"NOT YET SUPPORTED",8.72,1.83,3.48,.35,13,RED,True)
    add_bullets(s,["An exact nucleation time.","A nucleation rate.","A universal causal effect of dr.","A pure bulk FCC phase."],8.68,2.30,3.42,2.55,16,INK)
    add_rect(s,1.23,5.88,10.88,.64,ORANGE,ORANGE,True); add_text(s,"Next: multiple seeds + intermediate dr values + longer trajectories",1.36,5.91,10.62,.56,17,WHITE,True,PP_ALIGN.CENTER)
    add_footer(s,16)

    path=OUT/"MC_NPT_Yukawa_Replication_Results.pptx"; prs.save(path)
    with open(OUT/"build_summary.txt","w") as f:
        f.write(f"Deck: {path.name}\nSlides: {len(prs.slides)}\n\n")
        for name,m in [("dr_0.01",m1),("dr_0.04",m4)]: f.write(name+"\n"+"\n".join(f"  {k}: {v}" for k,v in m.items())+"\n")
        f.write("\nSnapshots (cycle, largest domain, FCC, HCP):\n")
        for (cyc,_),(_,n,fcc,hcp) in zip([(0,''),(2049000,''),(2112000,''),(2285000,''),(3000000,'')],snaps): f.write(f"  {cyc}: {n}, {fcc}, {hcp}\n")
    print(path)


if __name__ == "__main__": build_deck()
