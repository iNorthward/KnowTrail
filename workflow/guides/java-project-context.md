---
title: 确认 Java 项目上下文
module: workflow
type: guide
updated: 2026-09-19
sources:
  - .cursor/rules/java-coding-standards.mdc
  - workflow/config.json
---

<!-- wiki:metadata:start -->
# 确认 Java 项目上下文

| 字段 | 内容 |
|---|---|
| module | workflow |
| type | guide |
| updated | 2026-09-19 |
| sources | .cursor/rules/java-coding-standards.mdc · workflow/config.json |
<!-- wiki:metadata:end -->

## 前提

要在实际 Java 工程工作时，需要了解其构建、分层和领域约定。按 [项目补充规程](../project-setup.md) 取证，不预填项目约定。

## 步骤

读取 POM 与构建入口；找到同类 API、Service、持久化和测试；确认鉴权、异常、配置读取和数据归属。区分源码事实与已生效约定；仅将已有明确约定或经使用者确认的规则整理到权威位置。不要因局部实现稳定就自动写入 custom。

## 示例

例如项目采用某种持久化工具时，沿已有实现核对参数、事务和查询行为；不因工作流引入而更换其实现方式。

## 验证

项目约定应有生效文档或明确决策，源码观察单独标识。构建是否执行及结果分别记录，不把未验证写成通过。

## 常见问题

没有源码依据的包名、表名、鉴权注解保留未知；不要从通用模板推断业务事实。
