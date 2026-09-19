---
title: 版本 SQL 交付惯例
module: workflow
type: pattern
updated: 2026-09-19
sources:
  - .cursor/rules/java-version-delivery.mdc
  - workflow/templates/version-sql.md
---

<!-- wiki:metadata:start -->
# 版本 SQL 交付惯例

| 字段 | 内容 |
|---|---|
| module | workflow |
| type | pattern |
| updated | 2026-09-19 |
| sources | .cursor/rules/java-version-delivery.mdc · workflow/templates/version-sql.md |
<!-- wiki:metadata:end -->

## 适用场景

实际工程启用 version-sql 约定且本次有 SQL 变更；不用于强迫替换已有迁移工具。

## 标准做法

读取 workflow/templates/version-sql.md。明确目标版本，提供正向与回滚；旧版本冻结。结构变更同步对应数据库段落，索引说明支撑的查询谓词。

## 示例

功能分支通过 WORKFLOW_TARGET_VERSION 明确目标版本；DDL 只写文件，数据库执行是另外的授权动作。

## 禁止事项

禁止推断最大目录为目标版本；禁止动态 SQL 绕过检查；禁止为不存在的数据库生成授权。

## 验证

运行版本、冻结、结构 Wiki 检查；人工审查回滚顺序、数据影响与字段内容。
