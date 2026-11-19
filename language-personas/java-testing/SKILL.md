---
name: java-testing
description: Java test-writing best practices covering Mockito, JUnit 5 structure, AssertJ assertions, fixtures, Testcontainers, parameterized tests, and test doubles. Use when writing, reviewing, or refactoring Java tests, adding test coverage, or working under src/test.
paths:
  - "src/test/**"
  - "**/*Test.java"
  - "**/*Tests.java"
---

# Java Testing

A collection of test-writing best practices for JUnit 5, AssertJ, Mockito, and Testcontainers. Designed for AI agents and LLMs to write readable, maintainable, and trustworthy tests.

## Categories

### Mockito [HIGH]
Mock only architectural boundaries, with strict, verifiable stubbing.

| Rule | Description |
|------|-------------|
| [mockito-argument-captor](rules/mockito-argument-captor.md) | Use ArgumentCaptor to inspect call arguments |
| [mockito-avoid-mocking-value-objects](rules/mockito-avoid-mocking-value-objects.md) | Never mock value objects |
| [mockito-mock-boundaries-only](rules/mockito-mock-boundaries-only.md) | Mock only architectural boundaries |
| [mockito-spy-sparingly](rules/mockito-spy-sparingly.md) | Use @Spy sparingly |
| [mockito-strict-stubbing](rules/mockito-strict-stubbing.md) | Rely on Mockito's strict stubbing |
| [mockito-verify-behavior-not-implementation](rules/mockito-verify-behavior-not-implementation.md) | Verify behavior, not implementation |

### JUnit 5 Structure [HIGH]
Structure JUnit 5 tests for clarity: one behavior per test, explicit lifecycle, readable names.

| Rule | Description |
|------|-------------|
| [junit5-structure-aaa-pattern](rules/junit5-structure-aaa-pattern.md) | Structure tests with arrange-act-assert |
| [junit5-structure-display-name](rules/junit5-structure-display-name.md) | Use @DisplayName for human-readable test names |
| [junit5-structure-lifecycle-annotations](rules/junit5-structure-lifecycle-annotations.md) | Use lifecycle annotations for shared setup and teardown |
| [junit5-structure-nested-test-classes](rules/junit5-structure-nested-test-classes.md) | Group related tests with @Nested |
| [junit5-structure-one-assertion-concept](rules/junit5-structure-one-assertion-concept.md) | Assert one behavioral concept per test |

### AssertJ Assertions [HIGH]
Write fluent, complete AssertJ assertions instead of terse JUnit asserts.

| Rule | Description |
|------|-------------|
| [assertj-assertthatthrownby](rules/assertj-assertthatthrownby.md) | Assert exceptions with assertThatThrownBy |
| [assertj-extracting-for-collections](rules/assertj-extracting-for-collections.md) | Use extracting to assert on collection elements' fields |
| [assertj-fluent-over-junit-asserts](rules/assertj-fluent-over-junit-asserts.md) | Prefer AssertJ's fluent assertions over JUnit's assertEquals |
| [assertj-soft-assertions](rules/assertj-soft-assertions.md) | Use SoftAssertions to report every failure in one run |

### Fixtures [HIGH]
Build and share test data and setup without hidden shared mutable state.

| Rule | Description |
|------|-------------|
| [fixtures-avoid-shared-mutable-fixtures](rules/fixtures-avoid-shared-mutable-fixtures.md) | Avoid shared mutable fixtures |
| [fixtures-builder-for-test-data](rules/fixtures-builder-for-test-data.md) | Use a test-data builder instead of telescoping constructors |
| [fixtures-extension-for-shared-setup](rules/fixtures-extension-for-shared-setup.md) | Extract cross-cutting setup into a JUnit extension |
| [fixtures-test-instance-per-method-default](rules/fixtures-test-instance-per-method-default.md) | Leave test instance lifecycle at per-method default |

Testcontainers rules are JVM-wide and live in [jvm-testing](../jvm-testing/SKILL.md). Apply them together with this skill.

### Parameterized Tests [MEDIUM]
Replace duplicated test methods with parameterized sources and readable case names.

| Rule | Description |
|------|-------------|
| [parametrized-csv-source](rules/parametrized-csv-source.md) | Use @CsvSource for compact scalar argument tables |
| [parametrized-enum-source](rules/parametrized-enum-source.md) | Use @EnumSource to cover a whole enum's cases |
| [parametrized-method-source](rules/parametrized-method-source.md) | Use @MethodSource for complex parameterized arguments |
| [parametrized-readable-display-names](rules/parametrized-readable-display-names.md) | Give parameterized tests readable display names |

### Test Doubles [MEDIUM]
Choose the right test double for the job and avoid mocking types you don't own.

| Rule | Description |
|------|-------------|
| [test-doubles-dummy-stub-mock-distinction](rules/test-doubles-dummy-stub-mock-distinction.md) | Know the difference between dummy, stub, and mock |
| [test-doubles-fake-over-mock](rules/test-doubles-fake-over-mock.md) | Prefer a fake over a mock for stateful collaborators |
| [test-doubles-no-mocking-what-you-dont-own](rules/test-doubles-no-mocking-what-you-dont-own.md) | Don't mock types you don't own |

## Quick Reference

### Mockito
```java
@ExtendWith(MockitoExtension.class)
class OrderServiceTest {
    @Mock PaymentGateway paymentGateway;   // real boundary: external HTTP call
    @InjectMocks OrderService service;

    @Test
    void appliesDiscountToRealOrder() {
        Order order = new Order(List.of(new LineItem("sku-1", Money.of("100.00"))));

        Order discounted = service.applyDiscount(order, Percentage.of(10));

        assertThat(discounted.total()).isEqualTo(Money.of("90.00"));
    }
}
```

### JUnit 5 Structure
```java
@Test
void discountAppliesToEligibleOrder() {
    Order order = new Order(customerId, List.of(item1, item2));

    order.applyDiscount(discountPolicy);

    assertThat(order.total()).isEqualByComparingTo("90.00");
}
```

### AssertJ Assertions
```java
@Test
void orderTotalsCorrectly() {
    assertThat(order.items()).hasSize(2).extracting(LineItem::sku).contains("sku-1");
    assertThat(order.total()).isEqualByComparingTo("90.00");
}
```

### Fixtures
```java
@Test
void appliesDiscountToEligibleOrder() {
    Order order = anOrder().withTotal("100.00").withCustomerTier(Tier.GOLD).build();

    Order discounted = service.applyDiscount(order);

    assertThat(discounted.total()).isEqualByComparingTo("90.00");
}
```

### Parameterized Tests
```java
@ParameterizedTest
@CsvSource({
    "100.00, 0.20, 120.00",
    "50.00,  0.10, 55.00"
})
void computesVat(BigDecimal net, BigDecimal rate, BigDecimal expected) {
    assertThat(service.applyVat(net, rate)).isEqualByComparingTo(expected);
}
```

### Test Doubles
```java
class InMemoryOrderRepository implements OrderRepository {
    private final Map<String, Order> store = new HashMap<>();

    @Override public void save(Order order) { store.put(order.id(), order); }
    @Override public Optional<Order> findById(String id) { return Optional.ofNullable(store.get(id)); }
}
```

## See Also

- [java-coding-standards](../java-coding-standards/SKILL.md) - General Java coding standards and best practices
- [java-tooling](../java-tooling/SKILL.md) - Build, static analysis, CI quality gate, dependency management, and formatting rules
