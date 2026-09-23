# CLAUDE.md

本文件为 Claude Code 在本仓库工作时提供指引。**始终用中文回复。**

> 详细的命名、标签与发文规范以 `AGENTS.md` 为准（该文件被 `.gitignore` 忽略，仅存在于本地）。本文件是其摘要加上从代码中读出的项目结构说明，两者冲突时以 `AGENTS.md` 为准。

## 项目概览

- 陈逸峰的个人中文博客（站点标题 "Voice"，域名 `www.chenyifeng.com`），基于 Hugo + PaperMod 主题。
- 仓库同时是一个 Obsidian vault：在 Obsidian 中写作，`.obsidian/` 不入库。Obsidian 配置为附件存放在当前目录（`./`）、使用标准 Markdown 链接，因此图片与 `index.md` 同目录。
- 部分提交由 Obsidian Git 插件自动生成（`vault backup: <时间>`）。

## 常用命令

```bash
hugo server -D        # 本地预览（含草稿）；加 -F 显示未来日期的文章
hugo server           # 本地预览（仅已发布）
hugo --minify         # 生产构建，输出到 public/（与 CI 相同）
git submodule update --init --recursive   # 初始化 PaperMod 子模块
```

- 本地预览速查见 `docs/local-preview.md`。
- 需要 Hugo extended `>= 0.146.0`（本机为 0.165.0 extended）。
- 没有自动化测试。验证方式：运行本地服务，检查渲染页面、链接、图片与主题行为；至少确保 `hugo --minify` 无报错。

## 部署

`.github/workflows/deploy.yml`：推送到 `main` 即触发，CI 用最新 Hugo extended 执行 `hugo --minify` 并发布到 GitHub Pages（`static/CNAME` 指定自定义域名）。**推送 main 等于上线**，`draft: false` 的文章会立即公开。

## 目录结构

- `content/` 各栏目（栏目由目录决定，同时在 `hugo.toml` 的 `menu.main` 与 `params.mainSections` 中登记）：
  - `yifeng-talks/` → 逸峰闲话
  - `property-rights/` → 业主维权
  - `5000-architect/` → 五千年架构师（目前仅有 `_index.md`）
  - `about/`、`search.md`（搜索页，依赖首页 JSON 输出 + Fuse.js，仅按标题搜索）
- `layouts/`：对 PaperMod 的覆盖，不要直接改 `themes/PaperMod/`。
  - `_default/_markup/render-image.html`：图片渲染钩子。按 alt 文本裁剪：含“题图”→ 900x383、“正方图”→ 900x900、“长方图”→ 900x500，其余缩放到 900 宽。图片必须是页面资源（与 `index.md` 同目录）才会被处理。
  - `_default/_markup/render-blockquote.html`：把 Obsidian callout（`> [!TYPE] 标题`）渲染为 `.callout-<type>` 盒子，否则按普通引用。
  - `_default/_markup/render-codeblock-mermaid.html` + `partials/extend_footer.html`：遇到 ```mermaid 代码块时才加载本地 `static/js/mermaid.min.js`，并随明暗主题切换。
  - `partials/post_meta.html`：按中文字符数计算字数与阅读时间（300 字/分钟）。
  - `partials/extend_head.html`：加载 `static/fonts/` 下的霞鹜文楷子集字体。
  - `partials/breadcrumbs.html`、`_default/search.html`：面包屑与搜索页定制。
- `assets/css/extended/`：PaperMod 自动加载的自定义 CSS（正文文楷、标题黑体、callout、搜索等样式）。
- `data/tag-whitelist.toml`：标签白名单（按栏目 `allowed`）与别名归并表（`aliases`）。
- `templates/`：Obsidian 模板（`post.md`）及发文指令模板说明（`publish-request.md`）。
- `archetypes/default.md`：Hugo 默认原型（TOML 前言），实际文章使用 YAML 前言，一般不用 `hugo new`。
- `public/`、`resources/_gen/` 为生成产物，已忽略。

## 文章格式

新文章使用目录模式：`content/<栏目目录>/<slug>/index.md`，图片放在同目录。现有文章前言格式如下：

```yaml
---
title: 上 ERP，不是买软件，而是老板的一场“变法”
date: 2026-03-04T09:00:00+08:00
draft: false
categories:
  - 逸峰闲话
tags:
  - 企业管理
  - ERP
  - 组织变革
series: []
---
![题图](Inserted-image-20260304095440.png)
```

- `categories` 沿用栏目中文名（注意 `hugo.toml` 只定义了 `tags` 和 `series` 两个 taxonomy，`categories` 目前仅作为元数据，不生成页面）。
- 正文开头通常是一张 alt 为“题图”的封面图。
- 一级标题只用于提取 `title`，落稿时标题写入前言。
- `markup.goldmark.renderer.hardWraps = true`：单个换行即换行，不需要空行分段。

## 命名与标签规范（摘要）

- slug：`YYYY-英文关键词`，`YYYY` 为发布年份；1–3 个核心概念译成英文，全小写，用 `-` 连接，不超过 30 字符，不含栏目名，禁止中文/拼音/整句，发布后不要频繁改名。
- tags：每篇 3–5 个中文标签（核心主题 1–2、方法论最多 1、领域 1–2），禁止情绪标签、同义重复、栏目名作标签。
- 自动选标签时必须优先使用 `data/tag-whitelist.toml` 的 `allowed` 列表，并用 `aliases` 归并近义词；白名单没有合适的，用归并后的近似标签，不默认创造新标签。全站标签总数控制在 50 个以内。
- 历史文章不因白名单调整而自动改标签，除非用户明确要求。

## 固定发文流程

用户以如下格式下达命令时，直接落稿，不先给方案：

```md
帮我发表文章
栏目：<逸峰闲话 / 业主维权 / 五千年架构师>
日期：<YYYY-MM-DD>
状态：草稿 / 发布
slug：自动 / <指定>
标签：自动 / <指定，逗号分隔>

正文：
<Markdown 正文>
```

- 栏目必须由用户指定；未提供时先追问，不得自行判断。
- 标题优先取正文一级标题，其次取 `标题` 字段；都没有则先追问。
- `草稿` → `draft: true`；`发布` → `draft: false`。
- 用户指定的标签优先保留，超出白名单可提示但不强改。
- 字段冲突时以用户明确指定的栏目和日期为准，再规范化其余部分。

## 其他约定

- 修改主题行为时，在根目录 `layouts/` 或 `assets/` 中覆盖，不要 fork 主题。
- TOML 使用 2 空格缩进；模板遵循文件现有风格。
- 提交信息用简短的祈使句（如 `Add new post on Hugo setup`）。
