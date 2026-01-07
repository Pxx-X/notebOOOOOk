import os
import re
import shutil


SOURCE_FILES = [
    r"D:\My2025\MyNotes\flow\EDA4PR.md",
    r"D:\My2025\MyNotes\flow\EDA4PR-Analog.md",
    r"D:\My2025\MyNotes\flow\EDA4PR-Digtal.md",
    r"D:\My2025\MyNotes\flow\EDA4PR-LCM.md",
    r"D:\My2025\MyNotes\flow\flow.md",
    r"D:\My2025\MyNotes\Other\Algorithms.md",
    r"D:\My2025\MyNotes\Other\Hardware.md",
    r"D:\My2025\MyNotes\Other\Literature.md",
    r"D:\My2025\MyNotes\Other\OS.md",
    r"D:\My2025\MyNotes\Other\Program.md",
    r"D:\My2025\MyNotes\Other\Tools.md",
]

ASSET_SOURCES = [
    r"D:\My2025\MyNotes\Other\assets",
    r"D:\My2025\MyNotes\flow\assets",
]

DEST_DOCS = r"D:\My2025\MyBlog\docs"
DEST_ASSETS = r"D:\My2025\MyBlog\docs\assets"


def detect_encoding(data):
    if data.startswith(b"\xEF\xBB\xBF"):
        return "utf-8-sig"
    if data.startswith(b"\xFF\xFE"):
        return "utf-16-le"
    if data.startswith(b"\xFE\xFF"):
        return "utf-16-be"
    try:
        data.decode("utf-8")
        return "utf-8"
    except UnicodeDecodeError:
        return "gbk"


def normalize_markdown(text, title):
    lines = re.split(r"\r?\n", text)
    out = []
    in_fence = False
    fence_re = re.compile(r"^\s*(?:[-*+]\s+)?(?:>\s*)*(```|~~~)")
    h1_count = 0
    i = 0
    admonition_re = re.compile(
        r"^(?P<indent>\s*)(?P<list>(?:[-*+]|\d+\.)\s+)?(?P<quote>>+\s*)"
        r"\[!(?P<kind>[A-Za-z]+)\]\s*(?P<rest>.*)$"
    )
    quote_re = re.compile(
        r"^(?P<indent>\s*)(?P<list>(?:[-*+]|\d+\.)\s+)?(?P<quote>>+)\s?(?P<rest>.*)$"
    )

    while i < len(lines):
        line = lines[i]

        if not in_fence:
            alert_match = admonition_re.match(line)
            if alert_match:
                indent = alert_match.group("indent") or ""
                list_prefix = indent + (alert_match.group("list") or "")
                kind = alert_match.group("kind").lower()
                if kind == "important":
                    kind = "info"
                content = []
                inline = alert_match.group("rest").strip()
                if inline:
                    content.append(inline)
                i += 1
                while i < len(lines):
                    next_line = lines[i]
                    if re.match(r"^\s*(?:[-*+]|\d+\.)\s+>+\s*(.*)$", next_line):
                        stripped = re.sub(r"^\s*(?:[-*+]|\d+\.)\s+>+\s?", "", next_line)
                        content.append(stripped)
                        i += 1
                    elif re.match(r"^\s*>+\s*(.*)$", next_line):
                        stripped = re.sub(r"^\s*>+\s?", "", next_line)
                        content.append(stripped)
                        i += 1
                    else:
                        break
                out.append(f"{list_prefix}!!! {kind}")
                if not content:
                    out.append(f"{list_prefix}    ")
                else:
                    for item in content:
                        out.append(f"{list_prefix}    {item}")
                continue

            quote_match = quote_re.match(line)
            if quote_match:
                indent = quote_match.group("indent") or ""
                list_prefix = indent + (quote_match.group("list") or "")
                content = []
                inline = quote_match.group("rest").strip()
                if inline:
                    content.append(inline)
                i += 1
                while i < len(lines):
                    next_line = lines[i]
                    if re.match(r"^\s*(?:[-*+]|\d+\.)\s+>+\s*(.*)$", next_line):
                        stripped = re.sub(r"^\s*(?:[-*+]|\d+\.)\s+>+\s?", "", next_line)
                        content.append(stripped)
                        i += 1
                    elif re.match(r"^\s*>+\s*(.*)$", next_line):
                        stripped = re.sub(r"^\s*>+\s?", "", next_line)
                        content.append(stripped)
                        i += 1
                    else:
                        break
                out.append(f"{list_prefix}!!! note")
                if not content:
                    out.append(f"{list_prefix}    ")
                else:
                    for item in content:
                        out.append(f"{list_prefix}    {item}")
                continue

        if not in_fence:
            line = re.sub(r"^(\s*[-*+])\s+(```|~~~)", r"\1   \2", line)
            line = re.sub(r"^(\s*(?:[-*+]|\d+\.)\s+)#(?=\S)", r"\1\\#", line)
            if re.match(r"^\s*(?:[-*+]|\d+\.)\s*$", line):
                i += 1
                continue
            line = re.sub(r"^(\s*>+\s*)#{1,6}(?=\s)", r"\1\\#", line)
            line = re.sub(r"^(\s*(?:[-*+]|\d+\.)\s+>+\s*)#{1,6}(?=\s)", r"\1\\#", line)
            line = re.sub(r"^(\s*(?:[-*+]|\d+\.)\s+)?(>+)(\S)", r"\1\2 \3", line)

        if fence_re.match(line):
            in_fence = not in_fence
            out.append(line)
            i += 1
            continue

        if not in_fence:
            m = re.match(r"^\s*(?:[-*+]|\d+\.)\s+(#{1,6})\s+(.*)$", line)
            if m:
                level = len(m.group(1))
                if level == 1:
                    h1_count += 1
                out.append(f"{'#' * level} {m.group(2)}")
                i += 1
                continue

            m = re.match(r"^\s{0,3}(#{1,6})([^ #])(.*)$", line)
            if m:
                rest = f"{m.group(2)}{m.group(3)}"
                if re.match(r"^(include|define|pragma|if|elif|endif|else|!/|region|endregion)\b", rest):
                    out.append(line)
                else:
                    level = len(m.group(1))
                    if level == 1:
                        h1_count += 1
                    out.append(f"{'#' * level} {rest}")
                i += 1
                continue
            m = re.match(r"^\s{0,3}(#{1,6})\s+(.*)$", line)
            if m:
                level = len(m.group(1))
                if level == 1:
                    h1_count += 1
                out.append(f"{'#' * level} {m.group(2)}")
                i += 1
                continue

        out.append(line)
        i += 1

    if h1_count > 1:
        demoted = []
        in_fence = False
        for line in out:
            if fence_re.match(line):
                in_fence = not in_fence
                demoted.append(line)
                continue
            if not in_fence:
                m = re.match(r"^(\s{0,3})(#{1,6})\s+(.*)$", line)
                if m:
                    level = len(m.group(2))
                    level = min(level + 1, 6)
                    demoted.append(f"{m.group(1)}{'#' * level} {m.group(3)}")
                    continue
            demoted.append(line)
        out = demoted

    if h1_count == 0 or h1_count > 1:
        insert_at = 0
        if out and out[0].strip() == "---":
            for idx in range(1, len(out)):
                if out[idx].strip() in ("---", "..."):
                    insert_at = idx + 1
                    break
        out.insert(insert_at, f"# {title}")
        if insert_at + 1 < len(out) and out[insert_at + 1].strip() != "":
            out.insert(insert_at + 1, "")

    return "\n".join(out)


def copy_and_fix_markdown(src, dst_dir):
    if not os.path.exists(src):
        print(f"Missing file: {src}")
        return
    os.makedirs(dst_dir, exist_ok=True)
    dst = os.path.join(dst_dir, os.path.basename(src))
    shutil.copy2(src, dst)

    with open(dst, "rb") as f:
        data = f.read()
    encoding = detect_encoding(data)
    text = data.decode(encoding)
    title = os.path.splitext(os.path.basename(src))[0]
    fixed = normalize_markdown(text, title)
    with open(dst, "wb") as f:
        f.write(fixed.encode("utf-8"))


def copy_assets(src_dir, dst_dir):
    if not os.path.isdir(src_dir):
        print(f"Missing assets folder: {src_dir}")
        return
    for root, _, files in os.walk(src_dir):
        rel = os.path.relpath(root, src_dir)
        target_dir = dst_dir if rel == "." else os.path.join(dst_dir, rel)
        os.makedirs(target_dir, exist_ok=True)
        for name in files:
            shutil.copy2(os.path.join(root, name), os.path.join(target_dir, name))


def main():
    os.makedirs(DEST_DOCS, exist_ok=True)
    os.makedirs(DEST_ASSETS, exist_ok=True)

    for path in SOURCE_FILES:
        copy_and_fix_markdown(path, DEST_DOCS)

    for src in ASSET_SOURCES:
        copy_assets(src, DEST_ASSETS)


if __name__ == "__main__":
    main()
