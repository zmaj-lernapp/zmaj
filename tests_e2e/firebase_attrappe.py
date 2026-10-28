# -*- coding: utf-8 -*-
"""Ein nachgestelltes Firebase fuer die Browsertests (19.10.2026, seit
28.10.2026 eine eigene Datei fuer test_cloud.py und test_anmeldung.py).

Die Attrappe beantwortet jede Anfrage an Firebase Auth, den Token-Dienst
und Firestore im Browser selbst (page.route) - kein Byte verlaesst den
Rechner. Sie kann, was die App braucht:
  - anonym und mit E-Mail anlegen (accounts:signUp), dabei EMAIL_EXISTS und
    WEAK_PASSWORD,
  - mit Passwort anmelden (accounts:signInWithPassword), mit dem Schutz vor
    E-Mail-Aufzaehlung: falsche Adresse und falsches Passwort heissen
    beide INVALID_LOGIN_CREDENTIALS,
  - mit Google anmelden (accounts:signInWithIdp, Token "google-probe"),
  - Mails anstossen (accounts:sendOobCode, PASSWORD_RESET und VERIFY_EMAIL;
    der Kopf X-Firebase-Locale wird mitgeschrieben),
  - den Ausweis erneuern (securetoken), auf Wunsch mit TOKEN_EXPIRED oder
    einem 503,
  - je Konto ein Dokument users/{uid} lesen, schreiben, loeschen,
  - Konten loeschen, auch mit CREDENTIAL_TOO_OLD_LOGIN_AGAIN,
  - und auf Wunsch jede Anfrage abbrechen wie ohne Netz (abbruch).
"""
import json
import urllib.parse

FIREBASE = ("identitytoolkit.googleapis.com", "securetoken.googleapis.com", "firestore.googleapis.com")
PROJEKT = "zmaj-probe"
SCHLUESSEL = "AIza" + "Probe" * 7          # erfunden, nur fuer die Tests
# Aus Stuecken, damit tests/test_cloud.py (kein echter Wert im Repo) ihn
# nicht fuer einen echten haelt.
CLIENT = "1234567" + "89012-" + "probe" * 6 + ".apps." + "googleusercontent.com"
UID = "uidProbe1"


def dok_pfad(uid=UID):
    return "firestore.googleapis.com/v1/projects/%s/databases/(default)/documents/users/%s" % (PROJEKT, uid)


class Attrappe:
    """Beantwortet die Anfragen an Firebase im Browser selbst.

    19.10.2026, fuers Loeschen: alt sind Ausweise, mit denen Firebase das
    Konto nicht mehr loescht (CREDENTIAL_TOO_OLD_LOGIN_AGAIN - die Anmeldung
    liegt zu lange zurueck); google_uid ist das Konto, das Googles Auswahl
    liefert; dok_fehler laesst das Loeschen der Sicherung scheitern.
    28.10.2026: konten (E-Mail -> Passwort, uid) fuer die Anmeldung mit
    E-Mail, mails fuer sendOobCode, token_fehler fuer securetoken
    ("TOKEN_EXPIRED" oder eine Zahl wie 503), abbruch fuer ein Netz, das
    nicht antwortet. anmelde_fehler laesst das Anmelden und Anlegen
    scheitern, wie token_fehler (Pruefbericht vom 28.10.: der Ausweg
    "Erst einmal weiterlernen" auch bei Fehlern von Firebase).
    kontingent_weg: Firestore beantwortet alles mit 429 RESOURCE_EXHAUSTED,
    wie wenn das Tageskontingent des Projekts aufgebraucht ist
    (Gegenpruefung 28.10.: Abmelden sagt dann nicht "brauchst Internet")."""

    def __init__(self):
        self.doks = {}
        self.anfragen = []
        self.gueltig = {"id-1", "id-2"}
        self.id_uid = {"id-1": UID, "id-2": UID}
        self.erneuern = {"r-1": UID}
        self.alt = set()
        self.google_uid = UID
        self.google_n = 0
        self.dok_fehler = False
        self.konto_weg = False
        self.geloescht_mit = []
        self.konten = {}
        self.mails = []
        self.token_fehler = None
        self.anmelde_fehler = None
        self.kontingent_weg = False
        self.abbruch = False
        self.n = 0

    # Das Dokument des Probekontos UID - so lesen es die Tests vom 19.10.
    @property
    def dok(self):
        return self.doks.get(UID)

    @dok.setter
    def dok(self, wert):
        if wert is None:
            self.doks.pop(UID, None)
        else:
            self.doks[UID] = wert

    def _ausweis(self, uid):
        self.n += 1
        neu = "id-%s-%d" % (uid, self.n)
        self.gueltig.add(neu)
        self.id_uid[neu] = uid
        return neu

    def konto_anlegen(self, email, pw, uid=None):
        uid = uid or "uidMail%d" % (len(self.konten) + 1)
        self.konten[email.lower()] = {"pw": pw, "uid": uid}
        self.erneuern["r-" + uid] = uid
        return uid

    def __call__(self, route, request):
        url, art = request.url, request.method
        kopf = {"Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "authorization, content-type, x-firebase-locale",
                "Access-Control-Allow-Methods": "GET, POST, PATCH, DELETE, OPTIONS"}
        if art == "OPTIONS":
            return route.fulfill(status=204, headers=kopf)
        if self.abbruch:
            self.anfragen.append(("ABBRUCH", url, ""))
            return route.abort()
        teile = urllib.parse.urlsplit(url)
        ausweis = request.headers.get("authorization", "")
        self.anfragen.append((art, teile.netloc + urllib.parse.unquote(teile.path), ausweis))

        def antwort(status, daten):
            route.fulfill(status=status, headers=kopf, content_type="application/json", body=json.dumps(daten))

        def fehler(grund, status=400):
            return antwort(status, {"error": {"code": status, "message": grund}})

        schluessel = urllib.parse.parse_qs(teile.query).get("key", [""])[0]
        if teile.netloc != "firestore.googleapis.com" and schluessel != SCHLUESSEL:
            return fehler("API_KEY_INVALID")
        daten = {}
        if teile.netloc == "identitytoolkit.googleapis.com":
            daten = json.loads(request.post_data or "{}")
        if self.anmelde_fehler and teile.path in (
                "/v1/accounts:signUp", "/v1/accounts:signInWithPassword", "/v1/accounts:signInWithIdp"):
            f = self.anmelde_fehler
            return fehler("UNAVAILABLE", f) if isinstance(f, int) else fehler(f)
        if teile.path == "/v1/accounts:signUp":
            if "email" not in daten:
                return antwort(200, {"localId": UID, "idToken": "id-1", "refreshToken": "r-1", "expiresIn": "3600"})
            email, pw = str(daten.get("email", "")), str(daten.get("password", ""))
            if "@" not in email:
                return fehler("INVALID_EMAIL")
            if email.lower() in self.konten:
                return fehler("EMAIL_EXISTS")
            if len(pw) < 6:
                return fehler("WEAK_PASSWORD : Password should be at least 6 characters")
            uid = self.konto_anlegen(email, pw)
            return antwort(200, {"localId": uid, "email": email, "idToken": self._ausweis(uid),
                                 "refreshToken": "r-" + uid, "expiresIn": "3600"})
        if teile.path == "/v1/accounts:signInWithPassword":
            k = self.konten.get(str(daten.get("email", "")).lower())
            if not k or k["pw"] != daten.get("password"):
                return fehler("INVALID_LOGIN_CREDENTIALS")
            return antwort(200, {"localId": k["uid"], "email": daten["email"], "idToken": self._ausweis(k["uid"]),
                                 "refreshToken": "r-" + k["uid"], "expiresIn": "3600", "registered": True})
        if teile.path == "/v1/accounts:sendOobCode":
            self.mails.append({"art": daten.get("requestType"), "email": daten.get("email"),
                               "idToken": daten.get("idToken"),
                               "sprache": request.headers.get("x-firebase-locale")})
            if daten.get("requestType") == "VERIFY_EMAIL" and daten.get("idToken") not in self.gueltig:
                return fehler("INVALID_ID_TOKEN")
            # Mit dem Schutz vor E-Mail-Aufzaehlung auch fuer unbekannte Adressen 200.
            return antwort(200, {"email": daten.get("email") or ""})
        if teile.netloc == "securetoken.googleapis.com":
            if isinstance(self.token_fehler, int):
                return fehler("UNAVAILABLE", self.token_fehler)
            if self.token_fehler:
                return fehler(self.token_fehler)
            form = urllib.parse.parse_qs(request.post_data or "")
            uid = self.erneuern.get((form.get("refresh_token") or [""])[0])
            if form.get("grant_type") != ["refresh_token"] or not uid:
                return fehler("INVALID_REFRESH_TOKEN")
            neu = "id-2" if uid == UID else self._ausweis(uid)
            return antwort(200, {"id_token": neu, "refresh_token": form["refresh_token"][0], "expires_in": "3600",
                                 "user_id": uid, "project_id": "1"})
        if teile.path == "/v1/accounts:signInWithIdp":
            if daten.get("postBody") != "id_token=google-probe&providerId=google.com":
                return fehler("INVALID_IDP_RESPONSE")
            self.google_n += 1
            neu = "id-g%d" % self.google_n
            self.gueltig.add(neu)
            self.id_uid[neu] = self.google_uid
            self.erneuern["r-1"] = UID
            return antwort(200, {"localId": self.google_uid, "idToken": neu, "refreshToken": "r-1",
                                 "email": "probe@gmail.example", "expiresIn": "3600"})
        if teile.path == "/v1/accounts:delete":
            token = daten.get("idToken")
            self.geloescht_mit.append(token)
            if token not in self.gueltig:
                return fehler("INVALID_ID_TOKEN")
            if token in self.alt:
                return fehler("CREDENTIAL_TOO_OLD_LOGIN_AGAIN")
            if self.konto_weg:
                return fehler("USER_NOT_FOUND")
            self.konto_weg = True
            uid = self.id_uid.get(token)
            for email in [e for e, k in self.konten.items() if k["uid"] == uid]:
                del self.konten[email]
            return antwort(200, {})
        if teile.netloc == "firestore.googleapis.com":
            vorn = "/v1/projects/%s/databases/(default)/documents/users/" % PROJEKT
            pfad = urllib.parse.unquote(teile.path)
            if not pfad.startswith(vorn):
                return antwort(404, {"error": {"status": "NOT_FOUND"}})
            if self.kontingent_weg:
                return antwort(429, {"error": {"code": 429, "message": "Quota exceeded.",
                                               "status": "RESOURCE_EXHAUSTED"}})
            uid = pfad[len(vorn):]
            token = ausweis[len("Bearer "):] if ausweis.startswith("Bearer ") else ""
            if token not in self.gueltig or self.id_uid.get(token) != uid:
                return antwort(403, {"error": {"status": "PERMISSION_DENIED"}})
            if art == "GET":
                return antwort(200, {"fields": self.doks[uid]}) if uid in self.doks \
                    else antwort(404, {"error": {"status": "NOT_FOUND"}})
            if art == "PATCH":
                self.doks[uid] = json.loads(request.post_data)["fields"]
                return antwort(200, {"fields": self.doks[uid]})
            if art == "DELETE":
                if self.dok_fehler:
                    return antwort(503, {"error": {"code": 503, "status": "UNAVAILABLE"}})
                self.doks.pop(uid, None)
                return antwort(200, {})
        return antwort(404, {"error": {"message": "unbekannt"}})


def wege(attrappe):
    return [(a, p) for a, p, _ in attrappe.anfragen]
