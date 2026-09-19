---
title: 工作流规则与项目规范的边界
module: workflow
type: decision
updated: 2026-09-19
sources:
  - .cursor/rules/agent-workflow.mdc
  - .cursor/rules/java-coding-standards.mdc
  - .cursor/rules/java-index.mdc
  - .cursor/rules/java-version-delivery.mdc
  - .cursor/rules/java-wiki.mdc
  - workflow/scripts/java/java_checks.py
---

<!-- wiki:metadata:start -->
# 工作流规则与项目规范的边界

| 字段 | 内容 |
|---|---|
| module | workflow |
| type | decision |
| updated | 2026-09-19 |
| sources | .cursor/rules/agent-workflow.mdc · .cursor/rules/java-coding-standards.mdc · .cursor/rules/java-index.mdc · .cursor/rules/java-version-delivery.mdc · .cursor/rules/java-wiki.mdc · workflow/scripts/java/java_checks.py |
<!-- wiki:metadata:end -->

## 背景

工作流负责让变更有依据、范围和验证；使用者负责技术栈与编码标准。两者混在一起会让通用工程强制别人的实现偏好。

## 约束

不删掉必要的审查、文档保护与失败传播。去掉技术偏好时也检查对应脚本，避免文本允许、硬门禁仍拒绝。

## 方案比较

继续内置一套 Java/MySQL 标准容易与实际项目冲突；完全清空所有规则又失去核查流程。采用通用流程加使用者填写区，并把固定格式保留为可选示例。

## 决策

| 文件 | 保留 | 使用者定义 / 不再默认强制 |
|---|---|---|
| agent-workflow | 五问、三档、最小阅读、范围与验证、已有文档保护 | 固定 SQL 形状、调度窗口、常量类实现 |
| java-coding-standards | 项目规范入口、同类实现取证、风险检查和验证 | DTO/Entity、Mapper/Wrapper、字段注释形式、注解、服务继承、异常与日期风格 |
| java-index | 查询证据、规模、计划、变更成本与交付提示 | 引擎、列顺序、特定索引配方 |
| java-version-delivery | 结构影响、发布与恢复核查 | 迁移框架、分支命名、目录、同文件回滚；示例检查器默认关闭 |
| java-wiki | 证据、业务分层、模板、索引、预览一致性 | 实际业务模块与专题内容 |

Java diff 的强制扫描保留既有参数文档保护；移除按 DTO/VO、Wrapper、断言写法和字段名字推断违规的扫描。敏感数据风险仍须核查，但不能只凭 Java 类名决定接口输出。

## 影响与验收

默认不再拒绝项目选择的 DTO 继承或 Wrapper 写法；仍会阻止清空保留方法的参数说明。可选版本冻结检查保留原有回归。Wiki 的 README、分层索引与预览信息由检查保持一致。
