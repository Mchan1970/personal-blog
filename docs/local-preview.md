# 本地启动 Hugo 速查

## 一键启动

```bash
cd ~/Obsidian/personal-blog
hugo server -D
```

浏览器打开 http://localhost:1313/ ，修改文章保存后页面会自动刷新。
停止：在终端按 `Ctrl + C`。

推荐的完整命令（草稿、未来日期的文章都显示，保存后自动跳到改动的页面）：

```bash
hugo server -D -F --navigateToChanged
```

## 常用参数

| 参数 | 作用 |
| --- | --- |
| `-D` | 显示草稿（`draft: true`） |
| `-F` | 显示发布日期还在未来的文章（提前写好的文章不加就看不到） |
| `--port 1314` | 1313 端口被占用时换一个端口 |
| `--navigateToChanged` | 保存文件后浏览器自动跳到被修改的页面 |

## 上线前自检

```bash
hugo --minify
```

这和 GitHub Actions 的构建方式一致，没有报错再推送。**推送到 `main` 就等于上线**，`draft: false` 的文章会立即公开。

## 常见问题

- **找不到 `hugo` 命令**：`brew install hugo`。需要 extended 版本且 `>= 0.146.0`，用 `hugo version` 检查。
- **主题缺失 / 页面空白**：`git submodule update --init --recursive`
- **端口被占用**：加 `--port 1314` 换一个端口，或者关掉之前开着的那个终端窗口。
- **文章不显示**：
  - 草稿要加 `-D`，未来日期要加 `-F`；
  - 文件必须放在 `content/<栏目>/<slug>/index.md`。
- **图片不显示**：图片必须和 `index.md` 在同一目录。

## 可选：设置快捷命令

在 `~/.zshrc` 末尾加一行：

```bash
alias blog='cd ~/Obsidian/personal-blog && hugo server -D -F --navigateToChanged'
```

执行 `source ~/.zshrc` 后，以后在终端输入 `blog` 就能启动。
