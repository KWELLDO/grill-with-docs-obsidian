# 对比实验：如何复现

完整的实验设计、结果表与三个实质发现见 [`../docs/对比实验与设计决策.md`](../docs/对比实验与设计决策.md) 第 0 节。

## 复现步骤

1. 准备题目：任意一份术语模糊、含架构级决策的方案文档（或直接用 `SEED.md` 里的要点）。
2. 准备回答脚本：预先写好第 1 轮的回答，避免两次跑出不同的输入。
3. A 遍：只读上游 `grill-with-docs`（即 `grilling` + `domain-modeling`）的规则，产出到 `A/`。
4. B 遍：只读本仓库的 `SKILL.md` + 三份格式文件，产出到 `B/`。
5. 对比：首轮问题数与覆盖、术语裁决是否带理由、「哪些术语待敲定」能否回答、术语与决策之间有无链接、改名成本、禁用词是否自相矛盾。

> 两遍必须**同一模型、同一题目、同一份回答脚本**，只有 skill 文本不同 —— 这样隔离出的才是 skill 文本质量。

## 关键证据一：原版出现自相矛盾

A 遍的 `CONTEXT.md`（节选）：

```
**Recursion**:
The return of an expanded rationality back into the system as a usable Reflection.
_Avoid_: Reflection, retrospection, update
```

定义把 `Reflection` 当独立概念使用，禁用词又禁掉了它 —— 同一张表里既用又禁。

B 遍把「回收」和「反思」拆成两张卡后无处躲：

```markdown
**不要用来指**：反思、复盘、更新 —— 「反思」是回收**产出**的东西（见 [[reflection]]）
```

## 关键证据二：改名成本的真相

用文件工具 `mv` 改名会让所有指向旧名的双链变死链（术语卡、ADR、索引页共 4 处要改 + 3 处残留）。
实测 `obsidian rename file=degradation name=scope-narrowing` 会**自动改写全部双链**，`unresolved` 回到空。

## 关键证据三：只有 B 能回答的三个问题

| 问题 | A | B |
|---|---|---|
| 哪些术语还没敲定 | 答不出（无 status 字段） | `base:query path=glossary.base view=待敲定` |
| 哪些决策提到了「体验记录」 | 只能全文 grep，ADR 与术语表之间零链接 | `backlinks path=glossary/experiential-record.md` |
| 全库有没有死链 | 得自己写脚本 | `unresolved` |
