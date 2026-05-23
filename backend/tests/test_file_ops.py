import tempfile
from pathlib import Path
from src.agent.tools.file_ops import read_file, write_file, list_directory


async def test_write_and_read_file():
    with tempfile.TemporaryDirectory() as tmp:
        vault = Path(tmp)
        result = await write_file({"path": "test.md", "content": "# Hello"}, vault_root=vault)
        assert result["ok"] is True
        assert (vault / "test.md").read_text() == "# Hello"

        result = await read_file({"path": "test.md"}, vault_root=vault)
        assert result["ok"] is True
        assert result["data"] == "# Hello"


async def test_read_nonexistent_file():
    with tempfile.TemporaryDirectory() as tmp:
        vault = Path(tmp)
        result = await read_file({"path": "missing.md"}, vault_root=vault)
        assert result["ok"] is False
        assert "not found" in result["error"]


async def test_path_traversal_rejected():
    with tempfile.TemporaryDirectory() as tmp:
        vault = Path(tmp)
        result = await read_file({"path": "../../etc/passwd"}, vault_root=vault)
        assert result["ok"] is False
        assert "traversal" in result["error"].lower()


async def test_list_directory():
    with tempfile.TemporaryDirectory() as tmp:
        vault = Path(tmp)
        (vault / "a.md").write_text("a")
        (vault / "b.md").write_text("b")
        (vault / "subdir").mkdir()
        (vault / "subdir" / "c.md").write_text("c")

        result = await list_directory({"path": "."}, vault_root=vault)
        assert result["ok"] is True
        assert "a.md" in result["data"]
        assert "b.md" in result["data"]
        assert "subdir/" in result["data"]
