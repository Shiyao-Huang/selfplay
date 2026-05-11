#!/usr/bin/env python3
"""Count Chinese characters and English words in text/markdown files.
Usage: python3 scripts/count_words.py [paths...]
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

CN_RE = re.compile(r"[\u4e00-\u9fff]")
EN_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")
SKIP_DIRS = {'.git', '.aha', 'node_modules', '.venv', '__pycache__'}
TEXT_SUFFIXES = {'.md', '.txt', '.py', '.ts', '.tsx', '.js', '.json', '.yaml', '.yml'}

def iter_files(paths: list[Path]):
    for p in paths:
        if p.is_dir():
            for child in p.rglob('*'):
                if any(part in SKIP_DIRS for part in child.parts):
                    continue
                if child.is_file() and (child.suffix in TEXT_SUFFIXES or child.name in {'AGENTS.md','SYSTEM.md'}):
                    yield child
        elif p.is_file():
            yield p

def count_file(path: Path):
    text = path.read_text(encoding='utf-8', errors='ignore')
    return len(CN_RE.findall(text)), len(EN_RE.findall(text)), len(text.encode('utf-8'))

def main():
    paths = [Path(x) for x in sys.argv[1:]] or [Path('research')]
    total_cn = total_en = total_bytes = 0
    rows = []
    for f in sorted(set(iter_files(paths))):
        cn, en, b = count_file(f)
        total_cn += cn; total_en += en; total_bytes += b
        rows.append((str(f), cn, en, b))
    print('file,cn_chars,en_words,bytes')
    for row in rows:
        print(f"{row[0]},{row[1]},{row[2]},{row[3]}")
    print(f"TOTAL,{total_cn},{total_en},{total_bytes}")
if __name__ == '__main__':
    main()
