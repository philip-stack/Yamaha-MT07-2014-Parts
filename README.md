# MT-07 (2014) – roter Start/Stopp-Schieber, rechte Lenkerarmatur

Nachbau der roten Schieberkappe der rechten Armatur (Yamaha 1WS-83975), 3D-Druck.

## Dateien
- `mt07_start_stop_switch_cap.stl` – druckfertig
- `mt07_start_stop_switch_cap.step` – CAD
- `mt07_start_stop_switch_cap.py` – parametrisches CadQuery-Skript (Masse oben im Block `P`)
- `snap_fit_test.py` – Rasttest für die Clip-Aufnahme (Nr. 1 passt: Rastkante 1,4 mm)
- `mt07_start_stop_switch_cap_preview.png` – Vorschau + Schnitt

## Clip-Aufnahme (am Motorrad getestet)
Zapfen 6,3 × 7,0 mm, 5 mm lang · Einführung 4,8 · Engstelle 4,0 · Rastkante 1,4 mm · Kammer 5,0 · Tiefe 4,4 · Länge 5,5

## Neu erzeugen
```
pip install cadquery trimesh
python3 mt07_start_stop_switch_cap.py
```

## Drucken
PETG oder ASA rot, 100 % Füllung, seitlich liegend.
