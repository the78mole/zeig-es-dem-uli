# Verwendungsanleitung / Usage Guide

## Installation der Voraussetzungen

### Ubuntu/Debian Host-System

```bash
# System aktualisieren
sudo apt-get update

# Erforderliche Pakete installieren
sudo apt-get install -y \
    debootstrap \
    qemu-user-static \
    binfmt-support \
    python3 \
    python3-pip \
    python3-yaml

# Python-Abhängigkeiten
pip3 install -r requirements.txt
```

## Grundlegende Verwendung

### 1. Minimal-Image erstellen

Das einfachste Beispiel für den Einstieg:

```bash
sudo ./scripts/build.sh -c configs/minimal.yaml
```

Dies erstellt ein minimales Ubuntu 22.04 ARM64-Image mit nur den wichtigsten Paketen.

### 2. NXP S32G2 Image erstellen

Vollständiges Image mit Hardware-Support:

```bash
sudo ./scripts/build.sh -c configs/s32g2-example.yaml
```

### 3. Debian-basiertes Image

Alternativ mit Debian statt Ubuntu:

```bash
sudo ./scripts/build.sh -c configs/s32g2-debian.yaml
```

## Erweiterte Optionen

### Konfiguration vor dem Build prüfen

```bash
./scripts/build.sh -c configs/s32g2-example.yaml --dry-run
```

Dies validiert die Konfiguration ohne tatsächlich ein Image zu bauen.

### Benutzerdefiniertes Output-Verzeichnis

```bash
sudo ./scripts/build.sh -c configs/minimal.yaml -o /tmp/my-images
```

### Temporäre Dateien behalten (Debugging)

```bash
sudo ./scripts/build.sh -c configs/minimal.yaml --keep-temp
```

Die temporären Dateien bleiben im `/tmp/sdk-build-*` Verzeichnis erhalten.

## Eigene Konfiguration erstellen

### Schritt 1: Beispiel kopieren

```bash
cp configs/minimal.yaml configs/meine-config.yaml
```

### Schritt 2: Anpassen

Öffne die Datei mit einem Editor:

```bash
nano configs/meine-config.yaml
```

Beispiel für eine angepasste Konfiguration:

```yaml
architecture: arm64

distribution:
  name: ubuntu
  release: jammy
  mirror: http://ports.ubuntu.com/ubuntu-ports

hostname: mein-embedded-system

root_password: geheim123

packages:
  # Basis
  - systemd
  - udev
  - network-manager
  
  # SSH
  - openssh-server
  
  # Meine zusätzlichen Pakete
  - python3
  - python3-pip
  - git
  - docker.io
  - nginx

output:
  name: mein-custom-image
  format: tar.gz
  compression: true
```

### Schritt 3: Validieren

```bash
./scripts/build.sh -c configs/meine-config.yaml --dry-run
```

### Schritt 4: Bauen

```bash
sudo ./scripts/build.sh -c configs/meine-config.yaml
```

## Konfigurationsoptionen im Detail

### Architektur

```yaml
architecture: arm64  # Optionen: arm64, armhf, amd64, i386
```

### Distribution

```yaml
distribution:
  name: ubuntu       # ubuntu oder debian
  release: jammy     # focal, jammy, mantic, noble (Ubuntu)
                     # buster, bullseye, bookworm (Debian)
  mirror: http://...  # Optional: Mirror-URL
```

### Pakete

```yaml
packages:
  - paket1
  - paket2
  - paket3
```

Tipp: Nutze `apt-cache search <begriff>` um Pakete zu finden.

### Output

```yaml
output:
  name: image-name
  format: tar.gz     # tar.gz, tar.bz2, tar.xz, ext4, squashfs
  compression: true  # Optional
```

### Erweiterte Optionen

```yaml
# Kernel
kernel:
  source: package           # package oder custom
  package: linux-image-generic

# Bootloader (Info für Dokumentation)
bootloader:
  type: u-boot
  defconfig: s32g2xxaevb_defconfig

# Partitionierung
partitions:
  boot:
    size: 256M
    filesystem: vfat
    mountpoint: /boot
  root:
    size: 2G
    filesystem: ext4
    mountpoint: /

# Netzwerk
network:
  interfaces:
    eth0:
      method: dhcp
    can0:
      enabled: true
      bitrate: 500000
```

## Image verwenden

### TAR-Archive

#### Auf SD-Karte extrahieren

```bash
# SD-Karte partitionieren (z.B. mit fdisk oder gparted)
sudo fdisk /dev/sdX

# Filesystem erstellen
sudo mkfs.ext4 /dev/sdX1

# Mounten
sudo mount /dev/sdX1 /mnt

# Image extrahieren
sudo tar xzf build/mein-image.tar.gz -C /mnt

# Sync und unmount
sync
sudo umount /mnt
```

#### In Verzeichnis extrahieren

```bash
mkdir my-rootfs
sudo tar xzf build/mein-image.tar.gz -C my-rootfs
```

### EXT4-Images

#### Direkt auf SD-Karte schreiben

```bash
sudo dd if=build/mein-image.ext4 of=/dev/sdX bs=4M status=progress conv=fsync
```

**Warnung:** Dies überschreibt alle Daten auf /dev/sdX!

#### Image mounten

```bash
sudo mount -o loop build/mein-image.ext4 /mnt
# Arbeite mit dem Image
sudo umount /mnt
```

## NXP S32G2 spezifische Anleitung

### 1. Image erstellen

```bash
sudo ./scripts/build.sh -c configs/s32g2-example.yaml
```

### 2. SD-Karte vorbereiten

Für NXP S32G2 benötigst du eine SD-Karte mit folgender Struktur:

```
/dev/sdX
├── Partition 1: Boot (FAT32, 256MB)
└── Partition 2: Root (EXT4, Rest)
```

Erstellen mit fdisk:

```bash
sudo fdisk /dev/sdX
# n -> neue Partition
# p -> primär
# 1 -> Partitionsnummer
# +256M -> Größe
# t -> Typ ändern
# c -> FAT32
# n -> zweite Partition (Rest des Speichers)
# w -> schreiben
```

### 3. Filesysteme erstellen

```bash
sudo mkfs.vfat -F 32 /dev/sdX1
sudo mkfs.ext4 /dev/sdX2
```

### 4. Root-Filesystem installieren

```bash
sudo mount /dev/sdX2 /mnt
sudo tar xzf build/s32g2-ubuntu-image.tar.gz -C /mnt
sudo umount /mnt
```

### 5. Bootloader und Kernel installieren

Für S32G2 benötigst du zusätzlich:

- **U-Boot**: Kompiliere U-Boot für S32G2
- **Kernel**: Kompiliere Linux-Kernel mit S32G2-Support
- **Device Tree**: s32g2xxaevb.dtb oder ähnlich

Diese Dateien müssen auf die Boot-Partition kopiert werden:

```bash
sudo mount /dev/sdX1 /mnt
sudo cp u-boot-s32.bin /mnt/
sudo cp Image /mnt/
sudo cp s32g2xxaevb.dtb /mnt/
sudo umount /mnt
```

### 6. Boot-Konfiguration

Erstelle eine `boot.scr` für U-Boot (Beispiel):

```
setenv bootargs 'console=ttyLF0,115200 root=/dev/mmcblk0p2 rootwait rw'
load mmc 0:1 ${kernel_addr_r} Image
load mmc 0:1 ${fdt_addr_r} s32g2xxaevb.dtb
booti ${kernel_addr_r} - ${fdt_addr_r}
```

Kompiliere zu boot.scr:

```bash
mkimage -A arm64 -O linux -T script -C none -n "Boot Script" -d boot.cmd boot.scr
```

## Troubleshooting

### Problem: "debootstrap not found"

**Lösung:**
```bash
sudo apt-get install debootstrap
```

### Problem: "qemu-aarch64-static not found"

**Lösung:**
```bash
sudo apt-get install qemu-user-static binfmt-support
```

### Problem: "Permission denied"

**Lösung:** Das Script benötigt Root-Rechte:
```bash
sudo ./scripts/build.sh -c configs/minimal.yaml
```

### Problem: Build schlägt fehl mit "Failed to mount"

**Lösung:** Stelle sicher, dass keine alten Mounts existieren:
```bash
# Zeige alle Mounts
mount | grep sdk-build

# Unmount manuell
sudo umount /tmp/sdk-build-*/rootfs/{proc,sys,dev/pts,dev} 2>/dev/null || true

# Versuche erneut
sudo ./scripts/build.sh -c configs/minimal.yaml
```

### Problem: "No space left on device"

**Lösung:** 
- Prüfe verfügbaren Speicherplatz: `df -h`
- Räume alten Build-Cache auf: `sudo apt-get clean`
- Lösche alte Build-Verzeichnisse: `sudo rm -rf /tmp/sdk-build-*`

### Problem: Packages können nicht installiert werden

**Lösung:**
- Prüfe Netzwerk-Verbindung
- Prüfe Mirror-URL in der Konfiguration
- Versuche einen anderen Mirror

## Best Practices

### 1. Kleine Iterationen

Starte mit einer minimalen Konfiguration und füge schrittweise Pakete hinzu.

### 2. Dry-Run nutzen

Validiere die Konfiguration immer zuerst:
```bash
./scripts/build.sh -c my-config.yaml --dry-run
```

### 3. Versionskontrolle

Speichere deine Konfigurationen in Git:
```bash
git add configs/my-config.yaml
git commit -m "Add custom configuration"
```

### 4. Dokumentation

Kommentiere deine Konfigurationen:
```yaml
# Meine Custom-Konfiguration für Projekt X
# Erstellt: 2024-01-15
# Zweck: Produktions-Image für Hardware Rev 2.1
architecture: arm64
...
```

### 5. Testing

Teste das Image in einer VM oder QEMU bevor du es auf Hardware nutzt:

```bash
# Für ARM64
qemu-system-aarch64 \
    -M virt \
    -cpu cortex-a57 \
    -m 1024 \
    -drive file=build/image.ext4,format=raw \
    -nographic
```

## Weitere Ressourcen

- [Hauptdokumentation](README.md)
- [Debian Debootstrap Wiki](https://wiki.debian.org/Debootstrap)
- [Ubuntu ARM](https://wiki.ubuntu.com/ARM)
- [NXP S32G Documentation](https://www.nxp.com/s32g)
