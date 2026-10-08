#!/usr/bin/env bash
# validate.py 的自测：建一份干净 fixture，确认基线通过，再逐项注入错误，
# 确认每一类都能被抓出来。脚本本身不可信的话，它抓到的「问题」也不可信。
#
# 用法: bash tools/selftest.sh
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VALIDATE="$HERE/validate.py"
FX="$(mktemp -d)"
trap 'rm -rf "$FX"' EXIT

pass=0
fail=0

# ---------- 干净 fixture ----------
build_fixture() {
  rm -rf "$FX"; mkdir -p "$FX/glossary" "$FX/docs/adr"
  cat > "$FX/glossary/order.md" <<'EOF'
---
term: 订单
en: Order
context: ordering
status: settled
created: 2026-09-29
---

# 订单

客户下达的、待履约的一组商品与服务。

**不要用来指**：交易、单据 —— 那些是[发票](./invoice.md)。

**相关**：[客户](./customer.md)
EOF
  cat > "$FX/glossary/customer.md" <<'EOF'
---
term: 客户
en: Customer
context: ordering
status: provisional
created: 2026-09-29
---

# 客户

下单的个人或组织。
EOF
  cat > "$FX/glossary/invoice.md" <<'EOF'
---
term: 发票
en: Invoice
context: billing
status: settled
created: 2026-09-29
---

# 发票

交付后发给客户的付款请求。见[订单](./order.md)。
EOF
  cat > "$FX/docs/adr/0001-event-sourced-write-model.md" <<'EOF'
---
title: 写模型采用事件溯源
date: 2026-09-29
context: ordering
---

# 写模型采用事件溯源

涉及术语：[订单](../../glossary/order.md)
EOF
  cat > "$FX/CONTEXT.md" <<'EOF'
---
repo: fixture
updated: 2026-09-29
---

# 上下文索引

## 术语

### ordering

- [订单](./glossary/order.md) —— 待履约的一组商品与服务
- [客户](./glossary/customer.md) —— 下单的个人或组织

### billing

- [发票](./glossary/invoice.md) —— 付款请求

## 决策

- [0001 写模型采用事件溯源](./docs/adr/0001-event-sourced-write-model.md)（2026-09-29）

## 待敲定

- [客户](./glossary/customer.md) —— 边界待确认
EOF
}

expect_pass() {
  local label="$1"
  if python3 "$VALIDATE" "$FX" >/dev/null 2>&1; then
    echo "  ✓ $label"; pass=$((pass + 1))
  else
    echo "  ✗ $label —— 本该通过却失败了"; python3 "$VALIDATE" "$FX" | grep '✗' | sed 's/^/      /'
    fail=$((fail + 1))
  fi
}

expect_catch() {
  local label="$1" pattern="$2"
  local out
  out="$(python3 "$VALIDATE" "$FX" 2>&1)"
  if echo "$out" | grep -q "$pattern"; then
    echo "  ✓ $label"; pass=$((pass + 1))
  else
    echo "  ✗ $label —— 注入的错误没被抓到（grep '$pattern'）"; fail=$((fail + 1))
  fi
}

echo "validate.py 自测"
echo
echo "基线"
build_fixture
expect_pass "干净 fixture 通过全部检查"
echo
echo "注入错误，逐类求证"
build_fixture
sed -i 's|(./customer.md)|(./custmer.md)|' "$FX/glossary/order.md"
expect_catch "断链" "断链"

build_fixture
sed -i '1a slug: order' "$FX/glossary/order.md"
expect_catch "多余字段 slug" "消费不了的字段"

build_fixture
sed -i '1a aliases:\n  - 采购单' "$FX/glossary/order.md"
expect_catch "多余字段 aliases" "消费不了的字段"

build_fixture
cat > "$FX/glossary/incomplete.md" <<'EOF'
---
term: 残缺
en: Incomplete
created: 2026-09-29
---

# 残缺
EOF
expect_catch "缺必填字段 context/status" "缺必填字段"

build_fixture
sed -i 's|status: settled|status: done|' "$FX/glossary/invoice.md"
expect_catch "status 取值非法" "status 取值非法"

build_fixture
printf '\n见 [[order]]。\n' >> "$FX/glossary/invoice.md"
expect_catch "残留 wikilink" "残留 wikilink"

build_fixture
printf '\n![[order]]\n' >> "$FX/glossary/invoice.md"
expect_catch "残留 embed" "残留 embed"

build_fixture
sed -i 's|(./glossary/invoice.md)|(./glossary/invoice2.md)|' "$FX/CONTEXT.md"
expect_catch "索引指向不存在的产物" "断链"

build_fixture
cat > "$FX/glossary/ghost.md" <<'EOF'
---
term: 幽灵
en: Ghost
context: main
status: settled
created: 2026-09-29
---

# 幽灵
EOF
expect_catch "孤儿卡" "孤儿卡"

build_fixture
sed -i '/^- \[客户\](.\/glossary\/customer.md)/d' "$FX/CONTEXT.md"
expect_catch "索引漏列一张卡" "未被索引"

build_fixture
sed -i 's|^- \[客户\](.*)|- [发票](./glossary/invoice.md) —— 付款请求|' "$FX/CONTEXT.md"
expect_catch "待敲定清单与实际不符" "待敲定清单与实际不符"

build_fixture
cat >> "$FX/glossary/invoice.md" <<'EOF'

文档里举例写链接不算断链：

```md
见[订单](./nope-not-real.md)。
```

行内代码 ``[客户](./also-not-real.md)`` 同理。
EOF
expect_pass "代码块与行内代码里的示例链接不误报"

echo
echo "结果：通过 $pass，失败 $fail"
[ "$fail" -eq 0 ]
