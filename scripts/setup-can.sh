#!/bin/bash
# Setup CAN interface for NXP S32G2
# Dieses Script konfiguriert die CAN-Schnittstelle

set -e

# CAN-Konfiguration
CAN_INTERFACE=${CAN_INTERFACE:-can0}
CAN_BITRATE=${CAN_BITRATE:-500000}

echo "Konfiguriere CAN-Interface: $CAN_INTERFACE"

# Erstelle Systemd-Service für CAN
cat > /etc/systemd/system/can-setup.service << EOF
[Unit]
Description=CAN Interface Setup
After=network.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/local/bin/can-start.sh

[Install]
WantedBy=multi-user.target
EOF

# Erstelle Start-Script
cat > /usr/local/bin/can-start.sh << EOF
#!/bin/bash
ip link set $CAN_INTERFACE type can bitrate $CAN_BITRATE
ip link set up $CAN_INTERFACE
EOF

chmod +x /usr/local/bin/can-start.sh

# Aktiviere Service
systemctl enable can-setup.service

echo "CAN-Setup abgeschlossen"
