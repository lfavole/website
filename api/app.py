import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from website.wsgi import app  # noqa
