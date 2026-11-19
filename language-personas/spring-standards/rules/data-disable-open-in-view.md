---
title: Disable Open Session in View and Fetch Explicitly
impact: HIGH
impactDescription: removes hidden queries in the view layer and connections that late lazy loads can hold during serialization
tags: [spring, jpa, performance]
---

# Disable Open Session in View and Fetch Explicitly [HIGH]

## Description
Targets Spring Boot 4.x (Spring Framework 7). Boot enables `spring.jpa.open-in-view` by default, which keeps the JPA persistence context open for the whole request so lazy associations load while the response is serialized. That hides N+1 queries, and each late lazy load can acquire a connection and hold it until the request ends, depending on connection handling. Turn it off and load what each use case needs with fetch joins, entity graphs or projections.

## Bad Example
```yaml
spring:
  jpa:
    open-in-view: true # default
```
```java
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

interface OrderRepository extends JpaRepository<Order, Long> {
    List<Order> findAll(); // later: order.getItems().size() in the controller issues N queries
}
```

## Good Example
```yaml
spring:
  jpa:
    open-in-view: false
```
```java
import java.math.BigDecimal;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

record CustomerId(long value) {}

interface OrderSummary { String getId(); BigDecimal getTotal(); }

interface OrderRepository extends JpaRepository<Order, Long> {
    @Query("select o from Order o join fetch o.items where o.customerId = :id")
    List<Order> findWithItems(@Param("id") CustomerId id);

    List<OrderSummary> findByCustomerId(CustomerId id);
}
```

## Notes
- Enable `hibernate.generate_statistics` in tests, or use a query-count assertion, to catch N+1.
- A `LazyInitializationException` after disabling means a missing fetch, not a reason to re-enable it.

## References
- [Spring Boot: Open EntityManager in View](https://docs.spring.io/spring-boot/reference/data/sql.html#data.sql.jpa-and-spring-data.open-entity-manager-in-view)
