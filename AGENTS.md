# Agent 入口

本文件是工作流的单一入口，负责规则路由与加载时机。正文在 `.cursor/rules/*.mdc`；不在此复制另一套流程。

**用户只提需求。** Agent 按内核五问自判轻量、单点或完整，主动阅读、实现和检查。档位只认 `agent-workflow.mdc`。Git 提交仅在用户要求时执行，标题与正文使用中文（详见内核），无独立提交流程或额外命令入口。

## 接入任务入口

用户明确要求把 KnowTrail 接入某个项目时，先读取 `workflow/guides/project-adoption.md`，按用户选择的“完整接入”或“针对项目适配”执行。由 Agent 调查、实施、验证并交付结果，不要求用户手动填写配置、复制文件或运行检查。用户未选择时询问方式；普通开发任务不走接入初始化。

两种接入都携带 `workflow/project-setup.md`，由 Agent 收集证据、记录缺口、落实已确认约定；不根据 DO 等源码命名自动定制规则。基础接入、项目补充、业务验证分别报告。

本段是 KnowTrail 来源仓库的接入任务路由。整合到目标项目时按其上下文保留必要维护入口，不将本仓库“无业务 POM”等维护说明照搬过去。

## 分层与覆盖

1. L1 内核：`.cursor/rules/agent-workflow.mdc`。
2. L2 规则：下表启用的 Java、Wiki、索引和版本交付规则。
3. L3 团队补充：`.cursor/rules/custom/*.mdc`，只追加，随项目维护。
4. L4 个人补充：`.cursor/rules/local/*.mdc`，只追加，不进入公开内容。

后层不能静默关闭已启用规则的硬检查。`workflow/config.json` 只配置检查路径、构建和扩展，不代替规则正文。领域检查的启用清单与配置必须一致；项目约定由使用者决定，Agent 根据有效资料整理落实，空白不表示接受预设标准。

## 已启用规则与加载信号

| 规则 | 语义钩子 / 路径 | 权威文件 |
|---|---|---|
| java | 修改 Java 源码或构建；读取已确认的项目规范 | `.cursor/rules/java-coding-standards.mdc` |
| wiki | 表结构/关联变化；完整任务需要知识沉淀；修改 `wiki/**` | `.cursor/rules/java-wiki.mdc` |
| index | Mapper、原生 SQL、建表，或 Job/批量扫描 | `.cursor/rules/java-index.mdc` |
| 结构交付 | SQL/结构变化时核对项目交付约定，不自动启用示例格式 | `.cursor/rules/java-version-delivery.mdc` |

`version-sql` 示例检查器默认关闭；只有使用者明确选择该交付格式后才启用。读取结构交付规则不等于启用检查器。

本体未定义具体业务的受保护表名单、鉴权注解或配置常量。遇到这些内容先从实际项目证据确认，再按已有补充规则处理。

## IDE 并存

Cursor 根据 MDC 的 `alwaysApply` / `globs` 加载。Codex 开任务主动读取：

1. 本文件。
2. `.cursor/rules/agent-workflow.mdc`。
3. `workflow/task-start.md` 的判档部分。
4. 计划修改路径与语义钩子命中的全部规则，以及已有 custom/local 补充。

**适用规则取并集，钩子优先于路径。** 修改 Entity 时读取 Java 项目规范；确有结构变化再加载交付、Wiki 与索引规则。轻量只停止完整阅读，不停止规则路由。加载规则与执行检查分开判断：例外允许跳过具体检查，不等于无需阅读。

中途范围扩大，立即补读新命中的规则，不等用户提醒。脚本 TAGS 只提供识别线索，缺少标签不能免除按实际行为加载规则和核查的责任。

## 路径

| 用途 | 路径 |
|---|---|
| 工作流说明 / 开任务 | `workflow/README.md`、`workflow/task-start.md` |
| 内核和领域规则 | `.cursor/rules/` |
| 检查与构建 | `workflow/scripts/` |
| 检查配置 | `workflow/config.json` |
| 审计 / 交付 / handoff 模板 | `workflow/templates/` |
| Wiki 使用说明 / 分层索引 / 文档规范 | `wiki/README.md`、`wiki/index.md`、`workflow/guides/wiki-doc-template.md` |
| 完整任务阅读集 / 路由 | `workflow/guides/agent-essentials.md`、`workflow/guides/task-routing.md` |
| 待沉淀 / 跨会话记录 | `wiki/common/weekly-summary.md`、`wiki/.agent/` |
| 工作流看板（附带） | `workflow/dashboard/` |

## 自动收尾

收尾组合只认内核表。完整任务执行 `workflow/scripts/finish-audit.sh`，检查失败先修复，再形成变更审计与最终交付。Wiki 变更必须通过模板、索引和症状检查。有规则未覆盖的用户纠正才追加待沉淀；不自定级。

本仓库本身维护工作流和 Markdown Wiki，没有业务应用的根 POM。修改本体按实际范围运行脚本与回归，不伪造 Java 构建；验证构建能力时使用隔离的临时 Maven 工程。

## 工程维护

修改规则、脚本或模板后核对入口、引用和看板；实际检查结果写入本次交付。回归测试在 `workflow/tests/`，仅用于维护工作流，不默认复制到接入项目。产品说明描述当前能力和用法，不加入内部进度、未落实的服务承诺或开发对话记录。

## 本地工作记录

开发进度、计划、接入记录、验证日志、临时脚本和回滚备份统一放在项目根 `.local/knowtrail/`，由 `/.local/` 忽略，不进入产品目录或 Git。接入目标项目同样合并此忽略项；project-setup.md 只放通用规程，具体补充状态写本地记录。稳定的规则和业务知识仍维护在正式文件，不能把必要规范藏进临时目录。
