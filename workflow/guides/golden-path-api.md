---
title: 新增 HTTP 接口实现惯例
module: workflow
type: pattern
updated: 2026-09-19
sources:
  - .cursor/rules/agent-workflow.mdc
  - .cursor/rules/java-coding-standards.mdc
---

<!-- wiki:metadata:start -->
# 新增 HTTP 接口实现惯例

| 字段 | 内容 |
|---|---|
| module | workflow |
| type | pattern |
| updated | 2026-09-19 |
| sources | .cursor/rules/agent-workflow.mdc · .cursor/rules/java-coding-standards.mdc |
<!-- wiki:metadata:end -->

## 适用场景

新增对外接口，按完整任务处理。

## 标准做法

先读同类 Controller/Service/DTO，确认身份、权限、数据归属与输入上限。数据类型和分层按使用者的项目规范，核对事务与查询影响。

## 示例

先给请求/响应字段，再实现服务与持久化，最后接路由；补正常、非法输入、无权限、跨用户资源测试。

## 禁止事项

禁止用 URL 前缀代替鉴权；输出模型由项目定义，但必须核对其中的敏感数据与授权范围。

## 验证

编译受影响模块，运行针对性测试，核对 HTTP 路径提示和接口文档。

HTTP 路径提示只识别常见 Spring Mapping 注解差异，按实际变化核对调用兼容性和已有接口说明。仅鉴权行为或数据范围实际变化时加载对应项目规则；不强制注解、数据隔离字段、文档平台或上传动作。
