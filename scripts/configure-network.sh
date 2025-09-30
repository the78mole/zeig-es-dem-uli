#!/bin/bash
# Configure network interfaces
# Netzwerk-Schnittstellen konfigurieren

set -e

echo "Konfiguriere Netzwerk-Schnittstellen..."

# Erstelle NetworkManager-Konfiguration für Ethernet
cat > /etc/NetworkManager/system-connections/eth0.nmconnection << EOF
[connection]
id=eth0
type=ethernet
interface-name=eth0
autoconnect=true

[ipv4]
method=auto

[ipv6]
method=auto
EOF

chmod 600 /etc/NetworkManager/system-connections/eth0.nmconnection

# Aktiviere NetworkManager
systemctl enable NetworkManager

echo "Netzwerk-Konfiguration abgeschlossen"
