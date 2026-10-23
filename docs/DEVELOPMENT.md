# 开发与维护说明

[返回 README](../README.md)

## 分发架构

本仓库不启用 GitHub Pages，也不制作规则目录官网。Git 仓库保存导入索引、Markdown 单源目录和分发工具；
GitHub Releases 保存已经发布的加密 `.kyyrule` 与 `.kyybundle` 文件。
不存放漫画／视频内容、明文规则、可执行扩展、账号凭据、Cookie、Token、解密密钥或签名私钥。

## 索引与旧入口兼容

集合入口随发布更新，但集合内每个包的 URL 绑定具体 Release 标签，防止更新过程中混用版本。
`sources.json` 是**新仓库内** `all.json` 的兼容别名。
旧仓库中同名的 `sources.json` 是另一种发现目录格式，本项目不会改写它。
App 原有的大小、SHA-256、签名、解密及锁定规则校验继续生效。

既有 `/v1/rule-catalog`、`/v1/rule-packages/<release>/<id>.kyyrule`、
`/v1/rule-bundles/<release>/<channel>.kyybundle` 和 `/rules/<id>` 分发链仍保持原样。
老 `sources.json` 发现目录入口及其 Pages/raw 镜像也不受影响。
保留域名用于兼容不等于新建目录网站；本仓库新增的是 GitHub 分发渠道。

## 发布与更新边界

1. 原有私有规则审核、签名、加密与正式发布流程保持不变。
2. 本仓库只读取已公开发布的集合及加密包；不访问私有规则源码、不解密、不重新签名。
3. 完整／综合集合的版本及子集必须一致；每个包和集合包的字节数及 SHA-256 必须匹配。
4. 发布前重新读取上游集合，避免同步途中发生版本切换。
5. 文件上传到草稿 Release，GitHub 返回的每个附件 SHA-256 都验证通过才公开并切换 latest。
6. Release 公开后再更新 main 上的集合索引及自动生成的单源目录。拒绝序号回退、同序号换内容及改写已公开附件。
7. GitHub Actions 每 6 小时同步一次，也可以在 Actions 手动执行；失败时旧入口和上一个 Release 不变。

该同步工具只校验包的加密／签名**结构**及完整性，并不声称完成密码学签名验证；
密码学验证与解密仍由 App 原有导入链完成。没有把测试密钥或生产密钥放进此仓库。

## 单源目录生成

README 链接到 `SOURCES.md`（常规来源）和 `docs/SOURCES_ADULT.md`（成人来源单独入口）。
两份文件均由 `scripts/generate_source_directory.py` 从本仓库的 `all.json` 和 `general.json`
确定性生成，不手工增删条目。名称、规则 ID 和内容分级来自公开集合；不读取规则明文，
不解密、不请求源站，也不新增网站后台、二维码或 App 唤起协议。

生成器复用现有集合格式及固定版本 URL 校验，并要求两份集合的版本、序号及非成人子集完全一致。
名称以文本转义后输出，避免外部元数据破坏 Markdown 表格或注入链接／HTML。
条目按名称（忽略大小写）、规则 ID 排序；已移除的来源不会保留在新目录中。

- “导入链接”：`https://github.com/manga-rule-community/sources/releases/latest/download/<id>.kyyrule`，
  供用户复制到 App；指向获取时的最新 Release，不承诺自动安装或安装后自动更新。
- “下载该版本”：直接沿用集合内的固定版本 URL，便于获取目录快照对应的文件。
- `safe`、`teen`、`mature` 均属于常规目录；`adult` 仅出现在独立成人目录。分级不是年龄认证，
  也不证明内容授权、当前站点可用性或任何 App 的审核与推荐。

同步工作流仅在 Release 上传、附件哈希验证及公开成功后，从 `dist` 中的集合生成目录，
再将两份目录与四个元数据文件一起提交。目录不是 Release 附件，不改写已经公开的包或校验和。
独立测试工作流和同步前检查都会执行 `--check`，发现目录缺失或过期时失败，且不会改写文件。

## 本地验证

以下命令在仓库根目录执行。

需要 Python 3.11+、curl；发布还需要 GitHub CLI。没有第三方 Python 依赖。

```sh
python3 -m unittest discover -s tests -v
python3 scripts/generate_source_directory.py --check
# 调整生成器后重新生成，并提交两份 Markdown 目录：
python3 scripts/generate_source_directory.py
python3 scripts/mirror_release.py --output dist/preview
# 可选：从准备好的集合预览目录，不改仓库内的目录或线上发布：
python3 scripts/generate_source_directory.py --catalog-dir dist/preview --output-dir dist/directory-preview
# 只有显式指定 --publish 才会写入 GitHub Releases：
python3 scripts/mirror_release.py --output dist/release --publish
```

镜像工具每次运行使用空的输出目录；准备后若要发布请使用另一个空输出目录重新运行。`dist/` 不提交。
`all.json`、`general.json`、`sources.json`、`publication.json` 四个元数据文件以及
`SOURCES.md`、`docs/SOURCES_ADULT.md` 两份目录在发布成功后同步更新到 Git。本仓库的 `GITHUB_TOKEN` 只需
`contents: write`，不需要 App 仓库 Token、Cloudflare 密钥、App 签名证书或 App Store Connect 凭据。
