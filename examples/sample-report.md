## AI Code Review Gate

Scanned **10** file(s); found **5** issue(s).

### 🔴 CRITICAL (1)

| File | Line | Rule | Message |
| --- | --- | --- | --- |
| `SqlConcat.java` | 8 | `java.security.sql-injection-concat` | SQL string concatenated with variable 'userId'; this enables SQL injection. Use a PreparedStatement with '?' bind parameters. |

### 🟠 HIGH (2)

| File | Line | Rule | Message |
| --- | --- | --- | --- |
| `ResourceLeak.java` | 6 | `java.resource.leak-try-without-resources` | I/O resource created outside try-with-resources; use try (var in = new FileInputStream(...)) to guarantee closing. |
| `UnsafeSimpleDateFormat.java` | 4 | `java.thread-safety.static-simple-date-format` | SimpleDateFormat is not thread-safe; do not share it via a static field. Use a ThreadLocal, java.time.DateTimeFormatter, or create a new instance per use. |

### 🟡 MEDIUM (2)

| File | Line | Rule | Message |
| --- | --- | --- | --- |
| `BadNPE.java` | 3 | `java.npe.optional-chaining-needed` | Chained call 'user.getAddress().getCity()' may throw NPE: 'user' has no null/Optional guard. Use Optional.ofNullable(user).orElse(...) or an explicit null check. |
| `TxSwallowedException.java` | 7 | `java.tx.swallowed-exception` | @Transactional method catches an exception but never rethrows; the transaction will commit despite the failure. Rethrow or declare rollbackFor = Exception.class. |

