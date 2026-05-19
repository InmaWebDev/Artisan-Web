import py_compile
import os

SKIP_PARTS = ('__MACOSX', 'site-packages', 'venv', '.venv', '.git')
errors = 0
for root, dirs, files in os.walk('.'):
    # skip unwanted directories
    if any(part in root for part in SKIP_PARTS):
        continue
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            try:
                py_compile.compile(path, doraise=True)
                print('OK', path)
            except Exception as e:
                print('ERR', path, e)
                errors += 1
if errors:
    raise SystemExit(1)
else:
    print('All files compiled OK')
