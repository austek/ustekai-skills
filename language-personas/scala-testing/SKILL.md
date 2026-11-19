---
name: scala-testing
description: Scala test-writing best practices covering async testing, mocking discipline, ScalaCheck property-based testing, ScalaTest/MUnit structure, and fixtures. Use when writing, reviewing, or refactoring Scala tests, adding test coverage, or working in test sources.
paths:
  - "**/*Spec.scala"
  - "**/*Test.scala"
  - "**/*Suite.scala"
---

# Scala Testing

A collection of test-writing best practices for MUnit, ScalaTest, and ScalaCheck. Designed for AI agents and LLMs to write readable, maintainable, and trustworthy tests.

## Categories

### Async Testing [HIGH]
Test asynchronous and time-dependent code deterministically, without sleeping the test thread or reaching past the effect runner.

| Rule | Description |
|------|-------------|
| [async-testing-avoid-thread-sleep](rules/async-testing-avoid-thread-sleep.md) | Never use Thread.sleep to wait for async work |
| [async-testing-deterministic-clocks](rules/async-testing-deterministic-clocks.md) | Test time-dependent code with a simulated clock |
| [async-testing-future-recovertosucceededif](rules/async-testing-future-recovertosucceededif.md) | Assert expected Future failures with recoverToSucceededIf |
| [async-testing-io-testrunner](rules/async-testing-io-testrunner.md) | Let CatsEffectSuite run IO tests instead of calling unsafeRunSync yourself |

### Mocking Discipline [HIGH]
Reserve mocks for genuine external boundaries, and prefer fakes and in-memory interpreters for everything else.

| Rule | Description |
|------|-------------|
| [mocking-discipline-avoid-mockito-for-pure-fp](rules/mocking-discipline-avoid-mockito-for-pure-fp.md) | Avoid Mockito on pure, effect-typed code |
| [mocking-discipline-in-memory-interpreters](rules/mocking-discipline-in-memory-interpreters.md) | Write in-memory interpreters for repository and client traits |
| [mocking-discipline-mock-external-boundaries-only](rules/mocking-discipline-mock-external-boundaries-only.md) | Reserve mocks for the external system boundary |
| [mocking-discipline-prefer-fakes-over-mocks](rules/mocking-discipline-prefer-fakes-over-mocks.md) | Prefer fakes over mocks |

### ScalaCheck [MEDIUM]
Generate test inputs with ScalaCheck instead of hand-picking examples, and keep generators composable and shrinking-friendly.

| Rule | Description |
|------|-------------|
| [scalacheck-arbitrary-instances-for-domain-types](rules/scalacheck-arbitrary-instances-for-domain-types.md) | Provide Arbitrary instances for domain types |
| [scalacheck-forall-over-manual-loops](rules/scalacheck-forall-over-manual-loops.md) | Use forAll instead of hand-rolled input loops |
| [scalacheck-generator-composition](rules/scalacheck-generator-composition.md) | Compose generators from smaller generators |
| [scalacheck-property-based-for-pure-functions](rules/scalacheck-property-based-for-pure-functions.md) | Reach for property-based tests on pure functions |
| [scalacheck-shrinking-friendly-generators](rules/scalacheck-shrinking-friendly-generators.md) | Keep generators shrinking-friendly |

### ScalaTest & MUnit Structure [MEDIUM]
Structure ScalaTest and MUnit suites for clarity: one behavior per test, arrange-act-assert bodies, and readable naming.

| Rule | Description |
|------|-------------|
| [scalatest-munit-structure-aaa-pattern](rules/scalatest-munit-structure-aaa-pattern.md) | Structure test bodies as arrange-act-assert |
| [scalatest-munit-structure-nested-suites](rules/scalatest-munit-structure-nested-suites.md) | Nest suites by shared context, not by file convenience |
| [scalatest-munit-structure-one-behavior-per-test](rules/scalatest-munit-structure-one-behavior-per-test.md) | Assert one behavior per test |
| [scalatest-munit-structure-suite-naming](rules/scalatest-munit-structure-suite-naming.md) | Name test suites after the unit under test |
| [scalatest-munit-structure-tagged-tests](rules/scalatest-munit-structure-tagged-tests.md) | Tag slow or environment-dependent tests |

### Fixtures [MEDIUM]
Scope and share test setup without leaking mutable state across tests.

| Rule | Description |
|------|-------------|
| [fixtures-factory-methods-for-test-data](rules/fixtures-factory-methods-for-test-data.md) | Build test data with factory methods, not copy-pasted literals |
| [fixtures-munit-lifecycle](rules/fixtures-munit-lifecycle.md) | Prefer FunFixture over mutable beforeEach/afterEach in MUnit |
| [fixtures-narrowest-scope](rules/fixtures-narrowest-scope.md) | Scope fixtures to the narrowest level that needs them |
| [fixtures-scalatest-beforeandafter-traits](rules/fixtures-scalatest-beforeandafter-traits.md) | Match ScalaTest fixture traits to setup cost |

## Quick Reference

### Async Testing
```scala
import org.scalatest.concurrent.Eventually.eventually
import org.scalatest.time.{Seconds, Span}

class CacheSuite extends AnyFunSuite with Eventually:
  test("cache is populated after an async warm-up") {
    cache.warmUpAsync()

    eventually(timeout(Span(2, Seconds))) {
      assert(cache.get("key").isDefined)
    }
  }
```

### Mocking Discipline
```scala
test("processing an order saves it") {
  val repo = InMemoryOrderRepository.withOrder(pendingOrder)

  OrderService(repo).confirm(orderId)

  assertEquals(repo.findById(orderId).map(_.status), Some(OrderStatus.Confirmed))
  // asserts only the observable outcome, independent of how many times save() ran
}
```

### ScalaCheck
```scala
import org.scalacheck.Prop.forAll

class SortedInsertSuite extends munit.ScalaCheckSuite:
  property("inserting into a sorted list keeps it sorted") {
    forAll { (xs: List[Int], x: Int) =>
      val sorted = xs.sorted
      val result = sortedInsert(sorted, x)
      result.sorted == result && result.sorted(Ordering[Int]) == result
    }
  }
```

### ScalaTest & MUnit Structure
```scala
test("checkout applies a discount") {
  val cart = Cart.empty.addItem(Item("sku-1", price = 10.0))

  val discounted = Checkout.applyDiscount(cart, DiscountCode("SAVE10"))

  assertEquals(discounted.total, 9.0)
  assertEquals(discounted.appliedCode, Some(DiscountCode("SAVE10")))
}
```

### Fixtures
```scala
class OrderRepositorySuite extends munit.FunSuite:
  private val repoFixture = FunFixture[InMemoryOrderRepository](
    setup = _ => InMemoryOrderRepository.empty,
    teardown = _ => ()
  )

  repoFixture.test("saves and retrieves an order") { repo =>
    repo.save(sampleOrder)
    assertEquals(repo.findById(sampleOrder.id), Some(sampleOrder))
  }
```

## See Also

- [scala-coding-standards](../scala-coding-standards/SKILL.md) - General Scala coding standards and best practices
- [scala-tooling](../scala-tooling/SKILL.md) - Build, compiler flags, Scalafix, Scalafmt, Scalastyle, and Wartremover rules
- [jvm-testing](../jvm-testing/SKILL.md) - Testcontainers lifecycle, reuse and wait-strategy rules; this skill has no container rules of its own, so use these for integration tests
