"""Exercise installer safeguards in a temporary directory, never system firmware."""
import contextlib
import hashlib
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    'installer', Path(__file__).resolve().parents[1] / 'scripts/ish-firmware.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallerTests(unittest.TestCase):
    def test_real_hash_rejects_wrong_firmware(self):
        with self.assertRaises(ValueError):
            installer.validate(b'not firmware')

    def test_unsupported_model_rejected(self):
        with patch.object(Path, 'read_text', return_value='Other device'):
            with self.assertRaises(ValueError):
                installer.check_model()

    def test_check_install_refuse_overwrite_and_remove(self):
        # Synthetic fixture uses its own digest; production digest stays fixed.
        data = b'fixture firmware'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, target = root / 'source.bin', root / 'target.bin'
            source.write_bytes(data)
            with (patch.object(installer, 'TARGET', target),
                  patch.object(installer, 'SIZE', len(data)),
                  patch.object(installer, 'SHA256', hashlib.sha256(data).hexdigest()),
                  patch.object(installer, 'check_model'),
                  patch.object(installer.os, 'geteuid', return_value=0),
                  contextlib.redirect_stdout(io.StringIO())):
                def run(*args):
                    with patch('sys.argv', ['ish-firmware.py', *map(str, args)]):
                        installer.main()
                run(source)
                self.assertFalse(target.exists(), 'check-only must not write')
                run(source, '--install')
                self.assertEqual(target.read_bytes(), data)
                run(source, '--install')  # idempotent
                target.write_bytes(b'existing unrelated file')
                with self.assertRaises(ValueError):
                    run(source, '--install')
                with self.assertRaises(ValueError):
                    run('--remove')
                self.assertEqual(target.read_bytes(), b'existing unrelated file')
                target.unlink()
                target.symlink_to(source)
                with self.assertRaises(ValueError):
                    run(source, '--install')
                with self.assertRaises(ValueError):
                    run('--remove')
                self.assertEqual(source.read_bytes(), data)
                target.unlink()
                run(source, '--install')
                run('--remove')
                self.assertFalse(target.exists())


if __name__ == '__main__':
    unittest.main()
