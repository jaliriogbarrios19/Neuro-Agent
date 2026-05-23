async def handle_echo(args: dict) -> dict:
    text = args.get("text")
    if text is None:
        return {"ok": False, "error": "Missing required argument: 'text'"}
    return {"ok": True, "data": text}
