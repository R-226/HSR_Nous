#!/usr/bin/env python3
"""从 GitHub 更新 StarRailRes 数据文件到本地缓存."""

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import List, Optional

_GITHUB_RAW_URL = (
    "https://raw.githubusercontent.com/Mar-7th/StarRailRes/main/{index}/{lang}/{filename}"
)

CORE_FILES = [
    "characters.json",
    "character_skills.json",
    "character_skill_trees.json",
    "character_promotions.json",
    "character_ranks.json",
    "light_cones.json",
    "light_cone_promotions.json",
    "light_cone_ranks.json",
    "relic_sets.json",
    "relics.json",
    "relic_main_affixes.json",
    "relic_sub_affixes.json",
    "properties.json",
    "paths.json",
    "elements.json",
]


def _default_data_dir() -> Path:
    return Path(__file__).parent.parent.parent.parent / "data" / "starrailres"


def download_file(url: str, timeout: float = 30.0) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "HSR_Nous/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def run_update(
    *,
    data_dir: str,
    files: Optional[List[str]] = None,
    lang: str = "en",
    index: str = "index_new",
    timeout: float = 30.0,
    dry_run: bool = False,
) -> int:
    root = Path(data_dir)
    root.mkdir(parents=True, exist_ok=True)

    targets = files if files else CORE_FILES
    failed: List[str] = []
    updated: List[str] = []
    skipped: List[str] = []

    for filename in targets:
        url = _GITHUB_RAW_URL.format(index=index, lang=lang, filename=filename)
        out_dir = root / index / lang
        out_dir.mkdir(parents=True, exist_ok=True)
        local_path = out_dir / filename

        try:
            raw = download_file(url, timeout=timeout)
        except urllib.error.HTTPError as exc:
            print(f"[error] {filename}: HTTP {exc.code}", file=sys.stderr)
            failed.append(filename)
            continue
        except urllib.error.URLError as exc:
            print(f"[error] {filename}: {exc.reason}", file=sys.stderr)
            failed.append(filename)
            continue

        try:
            json.loads(raw)
        except json.JSONDecodeError as exc:
            print(f"[error] {filename}: invalid JSON - {exc}", file=sys.stderr)
            failed.append(filename)
            continue

        if local_path.exists():
            local_bytes = local_path.read_bytes()
            if local_bytes == raw:
                print(f"[skip] {filename}: identical to local")
                skipped.append(filename)
                continue

        if dry_run:
            print(f"[would update] {filename}: {len(raw)} bytes")
            continue

        local_path.write_bytes(raw)
        print(f"[updated] {filename}: {len(raw)} bytes")
        updated.append(filename)

    manifest_path = root / index / lang / "manifest.json"
    manifest = {
        "source": "https://github.com/Mar-7th/StarRailRes",
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "updated": updated,
        "skipped": skipped,
        "failed": failed,
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    total = len(targets)
    print(f"\n[summary] total={total}, updated={len(updated)}, skipped={len(skipped)}, failed={len(failed)}")
    return 1 if failed else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Update StarRailRes data from Mar-7th/StarRailRes GitHub repository."
    )
    parser.add_argument(
        "--data-dir",
        default=str(_default_data_dir()),
        help="Local directory to store data files",
    )
    parser.add_argument(
        "--lang", default="en", help="Language code (default: en)"
    )
    parser.add_argument(
        "--index", default="index_new", help="Index type: index_new or index_min (default: index_new)"
    )
    parser.add_argument(
        "--files",
        default="",
        help="Comma-separated file names to update (default: all core files)",
    )
    parser.add_argument(
        "--timeout", type=float, default=30.0, help="Network timeout in seconds"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Check remote files without writing"
    )
    args = parser.parse_args()

    files: Optional[List[str]] = None
    if args.files:
        files = [f.strip() for f in args.files.split(",") if f.strip()]

    return run_update(
        data_dir=args.data_dir,
        files=files,
        lang=args.lang,
        index=args.index,
        timeout=args.timeout,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    raise SystemExit(main())
