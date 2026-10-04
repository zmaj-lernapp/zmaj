# Security policy

## Supported versions

Only the latest release of the app and the `master` branch receive fixes.

## What matters here

Zmaj has no server and no accounts; learning progress never leaves the
device. The parts that can still go wrong, and that we want to hear about:

- anything that makes the app contact a server it should not, or send more
  than the privacy policy (`sprachen.py`, `set.datenschutz_text`) says;
- script injection through a backup file (Settings → Backup → Import) or
  through content strings rendered as HTML;
- secrets or personal data in this repository or its history;
- a compromised third-party file in `web/` (`lottie.min.js`, fonts).

## Reporting a vulnerability

Please **do not open a public issue.** Use GitHub's private reporting:
[Report a vulnerability](https://github.com/zmaj-lernapp/zmaj/security/advisories/new),
or write to **zmaj.lernapp@gmail.com** with "Security" in the subject.

You will get an answer within **5 days**. Confirmed issues are fixed in the
next release, normally within 30 days, and you are credited in the release
notes unless you prefer otherwise.

## What we already do

- CodeQL (`security-extended`) on Python, JavaScript and the workflows, on
  every pull request and weekly.
- gitleaks over the full git history on every push.
- OpenSSF Scorecard, all GitHub Actions pinned to commit SHAs, workflows
  with read-only default permissions.
- The app loads no remote scripts, fonts or analytics; third-party files are
  vendored and listed in `web/LIZENZEN.txt` and `REUSE.toml`.
