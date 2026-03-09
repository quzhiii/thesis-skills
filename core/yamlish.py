from __future__ import annotations

from pathlib import Path


def _strip_comment(raw: str) -> str:
    out: list[str] = []
    in_single = False
    in_double = False
    for ch in raw:
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == "#" and not in_single and not in_double:
            break
        out.append(ch)
    return "".join(out).rstrip()


def _tokenize(text: str) -> list[tuple[int, str]]:
    tokens: list[tuple[int, str]] = []
    for raw in text.splitlines():
        cleaned = _strip_comment(raw)
        if not cleaned.strip():
            continue
        indent = len(cleaned) - len(cleaned.lstrip(" "))
        tokens.append((indent, cleaned.strip()))
    return tokens


def _parse_scalar(value: str) -> object:
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    if value in {"null", "None", "~"}:
        return None
    if value.startswith(("'", '"')) and value.endswith(("'", '"')) and len(value) >= 2:
        return value[1:-1]
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def _is_list(tokens: list[tuple[int, str]], index: int, indent: int) -> bool:
    return (
        index < len(tokens)
        and tokens[index][0] == indent
        and tokens[index][1].startswith("- ")
    )


def _parse_block(
    tokens: list[tuple[int, str]], index: int, indent: int
) -> tuple[object, int]:
    if _is_list(tokens, index, indent):
        items: list[object] = []
        while index < len(tokens):
            current_indent, content = tokens[index]
            if current_indent != indent or not content.startswith("- "):
                break
            payload = content[2:].strip()
            index += 1
            if not payload:
                item, index = _parse_block(tokens, index, indent + 2)
                items.append(item)
            else:
                items.append(_parse_scalar(payload))
        return items, index

    mapping: dict[str, object] = {}
    while index < len(tokens):
        current_indent, content = tokens[index]
        if current_indent < indent:
            break
        if current_indent > indent:
            raise ValueError(f"Unexpected indentation near: {content}")
        if ":" not in content:
            raise ValueError(f"Expected key/value pair near: {content}")
        key, value = content.split(":", 1)
        key = key.strip()
        value = value.strip()
        index += 1
        if not value:
            child, index = _parse_block(tokens, index, indent + 2)
            mapping[key] = child
        else:
            mapping[key] = _parse_scalar(value)
    return mapping, index


def loads(text: str) -> dict[str, object]:
    tokens = _tokenize(text)
    if not tokens:
        return {}
    node, index = _parse_block(tokens, 0, tokens[0][0])
    if index != len(tokens):
        raise ValueError("Failed to parse full YAML payload")
    if not isinstance(node, dict):
        raise ValueError("Top-level YAML must be a mapping")
    return node


def load_yaml_file(path: str | Path) -> dict[str, object]:
    return loads(Path(path).read_text(encoding="utf-8"))
