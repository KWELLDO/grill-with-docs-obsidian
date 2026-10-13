# 中文命名对照表

本表把 SKILL.md 中约定为英文的文件名、文件夹名与固定小节名，映射为中文命名（frontmatter 字段名与取值保持英文）。它是对照表，不是定义表；术语的定义仍在 `glossary/` 的卡片里。用户若用中文沟通，按本表命名文件与文件夹，frontmatter 字段名保持英文。

## 表一 · 索引页与目录

| 英文 | 中文 |
|---|---|
| CONTEXT.md | 术语.md |
| CONTEXT-MAP.md | 术语地图.md |
| glossary/ | 术语/ |
| nodes/ | 节点/ |
| docs/adr/ | 决策记录/ |

> 注：目录改名后（如 `nodes/` → `节点/`），对应 `.base` 里的 `file.inFolder("<旧名>")` 必须改成新名，否则筛选失效。

## 表二 · base 文件与视图

| 英文 | 中文 |
|---|---|
| glossary.base | 术语.base |
| decisions.base | 决策.base |
| nodes.base | 节点.base |
| 视图 前沿候选 | 前沿候选 |
| 视图 待你拍板 | 待你拍板 |
| 视图 全部术语 / 待敲定 / 卡片视图 | 原样（已是中文，不改） |
| 视图 全部决策 / 未定与已废弃 | 原样 |

## 表三 · frontmatter 值（保持英文）

`type / context / updated / term / en / status / created / title / date / layer / gate / commit / state` 的**字段名与取值都保持英文**：`settled` / `provisional` / `open` / `dropped` / `main` / `and` / `or` / `人` / `AI`。原因：这些值被三个 `.base` 的 filter 消费（如 `state == "open"`、`status == "provisional"`、`file.inFolder("nodes")`），翻译后视图立刻失效。中文只用于 `displayName`、清单展示与正文。`人` / `AI` 是 `commit` 的取值，本来就是中文，保持不变。

## 表四 · 固定小节名

| 英文 | 中文 |
|---|---|
| 前置 | 前置（原样） |
| 结论 | 结论（原样） |
| 修改入口 | 修改入口（原样） |
| 相关 | 相关（原样） |

（表一、二的中文列是有实际用途的命名；表三提醒值保持英文；表四列出是提醒这些小节名本来就该用中文。）
