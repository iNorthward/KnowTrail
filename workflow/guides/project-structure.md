---
title: 工作流与 Wiki 的目录边界
module: workflow
type: decision
updated: 2026-09-19
sources:
  - AGENTS.md
  - README.md
  - workflow/README.md
  - wiki/templates/schema.json
---

<!-- wiki:metadata:start -->
# 工作流与 Wiki 的目录边界

| 字段 | 内容 |
|---|---|
| module | workflow |
| type | decision |
| updated | 2026-09-19 |
| sources | AGENTS.md · README.md · workflow/README.md · wiki/templates/schema.json |
<!-- wiki:metadata:end -->

## 背景

项目需要把规则执行和知识维护分别表达清楚，入口、目录和文档都必须能相互对应。

## 约束

按工作流与 Wiki 划分职责；MDC 可直接阅读；Wiki 遵守模板；HTML 是附带视图。接入时由 Agent 按执行指南处理已有规则冲突。

## 方案比较

按工作流和 Wiki 两个职责组织文件，统一入口与权威来源。项目自定义规则通过分层追加，避免在多个目录重复维护同一约定。

## 决策

采用 workflow/ 保存步骤、检查与交付模板，wiki/ 按实际业务模块保存知识，每个模块保留 README。根 AGENTS 编排 .cursor/rules 的内核和领域规则。HTML 放 workflow/dashboard。工作流阅读说明归 workflow/guides，wiki/system 仅放实际系统知识。公共 Wiki 类型与专用例外集中在 schema.json。

## 影响与验收

全仓引用统一；不存在额外命令流程和多套 Agent 入口；Wiki 格式检查全部通过；页面反映真实文件。接入时检查目标项目的规则冲突及引用完整性。
