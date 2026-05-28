# TODO — Offene Punkte aus der Roadmap

**Basis:** [plans/2026-05-22_danwa-modules-roadmap.md](plans/2026-05-22_danwa-modules-roadmap.md)

---

## Module-Repository (dieses Repo)

- [ ] **UI-Übersetzungspakete ins Modulformat überführen** — Die 55 ZIP-Dateien unter `ui-translations/` müssen als einzelne Module mit `manifest.json` + Profildatei strukturiert werden (Prio: hoch)
- [ ] **index.json-Generierung bei Release testen** — Erster `v1.0.0`-Tag wurde erstellt, publish.yml noch nicht getriggert (CI muss bestätigt werden)
- [ ] **Premium/Private Module** — Soll es später auch private Repos geben? Dann API-Key-Mechanismus nötig
- [ ] **Moderations-Prozess** — Wer reviewed PRs im Modul-Repo? Nur Repo-Owner oder Community?

## Danwa-Hauptprojekt (Backend)

- [ ] **Semver-Resolver** — Korrekte semver-Constraint-Prüfung einführen (`>=1.0.0`, `^2.0.0`, `~1.2.0`). Aktuell wird nur `!=` verglichen. Bibliothek: `packaging` oder `semver` für Python
- [ ] **Dependency-Resolver** — Prüfung und Auflösung von Modul-Abhängigkeiten beim Installieren:
  1. Alle referenzierten Dependencies sind installiert
  2. Installierte Versionen erfüllen semver-Constraints
  3. Keine zirkulären Dependencies
  4. Klare Fehlermeldungen mit Liste fehlender Module
- [ ] **GitHub-Index-Reader** — Abruf und Caching (5 Min) von `index.json` aus GitHub via `raw.githubusercontent.com`
- [ ] **GitHub-Release-Downloader** — Download von ZIPs aus GitHub Releases
- [ ] **Neue API-Endpunkte:**
  - `POST /api/v1/modules/install-from-repo` — Installation aus GitHub-Repo
  - `GET /api/v1/modules/repo-index` — Verfügbare Module abrufen
  - `POST /api/v1/modules/check-repo-updates` — Lokale vs. remote Versionen vergleichen
- [ ] **`prompt-modifier-text-only` Verzeichnisstruktur prüfen** — Wurde unter `agent-prompt-modifiers/` einsortiert. Prüfen ob die Typ-Ableitung in `type_derivation.py` damit korrekt funktioniert

## Danwa-Hauptprojekt (Frontend)

- [ ] **ModuleManager.svelte: Tab "GitHub"** — Neuer Tab im Build → Modules Bereich:
  - Durchsuchbare Liste verfügbarer Module aus dem Repo
  - Install-Button pro Modul
  - Anzeige von Version, Beschreibung, Übersetzungsstatus
- [ ] **Updates-Tab** — Zeigt Module mit `remote_version > local_version`

## CI/CD & Automatisierung

- [ ] **i18n-Sync-Automatismus** — Automatische Synchronisation von UI-Strings:
  - Danwa-CI extrahiert alle UI-Strings + zählt `total_strings`
  - Generiert aktualisiertes Translation-Base-Modul
  - Öffnet PR in `danwa-modules`: `chore: update translation base (942 strings)`
  - Aktualisiert `translation_stats` für alle Sprachpakete
  - **Entscheidung nötig:** Push (Danwa → Modul-Repo) oder Pull (Modul-Repo → Danwa)? Empfehlung: Push
- [ ] **Release-Strategie finalisieren** — Ein Tag pro Modul (`v1.2.0`) oder Gesamt-Release? Empfehlung: pro Modul

---

## Erledigt

- [x] Repository initialisiert (git, README, LICENSE, .gitignore)
- [x] Schema v3.0.0 erstellt (`schemas/module-manifest.json`)
- [x] 88 Module aus Danwa migriert und auf v3.0.0 angehoben
- [x] GitHub Actions: validate.yml + publish.yml
- [x] Scripts: validate.py, generate_index.py, migrate_modules.py
- [x] index.json mit 88 Modulen generiert
- [x] Migration Guide erstellt (`schemas/migration-guide.md`)
- [x] Initialer Commit + Push + Tag `v1.0.0`
