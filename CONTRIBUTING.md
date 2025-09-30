# Contributing

Vielen Dank für dein Interesse, zu diesem Projekt beizutragen!

## Wie kann ich beitragen?

Es gibt viele Möglichkeiten, zum Embedded Linux SDK beizutragen:

1. **Bugs melden**: Öffne ein Issue, wenn du einen Fehler findest
2. **Features vorschlagen**: Teile deine Ideen für neue Features
3. **Dokumentation verbessern**: Hilf uns, die Dokumentation zu erweitern
4. **Code beitragen**: Sende Pull Requests für Bugfixes oder neue Features
5. **Beispiel-Konfigurationen**: Teile deine Konfigurationen für neue Hardware

## Pull Requests

### Vorbereitung

1. Fork das Repository
2. Erstelle einen Branch für deine Änderungen:
   ```bash
   git checkout -b feature/mein-feature
   ```

3. Mache deine Änderungen und teste sie gründlich

4. Committe mit aussagekräftigen Commit-Messages:
   ```bash
   git commit -m "Add support for new architecture XYZ"
   ```

5. Pushe zu deinem Fork:
   ```bash
   git push origin feature/mein-feature
   ```

6. Öffne einen Pull Request

### Code-Style

- **Shell-Scripts**: Folge den üblichen Bash-Konventionen
  - Verwende `set -e` und `set -u`
  - Kommentiere komplexe Abschnitte
  - Nutze aussagekräftige Variablennamen

- **Python**: Folge PEP 8
  - Verwende 4 Spaces für Einrückung
  - Dokumentiere Funktionen mit Docstrings
  - Halte Funktionen kurz und fokussiert

- **YAML**: Halte die Struktur konsistent
  - Verwende 2 Spaces für Einrückung
  - Füge Kommentare für nicht-offensichtliche Optionen hinzu

### Testing

Bevor du einen PR einreichst:

1. Teste deine Konfigurationen:
   ```bash
   python3 scripts/validate_config.py configs/deine-config.yaml
   ```

2. Führe einen Dry-Run durch:
   ```bash
   ./scripts/build.sh -c configs/deine-config.yaml --dry-run
   ```

3. Wenn möglich, teste einen vollständigen Build

## Neue Hardware-Plattformen hinzufügen

Um Unterstützung für eine neue Hardware-Plattform hinzuzufügen:

1. Erstelle eine Beispiel-Konfiguration in `configs/`:
   ```yaml
   # configs/meine-hardware.yaml
   architecture: arm64
   distribution:
     name: ubuntu
     release: jammy
   hostname: meine-hardware
   packages:
     - systemd
     - ...
   output:
     name: meine-hardware-image
     format: tar.gz
   ```

2. Füge Hardware-spezifische Skripte in `scripts/` hinzu (falls nötig)

3. Dokumentiere die Hardware-spezifischen Anforderungen in `docs/`

4. Teste die Konfiguration gründlich

5. Öffne einen PR mit:
   - Der neuen Konfiguration
   - Dokumentation
   - Evtl. zusätzlichen Skripten

## Dokumentation

Gute Dokumentation ist wichtig! Wenn du Änderungen machst, aktualisiere bitte:

- `README.md`: Hauptübersicht
- `docs/README.md`: Detaillierte Dokumentation
- `docs/USAGE.md`: Verwendungsbeispiele
- Kommentare in Konfigurationsdateien

## Fragen?

Wenn du Fragen hast:

1. Schaue in die vorhandene Dokumentation
2. Durchsuche geschlossene Issues
3. Öffne ein neues Issue mit dem Label "question"

## Code of Conduct

Sei freundlich und respektvoll zu anderen Contributors. Wir wollen eine einladende und inklusive Community aufbauen.

## Lizenz

Durch das Beitragen stimmst du zu, dass deine Beiträge unter der MIT-Lizenz lizenziert werden.
