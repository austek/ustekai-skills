---
title: Expose Cold Flow for Streams and StateFlow for State
impact: MEDIUM
impactDescription: prevents duplicated upstream work and lost or stale emissions
tags: [coroutines, flow]
---

# Expose Cold Flow for Streams and StateFlow for State [MEDIUM]

## Description
A `Flow` is cold: each collector re-runs the producer. Use it for query results and event streams. Use `StateFlow` for current state with a value (always has one, conflates), and `SharedFlow` for events that must reach all collectors. Share an expensive cold flow with `shareIn`/`stateIn` and `SharingStarted.WhileSubscribed`. Never expose `MutableStateFlow` publicly.

## Bad Example
```kotlin
class Prices {
    val state = MutableStateFlow(Price.ZERO) // callers can write to it
}
```

## Good Example
```kotlin
class Prices(source: PriceSource, scope: CoroutineScope) {
    private val _latest = MutableStateFlow(Price.ZERO)
    val latest: StateFlow<Price> = _latest.asStateFlow()

    val shared: SharedFlow<Quote> = source.quotes()
        .shareIn(scope, SharingStarted.WhileSubscribed(5_000), replay = 0)
}
```

## Notes
- `StateFlow` drops intermediate values; use `SharedFlow` or a `Channel` when every event matters.
- `SharedFlow` with `replay = 0` loses events emitted while no collector is subscribed, and a late collector sees only the replay cache. It is not durable delivery: use a `Channel` or a persisted queue when every event must be retained.
- Collect with a lifecycle-bound scope; do not `launch` an endless collector without an owner.

## References
- [Flow](https://kotlinlang.org/docs/flow.html)
