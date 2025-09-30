# Embedded Linux SDK

Ein einfaches SDK zum Erstellen von Embedded Linux Images aus Debian/Ubuntu-Paketen für verschiedene Zielplattformen wie NXP S32G2.

## Überblick

Dieses SDK ermöglicht es, schnell und einfach Embedded Linux Images zu erstellen:

- 📦 **Basiert auf Debian/Ubuntu-Paketen** - Nutzt bewährte und gepflegte Software
- 🎯 **Zielplattform-spezifisch** - Unterstützt verschiedene Architekturen (ARM64, ARMhf, AMD64, i386)
- 🚀 **Einfache Konfiguration** - YAML-basierte Konfigurationsdateien
- 🔧 **Anpassbar** - Flexible Konfiguration von Paketen, Netzwerk, Bootloader, etc.
- 🏗️ **Cross-Compilation Support** - Baut Images für verschiedene Architekturen

## Schnellstart

### Voraussetzungen installieren

```bash
sudo apt-get update
sudo apt-get install -y debootstrap qemu-user-static python3 python3-pip python3-yaml
```

### Image erstellen

```bash
# Minimal-Image
sudo ./scripts/build.sh -c configs/minimal.yaml

# NXP S32G2 Image
sudo ./scripts/build.sh -c configs/s32g2-example.yaml
```

### Konfiguration erstellen

```yaml
# my-config.yaml
architecture: arm64

distribution:
  name: ubuntu
  release: jammy

hostname: my-target

packages:
  - systemd
  - openssh-server
  - network-manager

output:
  name: my-image
  format: tar.gz
```

```bash
sudo ./scripts/build.sh -c my-config.yaml
```

## Features

### Unterstützte Architekturen
- ARM64 (AArch64) - z.B. NXP S32G2, Raspberry Pi 4
- ARMhf (32-bit ARM)
- AMD64 (x86-64)
- i386 (32-bit x86)

### Unterstützte Distributionen
- **Ubuntu**: 20.04 (Focal), 22.04 (Jammy), 23.10 (Mantic), 24.04 (Noble)
- **Debian**: 10 (Buster), 11 (Bullseye), 12 (Bookworm)

### Output-Formate
- TAR-Archive (tar.gz, tar.bz2, tar.xz)
- EXT4-Filesystem-Images
- SquashFS (Read-only)

## Beispiele

Im `configs/` Verzeichnis findest du:
- **minimal.yaml** - Minimale Konfiguration für schnelle Tests
- **s32g2-example.yaml** - Vollständige Konfiguration für NXP S32G2 mit CAN, Netzwerk, etc.

## Dokumentation

Ausführliche Dokumentation findest du in [docs/README.md](docs/README.md):
- Detaillierte Konfigurationsoptionen
- Erweiterte Nutzung
- NXP S32G2 spezifische Informationen
- Troubleshooting
- Best Practices

## Struktur

```
.
├── configs/              # Beispiel-Konfigurationen
│   ├── minimal.yaml
│   └── s32g2-example.yaml
├── scripts/              # Build- und Helper-Skripte
│   ├── build.sh          # Haupt-Build-Script
│   ├── validate_config.py
│   ├── build_image.py
│   ├── setup-can.sh
│   └── configure-network.sh
├── docs/                 # Ausführliche Dokumentation
└── build/                # Build-Ausgabe (wird erstellt)
```

## Verwendung

### Konfiguration validieren
```bash
./scripts/build.sh -c configs/s32g2-example.yaml --dry-run
```

### Image mit benutzerdefiniertem Output-Verzeichnis
```bash
sudo ./scripts/build.sh -c configs/minimal.yaml -o /tmp/my-output
```

### Temporäre Dateien behalten (für Debugging)
```bash
sudo ./scripts/build.sh -c configs/minimal.yaml --keep-temp
```

## Image verwenden

### TAR-Archive extrahieren
```bash
# Auf SD-Karte
sudo tar xzf build/my-image.tar.gz -C /mnt/sdcard

# In Verzeichnis
mkdir rootfs
sudo tar xzf build/my-image.tar.gz -C rootfs
```

### EXT4-Images schreiben
```bash
# Direkt auf Device
sudo dd if=build/my-image.ext4 of=/dev/sdX bs=4M status=progress

# Oder mounten
sudo mount -o loop build/my-image.ext4 /mnt
```

## Lizenz

Open Source - siehe LICENSE Datei

## Support

- GitHub Issues für Bug-Reports und Feature-Requests
- GitHub Discussions für Fragen und Diskussionen