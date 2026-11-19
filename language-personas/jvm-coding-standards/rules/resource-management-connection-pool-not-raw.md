---
title: Acquire Database Connections from a Pool, Never Raw per Call
impact: CRITICAL
impactDescription: avoids paying full TCP-and-authentication connection setup cost on every single query
tags: [resource-management, connection-pool, database, performance]
---

# Acquire Database Connections from a Pool, Never Raw per Call [CRITICAL]

## Description
Opening a JDBC `Connection` directly with `DriverManager.getConnection(...)` pays the full cost of a new TCP handshake and database authentication on every single call — orders of magnitude slower than reusing an already-established connection, and under any real load this either exhausts the database's own connection limit or serializes the application behind connection setup latency. A connection pool (HikariCP, or the pool bundled with the application framework) opens a bounded, pre-warmed set of connections up front and hands them out and takes them back per unit of work — the application still calls `close()` on what it borrows, but that call returns the connection to the pool rather than tearing down the underlying socket. Never bypass the pool with a raw `DriverManager` call in application code; if a genuinely unpooled, exclusive connection is required (a schema migration tool, an administrative script), that is a distinct, narrow case with its own justification, not the default.

## Bad Example
```java
public Order findOrder(String id) throws SQLException {
    Connection conn = DriverManager.getConnection(url, user, password); // new TCP + auth handshake, every call
    try (PreparedStatement stmt = conn.prepareStatement("SELECT * FROM orders WHERE id = ?")) {
        stmt.setString(1, id);
        ResultSet rs = stmt.executeQuery();
        return rs.next() ? mapOrder(rs) : null;
    } finally {
        conn.close(); // tears the connection down entirely — the work of opening it is thrown away
    }
}
```

## Good Example
```java
public class OrderRepository {
    private final DataSource dataSource; // backed by a pool (e.g. HikariCP), configured once at startup

    public Optional<Order> findOrder(String id) throws SQLException {
        try (Connection conn = dataSource.getConnection(); // borrowed from the pool, not opened fresh
             PreparedStatement stmt = conn.prepareStatement("SELECT * FROM orders WHERE id = ?")) {
            stmt.setString(1, id);
            ResultSet rs = stmt.executeQuery();
            return rs.next() ? Optional.of(mapOrder(rs)) : Optional.empty();
        } // conn.close() returns it to the pool; the underlying socket stays open for reuse
    }
}
```

## Notes
- `try-with-resources` around a pooled `Connection` is still correct and required (`resource-management-try-with-resources`) — the pool changes what `close()` does, not whether it needs to be called.
- Size the pool to the database's actual connection budget and the application's real concurrency, not arbitrarily large — an oversized pool can overwhelm the database just as effectively as no pooling at all.
- A `DataSource` obtained from the pool should be constructed once (application startup, or via the framework's dependency injection) and shared, not recreated per request.

## References
- [HikariCP — About Pool Sizing](https://github.com/brettwooldridge/HikariCP/wiki/About-Pool-Sizing)
- [JDBC DataSource (Java SE 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.sql/javax/sql/DataSource.html)
