# Häufig gestellte Fragen (FAQ)

## Allgemein

### Was ist das Embedded Linux SDK?

Das Embedded Linux SDK ist ein Tool zum Erstellen von Embedded Linux Images aus Debian/Ubuntu-Paketen. Es nutzt debootstrap, um ein Basis-System zu erstellen und installiert dann benutzerdefinierte Pakete basierend auf einer YAML-Konfiguration.

### Für welche Hardware ist das SDK geeignet?

Das SDK ist für verschiedene Embedded-Plattformen geeignet:
- NXP S32G2 (Automotive)
- Raspberry Pi (alle ARM64-Modelle)
- BeagleBone
- Generic ARM64/x86-64 Plattformen

### Brauche ich Root-Rechte?

Ja, das Build-Script benötigt Root-Rechte (sudo), da es debootstrap ausführt und chroot verwendet.

### Kann ich das SDK in einem Container verwenden?

Ja, aber der Container muss privilegiert sein (`--privileged` Flag) und sollte Zugriff auf `/dev` haben.

## Konfiguration

### Wie erstelle ich eine eigene Konfiguration?

1. Kopiere eine Beispiel-Konfiguration: `cp configs/minimal.yaml configs/meine-config.yaml`
2. Passe die YAML-Datei an deine Bedürfnisse an
3. Validiere: `./scripts/build.sh -c configs/meine-config.yaml --dry-run`
4. Baue: `sudo ./scripts/build.sh -c configs/meine-config.yaml`

### Welche Pakete kann ich installieren?

Alle Pakete, die in den offiziellen Debian/Ubuntu-Repositories verfügbar sind. Nutze `apt-cache search` um Pakete zu finden.

### Kann ich eigene Pakete hinzufügen?

Ja, du kannst:
1. Eigene .deb-Pakete in das Rootfs kopieren (mit overlay_files)
2. Eigene APT-Repositories in der sources.list hinzufügen
3. Pakete aus PPAs installieren (bei Ubuntu)

### Wie ändere ich die Distribution?

Ändere die `distribution` Sektion in deiner Konfiguration:

```yaml
distribution:
  name: debian  # oder ubuntu
  release: bookworm  # oder jammy, focal, etc.
```

## Build-Prozess

### Wie lange dauert ein Build?

Das hängt von mehreren Faktoren ab:
- Anzahl der Pakete: 5-50+ Minuten
- Internet-Geschwindigkeit: Download der Pakete
- CPU-Geschwindigkeit: Debootstrap und Paket-Installation
- Architektur: Cross-Arch-Builds sind langsamer

Ein Minimal-Build dauert ca. 5-10 Minuten.
Ein vollständiger Build mit vielen Paketen kann 30-60 Minuten dauern.

### Kann ich den Build beschleunigen?

Ja:
1. Verwende einen lokalen Mirror: Ändere `distribution.mirror` in der Config
2. Verwende einen APT-Cache-Proxy (apt-cacher-ng)
3. Nutze eine schnellere Internetverbindung
4. Halte die Paketliste klein

### Was passiert bei einem Fehler?

Das Script stoppt bei Fehlern (`set -e`). Du kannst:
1. Den Fehler in den Logs analysieren
2. Temporäre Dateien behalten: `--keep-temp`
3. Manuell im Chroot debuggen
4. Die Konfiguration anpassen und erneut versuchen

### Kann ich einen abgebrochenen Build fortsetzen?

Nein, aktuell nicht. Der Build startet immer von vorne. Dies ist geplant für zukünftige Versionen.

## Output und Verwendung

### Welches Output-Format soll ich wählen?

Das hängt von deinem Anwendungsfall ab:

- **tar.gz**: Universal, gut für manuelle Installation
- **tar.xz**: Kleinere Dateigröße, langsamere Kompression
- **ext4**: Direkt auf SD-Karte schreibbar mit `dd`
- **squashfs**: Read-only, gut für Live-Systeme

### Wie groß ist ein typisches Image?

Das hängt von den installierten Paketen ab:
- Minimal: ~150-300 MB (tar.gz)
- Standard: ~500-800 MB (tar.gz)
- Vollständig: 1-2 GB (tar.gz)

### Wie verwende ich das Image auf Hardware?

Siehe [USAGE.md](USAGE.md) für detaillierte Anleitungen. Kurz:

1. **TAR**: Extrahiere auf SD-Karte oder eMMC
2. **EXT4**: Schreibe direkt mit `dd`
3. Installiere Bootloader (U-Boot) und Kernel separat

### Funktioniert das Image sofort?

Das Rootfs ist funktionsfähig, aber du benötigst noch:
- Bootloader (z.B. U-Boot)
- Kernel mit passenden Treibern
- Device Tree für deine Hardware
- Boot-Konfiguration

## Hardware-spezifisch

### Wie nutze ich das Image auf NXP S32G2?

1. Erstelle Image: `sudo ./scripts/build.sh -c configs/s32g2-example.yaml`
2. Bereite SD-Karte vor (Boot + Root Partitionen)
3. Kopiere Rootfs auf Root-Partition
4. Installiere U-Boot, Kernel, DTB auf Boot-Partition
5. Konfiguriere U-Boot Boot-Script

Siehe [USAGE.md](USAGE.md) für Details.

### Unterstützt das SDK den S32G2-Kernel?

Das SDK erstellt das Rootfs. Den S32G2-spezifischen Kernel musst du separat kompilieren und installieren. Es gibt Beispiel-Konfigurationen, die zeigen, wo der Kernel hingehört.

### Kann ich das für Raspberry Pi verwenden?

Ja! Es gibt eine Beispiel-Konfiguration: `configs/raspberry-pi4.yaml`

Für RPi benötigst du zusätzlich:
- Raspberry Pi Bootloader-Dateien
- Raspberry Pi Kernel
- RPi-spezifische Config-Dateien

## Troubleshooting

### Fehler: "debootstrap not found"

Installiere debootstrap:
```bash
sudo apt-get install debootstrap
```

### Fehler: "Failed to mount /proc"

Das kann mehrere Ursachen haben:
1. Vorherige Mounts nicht aufgeräumt
2. Fehlende Root-Rechte
3. SELinux/AppArmor-Probleme

Lösung:
```bash
# Räume alte Mounts auf
sudo umount /tmp/sdk-build-*/rootfs/{proc,sys,dev/pts,dev} 2>/dev/null || true

# Versuche erneut mit sudo
sudo ./scripts/build.sh -c configs/minimal.yaml
```

### Fehler: "Cannot install package XYZ"

Mögliche Ursachen:
1. Paket existiert nicht in der gewählten Distribution
2. Tippfehler im Paketnamen
3. Netzwerk-Problem
4. Mirror ist offline

Lösung:
1. Prüfe Paketnamen: `apt-cache search paket-name`
2. Prüfe Netzwerk: `ping -c 1 archive.ubuntu.com`
3. Versuche anderen Mirror

### Das gebaute Image bootet nicht

Checkliste:
1. Ist der Bootloader installiert?
2. Ist der Kernel vorhanden?
3. Ist der Device Tree korrekt?
4. Sind die Boot-Parameter korrekt?
5. Ist die Root-Partition korrekt in den Boot-Args angegeben?

Debug-Tipps:
- Aktiviere verbose Boot in U-Boot
- Schaue Serial Console Output
- Prüfe Kernel Command Line
- Teste mit anderem Kernel

### Das System startet, aber Netzwerk funktioniert nicht

1. Prüfe ob NetworkManager installiert ist: `packages: - network-manager`
2. Prüfe Netzwerk-Konfiguration im Image
3. Prüfe Hardware-Treiber für Netzwerk-Interface
4. Schaue in System-Logs: `journalctl -xe`

## Erweiterte Themen

### Kann ich das SDK erweitern?

Ja! Das SDK ist Open Source. Du kannst:
1. Eigene Skripte in `scripts/` hinzufügen
2. Die Python-Module erweitern
3. Neue Features implementieren
4. Pull Requests erstellen

Siehe [CONTRIBUTING.md](CONTRIBUTING.md).

### Unterstützt das SDK Custom-Kernel?

Aktuell verwendet das SDK Kernel aus den Paket-Repositories. Du kannst aber:
1. Einen eigenen Kernel kompilieren
2. Ihn manuell in das Image kopieren
3. Boot-Konfiguration anpassen

Support für automatische Custom-Kernel-Kompilierung ist geplant.

### Kann ich das für Production verwenden?

Das SDK ist ein Tool zum Erstellen von Images. Für Production solltest du:
1. Die Images gründlich testen
2. Security-Hardening durchführen
3. Updates-Mechanismus implementieren
4. Monitoring einrichten
5. Backup-Strategie haben

### Gibt es automatische Updates?

Nein, aktuell nicht. Du musst Updates manuell durchführen indem du:
1. Neue Pakete in die Konfiguration aufnimmst
2. Ein neues Image baust
3. Das Image auf die Hardware ausspielst

Ein OTA-Update-Mechanismus ist für zukünftige Versionen geplant.

### Kann ich mehrere Varianten gleichzeitig bauen?

Ja, erstelle einfach mehrere Konfigurationsdateien und baue sie nacheinander oder parallel (in verschiedenen Terminals):

```bash
sudo ./scripts/build.sh -c configs/variant1.yaml -o build/variant1 &
sudo ./scripts/build.sh -c configs/variant2.yaml -o build/variant2 &
```

### Wie sichere ich meine Images?

Empfohlene Praktiken:
1. Speichere Konfigurationen in Git
2. Versioniere deine Images
3. Erstelle Checksums: `sha256sum image.tar.gz > image.sha256`
4. Signiere Images (für zukünftige Versionen geplant)
5. Sichere Images auf mehreren Medien

## Support

### Wo finde ich Hilfe?

1. Schaue in die Dokumentation: `docs/`
2. Lies diese FAQ
3. Durchsuche GitHub Issues
4. Öffne ein neues Issue mit dem Label "question"

### Wie melde ich einen Bug?

1. Prüfe ob der Bug schon gemeldet wurde
2. Öffne ein neues Issue auf GitHub
3. Füge hinzu:
   - Beschreibung des Problems
   - Konfigurationsdatei
   - Fehlerlog
   - System-Informationen (OS, Version)
   - Schritte zur Reproduktion

### Kann ich kommerziellen Support bekommen?

Aktuell wird das Projekt community-maintained. Für kommerziellen Support kontaktiere bitte die Maintainer.
