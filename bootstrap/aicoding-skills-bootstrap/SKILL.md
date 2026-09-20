---
name: aicoding-skills-bootstrap
description: "当用户要求把 GitHub 仓库中的 skill 拉取/导入/同步到当前 Multica 工作区技能库时使用——支持整个仓库、仓库内指定目录、或只导入其中特定的几个 skill。触发词：拉取 skill、导入 skill、import skills、批量安装技能、同步 skill 仓库。"
---

# 从 GitHub 仓库拉取 skill 到 Multica 工作区

把 GitHub 仓库中的 skill 批量导入 Multica 技能库。导入通道是 `multica skill import`（本地 `.skill`/`.zip` 或 URL）；skill 只是说明书，不含可执行环境。

**附带文档完整性（最重要规则）**：`--url` 通道实测**只入库 SKILL.md，目录下的附带文档（references/ templates/ scripts/ 等全部丢失）**。凡源目录含 SKILL.md 以外文件的 skill，**必须走本地 zip 通道**；URL 通道仅适用于确认单文件的 skill。

## 输入参数

| 参数 | 必需 | 说明 |
|---|---|---|
| repo | 否 | `https://github.com/<owner>/<repo>`（默认扫 `skills/` 目录）；`.../tree/<ref>/<dir>`（指定目录，如 `.../tree/main/skills`） |
| only | 否 | 逗号分隔的 skill 名，只导入这些；省略 = 目录下全部 |

**清单模式（用户未给 repo 时）**：读取本技能目录下的 `sources.md`（用户手动维护的拉取清单），对表中每一行（仓库地址 + 可选 only）依次执行下述完整流程；逐行独立，单行失败不阻断其余行；汇总报告按来源分组。清单不存在或表中没有数据行时，提示用户先维护 `sources.md`，不要凭记忆猜测来源。

同名冲突默认**覆盖**（`--on-conflict overwrite`，保留技能 ID 与 agent 绑定，拉取即更新到仓库最新版）；用户明确要求"跳过/不更新已存在"时才用 `skip`。注意：overwrite 仅当当前用户是该技能的最初创建者时生效，非创建者会返回 `failed`（这是 Multica 服务端规则，无法绕过）。新工作区迁移场景：技能库为空，全部走 created，不会遇到冲突；同库重复拉取时，技能创建者与执行者同为运行时所有者，overwrite 正常生效。

## 步骤

1. **枚举**：列出 repo 目录下所有含 `SKILL.md` 的子目录（zread `get_repo_structure` 或 `gh api`）。仓库根没有 `skills/` 目录时，先向用户确认目录再继续。
2. **过滤**：按 only 过滤；only 中存在仓库里没有的名字时，明确报告，不静默忽略。only 与目录名匹配；导入后的入库技能名以 SKILL.md frontmatter 的 `name` 为准，两者不一致时在报告中注明。
3. **查重**：`multica skill list --output json` 取现有技能名集合，已存在的预标 overwrite（将更新）。
4. **下载源码**：`git clone --depth 1 <repo-url> <临时目录>`（指定了 ref 时 clone 后 `git checkout <ref>`；指定了子目录时后续步骤都在 `<临时目录>/<dir>` 下进行）。
5. **打包**：逐 skill 打 zip——zip 内**顶层就是 SKILL.md 与附带文件平级**（不打顶层目录）；排除 `.git` / `__pycache__` / `node_modules` 与 `.pyc`（超限对策，见陷阱表）：
   ```bash
   python - <<'EOF'
   import zipfile, os
   src = "<临时目录>/<dir>/<skill-dir>"
   with zipfile.ZipFile("./skill-<name>.zip", "w", zipfile.ZIP_DEFLATED) as z:
       for root, dirs, files in os.walk(src):
           dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "node_modules")]
           for f in files:
               if f.endswith((".pyc", ".zip")):
                   continue
               p = os.path.join(root, f)
               z.write(p, os.path.relpath(p, src))
   EOF
   ```
6. **导入**：前台串行执行，每个结果先落盘再解析：
   ```bash
   multica skill import --file "./skill-<name>.zip" \
     --on-conflict overwrite --output json > "./import-<name>.json" 2>&1
   jq -r '.status // "PARSE_FAIL"' "./import-<name>.json"
   ```
   `PARSE_FAIL` 时 cat 原始输出诊断，可重试一次；单个失败不阻断其余。
7. **校验补漏（强制，防附带文档丢失）**：对每个导入成功的 skill：
   - 枚举源目录文件清单，去掉 `SKILL.md` 本体，得应有效
   - `multica skill files list <skill-id> --output json` 得实有附件集
   - 缺失项逐个补传（源文件已在本地 clone 里，直接用）：
     ```bash
     multica skill files upsert <skill-id> --path "<zip内相对路径>" --content-file "<本地clone中的该文件>"
     ```
   - 补传后再 list 复核；数量仍不符的（超限被拒等）如实进报告
8. **汇总**：`multica skill list` 确认入库，输出汇总表（created / updated / skipped / failed + 原因 + **附件数 校验结果**），删除临时 json / zip / clone 目录。failed 且原因为非创建者时：报告该技能需由其创建者操作，或征得用户同意后改用 `skip` 保住现状。
9. **绑定（可选）**：用户指定 agent 时执行 `multica agent skills add <agent-id> --skill-ids <id>[,<id>]`（add 是追加式；**禁止用 set**，会清空该 agent 已有绑定），随后 `multica agent skills list <agent-id>` 验证。

## 陷阱（均为实测）

| 陷阱 | 对策 |
|---|---|
| **`--url` 直导只入库 SKILL.md，附带文档全丢**（qa/review/gstack 实测 0 附件；zip 通道实测完整） | 多文件 skill 一律本地 zip + 第 7 步校验补漏 |
| `skill files list` 只列附件，不含 SKILL.md 本体 | 校验对照时先从应有效中去掉 SKILL.md |
| 批量循环里 `$(...)` 内联管道 + jq 静默失败，造成大量假失败 | 结果一律先写文件再 jq 解析 |
| `npx skills add` | 装进外部本地环境而非 Multica 技能库，禁止使用 |
| 超限：单文件 1MiB / 每包 8MiB / 256 文件 / 上传 16MiB | 打包时排除 node_modules 等非说明书目录；仍超限的如实报告，不擅自拆改来源仓库 |
| `--on-conflict` 默认 fail，批量拉取遇重名即中断 | 批量场景显式传 overwrite（默认覆盖） |
| overwrite 遇到"非技能创建者"返回 failed | 属预期保护：报告原因，由创建者重跑或改用 skip |

## 边界

只做导入。用户要求"排除某 skill"= 不在 only 中列出即可；要求"删除/移除"库中已有技能是破坏性操作，确认意图后再走 `multica skill delete <id>`。
