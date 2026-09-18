# {{PROJECT_NAME}} 项目宪法

---

## 0. 适用范围

本文件是本仓库的统一 harness 宪法，**覆盖仓库所有目录与 {{MODULE_COUNT}} 个模块**（{{MODULE_LIST}}）。子模块内不再单独维护 CLAUDE.md / AGENTS.md / REVIEW.md——所有 agent 在仓库根 cwd 运行，统一读这套文档。

<!-- 分析指引：列出全部模块目录名；单模块项目删掉「模块」措辞 -->

---

## 1. 项目定位

**{{PROJECT_NAME}} 是{{BUSINESS_DESCRIPTION}}**，以{{REPO_STRUCTURE}}结构组织。

<!-- 分析指引：一句话业务定位（问用户或从 README 提取）；结构要点：有无顶层父 pom / monorepo / 聚合构建；各模块构建方式 -->

---

## 2. 模块结构表

| 模块 | 类型 | 技术栈 | 端口 |
|---|---|---|---|
| {{MODULE_ROW}} | {{...}} | {{...}} | {{...}} |

**模块定位字典**（业务域 ↔ 模块 ↔ 数据库主表前缀）：见 `docs/architecture/index.md` §1——需求落域、代码落位、表定位一律查该表，本表只做结构概览。

<!-- 分析指引：每个模块一行，从 pom.xml/package.json 提取依赖与版本，端口从配置文件提取；前端模块「技术栈」列必须写明 Vue 2 / Vue 3 + 组件库（如 Vue3+Arco）——这是前端设计第零步版本判断的权威源 -->

---

## 3. 通信与基础设施

- {{INFRASTRUCTURE_ITEMS}}

<!-- 分析指引：逐条列出（有才写）：前后端代理、服务互调/注册中心、数据库、缓存、消息队列、对象存储、流程引擎、外部系统接口、私服/内网依赖。地址可写，凭据永不写 -->

---

## 4. 构建命令

- {{BUILD_COMMANDS}}

<!-- 分析指引：前端/后端各自构建命令；明确「是否有顶层聚合构建」——没有则强调必须先 cd 到模块 -->

---

## 5. 构建工具路径约定

{{BUILD_TOOL_PATH}}

<!-- 分析指引：Maven/JDK 等本机路径与版本约定；无特殊约定的项目可删本节 -->

---

## 6. OpenSpec 工作流（强制顺序）

无论是否使用自定义 schema，必须按以下顺序创建 artifact：

```
proposal → specs → design → tasks
```

| 顺序 | Artifact | 核心问题 |
|------|----------|----------|
| 1 | proposal | WHY — 为什么做 |
| 2 | specs | WHAT — 做什么 |
| 3 | design | HOW — 怎么做 |
| 4 | tasks | 执行 |

**判断口诀：先需求后设计，先 WHAT 后HOW。** 即使多个 artifact 同时 ready，也必须先 specs 后 design。

---

## 7. TDD 强约束

TDD 由 **superpowers:test-driven-development skill** 执行：Tech-Lead 产出的 plan.md 步骤已内含下述 5 步，Developer 逐条走红绿循环，Reviewer 按测试先行证据把关。5 步口径：

1. 写失败测试
2. 确认测试失败
3. 实现代码
4. 确认测试通过
5. 提交

`openspec/config.yaml` 中 `tdd_enforcement: strict`，跳步会被 Reviewer 打回。

---

## 8. 分层规则

{{LAYERING_RULES}}

<!-- 分析指引：抽样现有代码归纳（每类 ≥3 例）：分层链路、各层命名约定、Entity/DTO 规则、允许/禁止的用法。无分层传统的新项目则写目标分层规则并标注「新建约定」 -->

---

## 9. 平台包优先级

{{PLATFORM_PACKAGES}}

<!-- 分析指引：若存在自研/二方平台包体系：场景→用平台包→不要引入的映射表；无则删本节 -->

---

## 10. 保护目录（写入会被 hook 拒绝）

以下路径 **禁止** Edit/Write，由 `.claude/hooks/guard_write.py` 拦截：

{{PROTECTED_PATHS}}

<!-- 分析指引：默认清单 application*.yml / db / sql / settings.xml / pom.xml，按仓库实际调整，须与 hook 的 PROTECTED_PATTERNS 一致 -->

如需变更，必须在 `design.md` 中显式声明，并经 Reviewer 审核通过。

---

## 11. 命名约定提醒（重要）

{{NAMING_RED_LINE}}；拼音/缩写对照见 `docs/architecture/implicit-contracts.md`，接口与数据库命名详单见 `docs/standards/api.md` / `docs/standards/database.md`。

<!-- 分析指引：只写一句话红线（如「业务路径拼音缩写禁止幻觉式重命名」）；详单与 checklist 全部进 standards/，本节不展开 -->

---

## 12. 统一响应格式

后端响应统一 {{RESPONSE_WRAPPER}} 包装；结构、错误码段、分页字段等前端硬依赖详见 `docs/standards/api.md`，违反即打回。

<!-- 分析指引：只写包装类一句话（如 Result<T>）；字段级约定进 standards/api.md；无后端则删本节 -->

---

## 13. 日志规范

{{LOGGING_RED_LINE}}；级别/必含要素/异常处理详单见 `docs/standards/api.md` 日志节。

<!-- 分析指引：只写一句话红线（注解/级别要求）；无特殊约定可删本节 -->

---

## 14. 平台能力帮助文档（docs/help/）

- **涉及平台集成的需求（{{CAPABILITY_LIST}}）**：先读 `docs/help/index.md` 能力清单，再读对应能力文档，按文档方式实现
- **适用时点**：PM 写 proposal/design（技术可行性与 HOW、超时/重试/降级策略）、Developer 实现前、Reviewer 审查时——均按此路由
- `index.md` 的「通用约定」与「受保护/慎用清单」视同宪法红线，违反会被 Reviewer 打回
- 新平台能力的使用经验：可复用的做法补 `docs/help/` 对应文档；一次性踩坑进 `docs/lessons/` 对应角色文件

---

## 15. 文档体系入口

- `docs/index.md` 是 docs/ 唯一导航入口（各角色必读顺序 + 文档维护规则）；本宪法只保留红线，详单都在 docs/ 下
- 常用定位：业务域/术语 → `docs/product/index.md`；模块↔表前缀 → `docs/architecture/index.md` §1；表结构 → `docs/database/index.md`；测试口径 → `docs/standards/testing.md`
- 文档随 change 同步更新（Tech-Lead 安排 task），不允许「事后补文档」
