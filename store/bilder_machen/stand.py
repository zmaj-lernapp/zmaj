# -*- coding: utf-8 -*-
"""Vorfuehr-Lernstand fuer die Store-Bilder, auf heute verschoben.

Grundlage ist testdaten/zmaj-screenshots.json. Die Lerntage dort enden am
19.09.2026 - ohne Verschieben stuende auf dem ersten Bild "Deine Lernserie
ist leider gerissen". Bewertung und Einstufung gelten als erledigt, damit
keine Karte ueber dem Bild liegt.
"""
import datetime, json, os

HIER = os.path.dirname(os.path.abspath(__file__))
QUELLE = os.path.join(HIER, "..", "..", "testdaten", "zmaj-screenshots.json")
ZIEL = os.path.join(HIER, "_stand.json")

s = json.load(open(QUELLE, encoding="utf-8"))["stand"]
heute = datetime.date.today()
s["tage"] = sorted((heute - datetime.timedelta(days=i)).isoformat() for i in range(47))
s["rekord"] = 47
s["frost"] = []
s["bewertung"] = {"gezeigt": [], "nein": True, "bewertet": False}
s["einstufung"] = {"tag": s["tage"][0], "wahl": "neu", "bis": ""}
json.dump(s, open(ZIEL, "w", encoding="utf-8"), ensure_ascii=False)
print("Lernstand:", len(s["tage"]), "Tage bis", s["tage"][-1])
