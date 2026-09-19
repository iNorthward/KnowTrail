# 工作流

工作流由规则、步骤、检查和交付模板组成。Agent 从根目录 AGENTS.md 进入，按内核五问识别范围，再选择轻量、单点或完整流程。用户不需要选择档位或执行额外命令。

接入后的项目资料由 Agent 按 [项目补充规程](project-setup.md) 收集、确认、落盘与验证，两种接入模式均适用。

## 文件职责

| 位置 | 职责 |
|---|---|
| `.cursor/rules/agent-workflow.mdc` | 三档、五问、编码原则与唯一收尾表 |
| `.cursor/rules/java-*.mdc` | Java、Wiki、索引和版本 SQL 规则 |
| [guides/README.md](guides/README.md) | 开任务阅读集、场景核查、审计与 Wiki 写法；不属于业务知识 |
| `task-start.md` | 按档位执行开任务和最小阅读 |
| `config.json` | 路径、可选 JDK 主版本、构建命令、热表和附加检查 |
| `scripts/` | 根据 Git 快照给出可验证的检查结果 |
| `templates/` | 审计、交付、跨会话记录和版本 SQL 格式 |
| `tests/` | 参数保护、冻结规则及本体一致性回归 |
| `dashboard/` | 浏览规则与流程；本地服务支持更新，不执行检查 |

## 检查方式

完整收尾运行 `bash workflow/scripts/finish-audit.sh`；单点和轻量按内核的收尾表选择检查。脚本默认审暂存、未暂存和未跟踪文件；`--base=<sha>` 审提交基线到 HEAD 的已提交变更，不能用空工作区代替分支审查。

Java 构建遵循当前环境或显式指定的 JDK，不自动切换版本；Maven 使用 Wrapper 或 Maven，其他工具通过完整自定义命令接入。目录分类与环境配置见 [脚本说明](scripts/README.md)。编译不等于测试，Agent 根据行为变化补针对性验证。本体没有业务应用 POM，纯规则和文档修改无需编译 Java。

Wiki 格式检查核对公共头部、正文结构、索引和来源路径。业务内容、查询计划与数据库文档是否正确仍须审阅。HTTP 路径、索引 DDL、可选复核和待沉淀提示也不能冒充业务验证通过。

## 定制边界

团队规则放 `.cursor/rules/custom/`，个人规则放 `local/`。启用或停用领域规则时同时维护 AGENTS 路由、MDC 和 config 中 packs，不能只改其中一处。`checks` 接收附加门禁的 argv 数组，失败或超时阻断完整收尾。

Java 项目规范由 Agent 根据已有项目约定在 java-coding-standards.mdc 中整理，使用者可调整；不预设 MyBatis、DTO/Entity 分层或注解要求。索引核查不绑定数据库引擎。版本 SQL 示例与冻结检查保留但默认关闭，由使用者选择；其他交付机制配置自身检查。

## 维护验证

```bash
python3 workflow/scripts/wiki/wiki_metadata.py --write
python3 -m unittest discover -s workflow/tests -v
bash workflow/scripts/wiki/lint-wiki-format.sh
bash workflow/scripts/wiki/lint-wiki-index.sh
bash workflow/dashboard/update.sh
```

这些是维护者和 Agent 的检查入口，不是要求使用者每天执行的步骤。当前不自动提交，不提供安装器，也不自动改写其他项目。
