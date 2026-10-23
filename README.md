# Community Rule Sources

本仓库由社区成员维护，提供可供兼容阅读器（包括 KiokuYomi）导入的可选加密规则集合，
通过 GitHub Releases 分发。

本仓库不是 KiokuYomi 的官方仓库，也不是任何 App 的官方规则渠道。规则由社区成员
自行制作和提交；KiokuYomi 开发者不审核、不推荐、不保证这些规则，App 也不内置任何第三方站点。

本仓库不托管漫画或视频内容。使用者应仅访问已获授权的内容，并遵守适用法律及相关服务条款。

## 按来源查找与单独导入

**[打开单源规则目录（不含成人来源）](SOURCES.md)**

不需要添加整套集合：打开目录，用浏览器“在页面中查找”搜索名称或规则 ID，
对所需来源的“导入链接”右键／长按并复制地址，再粘贴到兼容阅读器的远程规则导入入口，
检查导入预览后自行确认。也可以下载固定版本的 `.kyyrule` 文件后手动导入。

目录中的稳定地址指向最新 Release 中对应的单源包；点击链接可能直接下载文件，
不表示能一键唤起 App 安装，也不保证安装后自动更新。
目录随已发布集合自动生成；常规目录仍可能包含 mature（成熟内容）分级，并非全年龄目录。

[成人来源单独目录](docs/SOURCES_ADULT.md) 仅供符合适用年龄及法律要求的使用者主动查看。

## 手动添加订阅

在 KiokuYomi 的规则集合／远程规则导入入口粘贴 HTTPS 集合链接，检查导入预览后自行确认。

**综合集合（不含成人来源）：**

```text
https://github.com/manga-rule-community/sources/releases/latest/download/general.json
```

**完整集合（可能包含成人来源；使用者需符合适用年龄及法律要求）：**

```text
https://github.com/manga-rule-community/sources/releases/latest/download/all.json
```

GitHub raw 备用集合入口：

```text
https://raw.githubusercontent.com/manga-rule-community/sources/main/general.json
https://raw.githubusercontent.com/manga-rule-community/sources/main/all.json
```

## 兼容入口

原 `kiokuyomi-Community/sources` 仓库继续保留，作为兼容镜像；两个仓库分发同一组已发布的
加密规则包，订阅其中一个即可，不需要同时添加。

## 反馈与移除请求

版本、导入问题或移除请求，请通过[仓库 Issues](https://github.com/manga-rule-community/sources/issues) 提交。
权利方请提供规则 ID、涉及的权利及可核实的请求依据；不要在公开 Issue 上传身份证明、
账号凭据、私密材料或受版权保护的完整内容。移除需同步正式上游及相应分发渠道，而不只是改 README。

仅用于有权访问的内容。规则加密和项目分离并不替代授权、版权及平台政策要求。

## 开发文档

分发架构、发布流程和本地验证方式见 [开发与维护说明](docs/DEVELOPMENT.md)。
