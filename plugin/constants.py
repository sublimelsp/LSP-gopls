from __future__ import annotations

import re

PACKAGE_NAME = str(__package__).partition(".")[0]

TAG = "0.11.0"
GOPLS_BASE_URL = "golang.org/x/tools/gopls@v{tag}"
RE_VER = re.compile(r"go(\d+)\.(\d+)(?:\.(\d+))?")
