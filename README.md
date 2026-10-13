# grill-with-docs-obsidian

中文版「拷问 + 沉淀文档」：不依不饶地追问一个计划或设计，把过程中敲定的**术语**和不可逆的**决策**当场写进 Obsidian 知识库（双链术语卡 + ADR + 索引页 + Bases 表）。带决策分层与授权：设计 DAG 以节点笔记形式落在 `nodes/`，图谱视图可见；ISO 四层（意图 / 架构 / 实现 / 运行）；托管策略表定谁考虑、谁提交。

上游是 [mattpocock/skills](https://github.com/mattpocock/skills) 的 `grill-with-docs`（组合 `grilling` + `domain-modeling`）。本仓库是它的 **Obsidian 变体**，**不修改、不替代**上游那两个 skill。

## 为什么要它

上游的产物是普通的 `CONTEXT.md` + `docs/adr/`，进不了 Obsidian 的图谱。改造解决三件事：

1. **概念无损** —— 术语一个概念一张卡（`glossary/<slug>.md`），落选的词和排除理由写在正文里而不是只列词表
2. **可连通** —— ADR、索引页、术语卡之间全部双链，Obsidian 的反链面板把散落各处的用法收拢到一处
3. **可查询** —— `glossary.base` / `decisions.base` / `nodes.base` 三张表，「哪些术语还没敲定」这类问题一条命令就能答

## 安装

```bash
npx skills add kwelldo/grill-with-docs-obsidian
# 或手动
git clone https://github.com/KWELLDO/grill-with-docs-obsidian
cp -r grill-with-docs-obsidian ~/.agents/skills/
```

需要 `~/.agents/skills/grill-with-docs-obsidian`（若用 npx 会自动建软链到各 harness）。

## 前置依赖

| skill | 作用 | 缺失会怎样 |
|---|---|---|
| `grilling` + `domain-modeling` | 拷问纪律、领域模型、ADR 三条件 | 必需 |
| `obsidian-cli` | `base:query` / `unresolved` / `backlinks` | 可选，退回文件读写 |
| `obsidian-bases` | `.base` 的完整 schema | 可选，本仓库自带模板 |
| `obsidian-markdown` | 双链、嵌入、frontmatter 语法 | 可选 |

官方三个：

```bash
npx skills add kepano/obsidian-skills@obsidian-cli kepano/obsidian-skills@obsidian-bases kepano/obsidian-skills@obsidian-markdown
```

还需要 **Obsidian 1.9+**（Bases 核心插件 + 官方 CLI），并把**项目仓库根目录**用「打开文件夹」当 vault。

## 产物布局

```
<项目仓库根>/
├── CONTEXT.md          索引页：按 context 分组的双链清单 + 内嵌三张 Base
├── CONTEXT-MAP.md      仅多上下文时
├── glossary/           术语卡，一个概念一个文件
├── docs/adr/           决策记录，0001-slug.md
├── glossary.base       术语总表
├── decisions.base      决策总表
├── nodes/              设计 DAG 节点，一个决策一个文件
└── nodes.base          节点总表
```

目录与文件名用英文，术语内容用中文（`glossary/order.md` 里 `term: 订单`），所以双链 `[[order]]` 稳定、跨语言可读、Base 排序不炸。

## 文件

- [`SKILL.md`](./SKILL.md) —— 主文件：拷问机制、术语纪律、ADR 纪律、CLI 接入、落盘规则
- [`TERM-FORMAT.md`](./TERM-FORMAT.md) —— 术语卡格式与 frontmatter 字段
- [`ADR-FORMAT.md`](./ADR-FORMAT.md) —— 决策记录格式与 frontmatter 字段
- [`INDEX-FORMAT.md`](./INDEX-FORMAT.md) —— 索引页、托管策略段、nodes.base 与节点笔记格式
- [`docs/对比实验与设计决策.md`](./docs/对比实验与设计决策.md) —— **改造过程 + 与原版的同题对比实验**
- [`experiment/`](./experiment/) —— 对比实验的种子、复现步骤与关键证据

## 设计上的几个硬决定

- **不存冗余字段。** 术语卡不存 `slug`（就是文件名），ADR 不存 `id`（YAML 会把 `0001` 解析成 `1`，且冗余于文件名）——`decisions.base` 用 `formula.adr_no: 'file.name.split("-")[0]'` 派生。
- **禁用词只写在正文那一行**，与理由同框：词 + 为什么排除 + 它其实指什么 + 相关卡。不另开 frontmatter 字段，因为两处可编辑就会漂移，而 Base 表格里看不到理由。
- **`aliases` 与被禁词语义相反，绝不交叉。** 把禁用词写进 `aliases` 等于把禁令注册成快捷方式。
- **`.base` 写错不报错** —— Obsidian 对未知键静默忽略，必须对着官方 schema 逐个核键名。
- **改名用 `obsidian rename`，不用 `mv`** —— 后者会静默留下断链。

## 效果对比（详见 docs/）

同一模型、同一题目、同一份回答脚本，只换 skill 文本：

| 指标 | 上游原版 | 本仓库 |
|---|---|---|
| 裁决易混词后**带排除理由**的比例 | 0 / 7 | 8 / 8 |
| 「哪些术语还没敲定」 | 答不出 | 一条命令 |
| 术语 ↔ 决策的链接 | 0 | 全连通 |
| 术语改名成本 | 1 次编辑 | 1 条命令 |

实验还发现**原版的词表会出现自相矛盾**（同一个词既用作概念又被禁用），而「一词一卡 + 互链 + 禁用词必带理由」的结构会把它挤出来。这是本改造最实质的收益。

**实验的局限也已记录**：只跑了 1 轮、回答是脚本化的，因此**上游最强的那项（多轮施压）没有被测到** —— 不能据此断言本仓库全面优于上游。

## 许可

上游 `mattpocock/skills` 的许可见其仓库。
