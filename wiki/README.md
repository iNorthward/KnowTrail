---
title: 项目知识库
module: system
type: guide
updated: 2026-09-19
sources:
  - wiki/templates/schema.json
  - AGENTS.md
---

<!-- wiki:metadata:start -->
# 项目知识库

| 字段 | 内容 |
|---|---|
| module | system |
| type | guide |
| updated | 2026-09-19 |
| sources | wiki/templates/schema.json · AGENTS.md |
<!-- wiki:metadata:end -->

## 前提

本目录保存实际项目的业务知识。工作流的开任务、审计和场景说明在 workflow/guides/，不作为业务专题塞进 system。

## 步骤

先从 [[index]] 按业务模块查找，再读该模块 README 和相关专题。新增模块使用 templates/module-readme.md，目录名取实际领域名称；模块内部可按子领域细分。专题按五类模板编写，更新模块 README 与总索引。

## 示例

目录形态（尖括号表示使用者定义的实际名称，不是已经存在的业务）：

```text
wiki/
  README.md                 知识库使用说明
  index.md                  按业务模块分组的总索引
  <业务模块>/README.md      模块职责、边界和子领域入口
  <业务模块>/<子领域>/...   该模块的概念、规则、决策与问题
  system/README.md          项目系统与跨领域技术知识
  database/README.md        数据字典入口
  common/README.md          跨模块公共知识
  templates/                文档素材和格式定义
```

当前没有真实业务模块，不预填用户、订单等演示领域。

## 验证

头部 YAML 是元数据唯一来源；正文标题和信息表用于预览，运行 `python3 workflow/scripts/wiki/wiki_metadata.py --write` 同步。格式检查会发现未同步、缺章节、失效来源及未登记页面。

## 常见问题

为什么同时有 README 和 index？README 说明怎么读、怎么维护，index 按领域定位文档。为什么预览能看到头部？正文信息区由 YAML 生成，预览隐藏 YAML 也不影响阅读。
