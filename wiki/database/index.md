---
title: 数据库字典
module: database
type: database
updated: 2026-09-19
sources:
  - .cursor/rules/java-wiki.mdc
  - workflow/scripts/sql/lint-schema-wiki.py
---

<!-- wiki:metadata:start -->
# 数据库字典

| 字段 | 内容 |
|---|---|
| module | database |
| type | database |
| updated | 2026-09-19 |
| sources | .cursor/rules/java-wiki.mdc · workflow/scripts/sql/lint-schema-wiki.py |
<!-- wiki:metadata:end -->

## 用途

保存实际项目的表字段、索引和结构来源。本体没有业务表，当前无表条目。

## 维护规则

每张表使用二级标题，格式为 ``## `逻辑库.表名` ``。段落记录字段/索引与来源；结构变更同步对应段落。关联语义见 [关系记录说明](../../workflow/guides/database-relations.md)。

## 表结构

暂无。只有获得真实结构证据后才新增表段落。
