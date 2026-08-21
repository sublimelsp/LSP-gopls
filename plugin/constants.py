from __future__ import annotations

import re

TAG = "0.11.0"
GOPLS_BASE_URL = "golang.org/x/tools/gopls@v{tag}"
RE_VER = re.compile(r"go(\d+)\.(\d+)(?:\.(\d+))?")
