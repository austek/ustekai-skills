---
title: Never Launch Coroutines in GlobalScope
impact: CRITICAL
impactDescription: GlobalScope work is never cancelled with its caller, leaking tasks and swallowing failures
tags: [coroutines, structured-concurrency]
---

# Never Launch Coroutines in GlobalScope [CRITICAL]

## Description
Every coroutine needs an owner with a bounded lifetime. `GlobalScope.launch` has no parent, so cancellation and exceptions do not propagate and the work can outlive the request, the test, or the application. Use `coroutineScope { }` inside a suspend function, or inject a `CoroutineScope` tied to a component's lifecycle.

## Bad Example
```kotlin
fun onEvent(event: Event) {
    GlobalScope.launch { handler.handle(event) }
}
```

## Good Example
```kotlin
class EventProcessor(private val scope: CoroutineScope, private val handler: Handler) {
    fun onEvent(event: Event) = scope.launch { handler.handle(event) }
}

suspend fun loadAll(ids: List<Id>): List<Item> = coroutineScope {
    ids.map { async { repository.load(it) } }.awaitAll()
}
```

## Notes
- Use `supervisorScope` when one child's failure must not cancel its siblings.
- Cancel an owned scope on shutdown: `scope.cancel()`.

## References
- [Coroutines basics: structured concurrency](https://kotlinlang.org/docs/coroutines-basics.html#structured-concurrency)
