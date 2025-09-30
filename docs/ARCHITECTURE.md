# SDK Architektur

## Überblick

Das Embedded Linux SDK ist ein modulares System zum Erstellen von Embedded Linux Images. Diese Dokumentation erklärt die Architektur und das Zusammenspiel der Komponenten.

## Komponenten

```
Embedded Linux SDK
│
├── Konfiguration (YAML)
│   └── Definiert Target, Pakete, Output
│
├── Build-System
│   ├── build.sh (Hauptskript)
│   ├── validate_config.py (Validierung)
│   └── build_image.py (Image-Builder)
│
├── Helper-Skripte
│   ├── setup-can.sh
│   └── configure-network.sh
│
└── Output
    └── Fertige Images
```

## Build-Prozess

### Phase 1: Vorbereitung

```
User
  │
  │ Startet: ./scripts/build.sh -c config.yaml
  │
  ▼
build.sh
  │
  ├─► Argumente parsen
  ├─► Voraussetzungen prüfen (debootstrap, qemu, python3)
  └─► validate_config.py aufrufen
        │
        ├─► YAML laden und parsen
        ├─► Erforderliche Felder prüfen
        ├─► Werte validieren
        └─► Zusammenfassung ausgeben
```

### Phase 2: Image-Build

```
build.sh
  │
  └─► build_image.py starten
        │
        ├─► Konfiguration laden
        │
        ├─► Temporäre Verzeichnisse erstellen
        │     └── /tmp/sdk-build-XXXXX/rootfs/
        │
        ├─► debootstrap ausführen
        │     │
        │     ├─► Basis-System installieren
        │     ├─► Debian/Ubuntu Pakete herunterladen
        │     └─► Minimales System erstellen
        │
        ├─► QEMU Setup (bei Cross-Arch)
        │     └── qemu-<arch>-static kopieren
        │
        ├─► System konfigurieren
        │     │
        │     ├─► Hostname setzen (/etc/hostname)
        │     ├─► /etc/hosts erstellen
        │     └─► Root-Passwort setzen
        │
        ├─► Zusätzliche Pakete installieren
        │     │
        │     ├─► chroot in Rootfs
        │     ├─► apt-get update
        │     ├─► apt-get install <pakete>
        │     └─► apt-get clean
        │
        └─► Output-Image erstellen
              │
              ├─► tar.gz: Tarball packen
              ├─► ext4: Filesystem-Image erstellen
              └─► squashfs: Read-only Image
```

### Phase 3: Cleanup

```
build_image.py
  │
  ├─► Pseudo-Filesystems unmounten
  │     ├── /proc
  │     ├── /sys
  │     └── /dev
  │
  ├─► Temporäre Dateien löschen
  │     (wenn nicht --keep-temp)
  │
  └─► Image-Info ausgeben
        ├── Pfad
        └── Größe
```

## Datenfluss

```
config.yaml
    │
    │ 1. Gelesen von
    ▼
validate_config.py
    │
    │ 2. Validierung OK
    ▼
build_image.py
    │
    │ 3. Basis-System
    ▼
debootstrap
    │
    │ 4. Pakete von
    ▼
Debian/Ubuntu Mirror
    │
    │ 5. Rootfs erstellt
    ▼
/tmp/sdk-build-*/rootfs/
    │
    │ 6. Zusätzliche Pakete
    ▼
apt-get install
    │
    │ 7. Konfigurieren
    ▼
System-Setup
    │
    │ 8. Packen
    ▼
Output-Image (build/)
```

## Modul-Struktur

### build.sh

```bash
main()
  │
  ├── parse_arguments()
  │     └── Kommandozeilen-Optionen verarbeiten
  │
  ├── check_prerequisites()
  │     ├── debootstrap vorhanden?
  │     ├── qemu-user-static vorhanden?
  │     ├── python3 vorhanden?
  │     └── Root-Rechte?
  │
  ├── validate_config()
  │     └── Python-Validator aufrufen
  │
  └── build_image()
        └── Python-Builder aufrufen
```

### validate_config.py

```python
validate_config(config_path)
  │
  ├── YAML laden
  │
  ├── Erforderliche Felder prüfen
  │     ├── architecture
  │     ├── distribution
  │     ├── hostname
  │     └── output
  │
  ├── Werte validieren
  │     ├── Architektur in VALID_ARCHITECTURES?
  │     ├── Distribution bekannt?
  │     ├── Release bekannt?
  │     └── Output-Format gültig?
  │
  └── Zusammenfassung ausgeben
```

### build_image.py

```python
class ImageBuilder:
    
    build()
      │
      ├── load_config()
      │     └── YAML in self.config laden
      │
      ├── setup_directories()
      │     └── Temp-Verzeichnis erstellen
      │
      ├── run_debootstrap()
      │     └── subprocess: debootstrap
      │
      ├── setup_qemu()
      │     └── QEMU-Binary kopieren (falls nötig)
      │
      ├── configure_system()
      │     ├── Hostname setzen
      │     ├── /etc/hosts erstellen
      │     └── Root-Passwort setzen
      │
      ├── install_packages()
      │     ├── _chroot_run('apt-get update')
      │     └── _chroot_run('apt-get install ...')
      │
      ├── create_output_image()
      │     ├── tar: tar czf
      │     └── ext4: mkfs.ext4
      │
      └── cleanup()
            └── Temp-Dateien löschen
```

## Konfigurations-Schema

```yaml
# Grundstruktur der Konfiguration

architecture: <string>
  # Werte: arm64, armhf, amd64, i386

distribution:
  name: <string>        # ubuntu, debian
  release: <string>     # jammy, bookworm, etc.
  mirror: <url>         # Optional

hostname: <string>

root_password: <string>  # Optional

packages:                # Optional
  - <paket1>
  - <paket2>

kernel:                  # Optional
  source: <string>       # package, custom
  package: <string>      # Bei source: package

bootloader:              # Optional (Info)
  type: <string>
  defconfig: <string>

partitions:              # Optional
  boot:
    size: <string>
    filesystem: <string>
    mountpoint: <string>
  root:
    size: <string>
    filesystem: <string>
    mountpoint: <string>

network:                 # Optional
  interfaces:
    <name>:
      method: <string>   # dhcp, static
      enabled: <bool>
      bitrate: <int>     # Für CAN

customization:           # Optional
  post_install_scripts:
    - <script1>
  overlay_files:
    - src: <path>
      dest: <path>

output:
  name: <string>
  format: <string>       # tar.gz, tar.bz2, tar.xz, ext4, squashfs
  compression: <bool>    # Optional
```

## Erweiterbarkeit

### Neue Architektur hinzufügen

1. Füge in `validate_config.py` hinzu:
   ```python
   VALID_ARCHITECTURES = ['arm64', 'armhf', 'amd64', 'i386', 'riscv64']
   ```

2. Stelle sicher, dass QEMU-Support vorhanden ist

3. Teste mit einer Beispiel-Konfiguration

### Neue Distribution hinzufügen

1. Füge in `validate_config.py` hinzu:
   ```python
   VALID_DISTRIBUTIONS = {
       'ubuntu': [...],
       'debian': [...],
       'fedora': ['38', '39']  # Neu
   }
   ```

2. Prüfe ob debootstrap die Distribution unterstützt

3. Erstelle Beispiel-Konfiguration

### Neues Output-Format hinzufügen

1. Füge in `validate_config.py` hinzu:
   ```python
   VALID_OUTPUT_FORMATS = [..., 'btrfs']
   ```

2. Implementiere in `build_image.py`:
   ```python
   def create_output_image(self):
       if output_format == 'btrfs':
           # Implementierung
   ```

### Custom-Skripte einbinden

Erstelle Skripte in `scripts/` und füge sie der Konfiguration hinzu:

```yaml
customization:
  post_install_scripts:
    - scripts/mein-setup.sh
```

## Security-Überlegungen

### Root-Rechte

Das Script benötigt Root-Rechte für:
- debootstrap (erstellt Dateisystem-Struktur)
- chroot (wechselt in neue Root)
- mount/umount (Pseudo-Filesysteme)
- Device-Zugriff (für dd, mkfs)

### Netzwerk-Zugriff

Das Script lädt Pakete aus dem Internet:
- Verwende HTTPS-Mirrors wenn möglich
- Validiere Pakete mit APT (automatisch)
- Prüfe GPG-Signaturen (durch debootstrap)

### Temp-Dateien

Temporäre Dateien in `/tmp/`:
- Automatisch gelöscht nach Build
- Können mit `--keep-temp` behalten werden
- Enthalten potentiell sensitive Daten

## Performance-Optimierung

### Build-Geschwindigkeit

1. **Lokaler Mirror**: Nutze lokalen APT-Mirror
   ```yaml
   distribution:
     mirror: http://local-mirror/ubuntu-ports
   ```

2. **APT-Cache**: Nutze apt-cacher-ng
   ```bash
   echo 'Acquire::http::Proxy "http://localhost:3142";' > /etc/apt/apt.conf.d/02proxy
   ```

3. **Parallele Builds**: Mehrere Images gleichzeitig
   ```bash
   ./scripts/build.sh -c config1.yaml -o build/1 &
   ./scripts/build.sh -c config2.yaml -o build/2 &
   ```

### Image-Größe

1. **Minimale Pakete**: Nur notwendige Pakete
2. **Cleanup**: APT-Cache leeren (automatisch)
3. **Kompression**: XZ statt GZ für kleinere Dateien

## Testing

### Unit-Tests (geplant)

```python
# tests/test_validation.py
def test_validate_minimal_config():
    result = validate_config('configs/minimal.yaml')
    assert result == True

# tests/test_build.py
def test_create_tar_image():
    builder = ImageBuilder(...)
    builder.create_output_image()
    assert os.path.exists('output.tar.gz')
```

### Integration-Tests (geplant)

```bash
# tests/integration_test.sh
./scripts/build.sh -c configs/minimal.yaml -o /tmp/test
tar tzf /tmp/test/minimal-image.tar.gz | grep etc/hostname
```

## Logging und Debugging

### Log-Levels

- `[INFO]`: Normale Meldungen (grün)
- `[WARN]`: Warnungen (gelb)
- `[ERROR]`: Fehler (rot)

### Debug-Modus

```bash
# Temporäre Dateien behalten
sudo ./scripts/build.sh -c config.yaml --keep-temp

# Manuell im Chroot debuggen
sudo chroot /tmp/sdk-build-*/rootfs /bin/bash
```

### Verbose-Output

Für mehr Details:
```bash
bash -x ./scripts/build.sh -c config.yaml
```

## Best Practices

1. **Versionierung**: Nutze Git für Konfigurationen
2. **Dokumentation**: Kommentiere Custom-Configs
3. **Testing**: Teste Images vor Deployment
4. **Backup**: Sichere funktionierende Images
5. **Monitoring**: Überwache Build-Zeiten und -Größen
6. **Security**: Halte System und Pakete aktuell

## Zukünftige Entwicklung

Geplante Features:
- Docker-basierte Build-Umgebung
- GUI für Konfiguration
- Automatische Kernel-Kompilierung
- CI/CD-Integration
- Image-Signing
- OTA-Updates
- Custom-Package-Repositories
- Build-Cache
- Inkrementelle Builds
- Multi-Stage-Builds
