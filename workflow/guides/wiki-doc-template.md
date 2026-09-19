---
title: Wiki 文档规范
module: workflow
type: pattern
updated: 2026-09-19
sources:
  - wiki/templates/schema.json
  - .cursor/rules/java-wiki.mdc
---

<!-- wiki:metadata:start -->
# Wiki 文档规范

| 字段 | 内容 |
|---|---|
| module | workflow |
| type | pattern |
| updated | 2026-09-19 |
| sources | wiki/templates/schema.json · .cursor/rules/java-wiki.mdc |
<!-- wiki:metadata:end -->

## 适用场景

新增或修改 Wiki 专题时使用。规则与实际文档共用 `wiki/templates/schema.json`；文档格式检查读取这份定义。

## 标准做法

正文展示标题和元数据表，由 `wiki_metadata.py --write` 从 YAML 同步；预览不依赖编辑器是否显示 frontmatter。

公共头部必须有 title、module、type、updated、sources。updated 为实际修改日期；sources 是可核对的仓库相对路径或公开来源 URL，不填写不存在的源码。verified 可选，仅在核对来源后更新。bugfix 额外提供非空 symptoms，并在索引同一行登记症状。

| 类型 | 必需二级章节（顺序固定） |
|---|---|
| concept | 用途 → 核心规则 → 数据与流程 → 边界 → 相关链接 |
| pattern | 适用场景 → 标准做法 → 示例 → 禁止事项 → 验证 |
| bugfix | 现象 → 影响 → 根因 → 修复 → 回归点 |
| decision | 背景 → 约束 → 方案比较 → 决策 → 影响与验收 |
| guide | 前提 → 步骤 → 示例 → 验证 → 常见问题 |

正文可用三级标题展开细节，不用另造一套二级章节。decision 可选 status：proposed/adopted/implemented/superseded。不要为了格式编造内容；不适用项说明原因。

专用文档按 schema 中明确列出的路径检查：根索引、数据库字典和待沉淀记录。模板目录是写作素材，不是已完成专题；跨会话记录使用 workflow/templates/handoff.md。其余页面一律遵守五类之一。

## 示例

新接口实现惯例选择 [pattern 模板](../../wiki/templates/pattern.md)；故障复盘选择 [bugfix 模板](../../wiki/templates/bugfix.md)。已有文章优先补充，只有新的独立主题才新建。

业务模块的 README 是 concept 类型入口，模块名和子领域由使用者填写，不预设领域。

写完把 `[[业务模块/页面名]]` 登记到 [知识索引](../../wiki/index.md)，症状与该文档链接写在同一行。

## 禁止事项

禁止只有 YAML 头而正文仍是随意的“概述”；禁止虚构 sources 或 verified；禁止把模板示例当已验证业务事实；禁止为特殊文档无限增加豁免。

## 验证

运行 `workflow/scripts/wiki/lint-wiki-format.sh`、`lint-wiki-index.sh`、`lint-wiki-symptoms.sh`。自动检查结构与引用；内容准确性仍需对照 sources。
