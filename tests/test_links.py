# -*- coding: utf-8 -*-
"""Relative Links in der Dokumentation zeigen auf Dateien, die es gibt.

Ein toter Link im README ist das Erste, was ein Besucher findet."""
import io
import os
import re
import subprocess
from urllib.parse import unquote

LINK = re.compile(r"\]\(([^)\s]+)\)|(?:src|href)=\"([^\"]+)\"")


def markdown_dateien(wurzel):
    dateien = set()
    for extra in ([], ["--others", "--exclude-standard"]):
        aus = subprocess.run(["git", "ls-files", "-z"] + extra + ["*.md"], cwd=wurzel,
                             capture_output=True, text=True).stdout
        dateien.update(d for d in aus.split("\0") if d)
    return sorted(dateien)


def test_relative_links_existieren(wurzel):
    tot = []
    for datei in markdown_dateien(wurzel):
        if datei.startswith("mappe/"):
            continue       # Projektmappe: eigene Verweise auf Word-Abschnitte
        text = io.open(os.path.join(wurzel, datei), encoding="utf-8").read()
        text = re.sub(r"```.*?```", "", text, flags=re.S)       # Codeblöcke nicht
        for treffer in LINK.finditer(text):
            ziel = treffer.group(1) or treffer.group(2)
            if re.match(r"^(https?:|mailto:|#)", ziel):
                continue
            pfad = unquote(ziel.split("#")[0])
            if not pfad:
                continue
            voll = os.path.normpath(os.path.join(wurzel, os.path.dirname(datei), pfad))
            if not os.path.exists(voll):
                tot.append("%s → %s" % (datei, ziel))
    assert not tot, "\n".join(tot)
