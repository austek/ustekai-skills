---
name: scala-coding-standards
description: Scala coding standards and best practices covering null/option handling, effect systems, anti-patterns, concurrency, error handling, immutability, implicits/givens, API design, collections, pattern matching, for-comprehensions, naming, and Scaladoc. Use when writing, reviewing, or refactoring Scala code, or when the user asks about Scala style, design, or best practices.
paths:
  - "**/*.scala"
  - "build.sbt"
  - "build.mill"
---

# Scala Coding Standards

A comprehensive collection of Scala coding standards and best practices. Designed for AI agents and LLMs to generate high-quality, idiomatic, and maintainable Scala code.

## Categories

### Null & Option Handling [CRITICAL]
Represent absence and expected failure explicitly with Option and Either — never null.

| Rule | Description |
|------|-------------|
| [null-option-avoid-option-get](rules/null-option-avoid-option-get.md) | Never call .get on an Option |
| [null-option-either-for-expected-failure](rules/null-option-either-for-expected-failure.md) | Use Either for operations that can fail with a reason |
| [null-option-no-null-literal](rules/null-option-no-null-literal.md) | Never use null as a value |
| [null-option-option-for-absence](rules/null-option-option-for-absence.md) | Represent optional values with Option[T] |
| [null-option-orelse-chains-over-nested-match](rules/null-option-orelse-chains-over-nested-match.md) | Chain orElse instead of nesting match on Option |

### Effect Systems [HIGH]
Keep side effects wrapped in IO at the edges, and keep core logic pure and referentially transparent.

| Rule | Description |
|------|-------------|
| [effect-systems-direct-style-ox](rules/effect-systems-direct-style-ox.md) | Use Ox's direct-style supervised/fork for structured concurrency |
| [effect-systems-effect-boundary-at-edges](rules/effect-systems-effect-boundary-at-edges.md) | Keep IO at the edges; keep core logic pure |
| [effect-systems-io-for-side-effects](rules/effect-systems-io-for-side-effects.md) | Wrap side effects in IO instead of running them directly |
| [effect-systems-no-blocking-inside-effect](rules/effect-systems-no-blocking-inside-effect.md) | Never block a thread inside a non-blocking effect |
| [effect-systems-referential-transparency](rules/effect-systems-referential-transparency.md) | Keep effect-returning functions referentially transparent |
| [effect-systems-resource-safety](rules/effect-systems-resource-safety.md) | Acquire and release resources with Resource, not manual try/finally |

### Anti-Patterns [HIGH]
Recognize and eliminate recurring Scala anti-patterns that erode type safety, totality, and encapsulation.

| Rule | Description |
|------|-------------|
| [anti-patterns-no-asinstanceof-casts](rules/anti-patterns-no-asinstanceof-casts.md) | Never use asInstanceOf/isInstanceOf; pattern match instead |
| [anti-patterns-no-implicit-overuse](rules/anti-patterns-no-implicit-overuse.md) | Don't pile every dependency into using parameters |
| [anti-patterns-no-null-return](rules/anti-patterns-no-null-return.md) | A collection-returning method returns empty, never null |
| [anti-patterns-no-throw-in-pure-code](rules/anti-patterns-no-throw-in-pure-code.md) | A total-looking function signature must not throw |
| [anti-patterns-no-var-escape](rules/anti-patterns-no-var-escape.md) | Never let a local var escape the scope that declared it |

### Concurrency [HIGH]
Coordinate shared state and background work safely with immutable data, IO, and structured scopes.

| Rule | Description |
|------|-------------|
| [concurrency-avoid-shared-mutable-state](rules/concurrency-avoid-shared-mutable-state.md) | Never share a var or mutable collection across concurrent tasks |
| [concurrency-cancellation-safety](rules/concurrency-cancellation-safety.md) | Protect multi-step mutations with uncancelable, not ad hoc hope |
| [concurrency-execution-context-explicit](rules/concurrency-execution-context-explicit.md) | Require an ExecutionContext explicitly, don't import a default one |
| [concurrency-future-vs-io](rules/concurrency-future-vs-io.md) | Prefer IO over Future for new concurrent code |
| [concurrency-structured-concurrency-ox](rules/concurrency-structured-concurrency-ox.md) | Bound every concurrent fork to a structured scope |

### Error Handling [HIGH]
Model and propagate failures explicitly with Either, Try, and typed errors instead of throwing.

| Rule | Description |
|------|-------------|
| [error-handling-either-for-domain-errors](rules/error-handling-either-for-domain-errors.md) | Model domain errors with Either[E, A] |
| [error-handling-io-for-effectful-errors](rules/error-handling-io-for-effectful-errors.md) | Represent effectful, failable work with IO |
| [error-handling-no-throw-for-control-flow](rules/error-handling-no-throw-for-control-flow.md) | Never use throw for ordinary control flow |
| [error-handling-try-for-exception-boundaries](rules/error-handling-try-for-exception-boundaries.md) | Wrap exception-throwing calls in Try at the boundary |
| [error-handling-typed-errors-over-strings](rules/error-handling-typed-errors-over-strings.md) | Model errors as typed ADTs, not strings |

### Immutability [HIGH]
Default to immutable data and val bindings, updating through copy instead of mutation.

| Rule | Description |
|------|-------------|
| [immutability-avoid-mutable-builder-escape](rules/immutability-avoid-mutable-builder-escape.md) | Never let a mutable builder escape its construction scope |
| [immutability-case-class-for-data](rules/immutability-case-class-for-data.md) | Model data with case class, not plain classes |
| [immutability-copy-method-for-updates](rules/immutability-copy-method-for-updates.md) | Use copy to produce updated instances |
| [immutability-immutable-collections-default](rules/immutability-immutable-collections-default.md) | Default to immutable collections |
| [immutability-val-over-var](rules/immutability-val-over-var.md) | Prefer val over var |

### Implicits & Givens [MEDIUM]
Use Scala 3's given/using and extension methods deliberately, without implicit-driven surprises.

| Rule | Description |
|------|-------------|
| [implicits-givens-avoid-implicit-conversions](rules/implicits-givens-avoid-implicit-conversions.md) | Avoid implicit conversions; make the conversion explicit |
| [implicits-givens-context-bounds-syntax](rules/implicits-givens-context-bounds-syntax.md) | Use context bound syntax for a single using type class parameter |
| [implicits-givens-explicit-imports-no-wildcard](rules/implicits-givens-explicit-imports-no-wildcard.md) | Import givens by type, not with a blanket wildcard |
| [implicits-givens-extension-methods-over-implicit-class](rules/implicits-givens-extension-methods-over-implicit-class.md) | Use extension methods, not implicit class, to add methods to an existing type |
| [implicits-givens-scala3-syntax](rules/implicits-givens-scala3-syntax.md) | Use given/using, not Scala 2 implicit, for new code |
| [implicits-givens-type-class-pattern](rules/implicits-givens-type-class-pattern.md) | Model capabilities as type classes with given instances |

### API Design [MEDIUM]
Shape public constructors, traits, and types so they are hard to misuse.

| Rule | Description |
|------|-------------|
| [api-design-companion-object-factories](rules/api-design-companion-object-factories.md) | Construct through companion object factories, not a public constructor |
| [api-design-minimal-public-surface](rules/api-design-minimal-public-surface.md) | Keep the public surface to what callers actually need |
| [api-design-opaque-types-for-domain-primitives](rules/api-design-opaque-types-for-domain-primitives.md) | Wrap domain primitives in opaque types, not raw String/Long/Int |
| [api-design-smart-constructors](rules/api-design-smart-constructors.md) | Enforce invariants with a smart constructor, not a public constructor |
| [api-design-trait-for-abstraction-not-reuse](rules/api-design-trait-for-abstraction-not-reuse.md) | Use a trait to declare an abstraction, not to share an implementation |

### Collections [MEDIUM]
Use Scala's immutable collection API idiomatically, without unnecessary materialization.

| Rule | Description |
|------|-------------|
| [collections-avoid-mutable-builder-escape](rules/collections-avoid-mutable-builder-escape.md) | Never return a collection builder before calling .result() |
| [collections-immutable-by-default](rules/collections-immutable-by-default.md) | Default to structure-sharing immutable collections |
| [collections-lazylist-for-infinite-sequences](rules/collections-lazylist-for-infinite-sequences.md) | Use LazyList for self-referential or infinite sequences |
| [collections-prefer-map-filter-over-loops](rules/collections-prefer-map-filter-over-loops.md) | Prefer map/filter/fold over hand-written loops |
| [collections-view-for-lazy-chains](rules/collections-view-for-lazy-chains.md) | Use .view to avoid materializing intermediate collections in a chain |

### Pattern Matching [MEDIUM]
Match exhaustively and readably instead of chaining accessors or if/else.

| Rule | Description |
|------|-------------|
| [pattern-matching-destructuring-over-accessors](rules/pattern-matching-destructuring-over-accessors.md) | Destructure with pattern matching instead of chained accessors |
| [pattern-matching-guard-clauses](rules/pattern-matching-guard-clauses.md) | Use guard clauses inside match instead of nested conditionals |
| [pattern-matching-match-over-if-else-chains](rules/pattern-matching-match-over-if-else-chains.md) | Prefer match over long if/else if chains |
| [pattern-matching-no-catch-all-unless-intentional](rules/pattern-matching-no-catch-all-unless-intentional.md) | Don't add a case _ catch-all unless the fallback is genuinely intentional |
| [pattern-matching-sealed-trait-exhaustiveness](rules/pattern-matching-sealed-trait-exhaustiveness.md) | Model closed hierarchies with sealed trait/enum for exhaustive match |

### For-Comprehensions [MEDIUM]
Use for-comprehensions to compose monadic operations readably, not reflexively.

| Rule | Description |
|------|-------------|
| [for-comprehensions-avoid-nested-flatmap](rules/for-comprehensions-avoid-nested-flatmap.md) | Replace nested flatMap chains with a for-comprehension |
| [for-comprehensions-early-exit-with-either](rules/for-comprehensions-early-exit-with-either.md) | Use for-comprehensions over Either to short-circuit a validation pipeline |
| [for-comprehensions-monadic-composition](rules/for-comprehensions-monadic-composition.md) | Use for-comprehensions to compose monadic operations |
| [for-comprehensions-readability-over-cleverness](rules/for-comprehensions-readability-over-cleverness.md) | Don't force a for-comprehension where a direct call reads better |

### Naming [LOW]
Follow Scala's naming conventions for values, types, and symbolic methods.

| Rule | Description |
|------|-------------|
| [naming-lowercase-for-values](rules/naming-lowercase-for-values.md) | Use lowerCamelCase for values, methods, and parameters |
| [naming-symbolic-methods-sparingly](rules/naming-symbolic-methods-sparingly.md) | Reserve symbolic method names for well-established operators |
| [naming-uppercase-for-types](rules/naming-uppercase-for-types.md) | Use UpperCamelCase for classes, traits, objects, and type parameters |

### Scaladoc [LOW]
Document public API contracts precisely, without narrating the signature.

| Rule | Description |
|------|-------------|
| [scaladoc-example-tags-for-complex-apis](rules/scaladoc-example-tags-for-complex-apis.md) | Show a complex generic API's usage with @example, not prose alone |
| [scaladoc-no-signature-narration](rules/scaladoc-no-signature-narration.md) | Never restate a parameter's type or name in its own description |
| [scaladoc-public-api-contract](rules/scaladoc-public-api-contract.md) | Document the contract, not a restatement of the implementation |

## Quick Reference

### Null & Option Handling
```scala
def findDiscount(code: String): Option[BigDecimal] =
  discounts.get(code)

val total = for
  discount <- findDiscount(code)
  price    <- findPrice(sku)
yield price - discount
```

### Effect Systems
```scala
import cats.effect.IO

def logAndSave(order: Order): IO[Unit] =
  for
    _ <- IO.println(s"saving order ${order.id}") // describes the effect; nothing runs yet
    _ <- IO.delay(database.save(order))           // same — deferred until this IO is run
  yield ()
```

### Anti-Patterns
```scala
import cats.effect.{IO, Ref}

def counter(): IO[Ref[IO, Int]] = Ref.of[IO, Int](0)

for
  ref <- counter()
  a   <- ref.updateAndGet(_ + 1) // 1
  b   <- ref.updateAndGet(_ + 1) // 2
yield (a, b)
```

### Concurrency
```scala
import cats.effect.{IO, Ref}
import cats.syntax.parallel.*

def processAll(requests: List[Request], processed: Ref[IO, Int]): IO[Unit] =
  requests.parTraverse(req => handle(req) *> processed.update(_ + 1)).void
```

### Error Handling
```scala
enum OrderError:
  case EmptyCart
  case UnverifiedCustomer(customerId: String)

class OrderService:
  def placeOrder(cart: Cart, customer: Customer): Either[OrderError, Order] =
    for
      _ <- Either.cond(cart.items.nonEmpty, (), OrderError.EmptyCart)
      _ <- Either.cond(customer.isVerified, (), OrderError.UnverifiedCustomer(customer.id))
    yield Order(cart, customer)
```

### Immutability
```scala
def sumPositive(numbers: List[Int]): Int =
  numbers.filter(_ > 0).sum

case class RequestCounter(count: Int = 0):
  def increment: RequestCounter = copy(count = count + 1)
```

### Implicits & Givens
```scala
trait JsonEncoder[T]:
  def encode(value: T): String

given JsonEncoder[User] with
  def encode(value: User): String = s"""{"name":"${value.name}"}"""

def render[T](value: T)(using encoder: JsonEncoder[T]): String =
  encoder.encode(value) // resolved from scope for whatever T the caller passes, no manual threading
```

### API Design
```scala
final case class Email private (value: String):
  def domain: String = value.split("@").last

object Email:
  def parse(raw: String): Either[String, Email] =
    Either.cond(raw.contains("@"), new Email(raw), s"invalid email: $raw")
```

### Collections
```scala
def totalActive(orders: List[Order]): BigDecimal =
  orders
    .filter(_.status == OrderStatus.Active)
    .foldLeft(BigDecimal(0))(_ + _.amount)
```

### Pattern Matching
```scala
enum Shape:
  case Circle(radius: Double)
  case Rectangle(width: Double, height: Double)
  case Triangle(base: Double, height: Double)

def area(shape: Shape): Double = shape match
  case Shape.Circle(r)       => math.Pi * r * r
  case Shape.Rectangle(w, h) => w * h
  case Shape.Triangle(b, h)  => 0.5 * b * h
  // no default — compiler verifies this covers every Shape case
```

### For-Comprehensions
```scala
def shippingQuote(userId: String): Option[BigDecimal] =
  for
    address <- findAddress(userId)
    weight  <- findWeightKg(userId)
  yield address.zone.ratePerKg * weight
```

### Naming
```scala
trait PaymentGateway:
  def charge(amount: BigDecimal): Unit

class OrderService(gateway: PaymentGateway)
```

### Scaladoc
```scala
/** Charges `amount` against the configured payment gateway.
  *
  * @return `Left(PaymentError.InsufficientFunds)` when the gateway declines the charge,
  *         `Left(PaymentError.GatewayUnavailable)` when the gateway cannot be reached,
  *         `Right(receipt)` otherwise.
  */
def charge(amount: BigDecimal): Either[PaymentError, Receipt] = ???
```

## See Also

- [scala-testing](../scala-testing/SKILL.md) - Test-writing best practices for MUnit, ScalaTest, ScalaCheck, and mocking discipline
- [scala-tooling](../scala-tooling/SKILL.md) - Build, compiler flags, Scalafix, Scalafmt, Scalastyle, and Wartremover rules
- [jvm-coding-standards](../jvm-coding-standards/SKILL.md) - Runtime rules that apply to Scala as well: structured JSON logging, no secrets in logs, thread-safety documentation, connection pools, and virtual threads (Ox runs on them). Apply the Jackson and `ObjectMapper` guidance only when the project uses Jackson; skip it for circe or another codec. Apply the virtual-threads rule only on JDK 21+.
