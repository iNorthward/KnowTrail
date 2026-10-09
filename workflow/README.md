# 工作流

工作流由规则、步骤、检查和交付模板组成。Agent 从根目录 [AGENTS.md](../AGENTS.md) 进入。档位和收尾命令只认内核，判档五问在 [task-start.md](task-start.md)。用户不需要选择档位或执行额外命令。

接入后的项目资料由 Agent 按 [项目补充规程](project-setup.md) 收集、确认、落盘与验证，两种接入模式均适用。

## 文件职责

| 位置 | 职责 |
|---|---|
| `.cursor/rules/agent-workflow.mdc` | 三档表、收尾命令、硬门禁 |
| `.cursor/rules/java-*.mdc` | Java、Wiki、索引和版本 SQL 规则 |
| [guides/README.md](guides/README.md) | 开任务阅读集、场景核查、审计与 Wiki 写法；不属于业务知识 |
| `task-start.md` | 五问、加载顺序、按档执行的阅读步骤 |
| `config.json` | 路径、可选 JDK 主版本、构建命令、热表和附加检查 |
| `scripts/` | 根据 Git 快照给出可验证的检查结果 |
| `templates/` | 审计、交付、跨会话记录和版本 SQL 格式 |
| `tests/` | 参数保护、冻结规则及本体一致性回归 |
| `dashboard/` | 浏览规则与流程；本地服务支持更新，不执行检查 |

## 检查方式

收尾跑哪些脚本，只认内核收尾表。基线、JDK 和 Maven Wrapper 的行为见 [脚本说明](scripts/README.md)。本仓库的验证命令、不能用的构建方式和生成物见仓库根 AGENTS.md「本仓库验证」。

`config.json` 的 `checks` 是附加门禁的 argv 数组，失败或超时阻断完整收尾。编译不等于测试。HTTP 路径和索引 DDL 脚本只打印差异，不能当成业务验证通过。

## 定制边界

启用或停用领域规则时，同时改 AGENTS 的规则表、对应 MDC 和 config 的 `packs`。项目规范、索引引擎和版本 SQL 示例的取舍见 [规则边界](guides/rule-boundaries.md)；版本 SQL 示例默认关闭。

## 维护验证

命令以 AGENTS.md「本仓库验证」为准。改了 YAML 头要先跑那里的 `wiki_metadata.py --write`。这些是维护者和 Agent 的检查入口，不是要求使用者每天执行的步骤。当前不自动提交，不提供安装器，也不自动改写其他项目。
