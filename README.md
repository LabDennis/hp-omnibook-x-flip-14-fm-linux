# HP OmniBook X Flip 14-fm0xxx — Linux fixes

Linux setup notes and tools for the **HP OmniBook X Flip 14-fm0xxx (Intel Lunar Lake)**, tested on **14-fm0153ng / BZ7Z3EA#ABD**, board **8D9F**, with CachyOS and KDE Plasma/Wayland.

- Enable automatic screen rotation with the matching HP Intel ISH firmware.
- Update the BIOS from F.10 to F.20 using the internal EFI partition and HP recovery.
- Identify the hardware and validate the sensor firmware before installation.

See [supported hardware](HARDWARE.md) and the [BIOS update guide](BIOS-UPDATE.md). Firmware is obtained directly from HP; this repository contains only project documentation, scripts and tests.

## Rotation and tablet sensors

Automatic rotation works with HP OEM **ishS_SI_5.8.0.7718.bin**, installed as `/usr/lib/firmware/intel/ish/ish_lnlm_12128606.bin`.

**Verified download: [HP SP156899.exe](https://ftp.hp.com/pub/softpaq/sp156501-157000/sp156899.exe)** — Intel Integrated Sensor Solution Driver 5.8.32.0 Rev.A. HP lists this under Driver-Chipset for the [OmniBook X Flip 14-fm0000, Windows 11 24H2](https://support.hp.com/us-en/drivers/hp-omnibook-x-flip-14-inch-2-in-1-laptop-next-gen-ai-pc-14-fm0000/2102686808). The [official package metadata](https://ftp.hp.com/pub/softpaq/sp156501-157000/sp156899.cva) explicitly includes `SysId01=0x8D9F`. An old Windows installation is not needed to obtain the file.

Extract the package as an archive; do not run the Windows installer on Linux. The required archive member is:

```text
Driver/IshHeciExtensionTemplate/FWImage/0003/ishS_SI_5.8.0.7718.bin
```

Use the file in **IshHeciExtensionTemplate** above; the `IshHeci` directory contains a different firmware version.

No firmware is automatically downloaded. Expected file:

```text
Size:   645632 bytes
SHA256: 2d9f9bd732bfc80208b50645ff9fc6fdc1b046be71f7d4780ea6858d1676c759
```

From the project folder, check the system and validate your file:

```bash
python3 scripts/diagnose.py
python3 scripts/ish-firmware.py /absolute/path/ishS_SI_5.8.0.7718.bin
```

The second command only validates. Installation explicitly requires:

```bash
sudo python3 scripts/ish-firmware.py /absolute/path/ishS_SI_5.8.0.7718.bin --install
sudo mkinitcpio -P
```

For this CachyOS setup, let initramfs generation finish successfully, then reboot when convenient. The installer refuses other models, wrong firmware and existing destination files. It does not change the BIOS, keyboard, boot parameters or display configuration. Initramfs integration for distributions using other generators is not implemented.

After reboot:

```bash
python3 scripts/diagnose.py
monitor-sensor
```

Check that `accel_3d`, `gyro_3d` and hinge devices appear, and that orientation events change. Then test KDE automatic rotation in tablet mode, touch alignment, keyboard/touchpad deactivation when folded, and recovery after suspend. Sensor registration alone does not prove all tablet behavior works. Only add a mount-matrix correction if observed orientation is wrong.

To remove the exact installed override:

```bash
sudo python3 scripts/ish-firmware.py --remove
sudo mkinitcpio -P
```

Reboot afterward. Removal verifies the firmware hash and refuses symlinks or different content. The original packaged firmware remains untouched.

## BIOS update

[BIOS-UPDATE.md](BIOS-UPDATE.md) describes the tested F.10 → F.20 update using original HP files on the internal EFI System Partition.

Firmware and raw logs are excluded from Git. Review diagnostic output before sharing it.
