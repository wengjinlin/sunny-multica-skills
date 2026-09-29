# 第②步拉取通道：技能批量入库（精简固定版）

> 场景固定（新工作区首装），方法论提炼自 aicoding-skills-bootstrap skill。本文档自带完整操作步骤，**不依赖**该 skill 已挂载——本步执行时技能库里只有本 skill（鸡生蛋），全部操作只用 `git` / `multica` CLI 与本文档。

## 来源（固定两个）

| 来源 | 仓库 | 范围 |
|---|---|---|
| 主 | `https://github.com/wengjinlin/sunny-multica-skills` | `skills/` 与 `bootstrap/` 下全部含 SKILL.md 的目录 |
| 辅 | `https://github.com/obra/superpowers` | 仓库内全部含 SKILL.md 的目录（Tech-Lead / Developer 的 plan / TDD 能力依赖） |

## 步骤

1. **克隆**：逐来源 `git clone --depth 1 <repo-url> <临时目录>`（临时目录用完即删，不得进 `.gitignore` 管辖外的仓库目录——用系统临时路径）。

2. **枚举**：对每个 clone 目录 glob `**/SKILL.md`（不预设目录层级，结构无关），每个命中的父目录即一个 skill 目录。

3. **打包**：逐 skill 打 zip——zip 内**顶层就是 SKILL.md 与附带文件平铺**（不打顶层目录）；排除 `.git` / `__pycache__` / `node_modules` 与 `.pyc` / `.zip`：

   ```bash
   python - <<'EOF'
   import zipfile, os
   src = "<clone临时目录>/<skill目录>"
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

4. **导入**：前台串行执行，每个结果**先落盘再解析**：

   ```bash
   multica skill import --file "./skill-<name>.zip" \
     --on-conflict overwrite --output json > "./import-<name>.json" 2>&1
   jq -r '.status // "PARSE_FAIL"' "./import-<name>.json"
   ```

   `PARSE_FAIL` 时 cat 原始输出诊断，可重试一次；**单个失败不阻断其余**。新工作区首装技能库为空，全部走 created，不会遇到覆盖冲突。

5. **附件校验补漏（强制，防附带文档丢失）**：对每个导入成功的 skill：
   - 枚举源目录文件清单，去掉 `SKILL.md` 本体，得**应有效**
   - `multica skill files list <skill-id> --output json` 得**实有附件集**
   - 缺失项逐个补传（源文件已在本地 clone 里，直接用）：

     ```bash
     multica skill files upsert <skill-id> --path "<zip内相对路径>" --content-file "<本地clone中的该文件>"
     ```

   - 补传后再 list 复核；数量仍不符的（超限被拒等）如实进报告

6. **挂载（本 skill 执行者 Mika 自用，后续步骤 Skill 调用依赖）**：
   - `multica skill list --output json` 按 name 解析 id（共 6 个：`aicoding-skills-bootstrap` / `aicoding-agent-bootstrap` / `aicoding-project-init` / `aicoding-orchestration-bootstrap` / `aicoding-harness-bootstrap` / `aicoding-db-schema-export`）
   - `multica agent list --output json` 取 Mika 的 UUID
   - `multica agent skills add <Mika-UUID> --skill-ids <上述6个id逗号列表>`
   - `add` 是追加式；**禁止用 set**，会清空该 agent 已有绑定
   - 缺失的 skill（导入失败的那几个）：只登记不阻断，留给终局报告的缺失登记

7. **汇总**：`multica skill list` 确认入库，输出汇总表（created / updated / failed + 原因 + 附件校验结果）；删除临时 json / zip / clone 目录。

## 陷阱（均为 aicoding-skills-bootstrap 实测，适用项照搬）

| 陷阱 | 对策 |
|---|---|
| `--url` 直导只入库 SKILL.md，附带文档全丢 | 一律本地 zip + 第 5 步校验补漏 |
| `skill files list` 只列附件，不含 SKILL.md 本体 | 校验对照时先从应有效中去掉 SKILL.md |
| 批量循环里 `$(...)` 内联管道 + jq 静默失败，造成大量假失败 | 结果一律先写文件再 jq 解析 |
| 超限：单文件 1MiB / 每包 8MiB / 256 文件 / 上传 16MiB | 打包排除 node_modules 等非说明书目录；仍超限的如实报告，不擅自拆改来源仓库 |
| `--on-conflict` 默认 fail，批量拉取遇重名即中断 | 批量场景显式传 overwrite |
| `npx skills add` | 装进外部本地环境而非 Multica 技能库，禁止使用 |
