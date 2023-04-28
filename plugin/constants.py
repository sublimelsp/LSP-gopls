import re

DEFAULT_COMMAND = '${storage_path}/LSP-gopls/bin/gopls'
PACKAGE_NAME = __package__.partition('.')[0]
SESSION_NAME = 'gopls'
SETTINGS = 'LSP-gopls.sublime-settings'

TAG = '0.11.0'
GOPLS_BASE_URL = 'golang.org/x/tools/gopls@v{tag}'
RE_VER = re.compile(r'go(\d+)\.(\d+)(?:\.(\d+))?')

