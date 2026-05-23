from pathlib import Path


async def _resolve_path(rel_path: str, vault_root: Path) -> Path:
    resolved = (vault_root / rel_path).resolve()
    if not resolved.is_relative_to(vault_root.resolve()):
        raise ValueError("Path traversal rejected")
    return resolved


async def read_file(args: dict, vault_root: Path) -> dict:
    try:
        target = await _resolve_path(args["path"], vault_root)
    except ValueError as e:
        return {"ok": False, "error": str(e)}
    if not target.exists():
        return {"ok": False, "error": f"File not found: {args['path']}"}
    return {"ok": True, "data": target.read_text(encoding="utf-8")}


async def write_file(args: dict, vault_root: Path) -> dict:
    try:
        target = await _resolve_path(args["path"], vault_root)
    except ValueError as e:
        return {"ok": False, "error": str(e)}
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(args.get("content", ""), encoding="utf-8")
    return {"ok": True, "path": args["path"]}


async def list_directory(args: dict, vault_root: Path) -> dict:
    try:
        target = vault_root / args.get("path", ".")
        resolved = target.resolve()
        if not resolved.is_relative_to(vault_root.resolve()):
            raise ValueError("Path traversal rejected")
    except ValueError as e:
        return {"ok": False, "error": str(e)}
    if not resolved.exists():
        return {"ok": False, "error": f"Directory not found: {args.get('path', '.')}"}
    entries = []
    for p in sorted(resolved.iterdir()):
        name = p.name + ("/" if p.is_dir() else "")
        entries.append(name)
    return {"ok": True, "data": entries}
