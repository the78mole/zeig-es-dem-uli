#!/bin/bash
# Embedded Linux SDK - Haupt-Build-Script
# Main build script for creating embedded Linux images

set -e  # Exit on error
set -u  # Exit on undefined variable

# Farben für Ausgabe
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging-Funktionen
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Hilfe anzeigen
show_help() {
    cat << EOF
Embedded Linux SDK - Image Builder

Usage: $0 [OPTIONS]

Options:
    -c, --config FILE       Pfad zur Konfigurations-YAML-Datei (erforderlich)
    -o, --output DIR        Ausgabe-Verzeichnis (Standard: ./build)
    -k, --keep-temp         Temporäre Dateien behalten
    -h, --help              Diese Hilfe anzeigen
    --dry-run               Konfiguration prüfen ohne zu bauen

Beispiele:
    $0 -c configs/s32g2-example.yaml
    $0 -c configs/minimal.yaml -o /tmp/output
    $0 --config configs/s32g2-example.yaml --dry-run

Beschreibung:
    Dieses Tool erstellt Embedded Linux Images aus Debian/Ubuntu-Paketen.
    Die Konfiguration erfolgt über YAML-Dateien.

Voraussetzungen:
    - debootstrap
    - qemu-user-static (für Cross-Arch-Builds)
    - Python 3 mit PyYAML
    - Root-Rechte (sudo)

EOF
}

# Variablen
CONFIG_FILE=""
OUTPUT_DIR="./build"
KEEP_TEMP=false
DRY_RUN=false
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Argumente parsen
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -c|--config)
                CONFIG_FILE="$2"
                shift 2
                ;;
            -o|--output)
                OUTPUT_DIR="$2"
                shift 2
                ;;
            -k|--keep-temp)
                KEEP_TEMP=true
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unbekannte Option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# Voraussetzungen prüfen
check_prerequisites() {
    log_info "Prüfe Voraussetzungen..."
    
    local missing=()
    
    # Prüfe auf erforderliche Tools
    command -v debootstrap >/dev/null 2>&1 || missing+=("debootstrap")
    command -v python3 >/dev/null 2>&1 || missing+=("python3")
    command -v qemu-aarch64-static >/dev/null 2>&1 || missing+=("qemu-user-static")
    
    if [ ${#missing[@]} -gt 0 ]; then
        log_error "Fehlende Programme: ${missing[*]}"
        log_info "Installation mit: sudo apt-get install ${missing[*]}"
        return 1
    fi
    
    # Prüfe Python-Module
    if ! python3 -c "import yaml" 2>/dev/null; then
        log_error "Python-Modul 'yaml' fehlt"
        log_info "Installation mit: pip3 install pyyaml"
        return 1
    fi
    
    # Prüfe Root-Rechte für tatsächlichen Build
    if [ "$DRY_RUN" = false ] && [ "$EUID" -ne 0 ]; then
        log_error "Dieses Script benötigt Root-Rechte (sudo)"
        return 1
    fi
    
    log_info "Alle Voraussetzungen erfüllt"
    return 0
}

# Konfiguration validieren
validate_config() {
    log_info "Validiere Konfiguration: $CONFIG_FILE"
    
    if [ ! -f "$CONFIG_FILE" ]; then
        log_error "Konfigurationsdatei nicht gefunden: $CONFIG_FILE"
        return 1
    fi
    
    # Verwende Python-Script zur Validierung
    python3 "${SCRIPT_DIR}/validate_config.py" "$CONFIG_FILE"
    return $?
}

# Main-Build-Funktion
build_image() {
    log_info "Starte Image-Build..."
    log_info "Konfiguration: $CONFIG_FILE"
    log_info "Ausgabe: $OUTPUT_DIR"
    
    # Erstelle Ausgabe-Verzeichnis
    mkdir -p "$OUTPUT_DIR"
    
    # Rufe Python-Build-Script auf
    python3 "${SCRIPT_DIR}/build_image.py" \
        --config "$CONFIG_FILE" \
        --output "$OUTPUT_DIR" \
        $([ "$KEEP_TEMP" = true ] && echo "--keep-temp")
    
    log_info "Build erfolgreich abgeschlossen!"
    log_info "Image verfügbar in: $OUTPUT_DIR"
}

# Haupt-Funktion
main() {
    echo "=================================="
    echo "Embedded Linux SDK - Image Builder"
    echo "=================================="
    echo
    
    parse_arguments "$@"
    
    # Prüfe ob Konfiguration angegeben wurde
    if [ -z "$CONFIG_FILE" ]; then
        log_error "Keine Konfigurationsdatei angegeben!"
        show_help
        exit 1
    fi
    
    # Führe Schritte aus
    check_prerequisites || exit 1
    validate_config || exit 1
    
    if [ "$DRY_RUN" = true ]; then
        log_info "Dry-Run: Konfiguration ist valide"
        exit 0
    fi
    
    build_image || exit 1
}

# Starte Script
main "$@"
