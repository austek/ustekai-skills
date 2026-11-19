# Section Definitions

## Anti-Patterns (anti-patterns)
**Impact:** CRITICAL

Recognize and eliminate recurring Java anti-patterns that erode correctness, encapsulation, and readability.

**Rules:**
- `anti-patterns-no-catch-throwable` - Never catch throwable or error
- `anti-patterns-no-god-classes` - Split god classes along responsibility boundaries
- `anti-patterns-no-magic-numbers` - Replace magic numbers and strings with named constants
- `anti-patterns-no-static-mutable-state` - Never expose mutable static state
- `anti-patterns-no-utility-class-overuse` - Don't default to static utility classes for behavior that belongs on a type

## Resource Management (resource-management)
**Impact:** CRITICAL

Acquire and release JVM and I/O resources deterministically, without leaks or hand-written cleanup.

**Rules:**
- `resource-management-autocloseable-implementation` - Implement AutoCloseable correctly for custom resource-holding classes
- `resource-management-no-manual-finally-close` - Never hand-write a finally block to close a resource
- `resource-management-try-with-resources` - Always use try-with-resources for AutoCloseable values

## Concurrency (concurrency)
**Impact:** HIGH

Coordinate shared state and background work safely across threads and virtual threads.

**Rules:**
- `concurrency-executor-service-lifecycle` - Always shut down an ExecutorService
- `concurrency-structured-concurrency` - Use StructuredTaskScope for fan-out/fan-in tasks
- `concurrency-scoped-values-over-threadlocal` - Use ScopedValue instead of ThreadLocal for per-request context

## API Design (api-design)
**Impact:** HIGH

Shape public class and method surfaces so they are hard to misuse.

**Rules:**
- `api-design-builder-for-many-params` - Use a builder when a constructor needs many parameters
- `api-design-fluent-method-chaining` - Design fluent APIs for method chaining where the domain fits
- `api-design-minimal-visibility` - Minimize the visibility of every class and member
- `api-design-no-boolean-parameter-trap` - Avoid the boolean parameter trap — name the choice
- `api-design-return-interface-not-impl` - Return the interface type, not the concrete implementation

## Error Handling (error-handling)
**Impact:** HIGH

Propagate, translate, and represent failures explicitly instead of hiding or discarding them.

**Rules:**
- `error-handling-checked-vs-unchecked` - Choose checked vs. unchecked exceptions deliberately
- `error-handling-custom-exception-hierarchy` - Design a purposeful custom exception hierarchy
- `error-handling-either-vavr` - Use Vavr either for expected, recoverable failures
- `error-handling-exception-translation-at-boundary` - Translate low-level exceptions at architectural boundaries
- `error-handling-no-swallowed-exceptions` - Never write an empty catch block

## Immutability (immutability)
**Impact:** HIGH

Default to immutable state and defensive construction to eliminate whole classes of bugs.

**Rules:**
- `immutability-builder-for-complex-construction` - Use the builder pattern for objects with many optional fields
- `immutability-defensive-copy` - Defensively copy mutable constructor inputs and getter outputs
- `immutability-final-fields` - Make fields final by default
- `immutability-records-for-data` - Prefer records over mutable POJOs for data carriers
- `immutability-unmodifiable-collections` - Use List.copyOf/Collections.unmodifiableX at API boundaries

## Object-Oriented Design (oo-design)
**Impact:** HIGH

Apply core object-oriented design principles for maintainable, extensible class hierarchies.

**Rules:**
- `oo-design-avoid-deep-inheritance-hierarchies` - Avoid deep inheritance hierarchies
- `oo-design-composition-over-inheritance` - Favor composition over inheritance
- `oo-design-dependency-injection-over-static-singletons` - Prefer dependency injection over static singletons
- `oo-design-favor-interfaces-for-abstraction` - Favor interfaces over abstract classes for abstraction
- `oo-design-single-responsibility` - Give each class a single responsibility

## Sealed Types & Pattern Matching (sealed-pattern)
**Impact:** HIGH

Model closed sets of variants with sealed types and exhaustive pattern matching.

**Rules:**
- `sealed-pattern-no-instanceof-chains` - Replace instanceof chains with exhaustive switch over a sealed type
- `sealed-pattern-permits-clause-explicit` - Write the permits clause explicitly when it aids readability
- `sealed-pattern-record-patterns` - Destructure sealed record hierarchies with record patterns
- `sealed-pattern-sealed-interface-over-enum-hierarchy` - Model closed variant sets as a sealed interface, not an enum-and-field hack
- `sealed-pattern-switch-exhaustiveness` - Switch exhaustively over sealed types — no default branch

## Javadoc (javadoc)
**Impact:** HIGH

Document public API contracts precisely, without narrating the signature.

**Rules:**
- `javadoc-markdown-comments` - Use Markdown doc comments for new code on JDK 23+
- `javadoc-no-signature-narration` - Never narrate the signature in a doc comment
- `javadoc-param-return-tags-only-when-non-obvious` - Write @param/@return tags only when they add information
- `javadoc-public-api-contract` - Document the contract, not the implementation, on public APIs
- `javadoc-summary-first` - Start every doc comment with a summary sentence
- `javadoc-throws-documentation` - Document every checked and meaningful unchecked throws

## Records (records)
**Impact:** HIGH

Use records correctly as immutable, validated data carriers.

**Rules:**
- `records-canonical-constructor-validation` - Validate invariants in the record's canonical constructor
- `records-compact-constructor-normalization` - Normalize component values in the compact constructor
- `records-implement-interface-for-behavior` - Implement an interface on a record to add shared behavior
- `records-no-mutable-fields` - Never give a record a mutable component or backing field

## Reflection & Serialization (reflection-serialization)
**Impact:** HIGH

Keep reflection and serialization at the edges of the system, configured explicitly.

**Rules:**
- `reflection-serialization-avoid-field-injection` - Prefer constructor injection over reflective field injection
- `reflection-serialization-avoid-for-business-logic` - Keep reflection out of business logic

## Modules (modules)
**Impact:** HIGH

Manage module and package boundaries deliberately across Gradle and JPMS.

**Rules:**
- `modules-api-vs-implementation-gradle-config` - Declare Gradle dependencies as api or implementation deliberately
- `modules-avoid-split-packages` - Never split one package across multiple modules
- `modules-jpms-explicit-exports` - Export only packages that are part of the public API

## Collections & Streams (collections-streams)
**Impact:** MEDIUM

Use the Collections and Stream APIs idiomatically, without redundant materialization or hidden side effects.

**Rules:**
- `collections-streams-avoid-redundant-materialization` - Avoid redundant materialization between stream stages
- `collections-streams-collectors-tox` - Pick the right collectors factory for the shape you need
- `collections-streams-list-of` - Prefer List.of/Set.of/Map.of over mutable factory methods
- `collections-streams-no-side-effects` - No mutation inside stream operations
- `collections-streams-parallel-stream-caution` - Reserve parallelStream() for CPU-bound, sizable, independent work
- `collections-streams-prefer-stream-pipeline` - Prefer stream pipelines over manual loops for transformations

## Generics (generics)
**Impact:** MEDIUM

Use Java generics safely, without raw types or unchecked casts.

**Rules:**
- `generics-avoid-generic-array-workarounds` - Avoid generic array creation workarounds — use List<T> instead
- `generics-bounded-wildcards` - Use bounded wildcards at API boundaries (PECS)
- `generics-generic-method-over-class` - Prefer a generic method over a generic class when only the method needs it
- `generics-no-raw-types` - Never use raw generic types
- `generics-no-unchecked-casts` - Avoid @SuppressWarnings("unchecked") casts outside factory internals

## Nullability (nullability)
**Impact:** MEDIUM

Represent absence explicitly with Optional at API boundaries, never as a field or parameter type.

**Rules:**
- `nullability-no-optional-collection` - Return an empty collection, never optional of a collection
- `nullability-no-optional-field` - Never use optional as a field type
- `nullability-no-optional-param` - Never accept optional as a method parameter
- `nullability-objects-requirenonnull` - Fail fast with Objects.requireNonNull at API boundaries
- `nullability-optional-return` - Return optional instead of null for absent values

## Performance (performance)
**Impact:** MEDIUM

Apply measured, targeted performance techniques instead of premature optimization.

**Rules:**
- `performance-array-vs-collection-hot-path` - Prefer primitive arrays over boxed collections in verified hot paths
- `performance-avoid-premature-optimization` - Measure before optimizing
- `performance-lazy-initialization` - Defer expensive initialization until first use
- `performance-stringbuilder-for-loops` - Use StringBuilder for string concatenation inside loops

## Naming (naming)
**Impact:** MEDIUM

Choose names that reveal intention and avoid encoding type or scope.

**Rules:**
- `naming-boolean-method-prefix` - Prefix boolean methods and fields with is/has/can
- `naming-consistent-getter-avoidance` - Avoid getX/setX naming for non-JavaBean types
- `naming-intention-revealing-names` - Choose intention-revealing names
- `naming-no-hungarian-notation` - Do not encode type or scope in names

## Modern Java 21–27 (modern-java)
**Impact:** MEDIUM

Adopt finalized language and library features by JDK version and keep preview features out of production.

**Rules:**
- `modern-java-ffm-over-jni` - Use the Foreign Function and Memory API instead of JNI
- `modern-java-flexible-constructor-bodies` - Validate arguments before super() with flexible constructor bodies
- `modern-java-no-final-field-mutation` - Do not mutate final fields through reflection
- `modern-java-no-preview-in-production` - Do not ship preview language features or APIs
- `modern-java-sequenced-collections` - Use sequenced collection methods for first, last and reversed access
- `modern-java-stream-gatherers` - Use stream gatherers for windowing and stateful steps
- `modern-java-unnamed-variables` - Name unused bindings with the unnamed variable _
