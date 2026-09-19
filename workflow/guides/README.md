---
title: 工作流阅读指南
module: workflow
type: guide
updated: 2026-09-19
sources:
  - AGENTS.md
  - workflow/README.md
---

<!-- wiki:metadata:start -->
# 工作流阅读指南

| 字段 | 内容 |
|---|---|
| module | workflow |
| type | guide |
| updated | 2026-09-19 |
| sources | AGENTS.md · workflow/README.md |
<!-- wiki:metadata:end -->

## 前提

这些文件说明 Agent 如何推进任务，不记录使用者的业务事实，因此归工作流而非业务 Wiki。

## 步骤

| 需要了解 | 阅读 |
|---|---|
| 开任务读什么 | [最小阅读集](agent-essentials.md)、[场景路由](task-routing.md) |
| 不同改动如何核查 | golden-path 系列与 [跨模块说明](cross-module-playbook.md) |
| 如何收尾 | [审计说明](change-audit-checklist.md)、[跨会话记录](agent-session-handoff.md) |
| Wiki 怎么写 | [文档模板](wiki-doc-template.md) |
| 哪些规则由使用者决定 | [规则边界](rule-boundaries.md)、[项目上下文](java-project-context.md) |
| Agent 如何执行接入 | [接入执行指南](project-adoption.md) |
| Agent 如何补充项目资料 | [项目补充规程](../project-setup.md) |
| 本体目录为何这样分 | [目录边界](project-structure.md) |

## 示例

新增 API 时按路由读接口核查说明和项目同类代码，不要求把本目录所有文件读一遍。说明中的核查问题不等于替项目选定框架与编码方式。

## 验证

规则以 MDC 与使用者填写的项目约定为准。引用路径必须存在；文档的元数据和可见信息由 wiki_metadata.py 同步。

## 常见问题

系统知识放哪里？实际鉴权、配置和基础设施机制放 wiki/system；具体业务放该业务模块。本目录只说明工作步骤，不替业务模块填写答案。

门禁脚本的保留依据与能力边界见 [门禁脚本保留与取舍](gate-review.md)。
