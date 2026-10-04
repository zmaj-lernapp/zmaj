# -*- coding: utf-8 -*-
r"""
paket_bauen.py  –  das PyPI-Paket zmaj-bosnian aus data/ bauen

    python3 paket_bauen.py            # kopiert data/*.json und baut nach paket/dist/
    python3 paket_bauen.py --nur-kopieren

Die JSON-Dateien liegen nicht doppelt im Repository: Sie werden erst hier aus
data/ ins Paket kopiert. Vorher prüft daten_exportieren.py, dass data/ zu
den Quelldateien passt - ein Paket aus veraltetem Stand gibt es nicht.
Veröffentlicht wird über .github/workflows/pypi.yml, nicht von Hand.
"""
import os
import shutil
import subprocess
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
PAKET = os.path.join(HIER, "paket")
ZIEL = os.path.join(PAKET, "src", "zmaj_bosnian", "daten")
DATEIEN = ("vocabulary", "sentences", "stories", "glossary", "grammar", "manifest")


def kopieren():
    sys.path.insert(0, HIER)
    import daten_exportieren
    if daten_exportieren.main(["--pruefen"]) != 0:
        raise SystemExit("data/ ist veraltet - erst  python3 daten_exportieren.py")
    os.makedirs(ZIEL, exist_ok=True)
    for name in DATEIEN:
        shutil.copyfile(os.path.join(HIER, "data", name + ".json"), os.path.join(ZIEL, name + ".json"))
    shutil.copyfile(os.path.join(HIER, "LICENSE-CONTENT"), os.path.join(PAKET, "LICENSE"))
    print("Daten ins Paket kopiert: %s" % ", ".join(DATEIEN))


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    kopieren()
    if "--nur-kopieren" in argv:
        return 0
    return subprocess.call([sys.executable, "-m", "build", "--outdir", os.path.join(PAKET, "dist"), PAKET])


if __name__ == "__main__":
    raise SystemExit(main())
