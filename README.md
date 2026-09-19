<div align="center">
  <img src="workflow/dashboard/assets/workflow-mark.svg" width="88" alt="KnowTrail 标志">
  <h1>知序 · KnowTrail</h1>
  <p><strong>让 AI 开发有章可循，让项目知识持续积累。</strong></p>
  <p>面向 Java 项目的 Agent 工作流与 Wiki</p>
</div>

使用 Agent 开发 Java 项目时，项目约定、任务上下文和实现依据需要持续维护。KnowTrail 将这些内容保存在项目中，供后续开发查阅和复用。

**工作流组织开发步骤，Wiki 保存项目知识，检查脚本提供验证结果。** 规则、文档和脚本都是可阅读、可修改、可随 Git 演进的普通文件。

## 工作方式

```text
描述需求 → 判断范围 → 阅读规则和同类实现 → 实现与验证
                                             ↓
下一次开发 ← 按业务模块检索 ← 沉淀必要知识 ← 交付依据
```

- **按改动范围执行。** 配置调整、单点修改、完整功能按三档处理，按需要读取资料、执行检查和维护文档。
- **项目规范由你决定。** Agent 整理已确认的 Java 项目约定；ORM、模块分层、数据库和编码风格由项目自行约定。
- **知识围绕业务组织。** 模块 README、子领域专题和症状索引，支持按模块、主题和缺陷症状检索。
- **检查结果明确。** 既有参数说明保护、Wiki 一致性、受影响模块编译与附加检查，失败会明确报告。
- **流程可查阅。** 工作流看板展示加载条件、检查链和源码；更新后再用 Agent 校对说明。

## 项目结构

```text
AGENTS.md                  Agent 入口：规则分层、加载路由、收尾
.cursor/rules/             内核 + 项目规范入口
workflow/
  task-start.md            五问判档与最小阅读
  project-setup.md         Agent 收集、确认与落实项目资料的规程
  guides/                  工作步骤和场景核查说明
  scripts/                 收尾入口 + audit/build/java/sql/wiki/lib 分类
  templates/               审计、交付、handoff、可选 SQL 示例
  dashboard/               工作流看板（附带功能）
  config.json              路径、构建、检查配置
  tests/                   回归验证
wiki/
  README.md                知识库使用说明
  index.md                 按业务模块分组的索引
  <业务模块>/README.md     使用者定义的模块入口
  system/                  跨业务系统知识
  database/                实际数据字典
  common/                  公共知识与待沉淀记录
  templates/               五类文档模板
```

## 接入你的项目

在目标项目中，让 Agent 读取 [接入执行指南](workflow/guides/project-adoption.md)，选择一种方式即可：

| 方式 | 适合的情况 |
|---|---|
| **完整接入** | 采用标准工作流目录，接入整套规则、Wiki、检查和附带看板 |
| **针对项目适配** | 保留已有规则、文档目录和构建方式，由 Agent 逐项接通相同能力 |

可以直接告诉 Agent：

> 按完整接入方式，将 KnowTrail 接入当前项目。请读取 KnowTrail 的 workflow/guides/project-adoption.md，完成接入与验收。

或：

> 按针对项目适配方式接入 KnowTrail，保留现有规范和知识库。请读取 KnowTrail 的 workflow/guides/project-adoption.md，完成适配与验收。

Agent 负责调查、配置、冲突处理、实施和检查，你不需要逐项复制文件或执行脚本。Agent 需能访问 KnowTrail 文件与目标项目；关键事实无法确定时会说明具体缺口。两种方式都附带 [Agent 项目补充规程](workflow/project-setup.md)：由 Agent 查找已有规范和数据库资料、维护缺口、落实已确认内容，不根据类名或目录猜测项目规则。

验收分别报告基础接入、项目补充和业务验证。通用工作流接通后即可用于具备必要依据的任务；构建环境、表关系等未确认内容会标明影响范围，不要求先补完所有资料。

## 工作流看板

看板展示任务流程、规则加载条件和检查步骤，可查看各阶段的说明与源码依据。

在项目根目录启动本地服务：

```bash
python3 workflow/dashboard/serve.py
```

服务默认使用系统分配的空闲端口，启动后打开终端输出的看板地址。点击 **更新看板** 可刷新规则与脚本快照；更新完成后，可复制校对提示词交给 Agent，核对流程说明。

也可以直接打开 [离线页面](workflow/dashboard/index.html) 阅读已生成的内容。页面更新方式与服务配置见 [看板说明](workflow/dashboard/README.md)。

## 哪些检查会执行

| 类别 | 作用 |
|---|---|
| 基础流程 | 识别 Git 范围、汇总结果，明确区分成功、失败与未执行 |
| 按改动执行 | Java 参数说明保护、项目构建、Wiki 格式/来源/索引/症状 |
| 非阻断提示 | HTTP 路径、索引 DDL、重复待沉淀项；执行异常会报告失败 |
| 明确选择后启用 | 版本 SQL 格式、冻结与结构字典同步 |
| 可选复核提醒 | 默认关闭；文档年限不判错，提醒工具异常也不阻断 |
| 使用者扩展 | 通过 checks 配置项目自己的检查 |

完整取舍与局限见 [门禁检查清单](workflow/guides/gate-review.md)。规则与检查不会证明所有业务语义正确，Agent 仍须核对权限、数据范围、查询规模和恢复方案。

构建工具、JDK 选择和自定义命令配置见 [脚本说明](workflow/scripts/README.md)。

## 开发与验证

脚本使用 Bash、Python 3.9+、Git 和 ripgrep。Java 构建默认支持 Maven/Maven Wrapper，其他工具使用自定义命令；JDK 遵循项目环境，不固定版本；Windows 入口通过 Git Bash 执行，平台验证范围见 [脚本检查说明](workflow/guides/gate-review.md)。阅读 Markdown 和离线看板不需要构建 Java。

```bash
python3 -m unittest discover -s workflow/tests -v
bash workflow/scripts/finish-audit.sh
python3 workflow/dashboard/build-workflow-page.py --check
```

本仓库没有业务应用 POM。Java 编译回归在临时 Maven 工程执行；文档更新先同步 YAML 对应的可见信息区，再运行检查：

```bash
python3 workflow/scripts/wiki/wiki_metadata.py --write
```

## 继续了解

[工作流指南](workflow/guides/README.md) · [Wiki](wiki/README.md) · [规则边界](workflow/guides/rule-boundaries.md) · [看板说明](workflow/dashboard/README.md)

[Agent 接入执行指南](workflow/guides/project-adoption.md) · [Agent 项目补充规程](workflow/project-setup.md)

工作流脚本、看板和回归测试使用 Python 标准库，无需安装 Python 第三方依赖。项目检查在本地执行，不配置 GitHub 自动检查。

## License

[MIT](LICENSE)
