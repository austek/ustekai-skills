---
title: Validate Request DTOs at the Boundary and Never Expose JPA Entities
impact: HIGH
impactDescription: blocks mass-assignment, lazy-loading failures and accidental data exposure
tags: [spring, web, validation, security]
---

# Validate Request DTOs at the Boundary and Never Expose JPA Entities [HIGH]

## Description
Bind requests to dedicated DTO records with bean-validation annotations and `@Valid`, and map to the domain inside the service. Return response DTOs, not entities. Binding JSON straight onto an entity allows mass assignment of fields like `role`, and serializing an entity triggers lazy loading and leaks internal columns.

## Bad Example
```java
@PostMapping("/users")
User create(@RequestBody User user) { return repo.save(user); } // client can set id, role, passwordHash
```

## Good Example
```java
record CreateUser(@NotBlank @Size(max = 80) String name, @Email String email) {}
record UserView(String id, String name) {}

@PostMapping("/users")
@ResponseStatus(HttpStatus.CREATED)
UserView create(@Valid @RequestBody CreateUser body) {
    return UserView.from(service.create(body.name(), body.email()));
}
```

## Notes
- Kotlin: put validation annotations on constructor properties with an explicit use-site target, for example `@field:NotBlank`. Under Kotlin 2.4's default rule an unqualified annotation goes to the constructor parameter first, which Bean Validation treats as a parameter constraint, not a property constraint.
- Validate path and query parameters with `@Validated` on the controller and constraint annotations on the parameters.

## References
- [Validation](https://docs.spring.io/spring-framework/reference/core/validation/beanvalidation.html)
