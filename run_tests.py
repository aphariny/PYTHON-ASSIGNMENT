import importlib.util
import inspect
import tempfile
from pathlib import Path

TEST_FILE = Path(__file__).parent / 'tests' / 'test_system.py'
spec = importlib.util.spec_from_file_location('test_system', TEST_FILE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

names = [name for name in dir(mod) if name.startswith('test_')]
passed = failed = 0
for name in names:
    fn = getattr(mod, name)
    try:
        if 'tmp_path' in inspect.signature(fn).parameters:
            with tempfile.TemporaryDirectory() as tmp:
                fn(Path(tmp))
        else:
            fn()
        print(f'{name}: PASS')
        passed += 1
    except Exception as exc:
        print(f'{name}: FAIL - {exc}')
        failed += 1
print(f'\nTOTAL: {passed} passed, {failed} failed')
raise SystemExit(1 if failed else 0)
