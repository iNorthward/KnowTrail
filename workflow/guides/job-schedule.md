---
title: 调度记录维护
module: workflow
type: guide
updated: 2026-09-19
sources:
  - .cursor/rules/java-coding-standards.mdc
  - .cursor/rules/java-wiki.mdc
---

<!-- wiki:metadata:start -->
# 调度记录维护

| 字段 | 内容 |
|---|---|
| module | workflow |
| type | guide |
| updated | 2026-09-19 |
| sources | .cursor/rules/java-coding-standards.mdc · .cursor/rules/java-wiki.mdc |
<!-- wiki:metadata:end -->

## 前提

实际项目存在调度任务，且调度窗口或处理行为发生变化。此处只定义记录方式，不预填任务清单。

## 步骤

在对应项目专题登记处理器、触发方式、时区、窗口、参数、重跑和失败恢复，并引用源码或配置。修改任务时同步这些记录。

## 示例

记录格式：处理器路径 / 调度表达式或触发来源 / 窗口含义 / 幂等键 / 失败恢复 / 核验日期。没有实际值时说明未知，不填演示任务。

## 验证

对照真实调度配置与处理器确认时间窗口、重试语义和参数一致。

## 常见问题

修改已有处理器不一定需要新增专题；更新已有记录即可。调度平台名称由实际项目决定。
