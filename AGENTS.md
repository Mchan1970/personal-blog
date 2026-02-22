# Repository Guidelines

## Project Structure & Module Organization
- `content/`: Markdown posts and pages (primary site content).
- `archetypes/`: Content templates for new posts.
- `layouts/`: Custom Hugo templates and overrides.
- `assets/`: Source assets processed by Hugo Pipes (SCSS/JS, etc.).
- `static/`: Static files copied as-is to the site output.
- `data/` and `i18n/`: Structured data files and localization strings.
- `themes/PaperMod/`: Theme submodule (see `.gitmodules`), do not edit unless intentionally customizing the theme.
- `hugo.toml`: Site configuration (base URL, language, theme, taxonomies).

## Build, Test, and Development Commands
- `hugo server -D`: Run the local dev server including drafts.
- `hugo server`: Run the local dev server with published content only.
- `hugo`: Build the production site into `public/` (generated output).

Hugo PaperMod requires Hugo extended `>= 0.146.0` per the theme templates.

## Coding Style & Naming Conventions
- Content files: use lowercase, hyphenated slugs (example: `content/posts/my-first-post.md`).
- Front matter: keep titles in Title Case, and use `tags` or `series` arrays defined in `hugo.toml`.
- Templates and partials in `layouts/` should mirror Hugo’s naming conventions (example: `layouts/_default/single.html`).
- Keep indentation consistent with existing files (2 spaces in TOML; follow file-local style for templates).

## Testing Guidelines
- No automated test suite is configured in this repository.
- Validate changes by running the local server and checking rendered pages, links, and theme behavior.

## Commit & Pull Request Guidelines
- This repository has no commit history yet, so there is no established commit message convention.
- Suggested commit pattern: short, imperative summaries (example: `Add new post on Hugo setup`).
- PRs should include: a brief description, relevant screenshots of key pages, and any linked issues.

## Configuration & Submodules
- Initialize and update the theme submodule if needed:
  - `git submodule update --init --recursive`
- If you customize theme files, prefer placing overrides in `layouts/` or `assets/` at the root to avoid forking the theme.

## Agent-Specific Instructions
- Always respond in Chinese.

## 博客文件命名与标签规范（v1.0）
### 文件命名（Slug 规则）
- 标准格式：`YYYY-核心主题英文slug.md`，`YYYY` 取发布日期年份。
- 生成规则：从标题提取 1–3 个核心概念 → 翻译为英文关键词 → 全小写 → 用 `-` 连接 → 不超过 30 字符 → 不翻译完整标题 → 不包含栏目名称。
- 禁止：中文文件名、拼音、完整句子、空格、频繁改名。
- 系列文章：仅在确有顺序时使用 `YYYY-topic-01.md`。

### 标签（Tags 规则）
- 每篇 3–5 个中文标签，统一使用 `tags`（数组）。
- 结构要求：
  - 核心主题标签 1–2 个
  - 方法论标签最多 1 个
  - 领域标签 1–2 个
- 禁止：情绪标签、重复语义、栏目名称作为标签、超过 5 个。

### 栏目与标签分离
- 栏目由目录控制：`content/property-rights/`、`content/5000-architect/`。
- 标签只表达核心概念、方法、领域，不重复栏目。

### 长期演化
- 标签总量控制在 50 个以内。
- 避免同义词并存，新标签需有概念独立性。
- 每半年审查一次标签体系。
