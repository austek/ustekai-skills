# Section Definitions

## Testcontainers (testcontainers)
**Impact:** HIGH

Run real dependencies in tests with correctly scoped container lifecycle and explicit wait strategies.

**Rules:**
- `testcontainers-container-reuse` - Reuse containers across a test run instead of restarting per class
- `testcontainers-lifecycle-scope` - Match container lifecycle scope to what the container represents
- `testcontainers-wait-strategy-explicit` - Declare an explicit wait strategy for every container
