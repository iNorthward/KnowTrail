---
title: MQ 消费实现惯例
module: workflow
type: pattern
updated: 2026-09-19
sources:
  - .cursor/rules/agent-workflow.mdc
  - .cursor/rules/java-coding-standards.mdc
---

<!-- wiki:metadata:start -->
# MQ 消费实现惯例

| 字段 | 内容 |
|---|---|
| module | workflow |
| type | pattern |
| updated | 2026-09-19 |
| sources | .cursor/rules/agent-workflow.mdc · .cursor/rules/java-coding-standards.mdc |
<!-- wiki:metadata:end -->

## 适用场景

新增消费者或改变消息处理契约。

## 标准做法

说明消息格式、版本、幂等键、确认时机、重试和失败归宿。外部操作与本地事务分开评估，记录可恢复状态。

## 示例

同一业务事件重复到达时根据业务幂等键识别；只有处理完成后才确认消息。

## 禁止事项

禁止默认消息只投递一次；禁止吞掉失败让消息丢失；禁止在日志暴露敏感载荷。

## 验证

验证重复、乱序、失败重试和无效消息，确认既有消费者契约不被破坏。
