# 本地 Git 工作流

工作目录：`C:/Users/owner/Desktop/test/Mod3-MHW-Importer-upstream`。当前分支：`blender-5.2-compat`。基于 upstream master `364c2609562436cbbee8dca3a2c91c1a4fe6bc6c`。

旧目录 `C:/Users/owner/Desktop/test/Mod3_MHW_Importer` 未修改。完整备份：`C:/Users/owner/Desktop/test-backup-20261003-203935`。同目录旧 ZIP 与旧目录相同，不能作为 upstream 原始代码证明。

Git 2.45.2 已安装；已有提交身份为 `ZMang <xqqxzzxyy@gmail.com>`，没有猜测或修改全局设置。GitHub CLI 未安装；本地工作不需要登录。远程名 `upstream` 指向原作者公共仓库，没有添加个人 fork，没有 push 或创建 PR。

## 日常查看

在 PowerShell 进入上述工作目录后：

```powershell
git status
git branch --show-current
git log --oneline --decorate -12
git diff
git diff --check
```

`status` 查看未提交文件；`diff` 审查改动；commit 是本地记录，不会自动上传。一次只处理一类问题，运行对应测试，再 `git add 文件路径`、`git diff --cached`、`git diff --cached --check`、`git commit -m '简明描述行为变化'`。优先明确列出文件，避免把私有模型、测试输出或整个旧目录加入提交。

## 获取作者后续更新

`git fetch upstream` 只下载远程历史，不覆盖当前文件。先检查工作区和 `git log HEAD..upstream/master --oneline`。需要合并/重放时先建立额外备份分支并确认工作区干净，然后按实际冲突决定；本轮没有自动做这些动作。不要运行 reset --hard、clean -fd 或删除旧参考版。

## 将来贡献

主维护目标是 `nn10n10/Mod3-MHW-Importer`；原作者 `AsteriskAmpersand/Mod3-MHW-Importer` 仍作为 `upstream` 参考。当前公开的 nn10n10 `master` 仍指向 upstream 基线；本地 `blender-5.2-compat` 尚未 push，且没有配置个人 fork 的 remote。发布前确认目标账号权限后，将其设为 `origin` 并 push 维护分支。上游 PR 是可选工作，需要另行明确决定。不要向 upstream 直接推送，不用 force push。当前 PR_DESCRIPTION_DRAFT.md 仅是可选草稿。

旧样本、备份和 audit-artifacts 位于仓库外；测试资产不提交。提交历史中的每个修复可通过 `git show 提交号` 独立查看；现有记录已按逻辑拆分，没有复制旧目录或用一个巨大 AI 修复提交覆盖所有内容。
