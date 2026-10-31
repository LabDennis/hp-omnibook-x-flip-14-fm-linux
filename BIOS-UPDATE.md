# BIOS F.10 → F.20 from CachyOS

Confirmed on **HP OmniBook X Flip 14-fm0153ng**, SKU **BZ7Z3EA#ABD**, system board **8D9F**, on 2026-10-31. This is the Intel Lunar Lake 14-fm0xxx family, not the AMD or Ultra Flip models.

Place the original HP recovery files on the **internal EFI System Partition (ESP)** and invoke firmware recovery with **Windows+B**. No installed Windows system is required. Verified BIOS after the update:

```text
bios_version: F.20
bios_date:    04/27/2026
```

Tested for this board and the F.10 → F.20 upgrade. Other boards and BIOS packages require separate verification.

## Official downloads

- [HP model driver page](https://support.hp.com/us-en/drivers/hp-omnibook-x-flip-14-inch-2-in-1-laptop-next-gen-ai-pc-14-fm0000/2102686808)
- [HP SP172509.exe: F.20 Rev.A](https://ftp.hp.com/pub/softpaq/sp172501-173000/sp172509.exe)
- [HP package metadata](https://ftp.hp.com/pub/softpaq/sp172501-173000/sp172509.cva), listing board 8D9F

The repository contains **no HP binaries, firmware, or third-party source code**. Obtain those files directly from HP. Do not substitute another board's firmware.

## Export the original files

The package contains an inner `8D9FF20.exe`, the Windows utility `HPFlashWinx64.exe`, `08D9F.fd`, and the `CrisisFolder` and `DEVFW` directories. Nested extraction depends on the package format; a simple 7-Zip extraction is not guaranteed to unpack every layer. Preserve the full extracted utility directory when running the HP application under Wine.

Run HP's utility under Wine and select **Copy** to export the firmware files, for example into Wine's Documents folder. Use Wine for file export; the actual update runs through the laptop's firmware recovery.

Retain these two sets of original files outside this repository:

1. The files produced by HP's Copy option: `08D9F.bin`, `08D9F.sig`, and the `08D9FME0` / `08D9FPD1` `.bin`, `.sig`, `.s12` files.
2. All files from the package's `CrisisFolder` and `DEVFW` directories, including their original EFI programs and signatures.

Keep the exported filenames and contents unchanged. The BIOS uses `08D9F.bin` and `08D9F.sig`; the device firmware includes the `.s12` files shown below.

## Prepare the internal ESP

Identify the ESP with `findmnt` and `lsblk`; do not assume every distribution uses `/boot`. On the tested CachyOS installation it was `/dev/nvme0n1p1`, FAT32, mounted at `/boot`.

Back up the existing `EFI/HP` directory, if present, to a location outside the ESP before changing it. Preserve the Linux bootloader and unrelated HP diagnostics. Verify enough free space for about 50 MB of recovery files plus temporary copies. Keep the backup outside Git because it may contain proprietary files and device-specific data.

Prepare this layout:

```text
<ESP>/EFI/HP/
├── BIOS/
│   ├── Current/
│   │   ├── 08D9F.bin
│   │   └── 08D9F.sig
│   ├── New/                    (empty)
│   └── Previous/               (empty)
├── BIOSUpdate/
│   └── all original files from CrisisFolder/
└── DEVFW/
    ├── Current/
    │   ├── 08D9FME0.bin
    │   ├── 08D9FME0.sig
    │   ├── 08D9FME0.s12
    │   ├── 08D9FPD1.bin
    │   ├── 08D9FPD1.sig
    │   └── 08D9FPD1.s12
    ├── New/                    (empty)
    ├── Previous/               (empty)
    └── original files from DEVFW/
```

Copy the contents of `CrisisFolder` directly into `BIOSUpdate`, not into another nested `CrisisFolder` directory. Likewise, copy the original device-update programs into `DEVFW` itself. There were **48 original files** in the prepared tree. Every destination file was compared against its source after copying, and writes were flushed with `sync`.

Secure Boot was disabled on the tested installation; this procedure has not been tested with it enabled.

## Invoke recovery

1. Disconnect the USB stick and leave AC power connected.
2. Shut the laptop down completely.
3. Hold **Windows+B**, then press and hold Power for **2–3 seconds**.
4. Release Power while continuing to hold Windows+B until recovery appears.
5. Allow the update to finish without interrupting power.

After returning to Linux, check:

```bash
cat /sys/class/dmi/id/board_name
cat /sys/class/dmi/id/bios_version
cat /sys/class/dmi/id/bios_date
```

For this recorded update the expected results were `8D9F`, `F.20`, and `04/27/2026`. Check boot and security settings after updating. An ESP backup restores the prepared files; it is **not** a BIOS rollback mechanism.

## References

- [HP BIOS recovery instructions](https://support.hp.com/us-en/document/ish_3932413-2337994-16)
- [Linux BIOS update guide using the internal ESP](https://dvdkon.ggu.cz/blogpost/hp_ex360_bios_update/)
