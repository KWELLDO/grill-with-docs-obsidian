#!/usr/bin/env python3
"""校验「拷问 + 沉淀文档」产物的完整性。

纯 Markdown 版没有 Obsidian 的反链面板、Bases 表和 unresolved 命令，
这个脚本代替它们。每次落盘后跑一次。

用法:
    python3 tools/validate.py [根目录]        # 默认校验当前目录
    python3 tools/validate.py --all           # 断链检查扩展到全仓所有 Markdown

检查项:
    1. 断链     —— 每个相对链接都指向真实存在的文件
                （默认只看产出物；--all 时非产出物的断链降级为警告）
    2. 字段     —— frontmatter 能解析，必填字段齐全
    3. 残留     —— 没有 [[双链]]、![[嵌入]]、.base、obsidian 命令
    4. 索引     —— CONTEXT.md 的清单与实际文件双向一致
    5. 孤儿卡   —— 每张术语卡都至少被一个别的文件链接
    6. 待敲定   —— 索引页的 provisional 清单与卡片现状一致

退出码 0 = 全部通过，1 = 有失败项。
"""

import re
import sys
from pathlib import Path

REQUIRED_TERM_FIELDS = {"term", "en", "context", "status", "created"}
REQUIRED_ADR_FIELDS = {"title", "date", "context"}

# 记录所有强制失败；仅提示的问题走 warnings
failures: list[str] = []
warnings: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def read_frontmatter(path: Path) -> dict | None:
    """返回 frontmatter 字典；没有 frontmatter 返回 None；解析失败记失败并返回 None。"""
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    try:
        import yaml
    except ImportError:
        # 不依赖 pyyaml：退化成极简解析，只取顶层 key: value
        data = {}
        for line in m.group(1).splitlines():
            km = re.match(r"^(\w+):\s*(.*)$", line)
            if km:
                data[km.group(1)] = km.group(2).strip().strip('"\'')
        return data
    try:
        return yaml.safe_load(m.group(1)) or {}
    except Exception as exc:  # noqa: BLE001
        fail(f"{path}: frontmatter 不是合法 YAML —— {exc}")
        return None


def collect_md(root: Path) -> list[Path]:
    return sorted(
        p for p in root.rglob("*.md")
        if ".git" not in p.parts and not p.name.startswith(".")
    )


def owned_files(root: Path) -> list[Path]:
    """本 skill 拥有的文件：术语卡、ADR、索引页。

    链接检查默认只看这些 —— 真实仓库里别的 Markdown 有自己的历史包袱，
    把它们的断链算进来会让「校验通过」变成不可能满足的门槛。
    """
    cards, adrs = artifact_files(root)
    owned = cards + adrs
    index = root / "CONTEXT.md"
    if index.exists():
        owned.append(index)
    return owned


def strip_code(text: str) -> str:
    """去掉围栏代码块与行内代码。

    文档里举例的链接（`[订单](./order.md)`）是示例文本，不是真链接；
    不剔除就会把「说明怎么写链接」这件事报成断链。
    """
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"~~~.*?~~~", "", text, flags=re.S)
    # 行内代码：支持多反引号包裹（``code``），否则内部含反引号的示例会漏网
    text = re.sub(r"(`+)[^\n]*?\1", "", text)
    return text


def check_links(root: Path, targets: list[Path], scope: str, owned: set[Path]) -> None:
    """1. 断链：相对链接必须指向存在的文件。外链、锚点、代码示例跳过。

    产出物里的断链是**失败**；`--all` 扩到的其他文件里的断链只算**警告** ——
    真实仓库里别人的 Markdown 有自己的历史包袱，而 skill 自己的文档还会
    举例写链接，把它们算成失败会让「校验通过」变成不可能满足的门槛。
    """
    total = 0
    for path in targets:
        text = strip_code(path.read_text(encoding="utf-8"))
        for target in re.findall(r"(?<!!)\[[^\]]*\]\(([^)]+)\)", text):
            target = target.strip().split("#")[0]
            if not target or re.match(r"^[a-z]+://", target) or target.startswith("mailto:"):
                continue
            total += 1
            if not (path.parent / target).resolve().exists():
                if path in owned:
                    fail(f"{path.relative_to(root)}: 断链 → {target}")
                else:
                    warn(f"{path.relative_to(root)}: 断链 → {target}（非产出物，仅供参考）")
    print(f"  · 断链检查（{scope}）：{total} 个相对链接")


def artifact_files(root: Path) -> tuple[list[Path], list[Path]]:
    """产出物：术语卡与 ADR。"""
    cards = sorted((root / "glossary").glob("*.md")) if (root / "glossary").is_dir() else []
    adrs = sorted((root / "docs" / "adr").glob("*.md")) if (root / "docs" / "adr").is_dir() else []
    return cards, adrs


def check_frontmatter(root: Path, files: list[Path]) -> None:
    """2. 字段：按所在目录判断文件类型，核对必填字段与字段名合法性。"""
    cards, adrs = artifact_files(root)
    targets = [(p, True) for p in cards] + [(p, False) for p in adrs]
    for path, is_term in targets:
        rel = path.relative_to(root)
        fm = read_frontmatter(path)
        if fm is None:
            fail(f"{rel}: 缺 frontmatter")
            continue
        required = REQUIRED_TERM_FIELDS if is_term else REQUIRED_ADR_FIELDS
        missing = required - set(fm)
        if missing:
            fail(f"{rel}: frontmatter 缺必填字段 {sorted(missing)}")
        allowed = required | (set() if is_term else {"status"})
        extra = set(fm) - allowed
        if extra:
            fail(f"{rel}: 出现纯 md 消费不了的字段 {sorted(extra)}")
        if is_term:
            if fm.get("status") not in {"settled", "provisional"}:
                fail(f"{rel}: status 取值非法 '{fm.get('status')}'（应为 settled 或 provisional）")
            if not fm.get("term"):
                fail(f"{rel}: term 为空")
    print(f"  · 校验了 {len(targets)} 个产出物的 frontmatter")


def check_leftovers(root: Path, files: list[Path]) -> None:
    """3. 残留：Obsidian 专属语法不应出现在产出物或索引页里。

    只扫产出物与索引页 —— skill 自己的格式说明文件会举反例，不属于检查范围。
    """
    cards, adrs = artifact_files(root)
    targets = cards + adrs
    index = root / "CONTEXT.md"
    if index.exists():
        targets.append(index)
    patterns = [
        (r"!\[\[", "embed ![[...]]"),
        (r"\[\[", "wikilink [[...]]"),
        (r"\.base\b", ".base 文件引用"),
        (r"\bbase:query\b", "base:query 命令"),
        (r"\bobsidian\b", "obsidian 命令"),
    ]
    for path in targets:
        text = path.read_text(encoding="utf-8")
        for pattern, label in patterns:
            hit = re.search(pattern, text)
            if hit:
                line_no = text[: hit.start()].count("\n") + 1
                fail(f"{path.relative_to(root)}:{line_no}: 残留 {label}")
    print(f"  · 扫描了 {len(targets)} 个文件的 Obsidian 残留")


def check_index(root: Path, files: list[Path]) -> None:
    """4. 索引：CONTEXT.md 的清单与实际文件双向一致。"""
    index = root / "CONTEXT.md"
    if not index.exists():
        warn("CONTEXT.md 不存在 —— 只有在还没有任何术语和决策时才正常")
        return
    text = index.read_text(encoding="utf-8")
    linked = set()
    for target in re.findall(r"(?<!!)\[[^\]]*\]\(([^)]+)\)", text):
        t = target.strip().split("#")[0]
        if t.endswith(".md") and "/" in t:
            linked.add(Path(t).name)

    cards, adrs = artifact_files(root)
    for missing in sorted({p.name for p in cards} - linked):
        fail(f"CONTEXT.md: 术语卡 glossary/{missing} 未被索引")
    for missing in sorted({p.name for p in adrs} - linked):
        fail(f"CONTEXT.md: 决策 docs/adr/{missing} 未被索引")
    for extra in sorted(linked - {p.name for p in cards} - {p.name for p in adrs}):
        if extra in {"CONTEXT.md", "README.md"}:
            continue
        fail(f"CONTEXT.md: 链接指向不存在的产物 {extra}")
    print(f"  · 索引覆盖 {len(cards)} 张术语卡、{len(adrs)} 条决策")


def check_orphans(root: Path, files: list[Path]) -> None:
    """5. 孤儿卡：每张术语卡都至少被一个别的文件链接。"""
    cards, _ = artifact_files(root)
    if not cards:
        return
    incoming: dict[str, int] = {c.name: 0 for c in cards}
    for path in files:
        text = strip_code(path.read_text(encoding="utf-8"))
        for target in re.findall(r"(?<!!)\[[^\]]*\]\(([^)]+)\)", text):
            name = Path(target.strip().split("#")[0]).name
            if name in incoming and path.name != name:
                incoming[name] += 1
    for name, count in sorted(incoming.items()):
        if count == 0:
            fail(f"glossary/{name}: 孤儿卡 —— 没有任何文档链接到它")
    print(f"  · 检查了 {len(incoming)} 张术语卡的入链")


def check_pending(root: Path, files: list[Path]) -> None:
    """6. 待敲定：索引页的 provisional 清单与卡片现状一致。"""
    index = root / "CONTEXT.md"
    if not index.exists():
        return
    text = index.read_text(encoding="utf-8")
    section = re.search(r"##+\s*待敲定(.*?)(?=\n##\s|\Z)", text, re.S)
    listed = set()
    if section:
        listed = {
            Path(t.strip().split("#")[0]).name
            for t in re.findall(r"(?<!!)\[[^\]]*\]\(([^)]+)\)", section.group(1))
        }
    cards, _ = artifact_files(root)
    actual = set()
    for card in cards:
        if (read_frontmatter(card) or {}).get("status") == "provisional":
            actual.add(card.name)
    if listed != actual:
        fail(
            "CONTEXT.md: 待敲定清单与实际不符 "
            f"（多列 {sorted(listed - actual)}，漏列 {sorted(actual - listed)}）"
        )
    else:
        print(f"  · 待敲定清单一致（{len(actual)} 项）")


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    check_all = "--all" in sys.argv
    root = Path(args[0] if args else ".").resolve()
    if not root.is_dir():
        print(f"不是目录: {root}")
        return 1

    files = collect_md(root)
    owned = owned_files(root)
    print(f"校验 {root}")
    print(f"  · 仓库内 {len(files)} 个 Markdown 文件，其中 {len(owned)} 个是本 skill 的产出物")
    if not owned:
        warn("没找到任何产出物（glossary/、docs/adr/、CONTEXT.md）—— 还没开始沉淀？")

    check_links(root, files if check_all else owned,
                "全仓 --all" if check_all else "产出物，加 --all 可扫全仓",
                set(owned))
    check_frontmatter(root, files)
    check_leftovers(root, files)
    check_index(root, files)
    check_orphans(root, files)
    check_pending(root, files)

    print()
    for w in warnings:
        print(f"  ⚠ {w}")
    for f in failures:
        print(f"  ✗ {f}")
    if failures:
        print(f"\n失败 {len(failures)} 项")
        return 1
    print("全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
