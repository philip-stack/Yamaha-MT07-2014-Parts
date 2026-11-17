"""
Rasttest 3 fuer den MT-07 Schieber.
Schmale Zapfen (passen ins Fenster neben der Fuehrungsschiene) mit Clip-Tasche,
Variante = Hoehe der Rastkante ueber der Oeffnung. Oben eine Griffplatte.
Nummer in die Griffplatte gepraegt. Drucken mit der Oeffnung nach OBEN
(Griffplatte unten auf dem Bett).
"""
import cadquery as cq

RASTKANTE = [1.4, 1.8, 2.2]   # Hoehe der Rastkante ueber der Oeffnung (mm)
NOSE_W = 4.0                  # Engstelle
ENTRY_W = 4.8
CHAMBER_W = 5.0
CLIP_L = 5.5                  # Laenge in Schieberichtung (Test 2: 4,0 war zu kurz)
RAMP = 0.35
NOSE_T = 0.4
DEPTH = 4.4
WALL = 0.75                   # Wand des Zapfens
PLUG_X = ENTRY_W + 2 * WALL   # 6,3 mm quer zum Lenker
PLUG_L = CLIP_L + 2 * WALL    # 5,5 mm in Schieberichtung
PLATE = (12.0, 10.0, 1.6)      # Griffplatte
PITCH = 15.0


def piece(rk, num):
    px, pl, pt = PLATE
    plate = cq.Workplane("XY").box(px, pl, pt, centered=(True, True, False)).edges("|Z").fillet(1.5)
    plug_h = DEPTH + 0.6
    plug = (cq.Workplane("XY").workplane(offset=pt).rect(PLUG_X, PLUG_L).extrude(plug_h)
            .edges("|Z").fillet(0.8))
    b = plate.union(plug)
    top = pt + plug_h                       # Oeffnung oben
    # Zapfen-Aussenkante oben leicht anfasen (leichter ins Fenster)
    b = b.faces(">Z").edges().chamfer(0.3)

    def slab(w, d0, d1):
        return cq.Workplane("XY").workplane(offset=top - d1).rect(w, CLIP_L).extrude(d1 - d0)

    d_nose_end = rk                          # Rastkante (gerade Flaeche)
    d_nose_start = rk - NOSE_T
    d_ramp_start = max(0.0, d_nose_start - RAMP)
    b = b.cut(slab(ENTRY_W, -0.1, d_ramp_start + 0.01))
    if d_nose_start > d_ramp_start:
        ramp = (cq.Workplane("XY").workplane(offset=top - d_ramp_start).rect(ENTRY_W, CLIP_L)
                .workplane(offset=-(d_nose_start - d_ramp_start)).rect(NOSE_W, CLIP_L).loft())
        b = b.cut(ramp)
    b = b.cut(slab(NOSE_W, d_nose_start - 0.01, d_nose_end + 0.01))
    b = b.cut(slab(CHAMBER_W, d_nose_end, DEPTH))
    txt = (cq.Workplane("XY").workplane(offset=0).center(-px / 2 + 2.6, 0)
           .text(str(num), 3.5, 0.5, kind="bold"))
    return b.cut(txt.translate((0, 0, -0.01)))


if __name__ == "__main__":
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    parts = None
    for i, rk in enumerate(RASTKANTE):
        p = piece(rk, i + 1).translate((i * PITCH, 0, 0))
        parts = p if parts is None else parts.union(p)
    print("gueltig:", parts.val().isValid())
    cq.exporters.export(parts, os.path.join(here, "snap_fit_test.stl"), tolerance=0.01, angularTolerance=0.05)
    cq.exporters.export(parts, os.path.join(here, "snap_fit_test.step"))
    print(f"Zapfen aussen: {PLUG_X:.1f} x {PLUG_L:.1f} mm")
    for i, rk in enumerate(RASTKANTE):
        print(f"Nr. {i+1}: Rastkante {rk} mm ueber der Oeffnung")
