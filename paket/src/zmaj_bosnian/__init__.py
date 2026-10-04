# -*- coding: utf-8 -*-
"""The open Bosnian course of Zmaj (https://github.com/zmaj-lernapp/zmaj).

Data: CC BY-SA 4.0, (c) 2026 Ajdin Hasic. Code of this module: same terms.
The JSON files are copied from the repository's data/ folder when the
package is built (see paket_bauen.py), so package and dataset never differ.
"""
import json
from functools import lru_cache
from importlib import resources

__all__ = ["vocabulary", "levels", "sections", "sentences", "stories",
           "glossary", "grammar", "manifest", "counts", "LANGUAGES"]

LANGUAGES = ("de", "en", "tr", "sv", "nl", "nb", "da", "fr")


@lru_cache(maxsize=None)
def _lade(name):
    text = resources.files(__package__).joinpath("daten", name + ".json").read_text(encoding="utf-8")
    return json.loads(text)


def vocabulary():
    """All 1,728 words: id, bs, level, level_position, section, translations, audio."""
    return _lade("vocabulary")["entries"]


def levels():
    """The 65 levels in course order, with labels and tips in 8 languages."""
    return _lade("vocabulary")["levels"]


def sections():
    """The 9 sections of the learning path."""
    return _lade("vocabulary")["sections"]


def sentences():
    """300 cloze sentences: cloze, answer, bs (full sentence), translations."""
    return _lade("sentences")["entries"]


def stories():
    """12 graded stories with translations, glossary and questions."""
    return _lade("stories")["entries"]


def glossary():
    """406 reading-glossary entries: bs and translations."""
    return _lade("glossary")["entries"]


def grammar(language="en"):
    """The 16 grammar lessons as shown in the given interface language."""
    return _lade("grammar")["lessons"][language]


def manifest():
    """Counts, licence and checksums of the dataset this package was built from."""
    return _lade("manifest")


def counts():
    return dict(manifest()["counts"])
