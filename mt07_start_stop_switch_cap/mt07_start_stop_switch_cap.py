"""
Yamaha MT-07 (2014-2017) - roter Start/Stopp-Schieber.
Nach Fotos + Massen vom Motorrad:
  - 4,5 mm schmaeler als v6
  - Clip-Aufnahme fuer die zwei Rastzungen im Schalter:
      Tiefe 4,0 mm, Breite 4,1 mm an der Oeffnung -> 4,2 mm innen (leicht hinterschnitten)
  - Nut fuer die Fuehrungsleiste rechts neben dem Fenster (Leiste ca. 1 x 2 mm)
  - alle Kanten verrundet
Koordinaten: X = Breite (parallel zum Lenker, +X = rechts), Y/Z = Biegeebene.
Winkel in Grad: 0 = oben, positiv = Richtung Fahrer / nach unten.
"""
import math
import cadquery as cq

P = dict(
    r_in=21.0,
    t=4.0,                 # Dicke Grundkoerper (mehr Fleisch wegen Nut + Rastnase)
    width=9.5,             # war 14
    th_start=-14.0,
    th_end=62.0,
    body_fillet=1.0,       # Verrundung Grundkoerper
    # Griffnase
    tab_width=12.0,        # war 16.5
    tab_fillet=1.2,
    tab_profile=[(-14, 0.0), (-11, 3.2), (-6, 6.0), (-2, 5.3), (3, 6.8),
                 (9, 4.2), (16, 1.0), (19, 0.0)],
    groove_th=[-11.0, -9.4, -7.8, -6.2],
    groove_deg=0.8, groove_d=0.5,
    # Gravuren
    engrave=0.5,
    symbol=True, symbol_face=((5.5, 6.0), (14.5, 1.5)), symbol_r=2.2, symbol_line=0.55,
    arrow=True, arrow_th=52.0, arrow_w=5.0, arrow_l=3.5,
    # Clip-Zapfen = Rasttest 3 Nr. 1 (passt am Motorrad)
    socket_th=26.0,        # Lage des Zapfens entlang des Bogens
    plug_x=6.3,            # Zapfen quer zum Lenker (passt zwischen Wand und Schiene)
    plug_l=7.0,            # Zapfen in Schieberichtung
    plug_h=5.0,            # Zapfenlaenge ab Innenseite des Schiebers
    plug_fillet=0.8,
    clip_l=5.5,            # Tasche in Schieberichtung
    entry_w=4.8,           # Einfuehrbereich
    nose_w=4.0,            # Engstelle Rastnase
    ramp=0.35,             # Anlaufschraege
    nose_t=0.4,            # Dicke Rastnase
    rastkante=1.4,         # Rastkante ueber der Oeffnung
    chamber_w=5.0,         # Kammer fuer Widerhaken
    clip_depth=4.4,        # Taschentiefe ab Oeffnung
    # Nut fuer Fuehrungsleiste (rechts)
    rail=True,
    rail_x=4.2,            # Nut beginnt 0,15 mm neben dem Zapfen, nach aussen offen            # Mitte der Nut ab Mitte Schieber, + = rechts
    rail_w=1.8,            # Leiste 1,0 + reichlich Spiel (v7 war zu eng)
    rail_d=2.7,            # Leiste 2,0 + Spiel
)


def pt(r, th):
    a = math.radians(th)
    return (-r * math.sin(a), r * math.cos(a))


def sector(r0, r1, th0, th1, w, x0=None):
    m = (th0 + th1) / 2
    s = (cq.Workplane("YZ").moveTo(*pt(r0, th0)).lineTo(*pt(r1, th0))
         .threePointArc(pt(r1, m), pt(r1, th1)).lineTo(*pt(r0, th1))
         .threePointArc(pt(r0, m), pt(r0, th0)).close().extrude(w))
    return s.translate((-w / 2 if x0 is None else x0, 0, 0))


def profile_r(prof, th):
    for (a0, r0), (a1, r1) in zip(prof, prof[1:]):
        if a0 <= th <= a1:
            return r0 + (r1 - r0) * (th - a0) / (a1 - a0)
    return prof[-1][1]


def try_fillet(shape, r, sel=None):
    for rr in (r, r * 0.75, r * 0.5, r * 0.3):
        try:
            res = (shape.edges(sel) if sel else shape.edges()).fillet(rr)
            if res.val().isValid():
                return res
        except Exception:
            pass
    return shape


def build(p=P):
    ri, t = p["r_in"], p["t"]
    ro = ri + t

    body = sector(ri, ro, p["th_start"], p["th_end"], p["width"])
    body = try_fillet(body, p["body_fillet"])

    # Griffnase
    prof = [(th, ro + dh) for th, dh in p["tab_profile"]]
    th0, th1 = prof[0][0], prof[-1][0]
    tab = (cq.Workplane("YZ").moveTo(*pt(ri + 0.5, th0)).lineTo(*pt(prof[0][1], th0))
           .spline([pt(r, th) for th, r in prof[1:]], includeCurrent=True)
           .lineTo(*pt(ri + 0.5, th1))
           .threePointArc(pt(ri + 0.5, (th0 + th1) / 2), pt(ri + 0.5, th0)).close()
           .extrude(p["tab_width"]).translate((-p["tab_width"] / 2, 0, 0)))
    tab = try_fillet(tab, p["tab_fillet"])
    body = body.union(tab)

    # Rillen
    for th in p["groove_th"]:
        rs = profile_r(prof, th)
        body = body.cut(sector(rs - p["groove_d"], rs + 4, th - p["groove_deg"] / 2,
                               th + p["groove_deg"] / 2, p["tab_width"] - 2.5))

    e = p["engrave"]
    if p["symbol"]:
        (tha, ha), (thb, hb) = p["symbol_face"]
        ya, za = pt(ro + ha, tha)
        yb, zb = pt(ro + hb, thb)
        ym, zm = (ya + yb) / 2, (za + zb) / 2
        ty, tz = yb - ya, zb - za
        n = math.hypot(ty, tz)
        ty, tz = ty / n, tz / n
        nrm = (0, tz, -ty)
        if nrm[1] * ym + nrm[2] * zm < 0:
            nrm = (0, -tz, ty)
        pl = cq.Plane(origin=(0, ym, zm), xDir=(1, 0, 0), normal=nrm)
        r, lw = p["symbol_r"], p["symbol_line"]
        body = body.cut(cq.Workplane(pl).workplane(offset=-e).circle(r).circle(r - lw).extrude(e + 2))
        body = body.cut(cq.Workplane(pl).workplane(offset=-e).transformed(rotate=(0, 0, 45))
                        .rect(2 * r + 1.2, lw).extrude(e + 2))

    if p["arrow"]:
        a = math.radians(p["arrow_th"])
        y, z = pt(ro, p["arrow_th"])
        pl = cq.Plane(origin=(0, y, z), xDir=(1, 0, 0), normal=(0, -math.sin(a), math.cos(a)))
        w, l = p["arrow_w"], p["arrow_l"]
        body = body.cut(cq.Workplane(pl).workplane(offset=-e)
                        .polyline([(-w / 2, l / 2), (w / 2, l / 2), (0, -l / 2)]).close()
                        .extrude(e + 1))

    # Clip-Zapfen (radial nach innen) mit Schnapptasche - wie Rasttest 3 Nr. 1
    a = math.radians(p["socket_th"])
    inward = (0, math.sin(a), -math.cos(a))
    outward = (0, -math.sin(a), math.cos(a))
    y0, z0 = pt(ri + 0.5, p["socket_th"])
    bpl = cq.Plane(origin=(0, y0, z0), xDir=(1, 0, 0), normal=inward)
    plug = cq.Workplane(bpl).rect(p["plug_x"], p["plug_l"]).extrude(p["plug_h"] + 0.5)
    plug = try_fillet(plug, p["plug_fillet"], "|Z")
    try:
        plug = plug.faces(">Z").edges().chamfer(0.3)
    except Exception:
        pass
    body = body.union(plug)
    yo, zo = pt(ri - p["plug_h"], p["socket_th"])
    opl = cq.Plane(origin=(0, yo, zo), xDir=(1, 0, 0), normal=outward)
    L = p["clip_l"]

    def slab(w, d0, d1):
        return cq.Workplane(opl).workplane(offset=d0).rect(w, L).extrude(d1 - d0)

    rk = p["rastkante"]
    dn0 = rk - p["nose_t"]
    dr0 = max(0.0, dn0 - p["ramp"])
    body = body.cut(slab(p["entry_w"], -0.3, dr0 + 0.01))
    if dn0 > dr0:
        body = body.cut(cq.Workplane(opl).workplane(offset=dr0).rect(p["entry_w"], L)
                        .workplane(offset=dn0 - dr0).rect(p["nose_w"], L).loft())
    body = body.cut(slab(p["nose_w"], dn0 - 0.01, rk + 0.01))
    body = body.cut(slab(p["chamber_w"], rk, p["clip_depth"]))

    # Nut fuer Fuehrungsleiste: entlang des Bogens an der Innenseite, rechts
    if p["rail"]:
        # nach rechts offen bis zum Rand -> keine duenne Restwand
        rail = sector(ri - 5, ri + p["rail_d"], p["th_start"] - 2, p["th_end"] + 2, 10,
                      x0=p["rail_x"] - p["rail_w"] / 2)
        body = body.cut(rail)
    return body


if __name__ == "__main__":
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    part = build()
    print("gueltig:", part.val().isValid(), "Volumen mm3:", round(part.val().Volume(), 1))
    bb = part.val().BoundingBox()
    print("Breite x:", round(bb.xlen, 2))
    cq.exporters.export(part, os.path.join(here, "mt07_start_stop_switch_cap.step"))
    cq.exporters.export(part, os.path.join(here, "mt07_start_stop_switch_cap.stl"),
                        tolerance=0.02, angularTolerance=0.1)
    print("ok")
