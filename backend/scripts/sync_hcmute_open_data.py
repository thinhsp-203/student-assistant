"""Sync public, non-personal HCM-UTE pages into the RAG document directory."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in {"script", "style", "noscript", "svg"}:
            self._skip += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style", "noscript", "svg"} and self._skip:
            self._skip -= 1

    def handle_data(self, data: str) -> None:
        if not self._skip:
            text = re.sub(r"\s+", " ", data).strip()
            if text:
                self.parts.append(text)


def fetch_text(url: str, timeout: int) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/131.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        parser = TextExtractor()
        parser.feed(response.read().decode(charset, errors="replace"))
    return "\n\n".join(parser.parts)


def safe_name(source_id: str) -> str:
    return re.sub(r"[^a-z0-9_-]+", "-", source_id.lower()).strip("-")


def sync(config_path: Path, output_dir: Path, timeout: int) -> tuple[int, int]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    synced = failed = 0
    output_dir.mkdir(parents=True, exist_ok=True)
    retrieved_at = datetime.now(timezone.utc).isoformat()

    for source in config["sources"]:
        try:
            content = fetch_text(source["url"], timeout)
            if len(content) < 80:
                raise ValueError("trang không có đủ nội dung văn bản")
            document = (
                f"# {source['title']}\n\n"
                f"> Nguồn chính thức: [{source['url']}]({source['url']})\n"
                f"> Danh mục: {source['category']}\n"
                f"> Đồng bộ lúc (UTC): {retrieved_at}\n"
                "> Đây là dữ liệu công khai, dùng cho mục đích minh họa và nghiên cứu. "
                "Cần đối chiếu thông báo mới nhất trước khi áp dụng thực tế.\n\n"
                f"{content}\n"
            )
            (output_dir / f"hcmute-{safe_name(source['id'])}.md").write_text(
                document, encoding="utf-8"
            )
            synced += 1
            print(f"[OK] {source['title']}")
        except Exception as exc:
            failed += 1
            print(f"[WARN] {source['title']}: {exc}", file=sys.stderr)
    return synced, failed


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    root = Path(__file__).resolve().parents[1]
    parser.add_argument(
        "--config",
        type=Path,
        default=root / "data" / "sources" / "hcmute_public_sources.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=root / "data" / "documents" / "hcmute",
    )
    parser.add_argument("--timeout", type=int, default=20)
    args = parser.parse_args()
    synced, failed = sync(args.config, args.output, args.timeout)
    print(f"Đã đồng bộ {synced} nguồn HCM-UTE; lỗi {failed}.")
    return 0 if synced and not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
