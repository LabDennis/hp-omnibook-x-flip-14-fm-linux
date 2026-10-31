#!/usr/bin/env python3
"""Validate and optionally install the model-specific OEM ISH firmware."""
import argparse
import hashlib
import os
from pathlib import Path
import sys

MODEL = "HP OmniBook X Flip Laptop 14-fm0xxx"
SHA256 = "2d9f9bd732bfc80208b50645ff9fc6fdc1b046be71f7d4780ea6858d1676c759"
SIZE = 645632
TARGET = Path('/usr/lib/firmware/intel/ish/ish_lnlm_12128606.bin')


def check_model():
    dmi = Path('/sys/class/dmi/id')
    if ((dmi / 'sys_vendor').read_text().strip() != 'HP'
            or (dmi / 'product_name').read_text().strip() != MODEL):
        raise ValueError('Unsupported device. No changes made.')


def validate(data):
    if len(data) != SIZE or hashlib.sha256(data).hexdigest() != SHA256:
        raise ValueError('Firmware size/SHA-256 mismatch. Expected OEM 5.8.0.7718. No changes made.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('firmware', nargs='?', type=Path)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--install', action='store_true', help='Write firmware (requires root)')
    group.add_argument('--remove', action='store_true', help='Remove only the matching OEM firmware')
    args = parser.parse_args()
    check_model()
    if args.remove:
        if args.firmware:
            parser.error('--remove takes no firmware file')
        if not TARGET.exists() and not TARGET.is_symlink():
            print('No local override installed.')
            return
        if TARGET.is_symlink():
            raise ValueError('Refusing to remove a symlink.')
        validate(TARGET.read_bytes())
        if os.geteuid() != 0:
            raise ValueError('Removal requires root.')
        TARGET.unlink()
        print('Removed OEM override. Run sudo mkinitcpio -P, then reboot.')
        return
    if args.firmware is None:
        parser.error('provide a local OEM firmware file, or --remove')
    data = args.firmware.read_bytes()
    validate(data)
    print(f'Validated OEM firmware: {SHA256}')
    print(f'Destination: {TARGET}')
    if not args.install:
        print('Check only. No changes made. Add --install to write firmware.')
        return
    if os.geteuid() != 0:
        raise ValueError('Installation requires root.')
    # Never overwrite files or symlinks managed by a distribution or another fix.
    if TARGET.exists() or TARGET.is_symlink():
        if not TARGET.is_symlink() and TARGET.read_bytes() == data:
            print('Identical override already present. No changes made.')
            return
        raise ValueError('Destination already exists. Refusing to overwrite it.')
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    with TARGET.open('xb') as out:
        try:
            os.fchmod(out.fileno(), 0o644)
            out.write(data)
            out.flush()
            os.fsync(out.fileno())
        except Exception:
            TARGET.unlink()
            raise
    print('Installed. Run sudo mkinitcpio -P, then reboot when ready.')
    print('After reboot: python3 scripts/diagnose.py and monitor-sensor')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as exc:
        sys.exit(str(exc))
