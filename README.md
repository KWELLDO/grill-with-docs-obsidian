# grill-with-docs-md

中文版「拷问 + 沉淀文档」的**纯 Markdown 实现**：不依不饶地追问一个计划或设计，把过程中敲定的**术语**和不可逆的**决策**当场写进仓库（术语卡 + ADR + 索引页 + 校验脚本）。

**不依赖 Obsidian、不依赖 Bases、不依赖任何 CLI。** 产物是普通 Markdown，GitHub、任何编辑器、任何静态站点生成器、任何 `grep` 都能用。

这是 `grill-with-docs-obsidian`（本仓库 `main` 分支）的**解耦版**。两者共享同一套拷问纪律与术语纪律，差别只在一件事：**术语与决策如何被发现和查询**。

| | `main`（Obsidian 版） | 本分支（纯 md 版） |
|---|---|---|
| 链接 | `[[双链]]` | 相对 Markdown 链接 |
| 查询 | Bases 表（`.base`） | 索引页 + `grep` |
| 断链检测 | `obsidian unresolved` | `tools/validate.py` |
| 反链 | `obsidian backlinks` | 孤儿卡检测（脚本） |
| 改名 | `obsidian rename` 自动改写双链 | `git mv` + 跑校验 + 手工修断链 |
| 别名 | `aliases` frontmatter（原生生效） | 不设该字段，同义说法写进正文 |
| 需要什么 | Obsidian 1.9+ 及其 CLI | 只要一个 Git 仓库 |

上游是 [mattpocock/skills](https://github.com/mattpocock/skills) 的 `grill-with-docs`（组合 `grilling` + `domain-modeling`）。本仓库**不修改、不替代**上游那两个 skill。

## 什么被摘掉了，什么留下了

**摘掉的只有「发现与查询」那一层**：双链、Bases 表、CLI 命令、`aliases` 字段。

**概念保全机制原样保留** —— 它从来不是 Obsidian 带来的：

- 术语一个概念一张卡（`glossary/<slug>.md`）
- 落选的词和**排除理由**写在正文同一行（词 + 为什么排除 + 它其实指什么 + 指向它的链接）
- ADR 三条门槛（难以逆转 / 脱离上下文反常 / 真实权衡）
- 索引页只索引不定义，术语卡是唯一真源

这套结构最实质的收益 —— 把「同一个词既当概念又当禁用词」这类自相矛盾挤出来 —— 在纯 md 下完全成立。

## 安装

```bash
git clone -b plain-md https://github.com/KWELLDO/grill-with-docs-obsidian
cp -r grill-with-docs-obsidian ~/.agents/skills/grill-with-docs-md
```

需要 `~/.agents/skills/grill-with-docs-md`（目录名与 `SKILL.md` 里的 `name` 一致）。

## 前置依赖

| skill | 作用 | 缺失会怎样 |
|---|---|---|
| `grilling` + `domain-modeling` | 拷问纪律、领域模型、ADR 三条件 | 必需 |
| 其他 | —— | **无**。不需要 Obsidian，不需要任何 CLI |

## 产物布局

```
<仓库根>/
├── CONTEXT.md          索引页：术语清单 + 决策清单 + 待敲定项，全部相对链接
├── glossary/           术语卡，一个概念一个文件
├── docs/adr/           决策记录，0001-slug.md
└── tools/validate.py   校验脚本
```

目录与文件名用英文，术语内容用中文（`glossary/order.md` 里 `term: 订单`），所以链接稳定、跨语言可读、目录排序不炸。

## 校验

```bash
python3 tools/validate.py            # 校验产出物
python3 tools/validate.py --all      # 断链检查扩展到全仓所有 Markdown
bash tools/selftest.sh               # 校验脚本自己的自测
```

`validate.py` 是 Obsidian 版三件能力的替代品：

| Obsidian 版 | 纯 md 替代 | 检查项 |
|---|---|---|
| `unresolved` | 断链检查 | 1 |
| `backlinks` | 孤儿卡检测 | 5 |
| `base:query` 过滤待敲定 | 索引页 `待敲定` 小节与 `status` 一致性 | 6 |

它只查**本 skill 拥有的文件**（`glossary/`、`docs/adr/`、`CONTEXT.md`）。真实仓库里别的 Markdown 有自己的历史包袱，把它们的断链算进来会让「校验通过」变成不可能满足的门槛 —— 想全扫用 `--all`（非产出物的断链只报警告）。

代码块与行内代码里的链接一律跳过，因为文档里举例写链接不是真链接。

`selftest.sh` 会建一份干净 fixture、确认基线通过，再逐项注入 12 类错误（断链、多余字段、缺必填、`status` 非法、`[[双链]]` 残留、孤儿卡、索引漏列、待敲定不一致……）并确认每一类都被抓到。**脚本本身不可信的话，它报的「通过」也不可信**，所以这一步是必须的。

开发这套脚本时它立刻抓到了三个真实 bug：ADR 模板里的相对路径 `../glossary/order.md` 从 `docs/adr/` 出发只到 `docs/glossary/`（正确是 `../../glossary/order.md`）；一处崩溃（`is_adr` 变量残留）；以及代码块/行内代码里的示例链接被误报成断链（现已有回归用例）。

## 文件

- [`SKILL.md`](./SKILL.md) —— 主文件：拷问机制、术语纪律、ADR 纪律、纯 md 落盘规则、收尾清单
- [`TERM-FORMAT.md`](./TERM-FORMAT.md) —— 术语卡格式与 frontmatter 字段
- [`ADR-FORMAT.md`](./ADR-FORMAT.md) —— 决策记录格式与 frontmatter 字段
- [`INDEX-FORMAT.md`](./INDEX-FORMAT.md) —— 索引页格式与校验脚本说明
- [`tools/validate.py`](./tools/validate.py) · [`tools/selftest.sh`](./tools/selftest.sh) —— 校验与自测
- [`docs/对比实验与设计决策.md`](./docs/对比实验与设计决策.md) —— 与原版的同题对比实验与设计决策
- [`docs/纯md解耦说明.md`](./docs/纯md解耦说明.md) —— 本分支摘掉了什么、为什么
- [`experiment/`](./experiment/) —— 对比实验的种子、复现步骤与关键证据

## 设计上的几个硬决定

- **不存冗余字段。** 术语卡不存 `slug`（就是文件名），ADR 不存 `id`（YAML 会把 `0001` 解析成 `1`，且冗余于文件名）。
- **不设 `aliases` 字段。** 纯 md 没有别名索引器会消费它；同义说法写进正文，让读到卡的人看到。
- **关系不存 frontmatter。** `related` / `terms` 在纯 md 里只是没人读的字符串，改用正文的相对链接 —— 在 GitHub 上能直接点，校验脚本也能顺着查。
- **禁用词只写在正文那一行**，与理由同框。两处可编辑就会漂移。
- **改名必须 `git mv` + 跑校验**，纯 md 没有工具替你改写引用。

## 许可

上游 `mattpocock/skills` 的许可见其仓库。
