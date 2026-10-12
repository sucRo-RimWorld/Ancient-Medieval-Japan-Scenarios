"""Validate that packaged Scenario archive includes only tracked subscriber files."""
from pathlib import Path
import fnmatch
import io
import subprocess
import unittest
import zipfile
ROOT = Path(__file__).resolve().parents[2]

class Packaging(unittest.TestCase):
    def test_subscriber_archive_matches_rimignore(self):
        rules=[x.strip() for x in (ROOT/'.rimignore').read_text().splitlines() if x.strip() and not x.startswith('#')]
        tracked=subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines()
        expected={p for p in tracked if not any(fnmatch.fnmatch(part,rule) for part in Path(p).parts for rule in rules)}
        data=subprocess.check_output(['git','archive','--format=zip','HEAD'],cwd=ROOT)
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            actual={p for p in archive.namelist() if not p.endswith('/')}
            self.assertEqual(actual,expected)
            self.assertTrue({"About/About.xml", "About/Manifest.xml", "About/Changelog.txt"}.issubset(actual))
            for path in actual:self.assertEqual(archive.read(path),(ROOT/path).read_bytes())

if __name__=='__main__':unittest.main()
