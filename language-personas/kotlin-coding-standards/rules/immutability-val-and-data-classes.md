---
title: Default to val, Immutable data classes and copy()
impact: HIGH
impactDescription: removes shared mutable state and makes values safe to pass between threads
tags: [immutability, data-classes]
---

# Default to val, Immutable data classes and copy() [HIGH]

## Description
Declare `val`, never `var`, unless the mutation is local and necessary. Model values as `data class` with only `val` properties and derive changes with `copy()`. Use `@JvmInline value class` for typed ids and units so a `UserId` cannot be passed as an `OrderId`.

## Bad Example
```kotlin
enum class Status { NEW, PAID }
data class Item(val sku: String)
data class Order(var status: Status, var items: MutableList<Item>)

fun addItem(order: Order, item: Item) {
    order.items.add(item)
}
```

## Good Example
```kotlin
import kotlinx.collections.immutable.PersistentList
import kotlinx.collections.immutable.persistentListOf

@JvmInline value class OrderId(val value: String)
enum class Status { NEW, PAID }
data class Item(val sku: String)

data class Order(
    val id: OrderId,
    val status: Status,
    val items: PersistentList<Item> = persistentListOf(),
) {
    fun add(item: Item): Order = copy(items = items.add(item))
}
```

## Notes
- A `val` of a `MutableList` type is still mutable; expose `List`, hold the mutable list privately.
- A plain `List` property can hold a caller-owned `MutableList`, through the constructor or `copy(items = ...)`. Type the property as `PersistentList` (or `ImmutableList`) from `kotlinx.collections.immutable` so every construction path is safe, and keep the elements (`Item`) immutable too.
- Validate invariants in `init { require(...) }`. `copy()` re-runs `init`, so invariants hold for derived values too.

## References
- [Data classes](https://kotlinlang.org/docs/data-classes.html)
- [Inline value classes](https://kotlinlang.org/docs/inline-classes.html)
