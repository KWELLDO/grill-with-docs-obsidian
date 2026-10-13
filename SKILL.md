---
name: grill-with-docs-obsidian
description: 中文版「拷问 + 沉淀文档」：不依不饶地追问一个计划或设计，把过程中敲定的术语和不可逆的决策当场写进 Obsidian 知识库（双链术语卡 + ADR + 索引页 + Bases 表，可用则走官方 obsidian CLI 校验）。带决策分层与授权：讨论被映射成设计 DAG（每个决策落成 `nodes/` 里的一张笔记，图谱视图可见），按 ISO 四层切托管策略（谁考虑、谁提交），AI 在自己被授权的层里直接处理，只把该人拍的抛给人；每个可介入点铺标记，用户可按需下探、按需生成适配自己心智模型的修改入口。Use when the user wants to stress-test / grill / 拷问 / 追问 / 压力测试 一个想法、方案或设计，并希望在过程中无损沉淀术语与决策。Obsidian 变体，配套 grilling、domain-modeling、obsidian-cli/bases/markdown 使用，不修改这些 skill。
disable-model-invocation: true
---

# 拷问并沉淀文档

用 Obsidian 承载「拷问」的产物。两条纪律同时进行：**每一个决策都问到底**，**每一个术语和决策当场写进库里**。本版本的决策结构（设计 DAG）落在 `nodes/`，每个决策是一张笔记，图谱视图里可见、可点开。

本 skill 是 `grilling` + `domain-modeling` 的 **Obsidian 变体**：这两个 skill 的行为已在此中文重写并加强，**不修改它们**。不属于 Obsidian 增强的领域知识（仓库布局、`CONTEXT-MAP.md` 格式、上下文关系）以 `domain-modeling` 的 `CONTEXT-FORMAT.md` 为准。

## 术语（本文内部用语）

- **拷问**：下面的提问循环。
- **设计 DAG**：一次讨论的完整决策结构。节点是决策，边是依赖。
- **节点**：`nodes/<slug>.md`，一张决策笔记。
- **边方向**：节点 B 的 `## 前置` 段里双链 A，表示 A 是 B 的前置；因此图谱箭头从 B 指向 A。
- **前置**：本节点 `## 前置` 里的出链。
- **后继**：指向本节点的入链（backlinks），即哪些节点把本节点列为前置。
- **考虑（compute）**：求值。只读、可重跑、可并行、错了重来无代价。类比 `git diff`、`terraform plan`、`EXPLAIN`。
- **提交（commit）**：拍板。写状态、有副作用、难回退、别人开始依赖它。类比 `git commit`、`terraform apply`、部署。
- **前沿（frontier）**：`state` 为 open、且就绪（门的条件满足）的节点集合。一轮 = 处理完整个前沿。
- **已决**：节点 `state: settled`。
- **已弃**：节点 `state: dropped`。
- **深度**：DAG 最长路径上的节点数。
- **下探**：沿后继走一层（找出依赖当前节点的节点）。
- **事实**：环境中能查到的东西（文件、代码、配置、依赖版本）。事实不进托管判定，AI 能自己查的自己查。
- **托管策略表**：`层 → (谁考虑, 谁提交)` 的映射。初始化时由用户冻结。
- **心智模型**：用户看得懂的介入形式（项目经理 / 初级开发 / 资深开发）。
- **路径生成**：真要改时，在节点笔记里生成修改入口。
- **介入标记**：表示「此处可介入」的记号（节点笔记 + 轮次里的 🔧 / ❓）。全层铺满。
- **介入路径**：用户真要改时生成的修改入口，写在节点笔记的 `## 修改入口` 段。按需生成。
- **校准**：按领域的用户测评动态调整托管策略表。AI 不自评。
- **术语**：本项目中一个概念的名字及其精确定义。
- **上下文（context）**：一个限界子域，一套术语在其中才成立。

---

## 零、开工前：定位库与初始化

### 0.1 定位库

1. 确认 vault 根：仓库根目录（用户会用 Obsidian「打开文件夹」）。若已存在 `CONTEXT.md` 则是索引页，已存在 `CONTEXT-MAP.md` 则是多上下文。
2. **把已有产物读全了再开口。** 读法按 Base 走 —— Base 的行就是这些文件，读它们等价于读表：
   - **CLI 可用时**：`obsidian vault=$V base:query path=glossary.base view=全部术语 format=md` 与 `path=decisions.base view=全部决策 format=md` 各跑一次，拿到的就是全量数据；再 `obsidian vault=$V unresolved` 确认库本身没有遗留死链。
   - **CLI 不可用时**：读 `glossary/*.md` 与 `docs/adr/*.md` 的 frontmatter 和正文（数据完全相同），并读 `glossary.base` / `decisions.base` 拿字段定义（顺便确认表的结构与设想一致）。
   - **`nodes/*.md`**：已有决策节点（frontmatter 的 `state`、`gate`，正文的 `## 前置` / `## 修改入口`）。CLI 可用时前沿候选一眼看全：`obsidian vault=$V base:query path=nodes.base view=前沿候选 format=md`。
   - `CONTEXT.md`：分组清单、三张表的概览，以及**托管策略段**。
   - 库里的**其他笔记**（日记、会议记录、需求文档）同样在读的范围：用户此前对这个项目的思考散在那里，先捞一遍，免得把已经定过的结论重新问一遍。
   - **设计文档**：记下它的章节清单，供会话结束前的覆盖检查用（见第二节）。
3. **带着已有词进入拷问。** 已有的术语不重新发明，已记录的决策不重新讨论；两者若与用户此刻的说法冲突，把冲突摆出来问，而不是默默采信新说法。
4. 目录按需懒创建，**没有内容就不建**：

```
<vault 根>/
├── CONTEXT.md              ← 索引页（人读清单 + 嵌入三张 Base 表 + 托管策略段）
├── CONTEXT-MAP.md          ← 仅多上下文时
├── glossary/               ← 术语卡，一个概念一个文件
├── nodes/                  ← 决策节点，一个决策一张笔记
├── docs/adr/               ← 决策记录，0001-slug.md 顺序编号
├── glossary.base           ← 术语总表
├── nodes.base              ← 节点总表
└── decisions.base          ← 决策总表
```

目录**英语**，文件**英语**，但**术语本身用中文**（`glossary/order.md` 里 `term: 订单`），所以双链 `[[order]]` 稳定、概念无损。

### 0.2 初始化：冻结托管策略

抽象在开工时冻结一次，之后只在触发重新校准时改。

1. **问心智模型**（三选一）：项目经理 / 初级开发 / 资深开发。用于生成适配的介入路径（见第五节）。
2. **呈现默认托管策略表**：

| 层 | 谁考虑 | 谁提交 | 路径生成 |
|---|---|---|---|
| 意图 | 人 | 人 | 低 |
| 架构 | AI | 人 | 高 |
| 实现 | AI | AI | 中 |
| 运行 | AI | AI | 低 |

用户可在初始化时改任意格。意图层人可请 AI 协助，但考虑与提交归人。
3. **写入 `CONTEXT.md` 的托管策略段并冻结**。格式见 [INDEX-FORMAT.md](./INDEX-FORMAT.md)。`CONTEXT.md` 是**唯一不等内容就建的文件**（它是索引页/活页，托管策略表要落在上面）。

### 0.3 既有资产

初始化时一并处理既有资产，默认值在初始化时呈现给人确认：

- **`CONTEXT.md` 已存在且不是索引页**（散文或已有定义区）：在顶部插入 frontmatter 与托管策略段，原内容保留。已有定义区（如 `## Language`）视为既有定义，不迁移为卡片；新术语写进 `glossary/`。
- **既有 ADR 没有 frontmatter**：补最小 frontmatter（`title`、`date`、`context`）。`date` 用文件首次入库日期：`git log --follow --diff-filter=A --format=%as -- <文件>`。正文不动。
- **既有术语没有卡片**：默认不迁移，除非人指定。
- **既有决策日志（如 `DECISIONS.md`）**：不纳入技能，除非人指定。
- 以上默认值写进初始化的呈现内容。

## 〇·一、Obsidian CLI：能用就用

**先探测**：`obsidian vaults` 能列出 vault 名 = CLI 可用（需 Obsidian 正在运行）。报错或空输出 = 不可用，**本节全部命令跳过**，改用普通文件读写，并告知用户「CLI 不可用，本次用文件方式落盘」。下文 `$V` = 目标 vault 名。

官方 CLI 能力、`file` 与 `path` 的区别、插件/主题开发命令见 `obsidian-cli` skill；`.base` 的 schema 与函数语法见 `obsidian-bases` skill；双链、嵌入、frontmatter 属性语法见 `obsidian-markdown` skill。**这三个 skill 是本 skill 的上位参考，格式细则以它们为准。**

| 动作 | 命令 |
|---|---|
| 读术语总表 | `obsidian vault=$V base:query path=glossary.base view=全部术语 format=md` |
| 读待敲定术语 | `obsidian vault=$V base:query path=glossary.base view=待敲定 format=md` |
| 读决策总表 | `obsidian vault=$V base:query path=decisions.base view=全部决策 format=md` |
| 看前沿候选 | `obsidian vault=$V base:query path=nodes.base view=前沿候选 format=md` |
| 改节点状态 | `obsidian vault=$V property:set name=state value=settled path=nodes/<slug>.md` |
| 找后继（谁依赖我） | `obsidian vault=$V backlinks path=nodes/<slug>.md` |
| **全库死链（收尾硬门槛）** | `obsidian vault=$V unresolved` |
| 某张卡的来源 | `obsidian vault=$V backlinks path=glossary/order.md counts` |
| 别名注册情况 | `obsidian vault=$V aliases verbose` |
| 孤立笔记 / 无出链笔记 | `obsidian vault=$V orphans` / `deadends`（代码仓库里整库都会被算作孤儿，此命令不可用于代码仓库，只在纯笔记库里用） |
| 读改 frontmatter | `obsidian vault=$V property:read name=status path=...` / `property:set name=status value=deprecated` |
| 搜库 | `obsidian vault=$V search:context query="订单" path=glossary` |
| **术语改名（连双链）** | `obsidian vault=$V rename file=<旧slug> name=<新slug>` |

**读和验证走 CLI，写走文件工具。** 分工不是偏好：CLI 强在拿到 Obsidian 自己的图谱视角（`base:query` 是真按 Base 过滤渲染，文件系统视角拿不到；`unresolved` 是权威死链清单）；而 `create content=` / `append content=` 传多行 YAML 要转义换行和缩进，极易被 shell 吃掉。建卡、改 frontmatter、改名用文件工具更稳。

**六个实测坑：**

1. **`base:views` 不接受 `path`** —— 它只看当前活动文件，会报 `Active file is not a base file`。要么先 `open path=glossary.base`，要么直接用 `base:query view=<名字>`。
2. **CLI 的 `format=md` 表头用原始属性名**（`title`、`status`），不套自定义 `displayName`（`formula.*` 列除外）。核数据用属性名。
3. **`base:query` 的第一列值是不带扩展名的文件名**（`order`，不是 `order.md`）—— 双链、文件名对不上时先记住这条。
4. **新写完文件，Obsidian 可能还没索引完**，此刻查 `unresolved` / `backlinks` 结果不对，先 `obsidian vault=$V reload` 再查。
5. **`reload` 之后 vault 会短暂不可用** —— Obsidian 正在重挂 socket，此刻任何命令都报 `Vault not found`（`backlinks` 会报「Command not found」）。等两三秒，或用 `obsidian vaults` 确认 vault 回来了再查。
6. **改名必须用 `obsidian rename`，不能用文件工具 `mv`。** 实测：`mv` 改名会让所有指向旧名的双链变成死链（术语卡、ADR、索引页里全是）；`obsidian rename file=<旧名> name=<新名>` 会**自动改写全部双链**。术语卡改名时（`term` 换词 → 文件名跟着换）这是唯一安全的做法。

## 一、决策分层与授权

拷问之前先把规则冻结：讨论映射成设计 DAG，每个节点过一遍托管策略表。

### 设计 DAG

- **节点** = `nodes/<slug>.md`，一张决策笔记。
- **边** = 正文 `## 前置` 段里的双链，只列**直接**前置。节点 B 的 `## 前置` 里双链 A，表示 A 是 B 的前置（图谱箭头从 B 指向 A）。
- **图谱可开箭头看方向**（图谱设置 → Display → Show arrows）：箭头从链接的笔记（B）指向被链接的笔记（A）。**AND/OR 不在图谱里** —— 门类型看节点的 `gate` 字段与 `nodes.base`。
- **运行时状态**写在 frontmatter 的 `state`（`open` / `settled` / `dropped`），用 `property:set` 更新；`nodes.base` 只做展示。
- 决策可以合并（两个前置指向同一个后继），DAG 天然支持；纯树会复制，复制会让同一个决策被算两次。

### ISO 四层

按抽象深度切，不是按阶段切：

| 层 | 回答什么 | 典型决策 |
|---|---|---|
| 意图 | 要什么 | 目标、范围、成功判据 |
| 架构 | 怎么搭 | 模块边界、集成方式、技术选型 |
| 实现 | 怎么写 | 数据结构、函数签名、错误处理 |
| 运行 | 怎么跑 | 部署、监控、运维流程 |

### 托管策略表与四种组合

**托管策略表** = `层 → (谁考虑, 谁提交)`，初始化时冻结（见 0.2）。每个节点按它归层，两格各自决定：谁考虑（compute）、谁提交（commit）。四种组合：

- **(AI, AI)**：AI 直接处理并声明。
- **(AI, 人)**：AI 推荐后问。
- **(人, 人)**：只问不推荐。
- **(人, AI)**：问后 AI 落盘。

### 例外：ADR 三条

一个节点同时满足 [ADR 三条](#四决策记录adr三条全中才写)（难逆、反常、真权衡）时，**无论在哪层，强制拉回人提交** —— 即组合里的第二格恒为「人」。一份规则，两个用途。

### 冻结后的规则

拷问循环只做一件事：每个节点过一遍托管策略表，按表决定是 AI 直接处理、AI 处理完声明、还是抛给用户。

## 二、拷问：设计 DAG + 前沿分轮

把讨论映射成设计 DAG，按**轮**推进。一轮 = 处理完整个前沿。

**前沿与就绪规则**：节点是前沿，当且仅当 `state: open` 且就绪：

- `gate: and` —— 所有前置 `settled` 才就绪。
- `gate: or` —— 任一前置 `settled` 即就绪。

前置为 `dropped` 时：`and` 节点卡住，回到用户问；`or` 节点看其余前置。落选的 OR 前置若再无其他后继依赖，标 `dropped`。

**一轮处理完整个前沿**，不是只问。前沿里混着四种节点，各有固定格式：

```
🔧 **A1** - **<事项标题>**：<一句话说明 AI 定了什么>
📌 我按 <X> 走了，有异议现在说。

---

❓ **Q1** - **<问题标题>**：<问题正文，可多段，可列多个选项>
➡️ <AI 的推荐答案>

---

❓ **Q2** - **<问题标题>**：<问题正文，可列选项与边界，不给推荐>

---

❓ **Q3** - **<问题标题>**：<问题正文，不给推荐；用户答后 AI 落盘>
```

双链指向相关节点或术语（`[[jwt]]`、`[[0002-refresh-token]]`）。

**轮推进**：本轮若有 ❓ 则停下等答案；只有 🔧 则 AI 声明后继续，直到出现 ❓ 或前沿为空。用户对某个 🔧 有异议，则该节点重开（`state` 改回 `open`）。

**每个节点先落盘为笔记。** 任何在轮次里出现的决策，先写成 `nodes/<slug>.md`（`state: open`），这就是**介入标记** —— 节点笔记本身在图谱里可见、可点开；轮次输出里另加 🔧 / ❓。状态变化用 `property:set` 维护（settled / dropped）。格式见 [INDEX-FORMAT.md](./INDEX-FORMAT.md) 的「节点笔记」段。节点的 state、标题或结论变动（含重开）后，同步 `CONTEXT.md` 的 `## 节点` 清单。

每轮回应都会重塑 DAG：已决节点把前沿向外推，解开原先被阻塞的问题。**重算前沿**再走下一轮。答案依赖本轮另一个未决问题的，归入**后续轮**，不现在问。

**事实归 AI。** 需要环境事实（文件系统、工具、依赖）时，派 sub-agent 去查，绝不问用户你能自己查到的东西。也不要在它上面干等：一个正在跑的探查就是一个未决的前置，只有它下游的问题等报告，前沿其余部分照现在处理。

会话在**前沿为空**时结束：DAG 每条分支都走过，没有东西被默认掉。**在用户确认已达成共识之前，不要动手实现。**

**会话结束前做一次覆盖检查**：列出设计文档的章节 → 决策点映射，每章节一行，标注「已开节点 / 不在本轮（写明理由）/ 外部依赖」。映射中仍有未处理的决策点时，不得以「前沿为空」结束 —— 要么开节点，要么标为不在本轮并请人确认。

## 三、术语纪律：当场落盘

术语是这次工作最贵的产物。**一个术语敲定的那个瞬间就写进 `glossary/<slug>.md`，不要攒到最后批量处理。** 格式见 [TERM-FORMAT.md](./TERM-FORMAT.md)。

过程中持续做四件事：

- **拿术语表挑战用户的用词。** 用户说出一个与 `glossary/` 已有定义冲突的词，立刻点破：「你定义的『取消』是 X，但你现在说的像是 Y。到底哪个对？」
- **把模糊、混用的词收敛成一个规范术语。**「你说的『账户』：是指 Customer 还是 User？那是两个东西。」定下后立刻建卡。
- **用具体场景压边界。** 讨论领域关系时，编边界场景逼用户把概念之间的界说清楚：「只有一条订单行时取消，和整单取消，走的是同一条流程吗？」
- **和代码对照。** 用户陈述某个机制如何运作时，去代码里核对。发现矛盾就摊开：「你的代码取消的是整张 Order，但你刚说可以部分取消。哪个是对的？」

**只收本项目特有的概念。** 通用编程概念（超时、错误类型、工具函数模式）不属于这里，即使项目里用得很多。加词前自问：这是这个上下文独有的概念，还是通用编程概念？只有前者才建卡。

## 四、决策记录（ADR）：三条全中才写

`docs/adr/`，顺序编号 `0001-slug.md`，格式见 [ADR-FORMAT.md](./ADR-FORMAT.md)。三条**全部**成立才提出来写：

1. **难以逆转** —— 事后改主意的代价是实打实的
2. **脱离上下文会显得反常** —— 未来的读者会问「为什么这么做？」
3. **真实权衡的结果** —— 确实有别的选项，你出于具体理由选了这个

缺任何一条就不写：好逆转就逆转，不反常就没人会问，没有替代方案就没有超出「我们做了显而易见的事」的东西值得记。

**什么够格**：架构形态；上下文之间的集成模式；有锁定成本的技术选择（数据库、消息总线、认证供应商、部署目标 —— 不是每个库，而是那些换起来要花一个季度的）；边界与范围决策（「客户数据归 Customer 上下文所有，其他上下文只按 ID 引用」，明确的「不」和「是」一样值钱）；刻意偏离显然路径的做法（「用裸 SQL 而不是 ORM，因为 X」—— 凡是正常读者会以为相反的地方）；代码里看不见的约束（合规、对外 API 契约）；以及**拒绝理由不明显的备选项**（否则六个月后会有人再提一次 GraphQL）。

满足三条的节点，**无论哪层，提交强制归人**，见第一节。

## 五、介入机制：标记铺满 + 路径按需

**介入是硬要求，不是可选项。** 关掉它，下探和校准同时失效 —— 用户没法测评自己不理解的东西，托管策略表就永远卡在初始值上。

**介入标记（全层铺满）**：每个在轮次中出现的决策都先落盘为 `nodes/<slug>.md`（`state: open`），节点笔记本身就是标记，在图谱里可见、可点开；轮次输出里另加 🔧 / ❓。成本 O(n)，作用是可发现性 —— 用户不知道哪里能改，就不会问。

**路径生成三档**（与托管策略同冻，写在托管策略段的「路径生成」列）：

- **高**：每轮末尾列出本轮节点的介入路径入口。
- **中**：用户点进节点时才生成。
- **低**：仅用户明确要求时生成。

标记全层都有，密度只差在路径生成。

**介入路径形式按心智模型**（初始化时已把握，直接查表）：

| 用户类型 | 介入路径形式 |
|---|---|
| 项目经理 | 一键即可看到效果 |
| 初级开发 | 几行命令即可看到效果 |
| 资深开发 | 给出不同的代码 |

生成的路径写在节点笔记的 `## 修改入口` 段，按需追加。

**下探协议**：用户对一个节点不满时，不需要接管它，而是**沿着后继走一层**，看哪些节点依赖它。走完即停。不改授权线 —— 下探是查询，不是重配置。CLI 用 `obsidian vault=$V backlinks path=nodes/<slug>.md`；纯文件方式时搜索 `nodes/` 下 `## 前置` 段里含 `[[<slug>` 的节点。

**校准**：同一子树被下探 **≥3 次**（默认值，称「反复」）说明线画错了，触发一次校准提议，而不是每次下探都动线。校准只改 `CONTEXT.md` 的托管策略段；改表若满足 ADR 三条（难逆、反常、真权衡）才写 ADR。

## 六、Obsidian 落盘规则

1. **双链术语。** ADR 正文、索引页、术语卡之间提到一个已建卡的术语时，写成 `[[order]]` 而不是「订单」。这让 Obsidian 的反向链接面板把散落各处的用法收拢到一处。
2. **frontmatter 是必填。** 术语卡和 ADR 都带 frontmatter —— 三张 `.base` 表（glossary.base、decisions.base、nodes.base）的数据源就是它。字段见格式文件。
3. **`.base` 懒创建。** `glossary.base`（第一张术语卡落盘时写）、`decisions.base`（第一条 ADR 落盘时写）、`nodes.base`（第一个节点落盘时写）—— 三者的模板都在 [INDEX-FORMAT.md](./INDEX-FORMAT.md)。它们都永远滞后于数据：每新增或改动一张卡/ADR/节点，若它引入了新的属性值（新的 `context`、新的 `status`、新的 `state`），同步更新对应 `.base` 的筛选与分组。用 Base 读、写、核对库，是这个 skill 面对 Obsidian 的默认姿势。
4. **写完 `.base` 拿 schema 核对键名。** Obsidian 对未知键静默忽略，表能渲染 ≠ 写对了。对着 `obsidian-bases` skill 的 schema 逐个核。
5. **索引页是活页。** 新术语建卡、新 ADR 落盘后，把 `CONTEXT.md` 的清单和嵌入同步 —— 见 [INDEX-FORMAT.md](./INDEX-FORMAT.md)。
6. **一切懒创建**：没有可写的东西就不建文件、不建目录。
7. **节点笔记的 frontmatter 与正文格式**见 [INDEX-FORMAT.md](./INDEX-FORMAT.md) 的「节点笔记」段。
8. **节点改名同样用 `obsidian rename`**（双链会自动改写）。
9. **节点的 state 变化用 `property:set`**，不要手改 frontmatter 的其他行。

## 七、每轮结束时的收尾清单

一轮作答落地后，逐条确认再进入下一轮：

- 本轮定下的每个术语，都已建成 `glossary/<slug>.md`（不是「待会儿一起写」）
- 本轮涉及、且满足三条条件的决策，都已落 `docs/adr/`，并已把术语双链进正文
- **本轮出现的每个决策都已落盘为 `nodes/<slug>.md`**
- **每个节点的 `state` 与 `nodes.base` 视图一致**（CLI 可用时用 `base:query` 核对）
- `CONTEXT.md` 清单、三张 `.base` 与实际文件一致
- **`CONTEXT.md` 的清单与托管策略段一致**
- **`CONTEXT.md` 内嵌 `![[glossary.base]]` / `![[nodes.base]]` / `![[decisions.base]]` 时，那些 `.base` 文件已经写好** —— 索引页先于 base 文件落盘会瞬时产生死链，顺序是 base 先、索引页后
- **CLI 可用时：`obsidian vault=$V unresolved` 返回空**。这是权威死链清单，比自己数双链可靠；刚改完文件先 `reload` 再查
- **`nodes/` 下每个非根节点的 `## 前置` 都非空，根节点写「无」**
- **`CONTEXT.md` 的 `## 节点` 清单中每个节点的 state 与标题，与节点文件一致**
- **本轮改过术语名：用 `obsidian rename` 而不是 `mv`** —— 后者会静默留下断链
- **本轮无「本该 AI 却抛给用户」的节点** —— 有的话，是托管策略表画错了，提校准
- 反向链接可用：每张新卡的「**相关**」小节里双链的目标都真实存在（`obsidian vault=$V backlinks path=<新卡> counts` 能看到来源）

**不要在用户确认达成共识之前实现任何东西。**

---

## 参考文件

- [TERM-FORMAT.md](./TERM-FORMAT.md) —— 术语卡格式与 frontmatter 字段
- [ADR-FORMAT.md](./ADR-FORMAT.md) —— ADR 格式与 frontmatter 字段
- [INDEX-FORMAT.md](./INDEX-FORMAT.md) —— `CONTEXT.md` 索引页、托管策略段、`nodes.base` 与节点笔记格式

## 上位参考（Obsidian 侧）

- `obsidian-cli` —— CLI 全部命令、`file` 与 `path` 的区别
- `obsidian-bases` —— `.base` 的完整 schema、filter 语法、函数
- `obsidian-markdown` —— 双链、嵌入、frontmatter 属性语法

这三个装不上或不可用时，本 skill 自带的内容仍足够完成全部工作（零·一节自动跳过），只是少了图谱视角的校验。
