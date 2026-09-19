---
title: 门禁脚本保留与取舍
module: workflow
type: decision
updated: 2026-09-19
sources:
  - workflow/scripts/finish-audit.sh
  - workflow/scripts/java/java_checks.py
  - workflow/config.json
  - workflow/tests/test_core.py
---

<!-- wiki:metadata:start -->
# 门禁脚本保留与取舍

| 字段 | 内容 |
|---|---|
| module | workflow |
| type | decision |
| updated | 2026-09-19 |
| sources | workflow/scripts/finish-audit.sh · workflow/scripts/java/java_checks.py · workflow/config.json · workflow/tests/test_core.py |
<!-- wiki:metadata:end -->

## 背景

脚本必须有明确职责、触发范围和失败语义。不能因为某个项目曾用过就作为所有使用者的硬门禁，也不能把脚本执行失败当作普通提示。

## 约束

保持通用流程、证据与失败传播。技术偏好不作为默认扫描规则；固定 SQL 交付格式需要主动选择。模板展示、Git 提交和安装不属于门禁。

## 方案比较

删除所有脚本会丢失可验证的收尾；全部默认执行又会强迫使用者遵循不适合的约定。因此按基础、条件、提示和可选能力保留，不增加一套独立安装或提交流程。

## 决策

脚本按 audit、build、java、sql、wiki、lib 分类，文件位置与构建配置见 [脚本目录说明](../scripts/README.md)。

| 文件 | 处置与依据 |
|---|---|
| audit-change-scope.sh、workflow_support.py | 保留：范围、配置、最近 POM、附加检查；不是业务规则；TAGS 仅为线索，语义核查由 Agent 完成 |
| finish-audit.sh、ci-lint.sh | 保留：一个收尾链；CI 必须选正确基线，不以空工作区代替分支审查 |
| lint-agent-diff.sh、java_checks.py | 保留：按快照编排，不再强制 DTO/Entity、Wrapper、断言或字段命名偏好 |
| lint-java-param.py | 保留：保护仍存在方法的参数说明；整个方法删除可通过 |
| compile.sh、compile-audit.sh、_common.sh | 条件保留：有 Java/构建影响才执行，遵循当前或显式指定的 JDK，支持 Maven 和自定义构建命令；不把编译当测试 |
| java_environment.py | 保留：验证当前/显式 JDK，不扫描安装目录、不自动切换版本 |
| compile.cmd、compile.ps1 | 保留薄入口：转发 Git Bash；尚未 Windows 实机验证 |
| lint-agent-docs.sh | 保留入口指引检查；修正已移动阅读集的路径，文本匹配能力有限 |
| lint-wiki-format.sh、lint-wiki-format.py | Wiki 与 workflow/guides 变更时：头部、模板、来源、可见信息区一致性 |
| lint-wiki-index.sh、lint-wiki-symptoms.sh、wiki_links.py | Wiki 变更时：模块文档注册与全部症状导航，支持中文路径、别名与锚点 |
| wiki_metadata.py | 保留同步工具：从 YAML 生成可见内容；不会替代知识核验 |
| lint-wiki-stale.sh、review-reminder.py | 可选提醒：wiki_review_days 默认 null；不按年限定级，提醒工具异常也只报告未完成 |
| check-precipitate.sh | 提示：重复同类待沉淀项，不自动把经验升级为规则 |
| lint-http-paths.sh | 提示：识别常见 Mapping 注解；只提示调用兼容性与已有说明，不强制鉴权模型或文档平台 |
| lint-index-ddl.sh | 提示：常见 SQL 索引变更；不证明执行计划或覆盖所有方言 |
| check-branch.sh、lint-version-freeze.py | 默认关闭：选用 version-sql 才检查目标版本和旧版本冻结 |
| lint-version-sql.sh | 默认关闭：只适用于明确选择的正向/回滚示例格式 |
| lint-schema-wiki.sh、lint-schema-wiki.py | 默认关闭：只适用于所选结构 SQL/字典约定；修正 Shell 入口缺少启用判断 |

已去除：资金表/模拟盘等业务扫描、DTO 继承和 Wrapper 等技术偏好扫描、提交封装与安装流程。没有把剩余脚本宣称为完整安全扫描器。

## 影响与验收

HTTP 与索引检查执行异常会阻断；Wiki 定期复核是默认关闭的附带提醒，其失败仅标记 warn，不阻断。文档年限不代表知识失效，不要求刷新日期或自动登记 P2。阅读集路径与可选结构检查入口已修正。

参数说明、版本冻结、Wiki、项目自选写法和真实 Maven 构建继续回归；增加看板同源更新、失败保留旧页面、提示词出现时机和提示脚本异常传播测试。未做跨平台实机和所有数据库方言验证。
