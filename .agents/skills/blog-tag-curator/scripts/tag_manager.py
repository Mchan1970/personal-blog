#!/usr/bin/env python3
"""
博客标签治理辅助工具 (Blog Tag Manager)
支持子命令:
  - audit: 全局盘点博客文章标签分布、白名单合规率、高频非白名单标签及孤岛标签
  - batch: 按条件抽取一批待清洗/重构标签的文章（输出标题、当前标签、非白名单诊断及正文摘要）
  - apply: 将确认后的新标签无损写回文章 YAML Front Matter
"""

import argparse
import collections
import glob
import json
import os
import re
import sys
import tomllib
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[4]
CONTENT_DIR = ROOT_DIR / "content"
WHITELIST_PATH = ROOT_DIR / "data" / "tag-whitelist.toml"


def load_whitelist():
    if not WHITELIST_PATH.exists():
        return {"max_total": 50, "allowed_by_section": {}, "all_allowed": set(), "aliases": {}, "methods": set()}
    with open(WHITELIST_PATH, "rb") as f:
        data = tomllib.load(f)
    allowed_by_section = {}
    all_allowed = set()
    for sec, cfg in data.get("sections", {}).items():
        sec_key = sec.replace("_", "-")
        tags = set(cfg.get("allowed", []))
        allowed_by_section[sec_key] = tags
        all_allowed.update(tags)
    methods = set(data.get("global", {}).get("preferred_method_tags", []))
    all_allowed.update(methods)
    aliases = data.get("aliases", {})
    return {
        "max_total": data.get("max_total_tags", 50),
        "per_post_min": data.get("per_post_min", 3),
        "per_post_max": data.get("per_post_max", 5),
        "allowed_by_section": allowed_by_section,
        "all_allowed": all_allowed,
        "aliases": aliases,
        "methods": methods,
    }


def parse_post(filepath: Path):
    text = filepath.read_text(encoding="utf-8")
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n(.*)$", text, re.S)
    if not m:
        return None
    fm_text, body = m.group(1), m.group(2)

    # Extract title
    title = ""
    tm = re.search(r'^title:\s*(.+)$', fm_text, re.M)
    if tm:
        title = tm.group(1).strip().strip('"\'')

    # Extract tags
    tags = []
    inline_m = re.search(r'^tags:\s*\[(.*?)\]\s*$', fm_text, re.M)
    if inline_m:
        raw = inline_m.group(1).strip()
        if raw:
            for item in raw.split(","):
                t = item.strip().strip('"\'')
                if t:
                    tags.append(t)
    else:
        block_m = re.search(r'^tags:\s*\r?\n((?:[ \t]*-[ \t]*.*\r?\n?)+)', fm_text, re.M)
        if block_m:
            for line in block_m.group(1).splitlines():
                t = re.sub(r'^[ \t]*-[ \t]*', '', line).strip().strip('"\'')
                if t:
                    tags.append(t)

    rel_path = filepath.relative_to(ROOT_DIR)
    parts = rel_path.parts
    section = parts[1] if len(parts) > 2 else "root"

    # Clean body excerpt
    clean_body = re.sub(r'!\[.*?\]\(.*?\)', '', body)
    clean_body = re.sub(r'\s+', ' ', clean_body).strip()

    return {
        "path": str(rel_path),
        "abs_path": str(filepath),
        "section": section,
        "title": title,
        "tags": tags,
        "excerpt": clean_body[:600],
    }


def get_all_posts():
    posts = []
    for p in sorted(CONTENT_DIR.rglob("*.md")):
        if p.name == "_index.md" or p.name == "search.md" or "about" in p.parts:
            continue
        parsed = parse_post(p)
        if parsed:
            posts.append(parsed)
    return posts


def diagnose_post(post, wl):
    sec = post["section"]
    allowed = wl["allowed_by_section"].get(sec, wl["all_allowed"]) or wl["all_allowed"]
    tags = post["tags"]
    issues = []
    non_wl = []
    alias_hits = []
    for t in tags:
        if t in wl["aliases"]:
            alias_hits.append(f"{t}->{wl['aliases'][t]}")
        elif t not in allowed and t not in wl["all_allowed"]:
            non_wl.append(t)
    if len(tags) < wl["per_post_min"] or len(tags) > wl["per_post_max"]:
        issues.append(f"数量={len(tags)}(需{wl['per_post_min']}-{wl['per_post_max']})")
    if alias_hits:
        issues.append("可归并:" + ",".join(alias_hits))
    if non_wl:
        issues.append("非白名单:" + ",".join(non_wl))
    return issues, non_wl, alias_hits


def cmd_audit(args):
    wl = load_whitelist()
    posts = get_all_posts()
    tag_counter = collections.Counter()
    non_wl_counter = collections.Counter()
    section_counter = collections.Counter()
    compliant_posts = 0
    needs_refactor_posts = 0

    for p in posts:
        section_counter[p["section"]] += 1
        for t in p["tags"]:
            tag_counter[t] += 1
        issues, non_wl, _ = diagnose_post(p, wl)
        for t in non_wl:
            non_wl_counter[t] += 1
        if not issues:
            compliant_posts += 1
        else:
            needs_refactor_posts += 1

    island_tags = [t for t, c in tag_counter.items() if c == 1]

    print("=== 博客标签全局盘点报告 (Tag Audit Report) ===")
    print(f"文章总数: {len(posts)} 篇 (按栏目: {dict(section_counter)})")
    print(f"当前全站唯一标签总数: {len(tag_counter)} 个 (目标上限: <= {wl['max_total']} 个)")
    print(f"当前白名单已收录标签数: {len(wl['all_allowed'])} / {wl['max_total']} 个")
    print(f"完全符合白名单与数量规范的文章: {compliant_posts} 篇")
    print(f"待清洗/重构的文章: {needs_refactor_posts} 篇")
    print(f"只出现 1 次的『孤岛标签』数量: {len(island_tags)} 个 (占总标签 {len(island_tags)*100//max(1,len(tag_counter))}%)")
    print()
    print("--- Top 30 高频非白名单标签 (需判断：吸纳进白名单 / 设为别名 / 剥离字面载体) ---")
    for t, c in non_wl_counter.most_common(30):
        print(f"  {t}: {c} 篇")
    print()
    print("--- 已在白名单中的标签使用频次 ---")
    for t in sorted(wl["all_allowed"], key=lambda x: (-tag_counter[x], x)):
        if tag_counter[t] > 0:
            print(f"  {t}: {tag_counter[t]} 篇")


def cmd_batch(args):
    wl = load_whitelist()
    posts = get_all_posts()
    selected = []
    for p in posts:
        if args.section and p["section"] != args.section:
            continue
        if args.tag and args.tag not in p["tags"]:
            continue
        issues, _, _ = diagnose_post(p, wl)
        if not args.all and not issues:
            continue
        p["issues"] = issues
        selected.append(p)

    total_matching = len(selected)
    batch = selected[args.offset : args.offset + args.limit]
    print(f"=== 待处理文章批次 (匹配总数: {total_matching}, 当前显示: {args.offset + 1} ~ {args.offset + len(batch)}) ===")
    for idx, p in enumerate(batch, start=args.offset + 1):
        print(f"\n[{idx}] 标题: {p['title']}")
        print(f"    路径: {p['path']} (栏目: {p['section']})")
        print(f"    原标签: {json.dumps(p['tags'], ensure_ascii=False)}")
        print(f"    诊断: {'; '.join(p['issues']) if p['issues'] else '合规'}")
        print(f"    摘要: {p['excerpt']}")


def update_file_frontmatter(filepath: Path, new_tags: list[str] = None, new_title: str = None):
    text = filepath.read_text(encoding="utf-8")
    m = re.match(r"^(---\r?\n)(.*?)(\r?\n---\r?\n.*)$", text, re.S)
    if not m:
        raise ValueError(f"No valid YAML front matter found in {filepath}")
    prefix, fm_text, suffix = m.group(1), m.group(2), m.group(3)
    new_fm = fm_text

    if new_title:
        safe_title = json.dumps(new_title, ensure_ascii=False)
        if re.search(r'^title:\s*.*$', new_fm, re.M):
            new_fm = re.sub(r'^title:\s*.*$', f'title: {safe_title}', new_fm, count=1, flags=re.M)
        else:
            new_fm = f'title: {safe_title}\n' + new_fm

    if new_tags is not None:
        inline_tag_str = "tags: [" + ", ".join(f'"{t}"' for t in new_tags) + "]"
        block_tag_str = "tags:\n" + "\n".join(f"  - {t}" for t in new_tags) + "\n"

        if re.search(r'^tags:\s*\[.*?\]\s*$', new_fm, re.M):
            new_fm = re.sub(r'^tags:\s*\[.*?\]\s*$', inline_tag_str, new_fm, count=1, flags=re.M)
        elif re.search(r'^tags:\s*\r?\n((?:[ \t]*-[ \t]*.*\r?\n?)+)', new_fm, re.M):
            new_fm = re.sub(r'^tags:\s*\r?\n((?:[ \t]*-[ \t]*.*\r?\n?)+)', block_tag_str, new_fm, count=1, flags=re.M)
        elif re.search(r'^tags:\s*$', new_fm, re.M):
            new_fm = re.sub(r'^tags:\s*$', inline_tag_str, new_fm, count=1, flags=re.M)
        else:
            new_fm = new_fm + "\n" + inline_tag_str

    filepath.write_text(prefix + new_fm + suffix, encoding="utf-8")


def cmd_apply(args):
    items = json.loads(args.json)
    wl = load_whitelist()
    updated = 0
    for item in items:
        rel_path = item["path"]
        raw_tags = item.get("tags")
        new_title = item.get("title")
        final_tags = []
        if raw_tags is not None:
            for t in raw_tags:
                canon = wl["aliases"].get(t, t)
                if canon not in final_tags:
                    final_tags.append(canon)
        target = ROOT_DIR / rel_path
        if not target.exists():
            print(f"[ERROR] 文件不存在: {rel_path}", file=sys.stderr)
            continue
        update_file_frontmatter(target, new_tags=final_tags if raw_tags is not None else None, new_title=new_title)
        updated += 1
        title_str = f' [title -> {new_title}]' if new_title else ''
        print(f"[OK] {rel_path}{title_str} -> {json.dumps(final_tags, ensure_ascii=False)}")
    print(f"\n共成功更新 {updated} 篇文章。")


def main():
    parser = argparse.ArgumentParser(description="博客标签治理辅助工具")
    subparsers = parser.add_subparsers(dest="cmd", required=True)

    subparsers.add_parser("audit", help="全局盘点标签现状")

    p_batch = subparsers.add_parser("batch", help="按批次读取待清洗文章")
    p_batch.add_argument("--section", help="按栏目筛选 (如 yifeng-talks, property-rights)")
    p_batch.add_argument("--tag", help="按包含特定旧标签筛选 (如 学择新西兰)")
    p_batch.add_argument("--offset", type=int, default=0, help="起始偏移量")
    p_batch.add_argument("--limit", type=int, default=12, help="每批文章数 (默认 12)")
    p_batch.add_argument("--all", action="store_true", help="包含已合规文章")

    p_apply = subparsers.add_parser("apply", help="批量写回确认后的标签")
    p_apply.add_argument("--json", required=True, help='JSON 数组，如 \'[{"path":"content/...","tags":["标签1","标签2"]}]\'')

    args = parser.parse_args()
    if args.cmd == "audit":
        cmd_audit(args)
    elif args.cmd == "batch":
        cmd_batch(args)
    elif args.cmd == "apply":
        cmd_apply(args)


if __name__ == "__main__":
    main()
