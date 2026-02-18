import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# Ensure tests do not fail due to missing API key in default config.
os.environ.setdefault("GEMINI_API_KEY", "test-key")
