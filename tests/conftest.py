"""Test configuration helpers.

Ensures the repository root is on ``sys.path`` so tests can import modules
regardless of how pytest is invoked.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add repository root to sys.path for reliable imports when running pytest via
# the console entrypoint (which may not insert the CWD by default in some
# environments).
REPO_ROOT = Path(__file__).resolve().parent.parent
root_str = str(REPO_ROOT)
if root_str not in sys.path:
    sys.path.insert(0, root_str)
