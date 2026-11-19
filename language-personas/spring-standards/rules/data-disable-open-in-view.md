---
title: Disable Open Session in View and Fetch Explicitly
impact: HIGH
impactDescription: removes hidden queries in the view layer and held connections during serialization
tags: [spring, jpa, performance]
---

# Disable Open Session in View and Fetch Explicitly [HIGH]

## Description
Boot enables `spring.jpa.open-in-view` by default, which keeps a JPA session and connection open for the whole request so lazy associations load while the response is serialized. That hides N+1 queries and holds connections under load. Turn it off and load what each use case needs with fetch joins, entity graphs or projections.

## Bad Example
```yaml
spring:
  jpa:
    open-in-view: true # default
```
```java
List<Order> findAll(); // later: order.getItems().size() in the controller issues N queries
```

## Good Example
```yaml
spring:
  jpa:
    open-in-view: false
```
```java
@Query("select o from Order o join fetch o.items where o.customerId = :id")
List<Order> findWithItems(CustomerId id);

interface OrderSummary { String getId(); BigDecimal getTotal(); }
List<OrderSummary> findByCustomerId(CustomerId id);
```

## Notes
- Enable `hibernate.generate_statistics` in tests, or use a query-count assertion, to catch N+1.
- A `LazyInitializationException` after disabling means a missing fetch, not a reason to re-enable it.

## References
- [Spring Boot: Open EntityManager in View](https://docs.spring.io/spring-boot/reference/data/sql.html#data.sql.jpa-and-spring-data.open-entity-manager-in-view)
