# Agent 入口

正文在 `.cursor/rules/*.mdc`。档位和收尾命令只认 `.cursor/rules/agent-workflow.mdc`。用户只描述需求；Agent 自判档位，不让用户选档、执行脚本或确认流程。Git 提交只在用户明确要求时做。

## 本仓库验证

本仓库没有业务应用根 POM。不要在仓库根执行 `mvn`、`./mvnw`、`mvn compile` 或 `mvn test`。要验证 Java 构建能力时，使用隔离的临时 Maven 工程，不要伪造本仓库能编译。

```bash
python3 -m unittest discover -s workflow/tests -v
bash workflow/scripts/finish-audit.sh
python3 workflow/dashboard/build-workflow-page.py --check
```

改了 `wiki/**` 或 `workflow/guides/*.md` 的 YAML 头之后，先执行 `python3 workflow/scripts/wiki/wiki_metadata.py --write`，再跑上面的收尾。`<!-- wiki:metadata:start -->` 与 `<!-- wiki:metadata:end -->` 之间的预览区由该命令生成。手改预览区，或只改 YAML 不重写预览，`lint-wiki-format.sh` 失败。

`workflow/dashboard/index.html` 由 `python3 workflow/dashboard/build-workflow-page.py` 生成。不要手改这个文件。`--check` 发现页面和当前规则不一致；`finish-audit.sh` 和 `ci-lint.sh` 不跑这项检查。改了规则、脚本或 `workflow/dashboard/page.template.html` 后要重新生成。

环境：Bash、Python 3.9+、Git、ripgrep。只用 Python 标准库，不安装第三方包。本仓库不配置 GitHub Actions。CI 要跑时用内核收尾里的 `ci-lint.sh`，不要另写一套检查。

## 规则分层

1. L1 内核：`.cursor/rules/agent-workflow.mdc`（`alwaysApply`）。
2. L2 为下表。`workflow/config.json` 的 `packs` 只能是 `java`、`wiki`、`index`、`version-sql` 的子集，并且和本表一致。启用或停用时同时改本表、对应 MDC 和 `packs`，不能只改一处。
3. L3 `.cursor/rules/custom/`、L4 `.cursor/rules/local/` 只追加，不能关掉已启用包的硬检查。

| 规则 | 语义钩子 / 路径 | 权威文件 |
|---|---|---|
| java | 修改 Java 源码或构建；读取已确认的项目规范 | `.cursor/rules/java-coding-standards.mdc` |
| wiki | 表结构/关联变化；完整任务需要知识沉淀；修改 `wiki/**` | `.cursor/rules/java-wiki.mdc` |
| index | Mapper、原生 SQL、建表，或 Job/批量扫描 | `.cursor/rules/java-index.mdc` |
| 结构交付 | SQL/结构变化时核对项目交付约定，不自动启用示例格式 | `.cursor/rules/java-version-delivery.mdc` |

`version-sql` 默认关闭。配置里写上 `version-sql` 时必须同时有 `wiki`，否则加载配置直接失败。读取结构交付规则不等于启用检查器。

本仓库没有受保护表名单、鉴权注解或配置常量。没有资料时不要编过滤字段、热表或 JOIN。`wiki/system` 只放跨业务系统知识，不放工作流操作手册；步骤放 `workflow/`。

## 加载

Cursor 按 MDC 的 `alwaysApply` / `globs` 注入。Codex 没有 glob，开任务读 `workflow/task-start.md` 的判档和加载节。中途范围扩大就补读新命中的规则。脚本输出的 TAGS 只是线索，没有标签不能跳过实际行为对应的规则。

路径索引在 `workflow/README.md`。只有用户明确要求把 KnowTrail 接进某个项目时，才读 `workflow/guides/project-adoption.md`；两种接法都带 `workflow/project-setup.md`。普通开发不走接入。不要把本仓库「没有业务 POM」写进目标项目的入口。

## 收尾与维护

收尾命令只认内核「收尾」表。改了规则、脚本或模板之后，跑「本仓库验证」里的命令，并重新生成看板。回归测试在 `workflow/tests/`，不默认复制到接入项目。产品说明只写当前能力和用法，不写内部进度或未落实的承诺。

开发进度、接入记录、验证日志和回滚备份放项目根 `.local/knowtrail/`，由 `/.local/` 忽略，不进 Git。必要规范写在正式文件里，不能只放在这个目录。
