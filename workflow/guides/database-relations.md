---
title: 数据库关系记录约定
module: workflow
type: concept
updated: 2026-09-19
sources:
  - .cursor/rules/java-index.mdc
  - .cursor/rules/java-wiki.mdc
---

<!-- wiki:metadata:start -->
# 数据库关系记录约定

| 字段 | 内容 |
|---|---|
| module | workflow |
| type | concept |
| updated | 2026-09-19 |
| sources | .cursor/rules/java-index.mdc · .cursor/rules/java-wiki.mdc |
<!-- wiki:metadata:end -->

## 用途

说明如何记录项目实际关系，避免凭字段名推断 JOIN。本页不声明任何业务表关联。

## 核心规则

记录关联键、基数、数据归属、软删除条件和来源。字段同名不构成关系证据；没有 FK 时以实现和明确业务约定共同核对。

## 数据与流程

从相关查询与结构资料确认关系，再把结论写入实际领域专题，并链接 [数据库字典](../../wiki/database/index.md) 的对应表段落。关系变更同步调用查询。

## 边界

本体没有业务数据库。脚本只核对结构变更和文档同步，不能证明关系语义正确。

## 相关链接

[数据库字典](../../wiki/database/index.md) · [golden-path-version-sql](golden-path-version-sql.md) · [知识索引](../../wiki/index.md)
