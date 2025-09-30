# Changelog

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

## [1.0.0] - 2024-01-15

### Hinzugefügt

- Initiales Release des Embedded Linux SDK
- YAML-basierte Konfiguration für Image-Builds
- Support für mehrere Architekturen (arm64, armhf, amd64, i386)
- Support für Ubuntu (Focal, Jammy, Mantic, Noble)
- Support für Debian (Buster, Bullseye, Bookworm)
- Debootstrap-basierter Build-Prozess
- Cross-Architektur-Build-Support mit QEMU
- Mehrere Output-Formate (tar.gz, tar.bz2, tar.xz, ext4, squashfs)
- Konfigurations-Validierung
- Dry-Run-Modus für Konfigurationsprüfung

#### Beispiel-Konfigurationen
- Minimal-Konfiguration für schnelle Tests
- NXP S32G2 Ubuntu-Konfiguration mit CAN und Netzwerk-Support
- NXP S32G2 Debian-Konfiguration
- Raspberry Pi 4 Konfiguration

#### Skripte
- `build.sh`: Haupt-Build-Script mit CLI-Interface
- `validate_config.py`: Konfigurations-Validierung
- `build_image.py`: Image-Builder-Implementierung
- `setup-can.sh`: CAN-Bus-Konfiguration
- `configure-network.sh`: Netzwerk-Setup

#### Dokumentation
- Umfangreiches README mit Schnellstart-Anleitung
- Detaillierte Dokumentation in `docs/README.md`
- Verwendungsanleitung in `docs/USAGE.md`
- Contributing-Guide
- MIT-Lizenz

### Features

- Automatische Paket-Installation aus Debian/Ubuntu-Repositories
- System-Konfiguration (Hostname, Root-Passwort, etc.)
- Flexible Paket-Auswahl
- Hardware-spezifische Anpassungen
- Build-Artefakte in konfigurierbarem Ausgabe-Verzeichnis
- Temporäre Dateien optional behalten für Debugging
- Farbige Logging-Ausgabe
- Umfangreiche Fehlerbehandlung

### Unterstützte Hardware

- NXP S32G2 (mit CAN-Bus und Netzwerk-Support)
- Raspberry Pi 4
- Generic ARM64-Plattformen
- Generic x86-64-Plattformen

## [Geplant für zukünftige Versionen]

### In Arbeit

- GUI für Konfigurations-Erstellung
- Docker-Container-Support für Build-Umgebung
- Automatische Kernel-Kompilierung
- U-Boot-Integration
- Image-Signing und Verschlüsselung
- OTA-Update-Mechanismus
- Custom Overlay-Dateisystem-Support
- Mehr Hardware-Plattformen
