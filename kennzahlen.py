# -*- coding: utf-8 -*-
r"""
kennzahlen.py  –  misst die Schwellen aus docs/codex-for-oss/PLAN.md, Abschnitt 5

    python3 kennzahlen.py                 # Tabelle ausgeben
    python3 kennzahlen.py --markdown      # als Markdown-Tabelle für PLAN.md

Was GitHub weiß (Sterne, Mitwirkende, Release-Downloads, Korrekturen,
Codex-Reviews), holt das Skript selbst über die öffentliche API – ohne
Zugang, nur mit Python. Mit einem Token in GITHUB_TOKEN sind mehr Abrufe pro
Stunde erlaubt.

Was GitHub nicht weiß (Play-Installationen, Hugging Face, Scorecard,
externe Verlinkungen), steht in docs/codex-for-oss/kennzahlen_manuell.json
und wird von Hand nachgetragen.

Rückgabewert 0, wenn genug Schwellen erreicht sind, um die Bewerbung
abzuschicken (PLAN.md: mindestens fünf von acht), sonst 1.
"""
import io
import json
import os
import sys
import urllib.error
import urllib.request

HIER = os.path.dirname(os.path.abspath(__file__))
REPO = "zmaj-lernapp/zmaj"
API = "https://api.github.com/repos/" + REPO
MANUELL = os.path.join(HIER, "docs", "codex-for-oss", "kennzahlen_manuell.json")
MAINTAINER = {"zmaj-lernapp"}
BOTS = ("[bot]",)
NOETIG = 5

# (Schlüssel, Bezeichnung, Schwelle zum Abschicken, Ziel) - wie PLAN.md §5
SCHWELLEN = [
    ("sterne", "GitHub-Sterne", 50, 150),
    ("installationen", "Play-Installationen", 300, 2000),
    ("downloads", "Datensatz-Downloads (Releases + Hugging Face)", 100, 500),
    ("mitwirkende", "externe Mitwirkende (Issue oder PR)", 3, 10),
    ("korrekturen", "übernommene Sprachkorrekturen", 5, 20),
    ("codex_reviews", "Pull Requests mit Codex-Review", 3, 10),
    ("scorecard", "OpenSSF Scorecard", 6.0, 7.5),
    ("verlinkungen", "externe Verlinkungen (HF, Kaggle, AnkiWeb, Zenodo)", 2, 4),
]


# ------------------------------------------------------------------- Abruf ---
def abruf(pfad):
    """Alle Seiten eines Listen-Endpunkts, oder das eine Objekt."""
    kopf = {"Accept": "application/vnd.github+json", "User-Agent": "zmaj-kennzahlen"}
    if os.environ.get("GITHUB_TOKEN"):
        kopf["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
    url, alles = API + pfad, []
    while url:
        with urllib.request.urlopen(urllib.request.Request(url, headers=kopf), timeout=20) as antwort:
            daten = json.loads(antwort.read().decode("utf-8"))
            weiter = antwort.headers.get("Link", "")
        if not isinstance(daten, list):
            return daten
        alles.extend(daten)
        url = None
        for teil in weiter.split(","):
            if 'rel="next"' in teil:
                url = teil[teil.index("<") + 1:teil.index(">")]
    return alles


def extern(login):
    return bool(login) and login not in MAINTAINER and not login.endswith(BOTS)


def von_github():
    repo = abruf("")
    issues = abruf("/issues?state=all&per_page=100")
    releases = abruf("/releases?per_page=100")
    kommentare = abruf("/issues/comments?per_page=100")

    leute = {i["user"]["login"] for i in issues if extern(i["user"]["login"])}
    korrekturen = sum(
        1 for i in issues
        if "pull_request" not in i and i["state"] == "closed" and i.get("state_reason") == "completed"
        and any(lbl["name"] == "language-correction" for lbl in i.get("labels", [])))
    reviews = {k["issue_url"] for k in kommentare if k.get("body", "").startswith("### Codex review")}
    downloads = sum(a["download_count"] for r in releases for a in r.get("assets", []))
    return {
        "sterne": repo["stargazers_count"],
        "mitwirkende": len(leute),
        "korrekturen": korrekturen,
        "codex_reviews": len(reviews),
        "downloads_github": downloads,
    }


def von_hand():
    if not os.path.exists(MANUELL):
        return {}
    return json.load(io.open(MANUELL, encoding="utf-8"))


# ---------------------------------------------------------------- Bewerten ---
def zusammenfuehren(github, hand):
    werte = dict(github)
    werte["downloads"] = github.get("downloads_github", 0) + hand.get("downloads_huggingface", 0)
    for schluessel in ("installationen", "scorecard", "verlinkungen"):
        werte[schluessel] = hand.get(schluessel)
    return werte


def bewerten(werte):
    """[(bezeichnung, wert, schwelle, ziel, erreicht)], Anzahl erreicht."""
    zeilen, erreicht = [], 0
    for schluessel, name, schwelle, ziel in SCHWELLEN:
        wert = werte.get(schluessel)
        ok = wert is not None and wert >= schwelle
        erreicht += ok
        zeilen.append((name, wert, schwelle, ziel, ok))
    return zeilen, erreicht


def ausgeben(zeilen, erreicht, markdown):
    if markdown:
        print("| Kennzahl | heute | Schwelle | Ziel | |")
        print("|---|---:|---:|---:|---|")
        for name, wert, schwelle, ziel, ok in zeilen:
            print("| %s | %s | %s | %s | %s |" % (name, "–" if wert is None else wert, schwelle, ziel,
                                                 "✅" if ok else "⬜"))
    else:
        for name, wert, schwelle, ziel, ok in zeilen:
            print("  %s  %-52s %8s  / %-6s (Ziel %s)" % ("✔" if ok else "·", name,
                                                         "–" if wert is None else wert, schwelle, ziel))
    print("\n%d von %d Schwellen erreicht – %s" % (
        erreicht, len(zeilen),
        "Bewerbung abschicken." if erreicht >= NOETIG else "noch %d bis zum Abschicken." % (NOETIG - erreicht)))


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    try:
        github = von_github()
    except (urllib.error.URLError, OSError, KeyError, ValueError) as fehler:
        print("GitHub nicht erreichbar (%s) – nur die Werte von Hand." % fehler)
        github = {}
    zeilen, erreicht = bewerten(zusammenfuehren(github, von_hand()))
    ausgeben(zeilen, erreicht, "--markdown" in argv)
    return 0 if erreicht >= NOETIG else 1


if __name__ == "__main__":
    raise SystemExit(main())
