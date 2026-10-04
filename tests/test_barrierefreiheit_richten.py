# -*- coding: utf-8 -*-
"""barrierefreiheit_richten.py passt auf den heutigen Stand von web/index.html.

Das Skript liegt bereit, bis der geschlossene Test vorbei ist (07.10.2026).
Ändert sich index.html vorher an einer seiner Stellen, soll das hier
auffallen und nicht erst am Tag des Builds. Ohne Browser, unter einer
Sekunde - die Messung mit axe steht in tests_e2e/."""
import re


def angewendet(text):
    import barrierefreiheit_richten
    return barrierefreiheit_richten.KENNUNG in text


def test_schalter_und_main_nach_dem_richten(index_html):
    import barrierefreiheit_richten
    text = index_html.replace("\r\n", "\n")
    if angewendet(text):
        return                       # schon geschrieben - dann gibt es nichts mehr zu prüfen
    neu, fehler = barrierefreiheit_richten.anwenden(text)
    assert not fehler, fehler
    # Jeder Schalter hat danach einen Namen aus einer sichtbaren Überschrift
    knoepfe = re.findall(r'<button class="switch"[^>]*>', neu)
    assert len(knoepfe) == 8
    assert all("aria-labelledby=" in k for k in knoepfe)
    assert neu.count("<main>") == 1 and neu.count("</main>") == 1
    assert neu.index("<main>") < neu.index('id="profileView"') < neu.index('id="settingsView"') \
        < neu.index("</main>") < neu.index('<footer data-t="app.fuss">')


def test_fehlende_stelle_bricht_ab(index_html):
    """Ist ein Anker weg, kommt ein Fehler - nicht ein halb geänderter Text."""
    import barrierefreiheit_richten
    text = index_html.replace("\r\n", "\n")
    if angewendet(text):
        return
    _, fehler = barrierefreiheit_richten.anwenden(text.replace('id="swAnim"', 'id="swAnimation"'))
    assert any(f.startswith("Schalter swAnim benannt:") for f in fehler), fehler


def _leuchtdichte(farbe):
    werte = [int(farbe[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    werte = [w / 12.92 if w <= 0.04045 else ((w + 0.055) / 1.055) ** 2.4 for w in werte]
    return 0.2126 * werte[0] + 0.7152 * werte[1] + 0.0722 * werte[2]


def _kontrast(a, b):
    hell, dunkel = sorted((_leuchtdichte(a), _leuchtdichte(b)), reverse=True)
    return (hell + 0.05) / (dunkel + 0.05)


def test_neue_farben_erreichen_4_5(index_html):
    """Die Farbwerte im Skript halten, was der Kommentar verspricht:
    jeder gedämpfte Ton mindestens 4,5:1 auf Grund, Fläche und sanftem Ton
    seiner Sektion (helle Fassung)."""
    import barrierefreiheit_richten
    text = index_html.replace("\r\n", "\n")
    if not angewendet(text):
        text, _ = barrierefreiheit_richten.anwenden(text)
    hell = text[text.index(":root{"):text.index("@media (prefers-color-scheme: dark)")]

    def token(name):
        return re.search(r"--%s:(#[0-9A-Fa-f]{6})" % re.escape(name), hell).group(1)

    for s in range(1, 10):
        matt = token("sek%d-matt" % s)
        for grund in ("grund", "flaeche", "sanft"):
            assert _kontrast(matt, token("sek%d-%s" % (s, grund))) >= 4.5, (s, grund)
    flaechen = [token("sek%d-flaeche" % s) for s in range(1, 10)] + [token("surface")]
    for name in ("good-text", "bad-text", "accent-text"):
        assert min(_kontrast(token(name), f) for f in flaechen) >= 4.5, name
