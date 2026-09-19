---
title: 跨会话记录
module: workflow
type: guide
updated: 2026-09-19
sources:
  - workflow/templates/handoff.md
  - workflow/task-start.md
---

<!-- wiki:metadata:start -->
# 跨会话记录

| 字段 | 内容 |
|---|---|
| module | workflow |
| type | guide |
| updated | 2026-09-19 |
| sources | workflow/templates/handoff.md · workflow/task-start.md |
<!-- wiki:metadata:end -->

## 前提

仅完整且预计跨多轮的任务维护记录；日常单点不为形式创建。

## 步骤

使用 workflow/templates/handoff.md，在 wiki/.agent/ 记录目标、范围、已完成、证据、未决事实和下一步。恢复时先核对实际 Git 状态，再续写。结束更新状态。

## 示例

记录“Wiki 格式检查已通过；待验证页面弹窗”，并附具体文件与命令，而非“已完成大部分”。

## 验证

下一次会话能从记录定位事实与待办；状态和代码一致，不包含凭据或无关聊天全文。

## 常见问题

多个未完成任务不能盲目合并；先匹配本次目标，过期记录标明状态再继续。
