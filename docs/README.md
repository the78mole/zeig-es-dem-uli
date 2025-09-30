# Embedded Linux SDK

Ein einfaches SDK zum Erstellen von Embedded Linux Images aus Debian/Ubuntu-Paketen für verschiedene Zielplattformen wie NXP S32G2.

## Features

- 🚀 **Einfache Konfiguration** - YAML-basierte Konfigurationsdateien
- 📦 **Debian/Ubuntu Pakete** - Nutzt bewährte Debian/Ubuntu-Pakete
- 🎯 **Multi-Architektur** - Unterstützt ARM64, ARMhf, AMD64, i386
- 🔧 **Anpassbar** - Flexible Konfiguration von Paketen, Netzwerk, etc.
- 🏗️ **Cross-Compilation** - Baut Images für verschiedene Architekturen
- 📋 **NXP S32G2 Support** - Vorkonfigurierte Beispiele für NXP S32G2

## Schnellstart

### Voraussetzungen

```bash
# Auf Ubuntu/Debian:
sudo apt-get update
sudo apt-get install -y \
    debootstrap \
    qemu-user-static \
    python3 \
    python3-pip \
    python3-yaml

# Python-Abhängigkeiten
pip3 install pyyaml
```

### Einfaches Beispiel

1. **Minimal-Image erstellen:**

```bash
sudo ./scripts/build.sh -c configs/minimal.yaml
```

2. **NXP S32G2 Image erstellen:**

```bash
sudo ./scripts/build.sh -c configs/s32g2-example.yaml
```

3. **Mit benutzerdefinierten Ausgabe-Verzeichnis:**

```bash
sudo ./scripts/build.sh -c configs/s32g2-example.yaml -o /tmp/my-build
```

## Konfiguration

### YAML-Struktur

Eine Konfigurationsdatei enthält folgende Hauptabschnitte:

```yaml
# Ziel-Architektur
architecture: arm64

# Distribution
distribution:
  name: ubuntu
  release: jammy
  mirror: http://ports.ubuntu.com/ubuntu-ports

# Hostname
hostname: mein-target

# Root-Passwort
root_password: geheim

# Pakete
packages:
  - systemd
  - openssh-server
  - ...

# Output
output:
  name: mein-image
  format: tar.gz
  compression: true
```

### Unterstützte Optionen

#### Architecture
- `arm64` - 64-bit ARM (z.B. NXP S32G2)
- `armhf` - 32-bit ARM mit Hardware-Float
- `amd64` - 64-bit x86
- `i386` - 32-bit x86

#### Distribution
- **Ubuntu**: focal (20.04), jammy (22.04), mantic (23.10), noble (24.04)
- **Debian**: buster (10), bullseye (11), bookworm (12)

#### Output-Formate
- `tar.gz` - Komprimiertes Tar-Archiv (Standard)
- `tar.bz2` - BZip2-komprimiertes Tar-Archiv
- `tar.xz` - XZ-komprimiertes Tar-Archiv
- `ext4` - EXT4-Dateisystem-Image
- `squashfs` - SquashFS-Dateisystem (Read-only)

## Beispiel-Konfigurationen

### 1. Minimal-System

Siehe: `configs/minimal.yaml`

Ein minimales System mit nur den notwendigsten Paketen.

### 2. NXP S32G2 System

Siehe: `configs/s32g2-example.yaml`

Ein vollständiges System für NXP S32G2 mit:
- Netzwerk-Support
- CAN-Bus-Support
- SSH-Server
- Entwicklungstools

## Erweiterte Nutzung

### Konfiguration validieren

Prüfe eine Konfiguration ohne zu bauen:

```bash
./scripts/build.sh -c configs/s32g2-example.yaml --dry-run
```

### Temporäre Dateien behalten

Für Debugging:

```bash
sudo ./scripts/build.sh -c configs/minimal.yaml --keep-temp
```

### Eigene Konfiguration erstellen

1. Kopiere eine Beispiel-Konfiguration:
```bash
cp configs/minimal.yaml configs/meine-config.yaml
```

2. Passe die Konfiguration an:
```bash
nano configs/meine-config.yaml
```

3. Baue das Image:
```bash
sudo ./scripts/build.sh -c configs/meine-config.yaml
```

## Verwendung der Images

### Tar-Archive

Extrahiere auf SD-Karte oder in ein Verzeichnis:

```bash
# Auf SD-Karte (z.B. /dev/sdX1)
sudo tar xzf build/mein-image.tar.gz -C /mnt/sdcard

# In Verzeichnis
mkdir rootfs
sudo tar xzf build/mein-image.tar.gz -C rootfs
```

### EXT4-Images

Mounte und kopiere oder schreibe direkt auf ein Device:

```bash
# Auf SD-Karte schreiben
sudo dd if=build/mein-image.ext4 of=/dev/sdX bs=4M status=progress

# Oder mounten
sudo mount -o loop build/mein-image.ext4 /mnt
```

## NXP S32G2 Spezifika

### Hardware-Features

Das S32G2-Beispiel aktiviert:

- **CAN-Bus**: Automatische Konfiguration von CAN-Interfaces
- **Ethernet**: DHCP-Konfiguration für eth0
- **SSH**: OpenSSH-Server für Remote-Zugriff

### Bootloader

Das SDK bereitet das Rootfs vor. Für den Bootloader (U-Boot) musst du:

1. U-Boot für S32G2 kompilieren
2. U-Boot auf Boot-Partition installieren
3. Device Tree und Kernel bereitstellen

### Kernel

Das Beispiel verwendet den Generic-Kernel. Für optimale S32G2-Unterstützung:

1. Verwende einen S32G2-spezifischen Kernel
2. Aktiviere notwendige Device-Treiber
3. Konfiguriere Device Tree für dein Board

## Architektur

```
zeig-es-dem-uli/
├── configs/              # Konfigurationsdateien
│   ├── minimal.yaml      # Minimal-Beispiel
│   └── s32g2-example.yaml # NXP S32G2 Beispiel
├── scripts/              # Build-Skripte
│   ├── build.sh          # Haupt-Build-Script
│   ├── validate_config.py # Konfigurations-Validierung
│   ├── build_image.py    # Image-Builder
│   ├── setup-can.sh      # CAN-Setup
│   └── configure-network.sh # Netzwerk-Setup
├── docs/                 # Dokumentation
└── build/                # Build-Ausgabe (wird erstellt)
```

## Build-Prozess

1. **Validierung**: Prüfung der Konfigurationsdatei
2. **Debootstrap**: Erstellen des Basis-Systems
3. **QEMU Setup**: Für Cross-Arch-Builds
4. **System-Konfiguration**: Hostname, Netzwerk, etc.
5. **Paket-Installation**: Installation zusätzlicher Pakete
6. **Image-Erstellung**: Packen in gewünschtes Format

## Troubleshooting

### Fehler: "debootstrap not found"

```bash
sudo apt-get install debootstrap
```

### Fehler: "qemu-aarch64-static not found"

```bash
sudo apt-get install qemu-user-static
```

### Fehler: "Permission denied"

Das Build-Script benötigt Root-Rechte:

```bash
sudo ./scripts/build.sh -c configs/minimal.yaml
```

### Fehler beim Mounten

Stelle sicher, dass keine Pseudo-Dateisysteme noch gemountet sind:

```bash
sudo umount /tmp/sdk-build-*/rootfs/{proc,sys,dev/pts,dev} 2>/dev/null || true
```

## Beitragen

Contributions sind willkommen! Bitte:

1. Erstelle einen Fork
2. Erstelle einen Feature-Branch
3. Committe deine Änderungen
4. Pushe zum Branch
5. Erstelle einen Pull Request

## Lizenz

Dieses Projekt ist Open Source. Siehe LICENSE-Datei für Details.

## Support

- **Issues**: Nutze GitHub Issues für Bugs und Feature-Requests
- **Diskussionen**: GitHub Discussions für Fragen und Diskussionen

## Weitere Ressourcen

- [NXP S32G2 Documentation](https://www.nxp.com/products/processors-and-microcontrollers/arm-processors/s32g-vehicle-network-processors:S32G)
- [Debian debootstrap](https://wiki.debian.org/Debootstrap)
- [Ubuntu for ARM](https://wiki.ubuntu.com/ARM)
