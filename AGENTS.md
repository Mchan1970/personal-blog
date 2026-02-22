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
