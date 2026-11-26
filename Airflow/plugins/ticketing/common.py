"""Atomic JSON checkpoints; business datasets stay in PostgreSQL."""
import json
import os
from pathlib import Path

DATA = Path(os.environ.get('DATA_DIR', '/opt/project/data'))

def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    temporary.replace(path)

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))
