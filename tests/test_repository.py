# -*- coding: utf-8 -*-
"""Was für das Repository als Ganzes gilt: keine Geheimnisse, gültige Lizenzen."""
import os
import subprocess

GEHEIM = ("mail_zugang.json", "tts_zugang.json", "keystore.properties",
          "codes.json", "sitzungen.json", "feedback.txt")


def git_dateien(wurzel):
    try:
        aus = subprocess.run(["git", "ls-files"], cwd=wurzel, capture_output=True,
                             text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        import pytest
        pytest.skip("kein git")
    return aus.splitlines()


def test_keine_zugangsdaten_eingecheckt(wurzel):
    dateien = git_dateien(wurzel)
    schlecht = [d for d in dateien
                if os.path.basename(d) in GEHEIM
                or d.endswith((".jks", ".keystore"))
                or os.path.basename(d).startswith("fortschritt_")]
    assert not schlecht, schlecht


def test_lizenzdateien_vorhanden(wurzel):
    for name in ("LICENSE", "LICENSE-CONTENT", "REUSE.toml", "TRADEMARK.md",
                 "LICENSES/AGPL-3.0-or-later.txt", "LICENSES/CC-BY-SA-4.0.txt"):
        assert os.path.exists(os.path.join(wurzel, name)), name
