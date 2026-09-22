# 测试规范

> 测试相关变更须遵循；Tester 产出 test-report、Reviewer 审测试覆盖均按本文件。
> TDD 5 步铁律见仓库根 CLAUDE.md §7；本文件管「测什么、测到什么程度、没测怎么声明」。

## 项目现状声明

{{TESTING_STATUS}}

<!-- 分析指引：如实声明存量测试状况（有无测试目录/框架引入未用/覆盖率数据/CI 是否跑测试）；这是「新旧代码口径」的划分依据，**禁止粉饰**；存量缺口按风险列表（哪层没测=什么风险） -->

## 新旧代码口径

{{TESTING_NEW_OLD_POLICY}}

<!-- 分析指引：新代码（harness 流程开发）TDD 不降级、无测试的 task 不允许过 review；旧代码修改的降级条件（手工验证 + 完成评论显式声明缺口）；紧急 hotfix 的补测时限（如 24h） -->

## 单元测试

{{TESTING_UNIT_RULES}}

<!-- 分析指引：框架选型（JUnit5+Mockito+AssertJ 等）、测试类/方法命名、given-when-then 结构、覆盖要求（正常路径+边界+异常路径各至少 1）、mock 边界（依赖可 mock，**被测对象禁止 mock 自己证明自己**）、用户上下文/静态工具的桩处理 -->

## 集成与接口测试

{{TESTING_INTEGRATION_RULES}}

<!-- 分析指引：何时需要集成测试、工具（@SpringBootTest/Testcontainers 等）、测试库策略；项目无集成测试基础设施时如实声明替代手段（EXPLAIN PLAN + 联调环境）并标注为技术债 -->

## 浏览器 QA（页面/流程类验收点）

> 与 Multica 侧 `aicoding-browser-qa` skill 同源（权威源在 skill）——本段是零依赖兜底口径，改双处同改。执行细节（browse 命令、报告模板）以 skill 为准。

**三档深度**：Quick（critical+high，冒烟）/ Standard（+medium，change 级验收，缺省）/ Exhaustive（+low，发布前）。

**severity 四级**：critical（阻断核心流程/数据丢失/崩溃）→ high（主要功能不可用无绕行）→ medium（可用有明显问题有绕行）→ low（外观小疵）。

**问题七类**：Visual/UI、Functional、UX、Content、Performance、Console/Errors、Accessibility。

**每页 8 步清单**：① 视觉扫描 ② 逐交互点击 ③ 表单（空提交/非法值/边界）④ 导航（进出/回退）⑤ 状态（空/加载/错误/溢出）⑥ Console 新增错误 ⑦ 响应式（按验收点）⑧ 账号边界（登录只用 Tester env 的测试账号 TEST_ACCOUNT，不切角色账号）。

**环境阻塞判定**：验收点菜单不可见或接口报 SEC-00021 → 角色未绑定新模块权限（绑定目标角色 = Tester env 的 TEST_ROLE），属环境阻塞非缺陷——记报告「环境阻塞」节提醒发起人绑定，不进问题清单、不影响健康评分。

**报告要求**：健康评分（基线 100，critical -25 / high -10 / medium -4 / low -1）+ 环境阻塞节（无/有+待办）+ 分级问题表（每条带截图证据与复现步骤）+ ship-readiness 结论；浏览器基座不可用或测试账号未配置（env 缺 TEST_ACCOUNT/TEST_PASSWORD）时按本清单手测并显式声明「降级」。

<!-- 分析指引：纯后端/无页面的项目删除本节；sunny 系前端保留并在表单专项处补 SunnyForm/EditGrid 检查点 -->

## 禁止的反模式

- {{TESTING_ANTIPATTERN}}

<!-- 分析指引：空测试/只为过 CI 的测试、只测 happy path、hardcode 业务 ID、mock 自己写的代码、忽略失败测试等，逐条 ❌ 附正确做法 -->

## 未测试缺口声明（格式模板）

```markdown
### 未测试说明
- {模块/方法}的{分支}：{手工验证覆盖方式/未覆盖原因}
- {已知风险}：{建议补测时点}
```

<!-- 分析指引：任何未覆盖路径必须在完成评论/PR 摘要按此格式显式声明；新代码无理由不写测试不允许过 review，缺口声明只适用于旧代码修改与降级场景 -->
