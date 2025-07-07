import os
import pytest

# List of script paths relative to repository root
SCRIPT_FILES = [
    'configure.sh',
    'convert_to_kindle.sh',
    'ingest_and_convert.sh',
    'merge.sh',
    'shuffle_split_files.sh',
    'split_markdown.sh',
    'ingest_and_convert.py',
]

@pytest.mark.parametrize('path', SCRIPT_FILES)
def test_script_is_executable(path):
    assert os.path.isfile(path), f"Script {path} does not exist"
    assert os.access(path, os.X_OK), f"Script {path} is not executable"

