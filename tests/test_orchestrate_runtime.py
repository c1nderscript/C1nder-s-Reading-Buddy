import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
import orchestrate_all


def test_orchestrate_runtime(tmp_path, monkeypatch):
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    sample = src_dir / "sample.md"
    sample.write_text("# Hello\nWorld")

    output_dir = tmp_path / "chunks"

    inputs = iter([str(output_dir), str(src_dir), "testbook"])
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    orchestrate_all.main()

    assert output_dir.is_dir()

    ledger_path = tmp_path / "ledger.json"
    assert ledger_path.exists()

    data = json.loads(ledger_path.read_text())
    assert "src" in data.get("folders", {})
    assert str(sample) in data["folders"]["src"]
