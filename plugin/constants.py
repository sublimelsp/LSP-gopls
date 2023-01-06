import re

PACKAGE_NAME = __package__.partition('.')[0]
SESSION_NAME = 'gopls'

TAG = '0.11.0'
GOPLS_BASE_URL = 'golang.org/x/tools/gopls@v{tag}'
RE_VER = re.compile(r'go(\d+)\.(\d+)(?:\.(\d+))?')

