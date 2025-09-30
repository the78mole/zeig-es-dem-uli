#!/bin/bash
# Quick Start Script für Embedded Linux SDK
# Installiert Voraussetzungen und führt einen Test-Build durch

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}Embedded Linux SDK - Quick Start${NC}"
echo -e "${BLUE}================================================${NC}"
echo

# Prüfe ob auf Ubuntu/Debian
if [ ! -f /etc/debian_version ]; then
    echo -e "${RED}Warnung: Dieses Script ist für Ubuntu/Debian optimiert.${NC}"
    echo "Andere Distributionen werden möglicherweise nicht unterstützt."
    echo
    read -p "Trotzdem fortfahren? (j/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Jj]$ ]]; then
        exit 1
    fi
fi

# Prüfe Root-Rechte für Installation
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}Hinweis: Für die Installation der Voraussetzungen werden Root-Rechte benötigt.${NC}"
    echo "Das Script wird versuchen, sudo zu verwenden."
    echo
    SUDO="sudo"
else
    SUDO=""
fi

# Funktion zum Prüfen ob Paket installiert ist
check_package() {
    if dpkg -l "$1" 2>/dev/null | grep -q "^ii"; then
        return 0
    else
        return 1
    fi
}

# Funktion zum Installieren von Paketen
install_packages() {
    local packages=()
    
    echo -e "${GREEN}[1/4] Prüfe erforderliche Pakete...${NC}"
    
    # Prüfe jedes Paket
    for pkg in debootstrap qemu-user-static binfmt-support python3 python3-pip python3-yaml; do
        if ! check_package "$pkg"; then
            packages+=("$pkg")
            echo "  - $pkg: nicht installiert"
        else
            echo "  - $pkg: installiert ✓"
        fi
    done
    
    # Installiere fehlende Pakete
    if [ ${#packages[@]} -gt 0 ]; then
        echo
        echo -e "${YELLOW}Folgende Pakete werden installiert: ${packages[*]}${NC}"
        echo
        
        $SUDO apt-get update
        $SUDO apt-get install -y "${packages[@]}"
        
        echo
        echo -e "${GREEN}Pakete erfolgreich installiert!${NC}"
    else
        echo
        echo -e "${GREEN}Alle Pakete sind bereits installiert!${NC}"
    fi
}

# Python-Abhängigkeiten installieren
install_python_deps() {
    echo
    echo -e "${GREEN}[2/4] Installiere Python-Abhängigkeiten...${NC}"
    
    # Prüfe ob PyYAML bereits installiert ist
    if python3 -c "import yaml" 2>/dev/null; then
        echo "  - PyYAML bereits installiert ✓"
        return 0
    fi
    
    if [ -f requirements.txt ]; then
        $SUDO pip3 install -r requirements.txt -q
        echo "  - PyYAML installiert ✓"
    else
        $SUDO pip3 install PyYAML -q
        echo "  - PyYAML installiert ✓"
    fi
}

# Beispiel-Konfiguration testen
test_validation() {
    echo
    echo -e "${GREEN}[3/4] Teste Konfigurations-Validierung...${NC}"
    echo
    
    if [ -f scripts/validate_config.py ] && [ -f configs/minimal.yaml ]; then
        python3 scripts/validate_config.py configs/minimal.yaml
    else
        echo -e "${RED}Fehler: Skripte oder Konfigurationen nicht gefunden${NC}"
        return 1
    fi
}

# Interaktive Auswahl für Test-Build
offer_test_build() {
    echo
    echo -e "${GREEN}[4/4] Test-Build (optional)${NC}"
    echo
    echo "Möchtest du einen Test-Build durchführen?"
    echo
    echo "Verfügbare Konfigurationen:"
    echo "  1) Container Test (AMD64, funktioniert in Dev-Container, ~5-10 Min, ~200 MB)"
    echo "  2) Minimal ARM64 (kann in Dev-Container fehlschlagen, ~5-10 Min, ~200 MB)"
    echo "  3) NXP S32G2 Ubuntu (kann in Dev-Container fehlschlagen, ~30-45 Min, ~800 MB)"
    echo "  4) NXP S32G2 Debian (kann in Dev-Container fehlschlagen, ~30-45 Min, ~800 MB)"
    echo "  5) Raspberry Pi 4 (kann in Dev-Container fehlschlagen, ~30-45 Min, ~800 MB)"
    echo "  6) Überspringen"
    echo
    
    read -p "Auswahl (1-6): " choice
    
    case $choice in
        1)
            config="configs/container-test.yaml"
            ;;
        2)
            config="configs/minimal.yaml"
            ;;
        3)
            config="configs/s32g2-example.yaml"
            ;;
        4)
            config="configs/s32g2-debian.yaml"
            ;;
        5)
            config="configs/raspberry-pi4.yaml"
            ;;
        6)
            echo
            echo -e "${BLUE}Setup abgeschlossen!${NC}"
            echo
            show_usage
            return 0
            ;;
        *)
            echo -e "${RED}Ungültige Auswahl${NC}"
            return 1
            ;;
    esac
    
    echo
    echo -e "${YELLOW}Starte Build mit: $config${NC}"
    echo -e "${YELLOW}Dies kann einige Minuten dauern...${NC}"
    echo
    
    # Prüfe zuerst mit Dry-Run
    echo -e "${YELLOW}Prüfe Konfiguration...${NC}"
    if ! ./scripts/build.sh -c "$config" --dry-run; then
        echo -e "${RED}Konfiguration ungültig!${NC}"
        return 1
    fi
    
    # Build starten
    echo -e "${YELLOW}Starte Build-Prozess...${NC}"
    if $SUDO ./scripts/build.sh -c "$config"; then
        echo
        echo -e "${GREEN}Build erfolgreich!${NC}"
        echo
        echo "Das fertige Image findest du im 'build/' Verzeichnis:"
        if [ -d build/ ] && [ "$(ls -A build/ 2>/dev/null)" ]; then
            ls -lh build/
        else
            echo -e "${RED}Fehler: Build-Verzeichnis ist leer oder nicht vorhanden!${NC}"
            echo -e "${YELLOW}Der Build ist wahrscheinlich fehlgeschlagen.${NC}"
            return 1
        fi
    else
        echo
        echo -e "${RED}Build fehlgeschlagen. Siehe Logs für Details.${NC}"
        echo
        echo -e "${YELLOW}Tipps zur Fehlerbehebung:${NC}"
        echo "  - In Dev-Container-Umgebungen funktioniert Cross-Arch-Compilation oft nicht"
        echo "  - Versuche eine AMD64-Konfiguration oder baue auf dem Zielsystem"
        echo "  - Prüfe die Netzwerkverbindung"
        echo "  - Stelle sicher, dass genügend Speicherplatz vorhanden ist"
        echo "  - Führe den Build mit --keep-temp aus für Debugging"
        echo "  - Schaue in die Logs für spezifische Fehlermeldungen"
        return 1
    fi
}

# Zeige Verwendungshinweise
show_usage() {
    echo -e "${BLUE}Nächste Schritte:${NC}"
    echo
    echo "1. Konfiguration erstellen oder anpassen:"
    echo "   cp configs/minimal.yaml configs/meine-config.yaml"
    echo "   nano configs/meine-config.yaml"
    echo
    echo "2. Konfiguration validieren:"
    echo "   ./scripts/build.sh -c configs/meine-config.yaml --dry-run"
    echo
    echo "3. Image bauen:"
    echo "   sudo ./scripts/build.sh -c configs/meine-config.yaml"
    echo
    echo -e "${BLUE}Dokumentation:${NC}"
    echo "   - README.md: Übersicht"
    echo "   - docs/USAGE.md: Detaillierte Verwendung"
    echo "   - docs/FAQ.md: Häufig gestellte Fragen"
    echo "   - docs/ARCHITECTURE.md: Technische Details"
    echo
}

# Hauptfunktion
main() {
    install_packages
    install_python_deps
    test_validation
    
    echo
    echo -e "${GREEN}✓ Voraussetzungen erfolgreich installiert!${NC}"
    
    offer_test_build
}

# Start
main
