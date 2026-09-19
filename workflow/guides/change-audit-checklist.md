---
title: 完整任务变更审计
module: workflow
type: pattern
updated: 2026-09-19
sources:
  - workflow/scripts/finish-audit.sh
  - workflow/templates/change-audit.md
  - workflow/templates/delivery.md
---

<!-- wiki:metadata:start -->
# 完整任务变更审计

| 字段 | 内容 |
|---|---|
| module | workflow |
| type | pattern |
| updated | 2026-09-19 |
| sources | workflow/scripts/finish-audit.sh · workflow/templates/change-audit.md · workflow/templates/delivery.md |
<!-- wiki:metadata:end -->

## 适用场景

完整任务结束或明确要求审查分支时使用。单点和轻量按内核收尾表，不套长报告。

## 标准做法

先确定工作区或提交基线范围，执行完整收尾。根据实际 diff 和必要上下文检查代码行为、数据范围、鉴权、幂等、查询规模与必要测试。TAGS 是识别线索，不是核查开关；缺少标签时仍按实际行为加载规则。在审计模板中记录行为、适用规则、阅读依据与结论，完成 SEMANTIC_REVIEW 对应的 Agent 核查。失败先修复，再填写 workflow/templates/change-audit.md；P0/P1 清零后使用 delivery.md。

## 示例

文档变更记录模板与引用检查通过、Java 编译不适用；实际 Java 变更必须给出受影响模块和构建证据。

## 禁止事项

禁止把未执行、工具不可用或空改动范围写成通过；禁止让自动标签替代业务评审；禁止在 P0/P1 未清时宣称完成。

## 验证

每项结论有命令、范围或源码依据；明确区分错误、提示和未验证项。审计后新修改涉及检查范围时重新执行相应验证。
