# Supported hardware

Tested configuration for the rotation fix and BIOS recovery guide:

| Component | Value |
| --- | --- |
| Model | HP OmniBook X Flip 14-fm0153ng |
| DMI family | HP OmniBook X Flip Laptop 14-fm0xxx |
| SKU | BZ7Z3EA#ABD |
| System board | 8D9F |
| Platform | Intel Lunar Lake, Core Ultra 5 226V |
| Intel ISH | PCI 8086:a845, subsystem 103c:8d9f |
| OS / desktop | CachyOS, KDE Plasma / Wayland |
| Kernel tested | 7.3.0-4-cachyos |
| BIOS update tested | F.10 → F.20 (2026-04-27) |

These instructions target the Intel 14-fm0xxx family. Other OmniBook families and board IDs require their own firmware packages.

Identify your device:

```bash
cat /sys/class/dmi/id/product_name
cat /sys/class/dmi/id/product_sku
cat /sys/class/dmi/id/board_name
cat /sys/class/dmi/id/bios_version
python3 scripts/diagnose.py
```

[HP specifications for 14-fm0153ng / BZ7Z3EA](https://www.hp.com/at-de/products/laptops/product-details/product-specifications/2103167132)
