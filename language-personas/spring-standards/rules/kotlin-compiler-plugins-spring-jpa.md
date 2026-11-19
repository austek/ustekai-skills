---
title: Apply the kotlin-spring and kotlin-jpa Compiler Plugins in Kotlin Projects
impact: HIGH
impactDescription: fixes final-class proxy failures and missing no-arg constructors without hand-opening classes
tags: [spring, kotlin, jpa, compiler-plugin]
---

# Apply the kotlin-spring and kotlin-jpa Compiler Plugins in Kotlin Projects [HIGH]

## Description
Kotlin classes are final, but Spring proxies (`@Transactional`, `@Configuration`, `@Cacheable`) need to subclass them. The `kotlin-spring` (all-open) plugin opens classes carrying Spring annotations. The `kotlin-jpa` (no-arg) plugin generates the no-arg constructor Hibernate needs for `@Entity`. Without them you get runtime proxy errors or "No default constructor for entity".

## Bad Example
```kotlin
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

data class NewOrder(val sku: String, val quantity: Int)

@Service
class OrderService { // final: @Transactional silently does nothing or fails
    @Transactional fun place(order: NewOrder) {}
}
```

## Good Example
```kotlin
plugins {
    kotlin("jvm")
    kotlin("plugin.spring")
    kotlin("plugin.jpa")
}
```
```kotlin
import jakarta.persistence.Entity
import jakarta.persistence.Id
import java.util.UUID

@Entity
class Customer(
    @Id val id: UUID,
    var name: String,
) // no data class: equals/hashCode on a mutable entity breaks Hibernate
```

## Notes
- From Kotlin 2.3.20, `kotlin-jpa` also applies all-open with the JPA preset, so entities are opened for lazy-association proxies without a manual `allOpen` block. Before 2.3.20 it only adds the no-arg constructor: either require 2.3.20 or later, or open the entities yourself:
  ```kotlin
  allOpen {
      annotation("jakarta.persistence.Entity")
      annotation("jakarta.persistence.MappedSuperclass")
      annotation("jakarta.persistence.Embeddable")
  }
  ```
- Do not make JPA entities `data class`es. Implement `equals`/`hashCode` on the id.
- Use `constructor injection` with a primary constructor; no `lateinit var` fields.

## References
- [Kotlin Spring compiler plugin](https://kotlinlang.org/docs/all-open-plugin.html#spring-support)
- [Kotlin JPA compiler plugin](https://kotlinlang.org/docs/no-arg-plugin.html#jpa-support)
