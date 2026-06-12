---
created: 2026-05-19
up:
  - "[[MOC-MicroVM]]"
related:
  - "[[Firecracker Overview & Core Concepts]]"
  - "[[Firecracker Jailer Security Architecture]]"
  - "[[Firecracker VirtIO Network and Block IO Rate Limiting]]"
  - "[[Flow of Firecracker SDK]]"
in:
  - "[[Atlas]]"
tags:
  - systems/microvm
  - devops/infrastructure
  - installation
---

# Firecracker Prerequisites & Installation

## Summary
Firecracker requires specific hardware virtualization support, a Linux host with kernel 4.14+, and guest kernels 5.10 or 6.1 with virtio configurations. Works on bare-metal or cloud VMs with nested virtualization (KVM kernel modules required). Installation involves enabling KVM kernel modules, setting device ACLs, and downloading the static binary from GitHub releases.

## Key Points
- **Hardware**: Requires 64-bit Intel, AMD, or ARM processor with VT-x/VT-d or SVM extensions enabled in BIOS. Works on bare-metal or cloud VMs with nested virtualization (KVM kernel modules required).
- **Host Kernel**: Linux 4.14+ minimum, 6.1+ recommended for PCI transport support
- **Guest Kernel**: Officially supports Linux 5.10 and 6.1 with architecture-specific virtio and serial console configurations
- **Binary Distribution**: Single static binary (~20MB) distributed via GitHub releases; no package manager required

## Prerequisites

### Hardware Requirements
- **Processor**: 64-bit Intel, AMD, or ARM (aarch64)
- **Virtualization Extensions**: VT-x/VT-d (Intel) or SVM (AMD) enabled in BIOS
- **Deployment**: Bare-metal Linux host required; nested virtualization usually not supported on cloud VMs 

### Host System Dependencies
```bash
sudo apt-get update && sudo apt-get install -y git wget curl build-essential iproute2 qemu-utils acl
```

### Host Kernel
- **Minimum**: Linux 4.14+
- **Recommended**: Linux 6.1+ (for PCI transport support)

## Guest Kernel Requirements

### Supported Versions
- Linux 5.10 (LTS)
- Linux 6.1 (LTS)

### Architecture-Specific Configurations

**x86_64:**
- Uncompressed ELF images
- `CONFIG_VIRTIO_BLK=y`
- `CONFIG_VIRTIO_NET=y`
- `CONFIG_SERIAL_8250_CONSOLE`
- `CONFIG_KVM_GUEST=y`

**aarch64:**
- PE-formatted images
- `CONFIG_ARM_AMBA`
- `CONFIG_RTC_DRV_PL031`

**Optional PCI Transport (v1.9+):**
- `CONFIG_PCI`
- Omit `pci=off` from kernel parameters

## Installation

### Step 1: Install System Dependencies
```bash
sudo apt-get update && sudo apt-get install -y git wget curl build-essential iproute2 qemu-utils acl
```

### Step 2: Enable KVM Kernel Modules
```bash
sudo modprobe kvm && sudo modprobe kvm_intel
# For AMD systems:
# sudo modprobe kvm_amd
ls -la /dev/kvm
```

### Step 3: Set Device Permissions
```bash
sudo setfacl -m u:${USER}:rw /dev/kvm
```

### Step 4: Download and Install Firecracker
```bash
curl -LO https://github.com/firecracker-microvm/firecracker/releases/download/v1.10.1/firecracker-v1.10.1-x86_64.tgz
tar -xzf firecracker-v1.10.1-x86_64.tgz
chmod +x firecracker-v1.10.1-x86_64
sudo mv firecracker-v1.10.1-x86_64 /usr/local/bin/firecracker
```

## Verification

1. **Verify KVM permissions:**
   ```bash
   ls -la /dev/kvm
   ```

2. **Confirm Firecracker installation:**
   ```bash
   firecracker --version
   ```

## Related / Links
- [[MOC-MicroVM]]
- [[KVM Configuration]]
- [[Guest Kernel Compilation]]
- [[Firecracker Overview & Core Concepts]]
- [[Flow of Firecracker SDK]]

---
*Confidence Score: 0.92*
**Reasoning**: Source provides explicit version numbers, kernel configuration flags, and exact shell commands. Hardware requirements are clearly specified. All commands preserved verbatim from source.