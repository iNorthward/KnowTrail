---
title: 新增 Job 实现惯例
module: workflow
type: pattern
updated: 2026-09-19
sources:
  - .cursor/rules/agent-workflow.mdc
  - .cursor/rules/java-coding-standards.mdc
---

<!-- wiki:metadata:start -->
# 新增 Job 实现惯例

| 字段 | 内容 |
|---|---|
| module | workflow |
| type | pattern |
| updated | 2026-09-19 |
| sources | .cursor/rules/agent-workflow.mdc · .cursor/rules/java-coding-standards.mdc |
<!-- wiki:metadata:end -->

## 适用场景

新增定时任务处理器。修改已有处理器单点逻辑不自动升级完整任务。

## 标准做法

明确调度窗口、重跑语义、幂等键与失败出口；先估数据量，再选 SQL 聚合、窗口或按键分页。更新调度说明。

## 示例

按实际业务定义处理窗口和失败恢复；重复执行的影响有明确处置。

## 禁止事项

禁止无上界全表加载，也禁止未经估算逐主体循环查询；禁止吞异常返回成功。

## 验证

覆盖空窗口、重复执行、局部失败和恢复；核对批量上界与索引，再编译。
