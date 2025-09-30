#!/usr/bin/env python3
"""
Konfigurationsvalidierung für Embedded Linux SDK
Configuration validation for Embedded Linux SDK
"""

import sys
import yaml
import argparse
from pathlib import Path

# Erforderliche Felder
REQUIRED_FIELDS = {
    'architecture': str,
    'distribution': dict,
    'hostname': str,
    'output': dict
}

# Gültige Architekturen
VALID_ARCHITECTURES = ['arm64', 'armhf', 'amd64', 'i386']

# Gültige Distributionen
VALID_DISTRIBUTIONS = {
    'ubuntu': ['focal', 'jammy', 'mantic', 'noble'],
    'debian': ['buster', 'bullseye', 'bookworm']
}

# Gültige Output-Formate
VALID_OUTPUT_FORMATS = ['tar.gz', 'tar.bz2', 'tar.xz', 'ext4', 'squashfs']


def validate_config(config_path):
    """Validiert eine Konfigurationsdatei"""
    
    print(f"Validiere Konfiguration: {config_path}")
    
    # Lade YAML
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"FEHLER: Datei nicht gefunden: {config_path}")
        return False
    except yaml.YAMLError as e:
        print(f"FEHLER: Ungültiges YAML: {e}")
        return False
    
    if not config:
        print("FEHLER: Leere Konfiguration")
        return False
    
    errors = []
    warnings = []
    
    # Prüfe erforderliche Felder
    for field, field_type in REQUIRED_FIELDS.items():
        if field not in config:
            errors.append(f"Erforderliches Feld fehlt: {field}")
        elif not isinstance(config[field], field_type):
            errors.append(f"Feld '{field}' hat falschen Typ (erwartet: {field_type.__name__})")
    
    # Prüfe Architektur
    if 'architecture' in config:
        if config['architecture'] not in VALID_ARCHITECTURES:
            errors.append(f"Ungültige Architektur: {config['architecture']}. "
                         f"Gültig: {', '.join(VALID_ARCHITECTURES)}")
    
    # Prüfe Distribution
    if 'distribution' in config and isinstance(config['distribution'], dict):
        if 'name' not in config['distribution']:
            errors.append("Distribution.name fehlt")
        elif config['distribution']['name'] not in VALID_DISTRIBUTIONS:
            warnings.append(f"Unbekannte Distribution: {config['distribution']['name']}")
        
        if 'release' not in config['distribution']:
            errors.append("Distribution.release fehlt")
        elif config['distribution']['name'] in VALID_DISTRIBUTIONS:
            valid_releases = VALID_DISTRIBUTIONS[config['distribution']['name']]
            if config['distribution']['release'] not in valid_releases:
                warnings.append(f"Unbekanntes Release: {config['distribution']['release']}. "
                               f"Bekannt: {', '.join(valid_releases)}")
    
    # Prüfe Output-Konfiguration
    if 'output' in config and isinstance(config['output'], dict):
        if 'name' not in config['output']:
            errors.append("Output.name fehlt")
        
        if 'format' in config['output']:
            if config['output']['format'] not in VALID_OUTPUT_FORMATS:
                errors.append(f"Ungültiges Output-Format: {config['output']['format']}. "
                             f"Gültig: {', '.join(VALID_OUTPUT_FORMATS)}")
    
    # Prüfe Packages (optional, aber sollte Liste sein)
    if 'packages' in config:
        if not isinstance(config['packages'], list):
            errors.append("Packages muss eine Liste sein")
        elif len(config['packages']) == 0:
            warnings.append("Keine Pakete angegeben")
    
    # Ausgabe der Ergebnisse
    print()
    if warnings:
        print("WARNUNGEN:")
        for warning in warnings:
            print(f"  ⚠ {warning}")
        print()
    
    if errors:
        print("FEHLER:")
        for error in errors:
            print(f"  ✗ {error}")
        print()
        print("Validierung fehlgeschlagen!")
        return False
    
    print("✓ Konfiguration ist valide")
    print()
    
    # Zeige Zusammenfassung
    print("Konfigurationszusammenfassung:")
    print(f"  Architektur: {config.get('architecture', 'N/A')}")
    print(f"  Distribution: {config.get('distribution', {}).get('name', 'N/A')} "
          f"{config.get('distribution', {}).get('release', 'N/A')}")
    print(f"  Hostname: {config.get('hostname', 'N/A')}")
    print(f"  Pakete: {len(config.get('packages', []))}")
    print(f"  Output: {config.get('output', {}).get('name', 'N/A')}.{config.get('output', {}).get('format', 'N/A')}")
    
    return True


def main():
    parser = argparse.ArgumentParser(description='Validiere SDK-Konfigurationsdatei')
    parser.add_argument('config', help='Pfad zur Konfigurationsdatei')
    
    args = parser.parse_args()
    
    if not validate_config(args.config):
        sys.exit(1)
    
    sys.exit(0)


if __name__ == '__main__':
    main()
