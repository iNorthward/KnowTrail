---
title: 跨模块修改惯例
module: workflow
type: pattern
updated: 2026-09-19
sources:
  - .cursor/rules/agent-workflow.mdc
  - .cursor/rules/java-coding-standards.mdc
---

<!-- wiki:metadata:start -->
# 跨模块修改惯例

| 字段 | 内容 |
|---|---|
| module | workflow |
| type | pattern |
| updated | 2026-09-19 |
| sources | .cursor/rules/agent-workflow.mdc · .cursor/rules/java-coding-standards.mdc |
<!-- wiki:metadata:end -->

## 适用场景

一次改动影响两个或更多业务模块，按完整任务处理。

## 标准做法

先画清调用与数据边界，列出契约变更和调用方。公共类型放在已有契约层；构建共享产物的模块串行。

## 示例

先修改提供方契约，再同步调用方，最后验证端到端异常和回滚影响。

## 禁止事项

禁止为了复用直接引入实现模块造成循环依赖；禁止只编译一侧就宣称整个链路通过。

## 验证

对照受影响模块清单编译并验证契约；完整收尾后输出审计结果。
