# Java 开任务（Agent 内部，用户零操作）

> **用户只说要做什么。** 本流程由 Agent 自动遵循，**不要**让用户输入额外命令，**不要**让用户确认档位。

## 0. 先判轻重（强制，先于完整阅读）

按 `.cursor/rules/agent-workflow.mdc`（内核）自判轻重，默答 5 问；第 4 问走 `AGENTS.md` pack **已启用的项目数据域**；写非主键 SQL 走 pack **java-index**（不升档）。档位名称即含义：

| 档 | 一眼 | 后续步骤 |
|----|------|----------------|
| **轻量** | 只动配置或数据 | **停**：不读路由、不写 wiki、不建 handoff；只改当前项目配置/数据落点。收尾见内核「收尾」表 |
| **单点** | 就改这一块代码（含改已有 SQL、改已有 Job） | 跳到 §2 单点；不跑完整阅读集 |
| **完整** | 跨模块 / 新增对外接口 / 改表或表关联 / 新增 Job Handler | §1 handoff → §3 阅读集 |

拿不准选更轻的一档；禁止问用户「这是轻量还是完整」。

## 1. Handoff（仅完整档）

1. 列出 `wiki/.agent/*.md`
2. 有 `status: in_progress|blocked` → **Read 并续写**
3. 新任务且预计 >1 轮 → 创建 `wiki/.agent/<task-slug>.md`

## 2. 单点

Read 目标模块 1～2 个同类实现（或 1 篇直接相关 wiki），然后改那些文件。禁止为「流程完整」打开 `task-routing` 全文或新建 wiki。

## 3. 最小阅读集（仅完整档）

1. `AGENTS.md`
2. `workflow/guides/agent-essentials.md`
3. `workflow/guides/task-routing.md` → 按场景追加 1～3 篇

## 4. Agent 自检（不单独发给用户）

- 档位、分支、已 Read 文档、参考样板
- **收尾步骤只认内核 `agent-workflow.mdc`「收尾」表**，此处不另列一套
- 完整任务结束时，按 `workflow/guides/change-audit-checklist.md` 输出《变更审计》；P0/P1 全清后继续输出《最终交付清单》

## 禁止

- 让用户执行脚本、触发额外命令或确认档位
- 轻量任务写 wiki / 跑 `finish-audit.sh`
- 用「这是单点」跳过 已启用领域规则的检查、java-index 索引核对或 `lint-agent-diff.sh`
- 完整档未 Read 路由就写跨模块代码
- 表关联无文档时臆造 JOIN
