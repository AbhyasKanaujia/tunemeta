import re
from pathlib import Path

from tunemeta import __version__


def test_version_matches_pyproject():
    pyproject = Path(__file__).parent.parent / "pyproject.toml"
    text = pyproject.read_text()
    match = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    assert match is not None, "couldn't find version in pyproject.toml"
    assert __version__ == match.group(1)
