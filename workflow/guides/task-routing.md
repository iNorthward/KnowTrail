---
title: 按场景选择阅读内容
module: workflow
type: guide
updated: 2026-09-19
sources:
  - AGENTS.md
  - .cursor/rules/agent-workflow.mdc
---

<!-- wiki:metadata:start -->
# 按场景选择阅读内容

| 字段 | 内容 |
|---|---|
| module | workflow |
| type | guide |
| updated | 2026-09-19 |
| sources | AGENTS.md · .cursor/rules/agent-workflow.mdc |
<!-- wiki:metadata:end -->

## 前提

先完成判档。本页供完整任务选阅读范围，规则加载仍由 AGENTS 的语义钩子和路径取并集。

## 步骤

| 场景 | 阅读 |
|---|---|
| 新增 HTTP 接口 | [golden-path-api](golden-path-api.md) |
| 新增 Job | [golden-path-job-handler](golden-path-job-handler.md) + [job-schedule](job-schedule.md) |
| MQ 消费 | [golden-path-mq-consumer](golden-path-mq-consumer.md) |
| 跨模块调用 | [golden-path-feign](golden-path-feign.md) + [cross-module-playbook](cross-module-playbook.md) |
| 结构或版本 SQL | [golden-path-version-sql](golden-path-version-sql.md) + [数据库字典](../../wiki/database/index.md) |
| 文档维护 | [wiki-doc-template](wiki-doc-template.md) |
| 完整收尾 | [change-audit-checklist](change-audit-checklist.md) |

## 示例

改已有 Job 的一个条件通常为单点，读同类代码即可；新增处理器才进入完整阅读。

## 验证

所选资料与本次行为变化直接相关。表结构同时命中 Java/Wiki/SQL/索引时全部加载，不互相替代。

## 常见问题

场景重叠时合并必要阅读；没有现成样板时先明确事实与边界，不机械生成全部交付物。
