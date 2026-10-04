# -*- coding: utf-8 -*-
r"""
hf_hochladen.py  –  den Datensatz auf Hugging Face stellen

    python3 hf_hochladen.py --probe          # nur zeigen, was hochginge
    HF_TOKEN=hf_... python3 hf_hochladen.py  # hochladen (braucht huggingface_hub)

Ziel ist das Dataset-Repository zmaj-lernapp/zmaj-bosnian (oder
--repo name/datensatz). data/README.md ist die Datenkarte: Hugging Face liest
ihren YAML-Kopf (Lizenz, Sprachen, Größe, Konfigurationen) und zeigt den
Text als Startseite. Hochgeladen wird genau, was in data/ steht - vorher
prüft daten_exportieren.py, dass es zu den Quelldateien passt.

Die Tonspur geht nicht mit (37 MB, 2332 Dateien); die Pfade in den Daten
zeigen ins GitHub-Repository und auf die Zip-Datei im Release.

Im Release-Workflow läuft das Skript von selbst, sobald das Secret HF_TOKEN
gesetzt ist. Den Token gibt es unter huggingface.co → Settings → Access
Tokens (Rolle "write"). Er gehört nie ins Repository.
"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
DATEN = os.path.join(HIER, "data")
STANDARD_REPO = "zmaj-lernapp/zmaj-bosnian"


def dateien():
    for wurzel, _, namen in os.walk(DATEN):
        for n in sorted(namen):
            pfad = os.path.join(wurzel, n)
            yield os.path.relpath(pfad, DATEN).replace(os.sep, "/"), os.path.getsize(pfad)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    repo = argv[argv.index("--repo") + 1] if "--repo" in argv else STANDARD_REPO
    sys.path.insert(0, HIER)
    import daten_exportieren
    if daten_exportieren.main(["--pruefen"]) != 0:
        return 1
    liste = sorted(dateien())
    print("\n%d Dateien, %.1f MB  ->  https://huggingface.co/datasets/%s"
          % (len(liste), sum(g for _, g in liste) / 1048576.0, repo))
    for name, groesse in liste:
        print("  %8.1f KB  %s" % (groesse / 1024.0, name))
    if "README.md" not in dict(liste):
        print("Abbruch: data/README.md (die Datenkarte) fehlt.")
        return 1
    if "--probe" in argv:
        print("\n(Probe. Zum Hochladen ohne --probe und mit HF_TOKEN.)")
        return 0
    token = os.environ.get("HF_TOKEN")
    if not token:
        print("HF_TOKEN fehlt - nichts hochgeladen.")
        return 1
    from huggingface_hub import HfApi
    api = HfApi(token=token)
    api.create_repo(repo, repo_type="dataset", exist_ok=True)
    version = os.environ.get("ZMAJ_VERSION", "Stand aus dem Repository")
    api.upload_folder(folder_path=DATEN, repo_id=repo, repo_type="dataset",
                      commit_message="Zmaj dataset %s" % version)
    print("hochgeladen: https://huggingface.co/datasets/%s" % repo)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
