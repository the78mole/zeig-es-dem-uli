#!/usr/bin/env python3
"""
Embedded Linux SDK - Image Builder
Hauptskript zum Erstellen von Embedded Linux Images
"""

import os
import sys
import yaml
import argparse
import subprocess
import shutil
import tempfile
import hashlib
from pathlib import Path


class ImageBuilder:
    """Klasse zum Erstellen von Embedded Linux Images"""
    
    def __init__(self, config_path, output_dir, keep_temp=False):
        self.config_path = Path(config_path)
        self.output_dir = Path(output_dir)
        self.keep_temp = keep_temp
        self.config = None
        self.rootfs_dir = None
        self.temp_dir = None
        
    def log_info(self, msg):
        print(f"\033[0;32m[INFO]\033[0m {msg}")
        
    def log_error(self, msg):
        print(f"\033[0;31m[ERROR]\033[0m {msg}")
        
    def log_warn(self, msg):
        print(f"\033[1;33m[WARN]\033[0m {msg}")
    
    def load_config(self):
        """Lädt die Konfiguration"""
        self.log_info(f"Lade Konfiguration: {self.config_path}")
        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)
    
    def setup_directories(self):
        """Erstellt temporäre Arbeitsverzeichnisse"""
        self.log_info("Erstelle Arbeitsverzeichnisse...")
        
        # Erstelle temporäres Verzeichnis
        self.temp_dir = Path(tempfile.mkdtemp(prefix='sdk-build-'))
        self.rootfs_dir = self.temp_dir / 'rootfs'
        self.rootfs_dir.mkdir(parents=True, exist_ok=True)
        
        self.log_info(f"Temporäres Verzeichnis: {self.temp_dir}")
        self.log_info(f"Root-Dateisystem: {self.rootfs_dir}")
    
    def run_debootstrap(self):
        """Führt debootstrap aus"""
        self.log_info("Führe debootstrap aus...")
        
        dist_name = self.config['distribution']['name']
        dist_release = self.config['distribution']['release']
        mirror = self.config['distribution'].get('mirror', 
            'http://ports.ubuntu.com/ubuntu-ports' if dist_name == 'ubuntu' 
            else 'http://deb.debian.org/debian')
        
        arch = self.config['architecture']
        
        # Debootstrap-Befehl
        cmd = [
            'debootstrap',
            '--arch', arch,
            '--variant=minbase',
            dist_release,
            str(self.rootfs_dir),
            mirror
        ]
        
        self.log_info(f"Befehl: {' '.join(cmd)}")
        
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            self.log_error(f"Debootstrap fehlgeschlagen: {e}")
            raise
    
    def setup_qemu(self):
        """Richtet QEMU für Chroot ein (bei Cross-Arch)"""
        host_arch = os.uname().machine
        target_arch = self.config['architecture']
        
        # Mapping zwischen YAML-Arch und QEMU
        qemu_arch_map = {
            'arm64': 'aarch64',
            'armhf': 'arm',
            'amd64': 'x86_64',
            'i386': 'i386'
        }
        
        qemu_arch = qemu_arch_map.get(target_arch, target_arch)
        
        # Prüfe ob Cross-Arch Build
        if (host_arch == 'x86_64' and target_arch in ['arm64', 'armhf']) or \
           (host_arch == 'aarch64' and target_arch in ['amd64', 'i386']):
            self.log_info(f"Cross-Arch Build erkannt: {host_arch} -> {target_arch}")
            self.log_info("Kopiere QEMU-Static...")
            
            qemu_binary = f'/usr/bin/qemu-{qemu_arch}-static'
            if os.path.exists(qemu_binary):
                shutil.copy2(qemu_binary, self.rootfs_dir / 'usr/bin/')
            else:
                self.log_warn(f"QEMU-Binary nicht gefunden: {qemu_binary}")
    
    def configure_system(self):
        """Konfiguriert das Basis-System"""
        self.log_info("Konfiguriere System...")
        
        # Setze Hostname
        hostname = self.config.get('hostname', 'target')
        (self.rootfs_dir / 'etc/hostname').write_text(hostname + '\n')
        
        # Erstelle /etc/hosts
        hosts_content = f"""127.0.0.1   localhost
127.0.1.1   {hostname}

# IPv6
::1         localhost ip6-localhost ip6-loopback
ff02::1     ip6-allnodes
ff02::2     ip6-allrouters
"""
        (self.rootfs_dir / 'etc/hosts').write_text(hosts_content)
        
        # Setze Root-Passwort (falls angegeben)
        if 'root_password' in self.config:
            password = self.config['root_password']
            # Erstelle gehashtes Passwort
            # Für Sicherheit sollte hier ein besserer Hash verwendet werden
            self.log_info("Setze Root-Passwort...")
            # Verwende chpasswd in chroot
            self._chroot_run(f"echo 'root:{password}' | chpasswd")
    
    def install_packages(self):
        """Installiert zusätzliche Pakete"""
        packages = self.config.get('packages', [])
        
        if not packages:
            self.log_info("Keine zusätzlichen Pakete zu installieren")
            return
        
        self.log_info(f"Installiere {len(packages)} Pakete...")
        
        # Update Package-Listen
        self.log_info("Aktualisiere Paketlisten...")
        self._chroot_run('apt-get update')
        
        # Installiere Pakete
        package_list = ' '.join(packages)
        self.log_info(f"Pakete: {package_list}")
        
        cmd = f'DEBIAN_FRONTEND=noninteractive apt-get install -y {package_list}'
        self._chroot_run(cmd)
        
        # Cleanup
        self.log_info("Räume APT-Cache auf...")
        self._chroot_run('apt-get clean')
    
    def _chroot_run(self, command):
        """Führt einen Befehl im Chroot aus"""
        # Mounte notwendige Pseudo-Dateisysteme
        self._mount_pseudo_fs()
        
        try:
            cmd = ['chroot', str(self.rootfs_dir), '/bin/bash', '-c', command]
            subprocess.run(cmd, check=True)
        finally:
            self._umount_pseudo_fs()
    
    def _mount_pseudo_fs(self):
        """Mountet Pseudo-Dateisysteme für Chroot"""
        mounts = [
            ('proc', 'proc'),
            ('sys', 'sysfs'),
            ('dev', 'devtmpfs'),
            ('dev/pts', 'devpts')
        ]
        
        for mount_point, fs_type in mounts:
            target = self.rootfs_dir / mount_point
            target.mkdir(parents=True, exist_ok=True)
            
            # Prüfe ob bereits gemountet
            if not subprocess.run(['mountpoint', '-q', str(target)]).returncode == 0:
                try:
                    subprocess.run(['mount', '-t', fs_type, fs_type, str(target)], 
                                   check=True, stderr=subprocess.DEVNULL)
                except subprocess.CalledProcessError:
                    pass  # Ignoriere Fehler beim Mounten
    
    def _umount_pseudo_fs(self):
        """Unmountet Pseudo-Dateisysteme"""
        mounts = ['dev/pts', 'dev', 'sys', 'proc']
        
        for mount_point in mounts:
            target = self.rootfs_dir / mount_point
            if target.exists():
                try:
                    subprocess.run(['umount', str(target)], 
                                   check=False, stderr=subprocess.DEVNULL)
                except Exception:
                    pass
    
    def create_output_image(self):
        """Erstellt das finale Output-Image"""
        self.log_info("Erstelle Output-Image...")
        
        output_name = self.config['output']['name']
        output_format = self.config['output'].get('format', 'tar.gz')
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = self.output_dir / f"{output_name}.{output_format}"
        
        self.log_info(f"Output: {output_file}")
        
        if output_format in ['tar.gz', 'tar.bz2', 'tar.xz']:
            # Erstelle Tarball
            compression_map = {
                'tar.gz': 'gz',
                'tar.bz2': 'bz2',
                'tar.xz': 'xz'
            }
            compression = compression_map[output_format]
            
            cmd = [
                'tar',
                f'--{compression}',
                '-cf', str(output_file),
                '-C', str(self.rootfs_dir),
                '.'
            ]
            
            subprocess.run(cmd, check=True)
            
        elif output_format == 'ext4':
            # Erstelle EXT4-Image
            size = self.config.get('partitions', {}).get('root', {}).get('size', '2G')
            
            # Erstelle leere Image-Datei
            subprocess.run(['dd', 'if=/dev/zero', f'of={output_file}', 
                          f'bs=1M', f'count=0', f'seek={size[:-1]}'], check=True)
            
            # Formatiere als EXT4
            subprocess.run(['mkfs.ext4', '-F', str(output_file)], check=True)
            
            # Mounte und kopiere Daten
            mount_point = self.temp_dir / 'mnt'
            mount_point.mkdir(exist_ok=True)
            
            subprocess.run(['mount', '-o', 'loop', str(output_file), str(mount_point)], 
                          check=True)
            
            try:
                subprocess.run(['cp', '-a', f'{self.rootfs_dir}/.', str(mount_point)], 
                              check=True)
            finally:
                subprocess.run(['umount', str(mount_point)], check=True)
        
        self.log_info(f"Image erfolgreich erstellt: {output_file}")
        
        # Zeige Dateigröße
        size = output_file.stat().st_size
        size_mb = size / (1024 * 1024)
        self.log_info(f"Größe: {size_mb:.2f} MB")
    
    def cleanup(self):
        """Räumt temporäre Dateien auf"""
        if not self.keep_temp and self.temp_dir:
            self.log_info("Räume temporäre Dateien auf...")
            
            # Stelle sicher, dass Pseudo-FS unmounted sind
            self._umount_pseudo_fs()
            
            # Lösche temporäres Verzeichnis
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        elif self.keep_temp:
            self.log_info(f"Temporäre Dateien behalten in: {self.temp_dir}")
    
    def build(self):
        """Haupt-Build-Funktion"""
        try:
            self.load_config()
            self.setup_directories()
            self.run_debootstrap()
            self.setup_qemu()
            self.configure_system()
            self.install_packages()
            self.create_output_image()
            
            self.log_info("Build erfolgreich abgeschlossen!")
            return True
            
        except Exception as e:
            self.log_error(f"Build fehlgeschlagen: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            self.cleanup()


def main():
    parser = argparse.ArgumentParser(description='Embedded Linux Image Builder')
    parser.add_argument('--config', required=True, help='Pfad zur Konfigurationsdatei')
    parser.add_argument('--output', required=True, help='Ausgabe-Verzeichnis')
    parser.add_argument('--keep-temp', action='store_true', 
                       help='Temporäre Dateien behalten')
    
    args = parser.parse_args()
    
    builder = ImageBuilder(args.config, args.output, args.keep_temp)
    
    if not builder.build():
        sys.exit(1)


if __name__ == '__main__':
    main()
