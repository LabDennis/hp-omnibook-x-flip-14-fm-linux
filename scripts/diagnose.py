#!/usr/bin/env python3
"""Read-only device checks; omits serial numbers, usernames and network IDs."""
from pathlib import Path
import platform
import shutil
import subprocess


def read(path):
    try:
        return Path(path).read_text().strip()
    except OSError:
        return '(unavailable)'


print('Kernel:', platform.release())
for key in ('sys_vendor', 'product_name', 'bios_version'):
    print(key + ':', read('/sys/class/dmi/id/' + key))
for key in ('subsystem_vendor', 'subsystem_device'):
    print('ISH ' + key + ':', read('/sys/bus/pci/devices/0000:00:12.0/' + key))
devices = sorted(Path('/sys/bus/iio/devices').glob('iio:device*'))
names = [read(device / 'name') for device in devices]
print('IIO devices:', ', '.join(names) or '(none)')
print('Accelerometer:', 'detected' if any('accel' in n.lower() for n in names) else 'NOT detected')
print('OEM override:', Path('/usr/lib/firmware/intel/ish/ish_lnlm_12128606.bin').exists())
print('Console keyboard config:', read('/etc/vconsole.conf'))
for package in ('iio-sensor-proxy', 'kscreen', 'plasma-workspace', 'linux-firmware'):
    if shutil.which('pacman'):
        result = subprocess.run(['pacman', '-Q', package], capture_output=True, text=True)
        print(result.stdout.strip() or f'{package}: unavailable')
print('Next: monitor-sensor in a desktop terminal; rotate device in tablet mode.')
