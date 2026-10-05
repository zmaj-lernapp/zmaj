"""Wörter und Kursstatistik offline über die öffentliche Paket-API abfragen."""

import argparse
import random

from . import LANGUAGES, counts, vocabulary


def _zeile(wort, sprache):
    return f"{wort['bs']} → {wort['translations'][sprache]}"


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m zmaj_bosnian")
    befehle = parser.add_subparsers(dest="befehl", required=True)
    wort = befehle.add_parser("word", help="Print one random Bosnian word and its meaning")
    suche = befehle.add_parser("search", help="Search Bosnian words and their meanings")
    suche.add_argument("text")
    for befehl in (wort, suche):
        befehl.add_argument("--lang", choices=LANGUAGES, default="en",
                            help="Translation language (default: en)")
    befehle.add_parser("stats", help="Print dataset counts")
    args = parser.parse_args(argv)
    if args.befehl == "stats":
        for name, zahl in sorted(counts().items()):
            print(f"{name}: {zahl}")
    elif args.befehl == "word":
        woerter = vocabulary()
        if not woerter:
            parser.error("The vocabulary is empty.")
        print(_zeile(random.choice(woerter), args.lang))
    else:
        text = args.text.strip().casefold()
        if not text:
            parser.error("Search text must not be empty.")
        treffer = [wort for wort in vocabulary()
                   if text in wort["bs"].casefold()
                   or text in wort["translations"][args.lang].casefold()]
        for wort in treffer:
            print(_zeile(wort, args.lang))
        if not treffer:
            print("No matching words.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
