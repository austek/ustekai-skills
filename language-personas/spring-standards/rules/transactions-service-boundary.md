---
title: Put @Transactional on Service Methods, Not Controllers or Repositories
impact: HIGH
impactDescription: one use case equals one transaction, with no self-invocation surprises
tags: [spring, transactions, jpa]
---

# Put @Transactional on Service Methods, Not Controllers or Repositories [HIGH]

## Description
A transaction should wrap a use case, so annotate the public service method that implements it. Mark read-only use cases `@Transactional(readOnly = true)`. Spring applies the annotation through a proxy, so calling a `@Transactional` method from another method of the same class bypasses it. Do not hold a transaction across a remote HTTP call.

## Bad Example
```java
@RestController
class OrderController {
    @Transactional // holds a connection for the whole request, including serialization
    @PostMapping("/orders")
    Order place(@RequestBody NewOrder body) { /* ... */ }
}
```

## Good Example
```java
@Service
class OrderService {
    @Transactional
    public Order place(NewOrder order) {
        Order saved = orders.save(Order.from(order));
        outbox.add(new OrderPlaced(saved.id())); // same transaction as the state change
        return saved;
    }

    @Transactional(readOnly = true)
    public Optional<Order> find(OrderId id) { return orders.findById(id); }
}
```

## Notes
- Kotlin: apply the `kotlin-spring` compiler plugin so `@Service` classes are open and proxies work.
- Publish events after commit with `@TransactionalEventListener(phase = AFTER_COMMIT)` or an outbox table.
- Call an external service outside the transaction, then open a short one to record the result.

## References
- [Declarative transaction management](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative.html)
