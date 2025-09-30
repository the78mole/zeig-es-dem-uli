# Build Flow Visualization

## Complete Build Process

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER STARTS BUILD                             │
│                    ./scripts/build.sh -c config.yaml                 │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     PHASE 1: VALIDATION                              │
├─────────────────────────────────────────────────────────────────────┤
│  1. Parse command line arguments                                    │
│     • config file path                                              │
│     • output directory                                              │
│     • options (--dry-run, --keep-temp)                              │
│                                                                      │
│  2. Check prerequisites                                             │
│     ✓ debootstrap installed?                                        │
│     ✓ qemu-user-static installed?                                   │
│     ✓ python3 & PyYAML available?                                   │
│     ✓ root privileges?                                              │
│                                                                      │
│  3. Validate configuration                                          │
│     ✓ YAML syntax correct?                                          │
│     ✓ Required fields present?                                      │
│     ✓ Valid architecture?                                           │
│     ✓ Valid distribution?                                           │
│     ✓ Valid output format?                                          │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     PHASE 2: PREPARATION                             │
├─────────────────────────────────────────────────────────────────────┤
│  1. Create temporary directories                                    │
│     /tmp/sdk-build-XXXXX/                                           │
│     └── rootfs/                                                     │
│                                                                      │
│  2. Load configuration                                              │
│     • Read YAML file                                                │
│     • Parse settings                                                │
│     • Set variables                                                 │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     PHASE 3: BASE SYSTEM                             │
├─────────────────────────────────────────────────────────────────────┤
│  1. Run debootstrap                                                 │
│     debootstrap --arch=<arch> <release> <rootfs> <mirror>           │
│                                                                      │
│  2. Download base packages                                          │
│     [====================] 100%                                     │
│     • Essential system packages                                     │
│     • Base utilities                                                │
│     • Package manager (apt)                                         │
│                                                                      │
│  3. Extract and setup                                               │
│     • Create directory structure                                    │
│     • Install base system                                           │
│     • Configure dpkg                                                │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     PHASE 4: CROSS-ARCH SETUP                        │
├─────────────────────────────────────────────────────────────────────┤
│  IF target_arch != host_arch:                                       │
│                                                                      │
│  1. Copy QEMU binary                                                │
│     cp /usr/bin/qemu-<arch>-static rootfs/usr/bin/                  │
│                                                                      │
│  2. Setup binfmt                                                    │
│     • Enable foreign architecture execution                         │
│     • Configure QEMU for chroot                                     │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     PHASE 5: SYSTEM CONFIGURATION                    │
├─────────────────────────────────────────────────────────────────────┤
│  1. Mount pseudo-filesystems                                        │
│     mount -t proc proc rootfs/proc                                  │
│     mount -t sysfs sysfs rootfs/sys                                 │
│     mount -t devtmpfs devtmpfs rootfs/dev                           │
│     mount -t devpts devpts rootfs/dev/pts                           │
│                                                                      │
│  2. Configure system                                                │
│     • Set hostname → /etc/hostname                                  │
│     • Create /etc/hosts                                             │
│     • Set root password (if specified)                              │
│     • Configure timezone                                            │
│                                                                      │
│  3. Setup network                                                   │
│     • Create network configuration                                  │
│     • Configure interfaces                                          │
│     • Setup DNS                                                     │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     PHASE 6: PACKAGE INSTALLATION                    │
├─────────────────────────────────────────────────────────────────────┤
│  1. Update package lists                                            │
│     chroot rootfs apt-get update                                    │
│                                                                      │
│  2. Install packages                                                │
│     FOR each package in config:                                     │
│       chroot rootfs apt-get install -y <package>                    │
│     [====================] 100%                                     │
│                                                                      │
│  3. Cleanup                                                         │
│     chroot rootfs apt-get clean                                     │
│     • Remove downloaded .deb files                                  │
│     • Clean apt cache                                               │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     PHASE 7: CUSTOMIZATION (Optional)                │
├─────────────────────────────────────────────────────────────────────┤
│  IF customization scripts configured:                               │
│                                                                      │
│  1. Run post-install scripts                                        │
│     • setup-can.sh                                                  │
│     • configure-network.sh                                          │
│     • custom scripts...                                             │
│                                                                      │
│  2. Copy overlay files                                              │
│     • Custom configuration files                                    │
│     • Additional binaries                                           │
│     • Device-specific files                                         │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     PHASE 8: IMAGE CREATION                          │
├─────────────────────────────────────────────────────────────────────┤
│  1. Unmount pseudo-filesystems                                      │
│     umount rootfs/{dev/pts,dev,sys,proc}                            │
│                                                                      │
│  2. Create output image                                             │
│     ┌─────────────────────────────────────────────────────┐        │
│     │ IF format = tar.gz:                                 │        │
│     │   tar czf output.tar.gz -C rootfs .                 │        │
│     │   [====================] 100%                       │        │
│     │                                                     │        │
│     │ IF format = ext4:                                   │        │
│     │   dd if=/dev/zero of=output.ext4 bs=1M count=2048   │        │
│     │   mkfs.ext4 -F output.ext4                          │        │
│     │   mount -o loop output.ext4 /mnt                    │        │
│     │   cp -a rootfs/. /mnt/                              │        │
│     │   umount /mnt                                        │        │
│     │                                                     │        │
│     │ IF format = squashfs:                               │        │
│     │   mksquashfs rootfs output.squashfs -comp xz        │        │
│     └─────────────────────────────────────────────────────┘        │
│                                                                      │
│  3. Calculate checksum                                              │
│     sha256sum output.* > output.sha256                              │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     PHASE 9: CLEANUP                                 │
├─────────────────────────────────────────────────────────────────────┤
│  IF --keep-temp NOT specified:                                      │
│                                                                      │
│  1. Remove QEMU binary                                              │
│     rm rootfs/usr/bin/qemu-*-static                                 │
│                                                                      │
│  2. Delete temporary directory                                      │
│     rm -rf /tmp/sdk-build-XXXXX/                                    │
│                                                                      │
│  ELSE:                                                              │
│     Keep temporary files in /tmp/sdk-build-XXXXX/                   │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     PHASE 10: COMPLETION                             │
├─────────────────────────────────────────────────────────────────────┤
│  ✓ Build completed successfully!                                    │
│                                                                      │
│  Output:                                                            │
│  • Image: build/<name>.<format>                                     │
│  • Size: XXX MB                                                     │
│  • Checksum: build/<name>.sha256                                    │
│                                                                      │
│  Next steps:                                                        │
│  1. Extract to SD card or eMMC                                      │
│  2. Install bootloader (U-Boot)                                     │
│  3. Install kernel and device tree                                  │
│  4. Configure boot parameters                                       │
│  5. Boot target hardware                                            │
└─────────────────────────────────────────────────────────────────────┘
```

## Example Timeline

### Minimal Build (~5-10 minutes)
```
[00:00] Phase 1-2: Validation & Preparation  ▓░░░░░░░░░  10%
[00:30] Phase 3: Base System (debootstrap)   ▓▓▓░░░░░░░  30%
[02:00] Phase 4-5: Setup & Configuration     ▓▓▓▓░░░░░░  40%
[03:00] Phase 6: Package Installation        ▓▓▓▓▓▓░░░░  60%
[04:30] Phase 7: Customization               ▓▓▓▓▓▓▓░░░  70%
[05:00] Phase 8: Image Creation              ▓▓▓▓▓▓▓▓░░  80%
[05:30] Phase 9-10: Cleanup & Completion     ▓▓▓▓▓▓▓▓▓▓  100%
```

### Full Build with many packages (~30-45 minutes)
```
[00:00] Phase 1-2: Validation & Preparation  ▓░░░░░░░░░  10%
[01:00] Phase 3: Base System (debootstrap)   ▓▓░░░░░░░░  20%
[05:00] Phase 4-5: Setup & Configuration     ▓▓▓░░░░░░░  30%
[25:00] Phase 6: Package Installation        ▓▓▓▓▓▓▓░░░  70%
[30:00] Phase 7: Customization               ▓▓▓▓▓▓▓▓░░  80%
[35:00] Phase 8: Image Creation              ▓▓▓▓▓▓▓▓▓░  90%
[40:00] Phase 9-10: Cleanup & Completion     ▓▓▓▓▓▓▓▓▓▓  100%
```

## Key Decision Points

### Architecture Selection
```
┌────────────────────────────────┐
│   Host Architecture?           │
│   Target Architecture?         │
└────────────┬───────────────────┘
             │
    ┌────────┴─────────┐
    │                  │
    ▼                  ▼
Same Arch          Cross Arch
    │                  │
    │              Install QEMU
    │              Setup binfmt
    │                  │
    └────────┬─────────┘
             │
             ▼
      Continue Build
```

### Output Format Selection
```
┌────────────────────────────────┐
│   Output Format?               │
└────────────┬───────────────────┘
             │
    ┌────────┼─────────┐
    │        │         │
    ▼        ▼         ▼
  TAR     EXT4    SquashFS
    │        │         │
    │        │         │
Compress  Format   Compress
    │        │         │
    └────────┴─────────┘
             │
             ▼
      Final Image
```

## Error Handling

At each phase, the build system checks for errors:

```
┌──────────────┐
│ Phase Start  │
└──────┬───────┘
       │
       ▼
┌──────────────┐     ┌─────────────┐
│ Execute      │────>│ Check Exit  │
│ Operation    │     │ Code        │
└──────────────┘     └──────┬──────┘
                            │
                 ┌──────────┴────────────┐
                 │                       │
                 ▼                       ▼
            Exit Code 0            Exit Code != 0
            (Success)               (Error)
                 │                       │
                 ▼                       ▼
        ┌─────────────────┐     ┌───────────────┐
        │ Continue to     │     │ Log Error     │
        │ Next Phase      │     │ Cleanup       │
        └─────────────────┘     │ Exit Build    │
                                └───────────────┘
```

## Debugging Flow

When using `--keep-temp`:

```
Build Fails
     │
     ▼
Temporary files preserved
     │
     └─> /tmp/sdk-build-XXXXX/
             │
             ├─> rootfs/          ← Full filesystem
             │    ├─> /etc/        ← Check configs
             │    ├─> /var/log/    ← Check logs
             │    └─> /usr/bin/    ← Check binaries
             │
             └─> build.log         ← Build output

Manual Debug:
  $ sudo chroot /tmp/sdk-build-XXXXX/rootfs /bin/bash
  # apt-get update
  # apt-get install <failed-package>
  # exit
```

## Success Indicators

```
✓ Configuration validated
✓ Prerequisites checked
✓ Base system created
✓ Packages installed
✓ System configured
✓ Image created
✓ Build completed

→ Image ready for deployment
```
