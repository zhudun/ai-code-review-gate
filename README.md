# ai-code-review-gate

> **让人能审查 AI 写的代码。** 一个跑在 PR 合并前的自动化门禁：用**确定性规则**把 AI 生成代码里的高风险模式揪出来，LLM 只做可选增强。

![version](https://img.shields.io/badge/version-0.1.0-blue)
![license](https://img.shields.io/badge/license-MIT-green)
![python](https://img.shields.io/badge/python-3.12-yellow)
![tests](https://img.shields.io/badge/tests-17%20passing-brightgreen)

---

## 为什么需要它

AI 编程助手（Cursor / Copilot / Claude Code 等）让写代码变快了，但也把风险藏进了黑盒：它会"顺手"写出一段看起来很对、实则埋雷的实现。最典型的几类：

- **NPE 链式调用**：`user.getAddress().getCity().getName()`，中间对象可能为 `null`。
- **资源泄漏**：`new FileInputStream(...)` 写在普通 `try { }` 里，忘了 `try-with-resources`。
- **线程安全**：把非线程安全的 `SimpleDateFormat` 做成 `static` 字段，高并发下偶发崩溃。
- **SQL 注入**：用字符串 `"select ... where id = " + userId` 拼 SQL。
- **事务边界**：`@Transactional` 方法里 `catch` 后只打日志不 rethrow，事务照样提交，数据不一致。
- **弱随机数**：在生成 token/密码时用 `new Random()` 而不是 `SecureRandom`。

我们的立场不是"不让 AI 写代码"，而是**在合并前把住这道关**。本工具用零依赖、可判定的规则在 CI 里秒级跑完，把上面这些模式直接标红。

## 与同类项目的取舍对比

| 维度 | alibaba/open-code-review | NVIDIA/SkillSpector | anthropics/claude-code-security-review | **ai-code-review-gate（本项目）** |
| --- | --- | --- | --- | --- |
| 定位 | 确定性管道 + LLM Agent 混合审查 | 安装/合并前扫描提示注入与供应链风险 | GitHub Action 内轻量安全审查 | **PR 合并前的"AI 代码反黑盒"门禁** |
| 规则确定性 | 多语言规则集（NPE/线程安全/XSS/SQLi） | 偏提示词/供应链 | 偏安全提示，规则较少 | **Java 优先的轻量确定性规则集** |
| LLM 依赖 | 重度依赖 LLM Agent | 可选 | 依赖 Claude | **可离线运行；LLM 仅可选增强，无 key 优雅跳过** |
| 语言 | 多语言 | 通用 | 通用 | **Java 优先，预留多语言扩展点** |
| 集成方式 | 平台/服务 | 扫描器 | GitHub Action | **纯 Python CLI + Composite Action + SARIF** |
| 体积 | 重 | 中 | 中 | **纯标准库，Action 轻量，秒级完成** |

**本项目取舍**：确定性规则优先、可离线、可测试、体积小；LLM 不进入主路径，只在配了 `OPENAI_API_KEY` 时额外组装提示词，绝不阻塞门禁。

## 快速开始

```bash
# 本地安装（core 零运行时依赖，仅测试需要 pytest）
pip install -e .

# 扫描一个目录，输出 Markdown 报告
python -m ai_code_review_gate scan ./src --format markdown

# JSON / SARIF（供 GitHub Code Scanning）
python -m ai_code_review_gate scan ./src --format json
python -m ai_code_review_gate scan ./src --format sarif

# CI 门禁：存在 >= 指定严重级别问题时退出码为 1
python -m ai_code_review_gate scan ./src --format sarif --fail-on medium
```

对仓库内自带样例跑一次，真实输出如下（见 [`examples/sample-report.md`](examples/sample-report.md)）：

```text
## AI Code Review Gate

Scanned **10** file(s); found **5** issue(s).

### 🔴 CRITICAL (1)
| File | Line | Rule | Message |
| --- | --- | --- | --- |
| `SqlConcat.java` | 8 | `java.security.sql-injection-concat` | SQL string concatenated with variable 'userId'... |

### 🟠 HIGH (2)
| `ResourceLeak.java` | 6 | `java.resource.leak-try-without-resources` | I/O resource created outside try-with-resources... |
| `UnsafeSimpleDateFormat.java` | 4 | `java.thread-safety.static-simple-date-format` | SimpleDateFormat is not thread-safe... |

### 🟡 MEDIUM (2)
| `BadNPE.java` | 3 | `java.npe.optional-chaining-needed` | Chained call 'user.getAddress().getCity()' may throw NPE... |
| `TxSwallowedException.java` | 7 | `java.tx.swallowed-exception` | @Transactional method catches an exception but never rethrows... |
```

没有任何问题时输出 `✅ No findings.`，退出码为 `0`。

## GitHub Action 接入

`.github/workflows/review-gate.yml` 已给出可复制即用的配置：

```yaml
name: AI Code Review Gate
on: [pull_request]
permissions:
  contents: read
  security-events: write
jobs:
  review-gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ./                       # 本仓库的 composite action
        with:
          fail-on: medium
          scan-path: .
```

Action 内部执行 `pip install .` 后运行 `python -m ai_code_review_gate scan . --format sarif --fail-on medium`，并把 SARIF 上传到 GitHub Code Scanning，结果直接出现在 PR 的 "Files changed" 行内标注里。

## 内置规则清单

| rule_id | 严重级别 | 检测内容 | 反例（会被标记） |
| --- | --- | --- | --- |
| `java.security.sql-injection-concat` | **critical** | SQL 字符串拼接非字面量变量 | `"select * from t where id = " + userId` |
| `java.resource.leak-try-without-resources` | **high** | I/O 资源未用 try-with-resources | `FileInputStream in = new FileInputStream(f);` 在普通 `try{}` 中 |
| `java.thread-safety.static-simple-date-format` | **high** | 非线程安全类做 static 共享状态 | `private static final SimpleDateFormat SDF = ...` |
| `java.npe.optional-chaining-needed` | **medium** | 三链式调用无 null/Optional 防护 | `user.getAddress().getCity().getName()` |
| `java.tx.swallowed-exception` | **medium** | `@Transactional` 吞异常不回滚 | `catch (Exception e) { log.error(...); }` 无 rethrow、无 `rollbackFor` |
| `java.security.weak-random` | **medium** | 弱随机数用于敏感场景 | `String token = ... new Random().nextLong() ...` 附近出现 password/token/secret |

## 架构

```
CLI (cli.py)
   │  argparse: scan <path> [--format] [--fail-on]
   ▼
RuleEngine (engine.py)
   │  递归发现 .java 文件 → 读一次文本 → 跑所有适用规则 → 聚合 Finding
   ▼
BaseRule (rules/base.py)
   │  id / languages / severity / applies() / check() -> list[Finding]
   ▼
Java Rules (rules/java/*.py)          Report (report/*.py)
   NPE / ResourceLeak / ThreadSafe      markdown / json / sarif
   / SQLi / Transaction / Random
            │
            └── llm/advisor.py（可选：无 OPENAI_API_KEY 时返回空列表，绝不阻塞）
```

**为什么确定性规则优先**：CI 门禁要求可重复、可离线、零误依赖。规则全部基于标准库（`re` + 行级启发式），不引入重型静态分析器，Action 体积小、秒级完成。**LLM 只做可选增强**：`llm/advisor.py` 只负责组装提示词，未配置 key 时直接返回空列表，门禁结果永远由确定性规则决定。

## 路线图

- **多语言扩展**：Python（危险 `eval` / 可变默认参数 / 路径拼接）、TypeScript（`any` / `dangerouslySetInnerHTML`）。
- **SARIF 看板**：在 PR 评论里按文件聚合展示趋势。
- **MCP 集成**：把规则引擎暴露为 MCP server，供 Claude Code 等在编码时即时反馈。
- **自定义规则 SDK**：让用户以一个子类即可新增规则，无需改引擎。

## 开发与测试

```bash
pip install -e . pytest
python -m pytest -q     # 全部测试实际跑通
```

## License

[MIT](./LICENSE)
