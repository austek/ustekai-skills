---
title: Put @Transactional on Service Methods, Not Controllers or Repositories
impact: HIGH
impactDescription: one use case equals one transaction, with no self-invocation surprises
tags: [spring, transactions, jpa]
---

# Put @Transactional on Service Methods, Not Controllers or Repositories [HIGH]

## Description
Targets Spring Boot 4.x (Spring Framework 7). A transaction should wrap a use case, so annotate the public service method that implements it. Mark read-only use cases `@Transactional(readOnly = true)`. Spring applies the annotation through a proxy, so calling a `@Transactional` method from another method of the same class bypasses it. Do not hold a transaction across a remote HTTP call.

## Bad Example
```java
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
class OrderController {
    private final OrderRepository orders;

    OrderController(OrderRepository orders) { this.orders = orders; }

    @Transactional // couples database transaction management to the web layer
    @PostMapping("/orders")
    Order place(@RequestBody NewOrder body) { return orders.save(Order.from(body)); }
}
```

## Good Example
```java
import java.util.Optional;
import org.springframework.data.repository.CrudRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

record OrderId(long value) {}
record NewOrder(String sku) {}
record OrderPlaced(OrderId orderId) {}
record Order(OrderId id, String sku) {
    static Order from(NewOrder order) { return new Order(new OrderId(0), order.sku()); }
}
interface OrderRepository extends CrudRepository<Order, OrderId> {}
interface Outbox { void add(Object event); }

@Service
class OrderService {
    private final OrderRepository orders;
    private final Outbox outbox;

    OrderService(OrderRepository orders, Outbox outbox) {
        this.orders = orders;
        this.outbox = outbox;
    }

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
- `@TransactionalEventListener(phase = AFTER_COMMIT)` runs in process after commit: a crash or listener failure loses the event. Use it for best-effort side effects; use an outbox table (as above) when publication must be durable.
- Call an external service outside the transaction, then open a short one to record the result.

## References
- [Declarative transaction management](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative.html)
