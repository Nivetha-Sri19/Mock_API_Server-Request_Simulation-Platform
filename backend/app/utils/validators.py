import re

def is_valid_path(path: str) -> bool:
    return bool(path) and path.startswith("/") and "//" not in path

def normalize_path(path: str) -> str:
    path = path.strip()
    if not path.startswith("/"):
        path = "/" + path
    if len(path) > 1:
        path = path.rstrip("/")
    return path
