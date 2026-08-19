#!/usr/bin/env python3
"""frontend/, backend/ 마크다운 콘텐츠를 읽어 site/index.html 정적 페이지를 생성한다.

사용법: python3 site/build.py
결과물: site/index.html (외부 네트워크 요청 없이 파일을 브라우저에서 바로 열어 쓸 수 있는 단일 HTML)
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
sys.path.insert(0, str(SITE))
from curriculum import (  # noqa: E402
    FRONTEND_ORDER,
    BACKEND_ORDER,
    FRONTEND_CATEGORY_ORDER,
    BACKEND_CATEGORY_ORDER,
)

ITEM_RE = re.compile(r"^-\s*\[(.*?)\]\(contents/([\w-]+)\.md\)\s*$")
CATEGORY_RE = re.compile(r"^##\s+(.*?)\s*$")


def parse_toc_category(path: Path):
    """toc-category.md -> [{name, desc, items: [id, ...]}]"""
    categories = []
    current = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip("\n")
        m = CATEGORY_RE.match(line)
        if m:
            current = {"name": m.group(1), "desc": "", "items": []}
            categories.append(current)
            continue
        m = ITEM_RE.match(line)
        if m and current is not None:
            current["items"].append(m.group(2))
            continue
        if current is not None and line.strip() and not current["items"]:
            # 카테고리 제목 바로 다음, 첫 항목 이전의 설명 문단
            current["desc"] = (current["desc"] + " " + line.strip()).strip()
    return categories


def apply_learning_order(categories, order_map):
    """curriculum.py에 정의된 추천 학습 순서로 각 카테고리의 items를 재정렬한다."""
    for cat in categories:
        order = order_map.get(cat["name"])
        if not order:
            continue
        rank = {item_id: i for i, item_id in enumerate(order)}
        # 순서 목록에 없는 id(콘텐츠가 새로 추가된 경우 등)는 뒤에 원래 순서대로 붙인다.
        cat["items"].sort(key=lambda item_id: rank.get(item_id, len(order)))


def apply_category_order(categories, category_order):
    """카테고리 배열 자체를 curriculum.py에 정의된 추천 순서로 재정렬한다."""
    if not category_order:
        return categories
    rank = {name: i for i, name in enumerate(category_order)}
    categories.sort(key=lambda cat: rank.get(cat["name"], len(category_order)))
    return categories


def build_section(subject_dir: Path, prefix: str, order_map, category_order=None):
    categories = parse_toc_category(subject_dir / "toc-category.md")
    items = {}
    for md_file in sorted((subject_dir / "contents").glob(f"{prefix}-*.md")):
        item_id = md_file.stem
        content = md_file.read_text(encoding="utf-8")
        items[item_id] = {"id": item_id, "content": content, "title": ""}

    # 제목은 toc.md에서 가져온다 (카테고리 목차에 없는 항목이 있을 수 있어 전체 목록 기준)
    toc_path = subject_dir / "toc.md"
    for line in toc_path.read_text(encoding="utf-8").splitlines():
        m = ITEM_RE.match(line.strip())
        if m:
            title, item_id = m.group(1), m.group(2)
            if item_id in items:
                items[item_id]["title"] = title

    # 카테고리에 속하지 않은 항목을 "기타"로 모은다
    categorized = {i for c in categories for i in c["items"]}
    leftovers = [i for i in items if i not in categorized]
    if leftovers:
        categories.append({"name": "기타", "desc": "카테고리 미분류 질문입니다.", "items": sorted(
            leftovers, key=lambda x: int(x.split("-")[1]))})

    apply_learning_order(categories, order_map)
    apply_category_order(categories, category_order)

    return {"categories": categories, "items": items}


def main():
    data = {
        "frontend": build_section(ROOT / "frontend", "fe", FRONTEND_ORDER, FRONTEND_CATEGORY_ORDER),
        "backend": build_section(ROOT / "backend", "be", BACKEND_ORDER, BACKEND_CATEGORY_ORDER),
    }

    template = (SITE / "template.html").read_text(encoding="utf-8")
    out = template.replace(
        "/*__DATA__*/", json.dumps(data, ensure_ascii=False)
    )
    (SITE / "index.html").write_text(out, encoding="utf-8")

    n_fe = len(data["frontend"]["items"])
    n_be = len(data["backend"]["items"])
    print(f"OK: frontend {n_fe}문항, backend {n_be}문항 -> site/index.html")


if __name__ == "__main__":
    main()
