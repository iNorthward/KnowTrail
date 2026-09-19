# 检查与构建脚本

根目录只提供 `finish-audit.sh`（完整收尾）和 `ci-lint.sh`（CI 同一检查链）两个编排入口。

| 目录 | 职责 |
|---|---|
| audit/ | 改动范围、Agent 指引检查 |
| build/ | 按范围构建、项目命令入口、Windows 薄入口 |
| java/ | 参数文档保护、Java diff 编排、HTTP Mapping 差异提示 |
| sql/ | 索引 DDL 提示；可选版本冻结、SQL 格式和结构字典检查 |
| wiki/ | 模板、索引、症状、过期、待沉淀与元数据同步 |
| lib/ | 配置、Git、JDK 环境等公共实现，不直接作为用户操作入口 |

HTTP 提示只提供常见 Spring Mapping 差异线索，不强制鉴权模型、数据归属规则或文档平台。索引脚本也不代替 JOIN 和查询计划核查，具体步骤见 `.cursor/rules/java-index.mdc`。

分支审计优先显式传入 `--base=<sha>`；自动推断的基线与 HEAD 相同时要求指定基线，避免把整条分支误判为空改动。

## 构建与 JDK

不预设 JDK 17，也不搜索机器上的 JDK 或覆盖不匹配的环境。优先使用 `WORKFLOW_JAVA_HOME`，其次 `JAVA_HOME`，否则使用当前 PATH 的 java/javac；两者主版本需一致。显式配置错误立即失败，不偷偷换用另一套。

`workflow/config.json` 的 `java_version` 默认 null，表示不额外限制运行构建的 JDK 主版本；填写 8、11、17、21 等整数则精确校验。这个字段不是编译目标版本，源码 release/target 和 toolchain 由项目构建文件决定。无法运行、版本不符或构建非零退出都会阻断。

Maven 项目优先使用构建根的 `mvnw`，否则使用 PATH 中的 `mvn`。默认执行 compile；`build_args` 可替换为项目需要的目标和参数。子模块在根 reactor 构建；独立 POM 在其自身目录构建。Wrapper 的权限、依赖下载和网络要求由项目负责，不自动安装工具。

其他构建工具、容器或专用流水线通过完整 argv 接入，例如 Gradle 项目：

```json
{
  "java_version": null,
  "build_command": ["./gradlew", "classes"],
  "build_args": [],
  "offline": false
}
```

这是配置片段，合并到现有 config。自定义命令在项目根目录执行一次，自行负责模块选择，不追加 Maven 参数；不经过 shell 字符串解析。需要离线时把对应工具的参数写进命令。自定义命令默认自行管理 JDK（例如容器）；若填写 java_version 或 WORKFLOW_JAVA_HOME，仍检查所指定的本地 JDK。

测试入口应通过 build_command/build_args 或 config 的 checks 明确接入；编译成功不等于测试通过。共享产物的构建串行执行。脚本运行环境为 Bash、Python 3.9+、Git、ripgrep；Windows 薄入口依赖 Git Bash，尚未实机验证。

## 可选 Wiki 复核提醒

`wiki_review_days` 默认 null（关闭）。只有项目需要定期复核时才填写正整数。超过天数仅输出 INFO，不标成缺陷或 P2，不修改日期；长期稳定文档可以一直保留。提醒脚本异常时完整收尾记录 warn，不阻断其他工作。模板、索引等内容一致性门禁仍按规则执行。

## 识别线索与语义核查

`TAGS` 用于导航，未命中或 `none` 不代表没有风险。范围扫描与完整收尾对有改动的范围输出 `SEMANTIC_REVIEW=pending`；无改动输出 `no_changes`。脚本不会根据命名决定免除业务审阅，也不输出其他 Agent 或审查工具的启动/跳过指令。

Agent 按实际 diff 和必要上下文核对调度、查询、结构、接口等相关行为，并在审计模板记录依据。自动检查成功与 Agent 语义核查完成分别报告；无需为未知命名增加项目专用路径配置。
