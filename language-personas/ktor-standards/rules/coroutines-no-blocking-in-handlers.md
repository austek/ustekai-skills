---
title: Never Block the Event Loop in Route Handlers
impact: CRITICAL
impactDescription: one blocking call can stall every request on the same Netty or CIO event-loop thread
tags: [ktor, coroutines, blocking]
---

# Never Block the Event Loop in Route Handlers [CRITICAL]

## Description
Ktor handlers run as coroutines on a small, CPU-sized pool. A blocking JDBC call, file read or `Thread.sleep` inside a handler holds that thread and stalls other requests. Call suspending APIs where they exist. Move unavoidable blocking work to `withContext(Dispatchers.IO)`, preferably inside the repository so handlers stay free of dispatcher choices. Do not use `runBlocking` in handlers.

## Bad Example
```kotlin
import io.ktor.server.application.call
import io.ktor.server.response.respond
import io.ktor.server.routing.Route
import io.ktor.server.routing.get
import kotlinx.serialization.Serializable

@Serializable
data class Row(val id: Long)

fun interface BlockingJdbc { fun query(sql: String): List<Row> }

fun Route.reportRoutes(jdbc: BlockingJdbc) {
    get("/report") {
        val rows = jdbc.query("select * from big_table") // blocks the event loop
        call.respond(rows)
    }
}
```

## Good Example
```kotlin
import io.ktor.server.application.call
import io.ktor.server.response.respond
import io.ktor.server.routing.Route
import io.ktor.server.routing.get
import javax.sql.DataSource
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.serialization.Serializable

@Serializable
data class Row(val id: Long)

class ReportRepository(private val db: DataSource, private val io: CoroutineDispatcher = Dispatchers.IO) {
    suspend fun load(): List<Row> = withContext(io) { db.connection.use { /* query */ emptyList() } }
}

fun Route.reportRoutes(repository: ReportRepository) {
    get("/report") { call.respond(repository.load()) }
}
```

## Notes
- Prefer a coroutine-aware driver (R2DBC) where it fits. JDBC stays blocking even behind Exposed's `newSuspendedTransaction`: it only moves the blocking call onto the dispatcher you pass.
- Bound `Dispatchers.IO` work with `Dispatchers.IO.limitedParallelism(n)` to protect a small connection pool.
- A blocking stack on virtual threads is an alternative; Ktor handlers are still coroutines, so keep the rule.

## References
- [Ktor coroutines in server](https://ktor.io/docs/server-requests.html)
- [limitedParallelism](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-coroutine-dispatcher/limited-parallelism.html)
