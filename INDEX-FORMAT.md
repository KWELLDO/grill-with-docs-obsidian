# 索引页与 Bases 格式

## 产物关系

```
<vault 根>/
├── CONTEXT.md          ← 索引页：术语清单（双链）+ 两张 Base 表内嵌
├── glossary/
│   ├── order.md
│   └── customer.md
├── glossary.base       ← 术语总表（数据源：glossary/ 下的 frontmatter）
├── docs/adr/
│   ├── 0001-event-sourced-write-model.md
│   └── 0002-*.md
└── decisions.base      ← 决策总表（数据源：docs/adr/ 下的 frontmatter）
```

两张 `.base` 的数据源就是 frontmatter —— 所以 frontmatter 字段是**必填**，不是装饰。

## `CONTEXT.md` 索引页

```md
---
type: context-index
context: main
updated: 2026-09-29
---

# 上下文索引

本项目的规范术语与已记录决策的入口。术语的唯一定义在 `glossary/`，决策的原文在 `docs/adr/` —— 这里是索引，不是定义。

## 术语

### ordering

- [[order]] 订单 —— 客户下达的、待履约的一组商品与服务
- [[customer]] 客户 —— 下单的个人或组织

### billing

- [[invoice]] 发票 —— 交付后发给客户的付款请求

## 决策

- `0001` [[0001-event-sourced-write-model|写模型采用事件溯源]]（2026-09-29）
- `0002` [[0002-manual-sql-over-orm|用裸 SQL 而不是 ORM]]（2026-09-29，proposed）

## 全部术语

![[glossary.base]]

## 全部决策

![[decisions.base]]
```

规则：

- **索引页只索引，不定义。** 一句话说明指向哪张卡/哪条 ADR，定义留给原文件。这样 `glossary/order.md` 是唯一真源，改词只改一处。
- **清单按 `context` 分组**，分组标题与 `CONTEXT-MAP.md`（多上下文）或 `main`（单上下文）一致。
- **两张 Base 内嵌在末尾**，方便一眼看全量；分组清单在上，方便顺着读。
- **每次新建术语卡或落盘 ADR 后同步本页**：`updated` 改当天日期，清单加一行。这是活页，不是开幕时写一次的东西。
- 决策行末尾的状态标注：`status` 字段存在时括注它，缺省（= accepted）就不写。

## `CONTEXT-MAP.md`（仅多上下文）

单上下文仓库**不要**这个文件 —— 有一个 `CONTEXT.md` 就够了。

**格式以 `domain-modeling` 的 `CONTEXT-FORMAT.md` 为准**（它已经完整给出 `CONTEXT-MAP.md` 的模板、单/多上下文判定、以及什么时候该问「这个话题属于哪个上下文」）。本文件不重复那份模板 —— 仓库布局、地图怎么写、上下文关系怎么描述，都是 `domain-modeling` 的领域知识，不属于 Obsidian 增强；重复一份只会造成分叉。

Obsidian 增强只在这里加这四条：

- **全仓链接**：`CONTEXT-MAP.md` 末尾挂上两张表的位置，让地图本身就是入口：

```md
## 本仓文档

- 术语总表：[[glossary.base]]
- 决策总表：[[decisions.base]]
```

- **编号全仓统一**：根 `docs/adr/` 和各上下文的 `docs/adr/` 接着同一个号往下编，不各自从 `0001` 开始。
- **术语卡只有一处**：`glossary/` 是全仓单表，上下文归属由 `context` 字段表达，**不在各上下文目录下再放一份术语卡** —— 一词两卡会让 `glossary.base` 出现重复行。
- **各上下文的 `CONTEXT.md` 是窄索引页**：格式同上，但只列该上下文的术语卡和 ADR 决策，并链接回根 `CONTEXT.md`。

## `glossary.base`

```yaml
filters:
  and:
    - file.inFolder("glossary")

properties:
  term:
    displayName: 术语
  en:
    displayName: 英文
  aliases:
    displayName: 照认的别名
  context:
    displayName: 上下文
  status:
    displayName: 状态
  related:
    displayName: 相关术语
  created:
    displayName: 建卡日期
  file.name:
    displayName: 文件

views:
  - type: table
    name: 全部术语
    order:
      - file.name
      - term
      - en
      - aliases
      - context
      - status
      - created
    groupBy:
      property: context
      direction: ASC
    summaries:
      term: Unique

  - type: table
    name: 待敲定
    order:
      - file.name
      - term
      - context
      - status
    filters:
      and:
        - 'status == "provisional"'

  - type: cards
    name: 卡片视图
    order:
      - file.name
      - term
      - en
      - related
      - context
```

## `decisions.base`

```yaml
filters:
  and:
    - file.inFolder("docs/adr")

properties:
  formula.adr_no:
    displayName: 编号
  title:
    displayName: 决策
  status:
    displayName: 状态
  date:
    displayName: 日期
  context:
    displayName: 上下文
  terms:
    displayName: 涉及术语
  file.name:
    displayName: 文件

formulas:
  adr_no: 'file.name.split("-")[0]'

views:
  - type: table
    name: 全部决策
    order:
      - formula.adr_no
      - title
      - context
      - status
      - date
      - terms
      - file.name

  - type: table
    name: 未定与已废弃
    order:
      - formula.adr_no
      - title
      - status
      - date
      - file.name
    filters:
      or:
        - 'status == "proposed"'
        - 'status == "deprecated"'
        - 'status == "superseded"'
```

## 维护规则

- **懒创建**：`glossary.base` 在第一张术语卡落盘时写，`decisions.base` 在第一条 ADR 落盘时写。
- **表永远跟得上数据**：新增的 `context` 或 `status` 取值要同步进 `groupBy` / `filters` / `summaries`，否则新值会静默落在默认分组里。
- `displayName` 用中文，`filters` / `properties` / `views` 这些**键名保持英文**（Obsidian Bases 的固定 schema）。
- **ADR 的 `status` 多数不存在**（缺省 = accepted），所以「未定与已废弃」视图靠 `status` 筛选就能把正常决策全放出去。
- **编号用 `formula.adr_no` 从文件名派生，不存字段。** YAML 会把 `id: 0001` 解析成数字 `1`（前导零丢失），而且它冗余于文件名。零填充到四位，Base 按文件名排就是编号顺序 —— **视图里不要加 `sort`**，官方 schema 没有这个键。
- **`.base` 写错不报错。** Obsidian 对未知键静默忽略：写一个 `bogusKey: 1` 进去，表照样正常渲染。所以「能渲染」不证明写对了，**必须对着 `obsidian-bases` skill 的 schema 逐个核对键名**。
- **CLI 输出的表头名不可信。** `base:query format=md` 对真实 frontmatter 属性显示**原始属性名**（`title`/`status`），自定义 `displayName` 只在 App 界面和 `formula.*` 列上体现。核数据用属性名，核表头没意义。
- **`aliases` 列只有一个用途**：一眼看出哪些词会命中哪张卡。发现同一个词出现在两张卡的 `aliases` 里，就是别名冲突 —— Base 查不出这种重复（它按行看，不按值看），靠眼睛扫这一列。
- `displayName` 用中文，`filters` / `properties` / `formulas` / `views` 这些**键名保持英文**（Obsidian Bases 的固定 schema）。完整 schema 与函数语法见 `obsidian-bases` skill。
- `.base` 依赖 Bases 核心插件。你的库若未启用（`.obsidian/core-plugins.json` 里 `"bases": true`），就只保留 `CONTEXT.md` 里的双链清单，`.base` 跳过并在收尾时说明原因。
