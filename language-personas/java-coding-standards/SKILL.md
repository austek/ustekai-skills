---
name: java-coding-standards
description: Java coding standards and best practices covering anti-patterns, resource management, concurrency, API design, error handling, immutability, object-oriented design, sealed types and pattern matching, Javadoc, records, reflection/serialization, modules, collections/streams, generics, nullability, performance, and naming. Use when writing, reviewing, or refactoring Java code, or when the user asks about Java style, design, or best practices.
paths:
  - "**/*.java"
  - "pom.xml"
  - "build.gradle"
  - "build.gradle.kts"
---

# Java Coding Standards

A comprehensive collection of Java coding standards and best practices. Designed for AI agents and LLMs to generate high-quality, idiomatic, and maintainable Java code.

## Categories

### Anti-Patterns [CRITICAL]
Recognize and eliminate recurring Java anti-patterns that erode correctness, encapsulation, and readability.

| Rule | Description |
|------|-------------|
| [anti-patterns-no-catch-throwable](rules/anti-patterns-no-catch-throwable.md) | Never catch throwable or error |
| [anti-patterns-no-god-classes](rules/anti-patterns-no-god-classes.md) | Split god classes along responsibility boundaries |
| [anti-patterns-no-magic-numbers](rules/anti-patterns-no-magic-numbers.md) | Replace magic numbers and strings with named constants |
| [anti-patterns-no-static-mutable-state](rules/anti-patterns-no-static-mutable-state.md) | Never expose mutable static state |
| [anti-patterns-no-utility-class-overuse](rules/anti-patterns-no-utility-class-overuse.md) | Don't default to static utility classes for behavior that belongs on a type |

### Resource Management [CRITICAL]
Acquire and release JVM and I/O resources deterministically, without leaks or hand-written cleanup.

| Rule | Description |
|------|-------------|
| [resource-management-autocloseable-implementation](rules/resource-management-autocloseable-implementation.md) | Implement AutoCloseable correctly for custom resource-holding classes |
| [resource-management-no-manual-finally-close](rules/resource-management-no-manual-finally-close.md) | Never hand-write a finally block to close a resource |
| [resource-management-try-with-resources](rules/resource-management-try-with-resources.md) | Always use try-with-resources for AutoCloseable values |

### Concurrency [HIGH]
Coordinate shared state and background work safely across threads and virtual threads.

| Rule | Description |
|------|-------------|
| [concurrency-executor-service-lifecycle](rules/concurrency-executor-service-lifecycle.md) | Always shut down an ExecutorService |
| [concurrency-structured-concurrency](rules/concurrency-structured-concurrency.md) | Use StructuredTaskScope for fan-out/fan-in tasks |
| [concurrency-scoped-values-over-threadlocal](rules/concurrency-scoped-values-over-threadlocal.md) | Use ScopedValue instead of ThreadLocal for per-request context |

### API Design [HIGH]
Shape public class and method surfaces so they are hard to misuse.

| Rule | Description |
|------|-------------|
| [api-design-builder-for-many-params](rules/api-design-builder-for-many-params.md) | Use a builder when a constructor needs many parameters |
| [api-design-fluent-method-chaining](rules/api-design-fluent-method-chaining.md) | Design fluent APIs for method chaining where the domain fits |
| [api-design-minimal-visibility](rules/api-design-minimal-visibility.md) | Minimize the visibility of every class and member |
| [api-design-no-boolean-parameter-trap](rules/api-design-no-boolean-parameter-trap.md) | Avoid the boolean parameter trap — name the choice |
| [api-design-return-interface-not-impl](rules/api-design-return-interface-not-impl.md) | Return the interface type, not the concrete implementation |

### Error Handling [HIGH]
Propagate, translate, and represent failures explicitly instead of hiding or discarding them.

| Rule | Description |
|------|-------------|
| [error-handling-checked-vs-unchecked](rules/error-handling-checked-vs-unchecked.md) | Choose checked vs. unchecked exceptions deliberately |
| [error-handling-custom-exception-hierarchy](rules/error-handling-custom-exception-hierarchy.md) | Design a purposeful custom exception hierarchy |
| [error-handling-either-vavr](rules/error-handling-either-vavr.md) | Use Vavr either for expected, recoverable failures |
| [error-handling-exception-translation-at-boundary](rules/error-handling-exception-translation-at-boundary.md) | Translate low-level exceptions at architectural boundaries |
| [error-handling-no-swallowed-exceptions](rules/error-handling-no-swallowed-exceptions.md) | Never write an empty catch block |

### Immutability [HIGH]
Default to immutable state and defensive construction to eliminate whole classes of bugs.

| Rule | Description |
|------|-------------|
| [immutability-builder-for-complex-construction](rules/immutability-builder-for-complex-construction.md) | Use the builder pattern for objects with many optional fields |
| [immutability-defensive-copy](rules/immutability-defensive-copy.md) | Defensively copy mutable constructor inputs and getter outputs |
| [immutability-final-fields](rules/immutability-final-fields.md) | Make fields final by default |
| [immutability-records-for-data](rules/immutability-records-for-data.md) | Prefer records over mutable POJOs for data carriers |
| [immutability-unmodifiable-collections](rules/immutability-unmodifiable-collections.md) | Use List.copyOf/Collections.unmodifiableX at API boundaries |

### Object-Oriented Design [HIGH]
Apply core object-oriented design principles for maintainable, extensible class hierarchies.

| Rule | Description |
|------|-------------|
| [oo-design-avoid-deep-inheritance-hierarchies](rules/oo-design-avoid-deep-inheritance-hierarchies.md) | Avoid deep inheritance hierarchies |
| [oo-design-composition-over-inheritance](rules/oo-design-composition-over-inheritance.md) | Favor composition over inheritance |
| [oo-design-dependency-injection-over-static-singletons](rules/oo-design-dependency-injection-over-static-singletons.md) | Prefer dependency injection over static singletons |
| [oo-design-favor-interfaces-for-abstraction](rules/oo-design-favor-interfaces-for-abstraction.md) | Favor interfaces over abstract classes for abstraction |
| [oo-design-single-responsibility](rules/oo-design-single-responsibility.md) | Give each class a single responsibility |

### Sealed Types & Pattern Matching [HIGH]
Model closed sets of variants with sealed types and exhaustive pattern matching.

| Rule | Description |
|------|-------------|
| [sealed-pattern-no-instanceof-chains](rules/sealed-pattern-no-instanceof-chains.md) | Replace instanceof chains with exhaustive switch over a sealed type |
| [sealed-pattern-permits-clause-explicit](rules/sealed-pattern-permits-clause-explicit.md) | Write the permits clause explicitly when it aids readability |
| [sealed-pattern-record-patterns](rules/sealed-pattern-record-patterns.md) | Destructure sealed record hierarchies with record patterns |
| [sealed-pattern-sealed-interface-over-enum-hierarchy](rules/sealed-pattern-sealed-interface-over-enum-hierarchy.md) | Model closed variant sets as a sealed interface, not an enum-and-field hack |
| [sealed-pattern-switch-exhaustiveness](rules/sealed-pattern-switch-exhaustiveness.md) | Switch exhaustively over sealed types — no default branch |

### Javadoc [HIGH]
Document public API contracts precisely, without narrating the signature.

| Rule | Description |
|------|-------------|
| [javadoc-markdown-comments](rules/javadoc-markdown-comments.md) | Use Markdown doc comments for new code on JDK 23+ |
| [javadoc-no-signature-narration](rules/javadoc-no-signature-narration.md) | Never narrate the signature in a doc comment |
| [javadoc-param-return-tags-only-when-non-obvious](rules/javadoc-param-return-tags-only-when-non-obvious.md) | Write @param/@return tags only when they add information |
| [javadoc-public-api-contract](rules/javadoc-public-api-contract.md) | Document the contract, not the implementation, on public APIs |
| [javadoc-summary-first](rules/javadoc-summary-first.md) | Start every doc comment with a summary sentence |
| [javadoc-throws-documentation](rules/javadoc-throws-documentation.md) | Document every checked and meaningful unchecked throws |

### Records [HIGH]
Use records correctly as immutable, validated data carriers.

| Rule | Description |
|------|-------------|
| [records-canonical-constructor-validation](rules/records-canonical-constructor-validation.md) | Validate invariants in the record's canonical constructor |
| [records-compact-constructor-normalization](rules/records-compact-constructor-normalization.md) | Normalize component values in the compact constructor |
| [records-implement-interface-for-behavior](rules/records-implement-interface-for-behavior.md) | Implement an interface on a record to add shared behavior |
| [records-no-mutable-fields](rules/records-no-mutable-fields.md) | Never give a record a mutable component or backing field |

### Reflection & Serialization [HIGH]
Keep reflection and serialization at the edges of the system, configured explicitly.

| Rule | Description |
|------|-------------|
| [reflection-serialization-avoid-field-injection](rules/reflection-serialization-avoid-field-injection.md) | Prefer constructor injection over reflective field injection |
| [reflection-serialization-avoid-for-business-logic](rules/reflection-serialization-avoid-for-business-logic.md) | Keep reflection out of business logic |

### Modules [HIGH]
Manage module and package boundaries deliberately across Gradle and JPMS.

| Rule | Description |
|------|-------------|
| [modules-api-vs-implementation-gradle-config](rules/modules-api-vs-implementation-gradle-config.md) | Declare Gradle dependencies as api or implementation deliberately |
| [modules-avoid-split-packages](rules/modules-avoid-split-packages.md) | Never split one package across multiple modules |
| [modules-jpms-explicit-exports](rules/modules-jpms-explicit-exports.md) | Export only packages that are part of the public API |

### Collections & Streams [MEDIUM]
Use the Collections and Stream APIs idiomatically, without redundant materialization or hidden side effects.

| Rule | Description |
|------|-------------|
| [collections-streams-avoid-redundant-materialization](rules/collections-streams-avoid-redundant-materialization.md) | Avoid redundant materialization between stream stages |
| [collections-streams-collectors-tox](rules/collections-streams-collectors-tox.md) | Pick the right collectors factory for the shape you need |
| [collections-streams-list-of](rules/collections-streams-list-of.md) | Prefer List.of/Set.of/Map.of over mutable factory methods |
| [collections-streams-no-side-effects](rules/collections-streams-no-side-effects.md) | No mutation inside stream operations |
| [collections-streams-parallel-stream-caution](rules/collections-streams-parallel-stream-caution.md) | Reserve parallelStream() for CPU-bound, sizable, independent work |
| [collections-streams-prefer-stream-pipeline](rules/collections-streams-prefer-stream-pipeline.md) | Prefer stream pipelines over manual loops for transformations |

### Generics [MEDIUM]
Use Java generics safely, without raw types or unchecked casts.

| Rule | Description |
|------|-------------|
| [generics-avoid-generic-array-workarounds](rules/generics-avoid-generic-array-workarounds.md) | Avoid generic array creation workarounds — use List<T> instead |
| [generics-bounded-wildcards](rules/generics-bounded-wildcards.md) | Use bounded wildcards at API boundaries (PECS) |
| [generics-generic-method-over-class](rules/generics-generic-method-over-class.md) | Prefer a generic method over a generic class when only the method needs it |
| [generics-no-raw-types](rules/generics-no-raw-types.md) | Never use raw generic types |
| [generics-no-unchecked-casts](rules/generics-no-unchecked-casts.md) | Avoid @SuppressWarnings("unchecked") casts outside factory internals |

### Nullability [MEDIUM]
Represent absence explicitly with Optional at API boundaries, never as a field or parameter type.

| Rule | Description |
|------|-------------|
| [nullability-no-optional-collection](rules/nullability-no-optional-collection.md) | Return an empty collection, never optional of a collection |
| [nullability-no-optional-field](rules/nullability-no-optional-field.md) | Never use optional as a field type |
| [nullability-no-optional-param](rules/nullability-no-optional-param.md) | Never accept optional as a method parameter |
| [nullability-objects-requirenonnull](rules/nullability-objects-requirenonnull.md) | Fail fast with Objects.requireNonNull at API boundaries |
| [nullability-optional-return](rules/nullability-optional-return.md) | Return optional instead of null for absent values |

### Performance [MEDIUM]
Apply measured, targeted performance techniques instead of premature optimization.

| Rule | Description |
|------|-------------|
| [performance-array-vs-collection-hot-path](rules/performance-array-vs-collection-hot-path.md) | Prefer primitive arrays over boxed collections in verified hot paths |
| [performance-avoid-premature-optimization](rules/performance-avoid-premature-optimization.md) | Measure before optimizing |
| [performance-lazy-initialization](rules/performance-lazy-initialization.md) | Defer expensive initialization until first use |
| [performance-stringbuilder-for-loops](rules/performance-stringbuilder-for-loops.md) | Use StringBuilder for string concatenation inside loops |

### Naming [MEDIUM]
Choose names that reveal intention and avoid encoding type or scope.

| Rule | Description |
|------|-------------|
| [naming-boolean-method-prefix](rules/naming-boolean-method-prefix.md) | Prefix boolean methods and fields with is/has/can |
| [naming-consistent-getter-avoidance](rules/naming-consistent-getter-avoidance.md) | Avoid getX/setX naming for non-JavaBean types |
| [naming-intention-revealing-names](rules/naming-intention-revealing-names.md) | Choose intention-revealing names |
| [naming-no-hungarian-notation](rules/naming-no-hungarian-notation.md) | Do not encode type or scope in names |

### Modern Java (21–27) [MEDIUM]
Adopt finalized language and library features by JDK version and keep preview features out of production.

| Rule | Description |
|------|-------------|
| [modern-java-ffm-over-jni](rules/modern-java-ffm-over-jni.md) | Use the Foreign Function and Memory API instead of JNI |
| [modern-java-flexible-constructor-bodies](rules/modern-java-flexible-constructor-bodies.md) | Validate arguments before super() with flexible constructor bodies |
| [modern-java-no-final-field-mutation](rules/modern-java-no-final-field-mutation.md) | Do not mutate final fields through reflection |
| [modern-java-no-preview-in-production](rules/modern-java-no-preview-in-production.md) | Do not ship preview language features or APIs |
| [modern-java-sequenced-collections](rules/modern-java-sequenced-collections.md) | Use sequenced collection methods for first, last and reversed access |
| [modern-java-stream-gatherers](rules/modern-java-stream-gatherers.md) | Use stream gatherers for windowing and stateful steps |
| [modern-java-unnamed-variables](rules/modern-java-unnamed-variables.md) | Name unused bindings with the unnamed variable _ |

## JDK Baseline

Target JDK 21 as the minimum and JDK 25 (the current LTS) as the preferred baseline. JDK 26 (March 2026) and JDK 27 (September 2026) are non-LTS; use them only where the team upgrades every six months. Rules tagged `java22`–`java26` apply only when the project's toolchain is at least that version; check `java.toolchain` or `maven.compiler.release` before suggesting them. Shared JVM rules (virtual threads, Jackson, build hygiene) live in [jvm-coding-standards](../jvm-coding-standards/SKILL.md).

## Quick Reference

### Anti-Patterns
```java
public void processMessage(Message message) {
    try {
        handler.handle(message);
    } catch (MessageProcessingException e) { // specific, documented, recoverable
        log.error("Failed to process message {}", message.id(), e);
        deadLetterQueue.send(message);
    }
    // an Error propagates uncaught, as it should
}
```

### Resource Management
```java
public String readFirstLine(Path path) throws IOException {
    try (BufferedReader reader = Files.newBufferedReader(path)) {
        return reader.readLine(); // reader.close() runs on every exit path
    }
}
```

### Concurrency
```java
try (ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor()) {
    for (Request request : requests) {
        executor.submit(() -> handle(request)); // one virtual thread per task
    }
} // close() awaits completion of submitted tasks
```

### API Design
```java
public static final class Builder {
    private final String url;
    private final String method;
    private int timeoutMs = 3000;

    public Builder timeoutMs(int timeoutMs) { this.timeoutMs = timeoutMs; return this; }
    public HttpRequest build() { return new HttpRequest(this); }
}

HttpRequest request = HttpRequest.builder("https://api.example.com", "GET")
    .timeoutMs(5000)
    .build();
```

### Error Handling
```java
public Either<ValidationError, Order> validate(OrderRequest request) {
    if (request.items().isEmpty()) {
        return Either.left(new ValidationError("order must have at least one item"));
    }
    return Either.right(new Order(request));
}

return validator.validate(request)
    .map(orderRepository::save)
    .fold(error -> ResponseEntity.badRequest().body(error.message()),
          order -> ResponseEntity.ok(order));
```

### Immutability
```java
public record Money(BigDecimal amount, String currency) {
    public Money {
        Objects.requireNonNull(amount, "amount");
        Objects.requireNonNull(currency, "currency");
        if (amount.scale() > 2) {
            throw new IllegalArgumentException("amount must have at most 2 decimal places");
        }
    }
}
```

### Object-Oriented Design
```java
public class InstrumentedList<E> {
    private final List<E> delegate;
    private int addCount = 0;

    public boolean add(E e) {
        addCount++;
        return delegate.add(e); // composes List, independent of its internals
    }
}
```

### Sealed Types & Pattern Matching
```java
sealed interface Shape permits Circle, Rectangle, Triangle {}

double area(Shape shape) {
    return switch (shape) {
        case Circle c -> Math.PI * c.radius() * c.radius();
        case Rectangle r -> r.width() * r.height();
        case Triangle t -> 0.5 * t.base() * t.height();
        // No default: the compiler verifies every permitted Shape is covered.
    };
}
```

### Javadoc
```java
/**
 * Returns the sum of {@link Order#total()} across all given orders.
 *
 * @param orders the orders to total; must not be {@code null} or contain {@code null}
 * @return the combined total, or {@link BigDecimal#ZERO} if {@code orders} is empty
 */
public BigDecimal totalValue(List<Order> orders) {
    return orders.stream().map(Order::total).reduce(BigDecimal.ZERO, BigDecimal::add);
}
```

### Records
```java
public record Percentage(int value) {
    public Percentage {
        if (value < 0 || value > 100) {
            throw new IllegalArgumentException("value must be 0-100, was " + value);
        }
    }
}

Percentage discount = new Percentage(150); // throws IllegalArgumentException immediately
```

### Reflection & Serialization
```java
public static final ObjectMapper DEFAULT = JsonMapper.builder()
        .addModule(new JavaTimeModule())
        .configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, true)
        .configure(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS, false)
        .serializationInclusion(JsonInclude.Include.NON_ABSENT)
        .build();
```

### Modules
```java
module com.example.billing {
    exports com.example.billing.api;

    requires java.sql;
    // com.example.billing.internal is not exported — usable inside the
    // module, invisible outside it
}
```

### Collections & Streams
```java
public List<String> activeAdminEmails(List<User> users) {
    return users.stream()
        .filter(User::isActive)
        .filter(user -> user.getRole() == Role.ADMIN)
        .map(User::getEmail)
        .map(String::toLowerCase)
        .toList();
}
```

### Generics
```java
// source only produces T (extends), destination only consumes T (super)
public static <T> void copy(List<? extends T> source, List<? super T> destination) {
    for (T item : source) {
        destination.add(item);
    }
}
```

### Nullability
```java
public Optional<User> findById(Long id) {
    return Optional.ofNullable(usersById.get(id));
}

repository.findById(id)
    .map(User::getEmail)
    .ifPresentOrElse(this::sendWelcomeEmail, () -> log.warn("No user found for id {}", id));
```

### Performance
```java
public String buildCsvLine(List<String> fields) {
    StringBuilder line = new StringBuilder();
    for (String field : fields) {
        line.append(field).append(','); // amortized O(1) per call
    }
    return line.toString();
}
```

### Naming
```java
public class SubscriptionRenewalQueue {
    private final List<Subscription> pendingRenewals = new ArrayList<>();

    public void enqueueIfEligible(Subscription subscription, RenewalStatus status) {
        if (status == RenewalStatus.ELIGIBLE) {
            pendingRenewals.add(subscription);
        }
    }
}
```

## See Also

- [java-testing](../java-testing/SKILL.md) - Test-writing best practices for JUnit 5, AssertJ, Mockito, and Testcontainers
- [java-tooling](../java-tooling/SKILL.md) - Build, static analysis, CI quality gate, dependency management, and formatting rules
