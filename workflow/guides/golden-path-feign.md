---
title: 跨服务调用实现惯例
module: workflow
type: pattern
updated: 2026-09-19
sources:
  - .cursor/rules/agent-workflow.mdc
  - .cursor/rules/java-coding-standards.mdc
---

<!-- wiki:metadata:start -->
# 跨服务调用实现惯例

| 字段 | 内容 |
|---|---|
| module | workflow |
| type | pattern |
| updated | 2026-09-19 |
| sources | .cursor/rules/agent-workflow.mdc · .cursor/rules/java-coding-standards.mdc |
<!-- wiki:metadata:end -->

## 适用场景

新增或修改服务间接口契约，不要求使用某个特定客户端框架。

## 标准做法

明确请求响应、鉴权传递、超时、重试与异常映射；模块依赖沿项目约定，并核对是否引入循环。幂等操作才考虑自动重试。

## 示例

先确认调用方真正需要的字段，再与提供方定义契约和错误码，分别验证两侧。

## 禁止事项

禁止直接依赖对方实现模块；禁止无条件重试非幂等写操作；禁止超时后假报成功。

## 验证

编译双方受影响模块，验证超时、鉴权失败、字段兼容及重试边界。
