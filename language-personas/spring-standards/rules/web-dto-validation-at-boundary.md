---
title: Validate Request DTOs at the Boundary and Never Expose JPA Entities
impact: HIGH
impactDescription: blocks mass-assignment, lazy-loading failures and accidental data exposure
tags: [spring, web, validation, security]
---

# Validate Request DTOs at the Boundary and Never Expose JPA Entities [HIGH]

## Description
Targets Spring Boot 4.x (Spring Framework 7). Bind requests to dedicated DTO records with bean-validation annotations and `@Valid`, and map to the domain inside the service. Return response DTOs, not entities. Binding JSON straight onto an entity allows mass assignment of fields like `role`, and serializing an entity triggers lazy loading and leaks internal columns.

## Bad Example
```java
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@Entity
class User {
    @Id String id;
    String name;
    String role;
    String passwordHash;
}

interface UserRepository extends JpaRepository<User, String> {}

@RestController
class UserController {
    private final UserRepository repo;

    UserController(UserRepository repo) { this.repo = repo; }

    @PostMapping("/users")
    User create(@RequestBody User user) { return repo.save(user); } // client can set id, role, passwordHash
}
```

## Good Example
```java
import jakarta.validation.Valid;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

record User(UUID id, String name) {}

interface UserService { User create(String name, String email); }

@RestController
class UserController {
    record CreateUser(@NotBlank @Size(max = 80) String name, @Email String email) {}

    record UserView(String id, String name) {
        static UserView from(User user) { return new UserView(user.id().toString(), user.name()); }
    }

    private final UserService service;

    UserController(UserService service) { this.service = service; }

    @PostMapping("/users")
    @ResponseStatus(HttpStatus.CREATED)
    UserView create(@Valid @RequestBody CreateUser body) {
        return UserView.from(service.create(body.name(), body.email()));
    }
}
```

## Notes
- Add `spring-boot-starter-validation`: `spring-boot-starter-webmvc` ships the Bean Validation API without a provider, so without it the constraints are silently ignored. Cover it with a test that posts an invalid body and expects 400.
- Kotlin: put validation annotations on constructor properties with an explicit use-site target, for example `@field:NotBlank`. Under Kotlin's default rule an unqualified annotation goes to the constructor parameter first, which Bean Validation treats as a parameter constraint, not a property constraint.
- Validate path and query parameters with constraint annotations directly on the controller method parameters. Do not add class-level `@Validated`: it switches to AOP validation, which throws `ConstraintViolationException` (a 500 under a catch-all handler). MVC's built-in method validation throws `HandlerMethodValidationException`, which `ResponseEntityExceptionHandler` maps to 400.

## References
- [Validation](https://docs.spring.io/spring-framework/reference/core/validation/beanvalidation.html)
