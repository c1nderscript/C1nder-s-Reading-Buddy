import os
import subprocess
import sys
from pathlib import Path


def test_ingest_and_convert_executes(tmp_path):
    script = Path(__file__).resolve().parents[1] / "ingest_and_convert.py"
    env = os.environ.copy()
    env["KB_DIR"] = str(tmp_path)
    subprocess.run([sys.executable, str(script)], cwd=tmp_path, env=env, check=True)
    assert (tmp_path / "ledger.json").exists()
