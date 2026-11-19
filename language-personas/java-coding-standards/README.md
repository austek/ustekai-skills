# Java Coding Standards

A comprehensive collection of Java coding standards and best practices, designed for AI agents and LLMs to generate high-quality Java code.

## Overview

This skill provides 82 rules across 18 categories (shared JVM rules live in `jvm-coding-standards`):

| Category | Prefix | Impact | Rules |
|----------|--------|--------|-------|
| Anti-Patterns | `anti-patterns-` | CRITICAL | 5 |
| Resource Management | `resource-management-` | CRITICAL | 4 |
| Concurrency | `concurrency-` | HIGH | 6 |
| API Design | `api-design-` | HIGH | 5 |
| Error Handling | `error-handling-` | HIGH | 5 |
| Immutability | `immutability-` | HIGH | 5 |
| Object-Oriented Design | `oo-design-` | HIGH | 5 |
| Sealed Types & Pattern Matching | `sealed-pattern-` | HIGH | 5 |
| Javadoc | `javadoc-` | HIGH | 4 |
| Records | `records-` | HIGH | 4 |
| Reflection & Serialization | `reflection-serialization-` | HIGH | 4 |
| Modules | `modules-` | HIGH | 3 |
| Collections & Streams | `collections-streams-` | MEDIUM | 6 |
| Generics | `generics-` | MEDIUM | 5 |
| Nullability | `nullability-` | MEDIUM | 5 |
| Performance | `performance-` | MEDIUM | 5 |
| Naming | `naming-` | MEDIUM | 4 |
| Modern Java (21–27) | `modern-java-` | MEDIUM | 7 |

## Structure

```
skills/java-coding-standards/
├── SKILL.md              # Skill overview with all rule summaries
├── metadata.json         # Metadata (version, description)
├── README.md             # This file
└── rules/
    ├── _sections.md      # Section definitions
    ├── _template.md      # Rule template
    ├── anti-patterns-*.md  # Anti-Patterns rules
    ├── resource-management-*.md # Resource Management rules
    ├── concurrency-*.md    # Concurrency rules
    ├── api-design-*.md     # API Design rules
    ├── error-handling-*.md # Error Handling rules
    ├── immutability-*.md   # Immutability rules
    ├── oo-design-*.md      # Object-Oriented Design rules
    ├── sealed-pattern-*.md # Sealed Types & Pattern Matching rules
    ├── javadoc-*.md        # Javadoc rules
    ├── records-*.md        # Records rules
    ├── reflection-serialization-*.md # Reflection & Serialization rules
    ├── modules-*.md        # Modules rules
    ├── collections-streams-*.md # Collections & Streams rules
    ├── generics-*.md       # Generics rules
    ├── nullability-*.md    # Nullability rules
    ├── performance-*.md    # Performance rules
    └── naming-*.md         # Naming rules
```

## Rules

### Anti-Patterns (CRITICAL)
- `anti-patterns-no-catch-throwable` - Never catch throwable or error
- `anti-patterns-no-god-classes` - Split god classes along responsibility boundaries
- `anti-patterns-no-magic-numbers` - Replace magic numbers and strings with named constants
- `anti-patterns-no-static-mutable-state` - Never expose mutable static state
- `anti-patterns-no-utility-class-overuse` - Don't default to static utility classes for behavior that belongs on a type

### Resource Management (CRITICAL)
- `resource-management-autocloseable-implementation` - Implement AutoCloseable correctly for custom resource-holding classes
- `resource-management-no-manual-finally-close` - Never hand-write a finally block to close a resource
- `resource-management-try-with-resources` - Always use try-with-resources for AutoCloseable values

### Concurrency (HIGH)
- `concurrency-executor-service-lifecycle` - Always shut down an ExecutorService
- `concurrency-structured-concurrency` - Use StructuredTaskScope for fan-out/fan-in tasks
- `concurrency-scoped-values-over-threadlocal` - Use ScopedValue instead of ThreadLocal for per-request context

### API Design (HIGH)
- `api-design-builder-for-many-params` - Use a builder when a constructor needs many parameters
- `api-design-fluent-method-chaining` - Design fluent APIs for method chaining where the domain fits
- `api-design-minimal-visibility` - Minimize the visibility of every class and member
- `api-design-no-boolean-parameter-trap` - Avoid the boolean parameter trap — name the choice
- `api-design-return-interface-not-impl` - Return the interface type, not the concrete implementation

### Error Handling (HIGH)
- `error-handling-checked-vs-unchecked` - Choose checked vs. unchecked exceptions deliberately
- `error-handling-custom-exception-hierarchy` - Design a purposeful custom exception hierarchy
- `error-handling-either-vavr` - Use Vavr either for expected, recoverable failures
- `error-handling-exception-translation-at-boundary` - Translate low-level exceptions at architectural boundaries
- `error-handling-no-swallowed-exceptions` - Never write an empty catch block

### Immutability (HIGH)
- `immutability-builder-for-complex-construction` - Use the builder pattern for objects with many optional fields
- `immutability-defensive-copy` - Defensively copy mutable constructor inputs and getter outputs
- `immutability-final-fields` - Make fields final by default
- `immutability-records-for-data` - Prefer records over mutable POJOs for data carriers
- `immutability-unmodifiable-collections` - Use List.copyOf/Collections.unmodifiableX at API boundaries

### Object-Oriented Design (HIGH)
- `oo-design-avoid-deep-inheritance-hierarchies` - Avoid deep inheritance hierarchies
- `oo-design-composition-over-inheritance` - Favor composition over inheritance
- `oo-design-dependency-injection-over-static-singletons` - Prefer dependency injection over static singletons
- `oo-design-favor-interfaces-for-abstraction` - Favor interfaces over abstract classes for abstraction
- `oo-design-single-responsibility` - Give each class a single responsibility

### Sealed Types & Pattern Matching (HIGH)
- `sealed-pattern-no-instanceof-chains` - Replace instanceof chains with exhaustive switch over a sealed type
- `sealed-pattern-permits-clause-explicit` - Write the permits clause explicitly when it aids readability
- `sealed-pattern-record-patterns` - Destructure sealed record hierarchies with record patterns
- `sealed-pattern-sealed-interface-over-enum-hierarchy` - Model closed variant sets as a sealed interface, not an enum-and-field hack
- `sealed-pattern-switch-exhaustiveness` - Switch exhaustively over sealed types — no default branch

### Javadoc (HIGH)
- `javadoc-markdown-comments` - Use Markdown doc comments for new code on JDK 23+
- `javadoc-no-signature-narration` - Never narrate the signature in a doc comment
- `javadoc-param-return-tags-only-when-non-obvious` - Write @param/@return tags only when they add information
- `javadoc-public-api-contract` - Document the contract, not the implementation, on public APIs
- `javadoc-summary-first` - Start every doc comment with a summary sentence
- `javadoc-throws-documentation` - Document every checked and meaningful unchecked throws

### Records (HIGH)
- `records-canonical-constructor-validation` - Validate invariants in the record's canonical constructor
- `records-compact-constructor-normalization` - Normalize component values in the compact constructor
- `records-implement-interface-for-behavior` - Implement an interface on a record to add shared behavior
- `records-no-mutable-fields` - Never give a record a mutable component or backing field

### Modern Java 21–27 (MEDIUM)
- `modern-java-ffm-over-jni` - Use the Foreign Function and Memory API instead of JNI
- `modern-java-flexible-constructor-bodies` - Validate arguments before super() with flexible constructor bodies
- `modern-java-no-final-field-mutation` - Do not mutate final fields through reflection
- `modern-java-no-preview-in-production` - Do not ship preview language features or APIs
- `modern-java-sequenced-collections` - Use sequenced collection methods for first, last and reversed access
- `modern-java-stream-gatherers` - Use stream gatherers for windowing and stateful steps
- `modern-java-unnamed-variables` - Name unused bindings with the unnamed variable _

### Reflection & Serialization (HIGH)
- `reflection-serialization-avoid-field-injection` - Prefer constructor injection over reflective field injection
- `reflection-serialization-avoid-for-business-logic` - Keep reflection out of business logic

### Modules (HIGH)
- `modules-api-vs-implementation-gradle-config` - Declare Gradle dependencies as api or implementation deliberately
- `modules-avoid-split-packages` - Never split one package across multiple modules
- `modules-jpms-explicit-exports` - Export only packages that are part of the public API

### Collections & Streams (MEDIUM)
- `collections-streams-avoid-redundant-materialization` - Avoid redundant materialization between stream stages
- `collections-streams-collectors-tox` - Pick the right collectors factory for the shape you need
- `collections-streams-list-of` - Prefer List.of/Set.of/Map.of over mutable factory methods
- `collections-streams-no-side-effects` - No mutation inside stream operations
- `collections-streams-parallel-stream-caution` - Reserve parallelStream() for CPU-bound, sizable, independent work
- `collections-streams-prefer-stream-pipeline` - Prefer stream pipelines over manual loops for transformations

### Generics (MEDIUM)
- `generics-avoid-generic-array-workarounds` - Avoid generic array creation workarounds — use List<T> instead
- `generics-bounded-wildcards` - Use bounded wildcards at API boundaries (PECS)
- `generics-generic-method-over-class` - Prefer a generic method over a generic class when only the method needs it
- `generics-no-raw-types` - Never use raw generic types
- `generics-no-unchecked-casts` - Avoid @SuppressWarnings("unchecked") casts outside factory internals

### Nullability (MEDIUM)
- `nullability-no-optional-collection` - Return an empty collection, never optional of a collection
- `nullability-no-optional-field` - Never use optional as a field type
- `nullability-no-optional-param` - Never accept optional as a method parameter
- `nullability-objects-requirenonnull` - Fail fast with Objects.requireNonNull at API boundaries
- `nullability-optional-return` - Return optional instead of null for absent values

### Performance (MEDIUM)
- `performance-array-vs-collection-hot-path` - Prefer primitive arrays over boxed collections in verified hot paths
- `performance-avoid-premature-optimization` - Measure before optimizing
- `performance-lazy-initialization` - Defer expensive initialization until first use
- `performance-stringbuilder-for-loops` - Use StringBuilder for string concatenation inside loops

### Naming (MEDIUM)
- `naming-boolean-method-prefix` - Prefix boolean methods and fields with is/has/can
- `naming-consistent-getter-avoidance` - Avoid getX/setX naming for non-JavaBean types
- `naming-intention-revealing-names` - Choose intention-revealing names
- `naming-no-hungarian-notation` - Do not encode type or scope in names

## Usage

This skill is automatically applied when working with Java files (`**/*.java`) and Java build files (`pom.xml`, `build.gradle`, `build.gradle.kts`).

## Rule Format

Each rule follows a consistent format:
- **Frontmatter**: title, impact level, tags
- **Description**: Why this rule matters
- **Bad Example**: Code to avoid
- **Good Example**: Recommended approach
- **Notes**: Additional tips and edge cases
- **References**: Documentation links

## Contributing

To add a new rule:
1. Copy `rules/_template.md`
2. Use the appropriate prefix (`anti-patterns-`, `resource-management-`, `concurrency-`, `api-design-`, `error-handling-`, `immutability-`, `oo-design-`, `sealed-pattern-`, `javadoc-`, `records-`, `reflection-serialization-`, `modules-`, `collections-streams-`, `generics-`, `nullability-`, `performance-`, `naming-`)
3. Follow the existing format
4. Update `_sections.md` and `SKILL.md`
