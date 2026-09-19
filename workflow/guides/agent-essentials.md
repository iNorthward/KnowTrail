---
title: 完整任务最小阅读集
module: workflow
type: guide
updated: 2026-09-19
sources:
  - AGENTS.md
  - workflow/task-start.md
---

<!-- wiki:metadata:start -->
# 完整任务最小阅读集

| 字段 | 内容 |
|---|---|
| module | workflow |
| type | guide |
| updated | 2026-09-19 |
| sources | AGENTS.md · workflow/task-start.md |
<!-- wiki:metadata:end -->

## 前提

已读 AGENTS 与内核并判断为完整任务。轻量不读本页；单点只读直接相关的同类实现。

## 步骤

先查看相关 handoff，再读 [task-routing](task-routing.md)。按场景选 1～3 篇说明及目标代码；动表结构才读对应表段落，动查询才核查相关索引。记录依据后实现，范围扩大补读新规则。

## 示例

新增 HTTP 接口：读取 [golden-path-api](golden-path-api.md) 和一组同类 Controller/Service/DTO；无需扫描所有 Job 和 MQ 文档。

## 验证

能说明交付物、计划路径、命中规则、同类实现与检查方式。未知事实单独记录，不能把“已读索引”当理解业务。

## 常见问题

没有 handoff 时不凭空继承别的任务；没有相关专题时从源码取证，确有新主题再写 Wiki。
