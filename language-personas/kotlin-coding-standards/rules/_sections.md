# Section Definitions

## Null Safety (null-safety)
**Impact:** CRITICAL

Keep Kotlin's null guarantees intact, including at Java boundaries.

**Rules:**
- `null-safety-no-bang-bang` - Never use the non-null assertion !!
- `null-safety-no-platform-type-leak` - Declare nullability explicitly on values from Java

## Coroutines (coroutines)
**Impact:** CRITICAL

Give every coroutine an owner, honor cancellation, and keep blocking off event-loop threads.

**Rules:**
- `coroutines-flow-hot-vs-cold` - Expose cold Flow for streams and StateFlow for state
- `coroutines-inject-dispatchers` - Inject dispatchers instead of hard-coding them
- `coroutines-no-globalscope` - Never launch coroutines in GlobalScope
- `coroutines-no-runblocking-in-production` - Do not call runBlocking in production code
- `coroutines-rethrow-cancellation` - Rethrow CancellationException when catching broad exceptions

## Error Handling (error-handling)
**Impact:** HIGH

**Rules:**
- `error-handling-sealed-errors-over-exceptions` - Model expected failures as values, not exceptions

## Immutability (immutability)
**Impact:** HIGH

**Rules:**
- `immutability-read-only-collections-in-api` - Expose read-only collection types in public APIs
- `immutability-val-and-data-classes` - Default to val, immutable data classes and copy()

## Sealed Types (sealed)
**Impact:** HIGH

**Rules:**
- `sealed-when-exhaustive-no-else` - Use exhaustive when over sealed types with no else branch

## Serialization (serialization)
**Impact:** HIGH

**Rules:**
- `serialization-jackson-kotlin-module` - Register the Jackson Kotlin module or use kotlinx.serialization consistently

## Idioms (idioms)
**Impact:** MEDIUM

**Rules:**
- `idioms-limit-scope-function-nesting` - Do not nest or chain scope functions
- `idioms-named-arguments-for-flags` - Use named arguments for booleans and same-typed parameters

## API Design (api-design)
**Impact:** MEDIUM

**Rules:**
- `api-design-explicit-api-mode` - Enable explicit API mode for libraries and shared modules

## Java Interop (interop)
**Impact:** LOW

**Rules:**
- `interop-jvm-annotations-only-when-needed` - Add @Jvm annotations only when a Java caller needs them

## Documentation (docs)
**Impact:** LOW

**Rules:**
- `docs-kdoc-avoid-param-return-tags` - Write KDoc as prose and avoid @param and @return tags
