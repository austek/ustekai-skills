---
title: Expose Read-Only Collection Types in Public APIs
impact: HIGH
impactDescription: callers cannot mutate internal state through a returned collection
tags: [immutability, collections, api-design]
---

# Expose Read-Only Collection Types in Public APIs [HIGH]

## Description
`List`, `Set` and `Map` are read-only views; `MutableList` and friends are mutable. Accept and return the read-only types. Keep the mutable collection private. A read-only reference can still be downcast on the JVM, so copy with `toList()` whenever the owner keeps a mutable backing collection, even if it never changes it afterwards.

## Bad Example
```kotlin
data class Item(val sku: String)

class Cart {
    val items: MutableList<Item> = mutableListOf()
}
```

## Good Example
```kotlin
data class Item(val sku: String)

class Cart {
    private val _items = mutableListOf<Item>()
    val items: List<Item> get() = _items.toList()

    fun add(item: Item) { _items += item }
}
```

## Notes
- Use `buildList { }` and `buildMap { }` to construct a collection and freeze it in one expression.
- Prefer sequences (`asSequence()`) for long multi-step pipelines on large collections.

## References
- [Collections overview](https://kotlinlang.org/docs/collections-overview.html)
