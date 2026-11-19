---
title: Test With Slices and @ServiceConnection Testcontainers
impact: HIGH
impactDescription: fast focused tests, and integration tests against a real database without manual wiring
tags: [spring, testing, testcontainers, boot4]
---

# Test With Slices and @ServiceConnection Testcontainers [HIGH]

## Description
Load only the layer under test: `@WebMvcTest` for controllers, `@DataJpaTest` for repositories, `@JsonTest` for serialization. Reserve `@SpringBootTest` for a few end-to-end checks. For real dependencies, declare a Testcontainers bean with `@ServiceConnection`; Boot configures the datasource URL itself, with no `@DynamicPropertySource`. Container lifecycle rules are in [jvm-testing](../../jvm-testing/SKILL.md).

Spring Boot 4 moved the test annotations into per-technology modules and removed `@MockBean`/`@SpyBean`. Use the new packages and `@MockitoBean`/`@MockitoSpyBean`.

## Bad Example
```java
@SpringBootTest // starts the whole context to test one controller
class OrderControllerTest {
    @MockBean OrderService service; // removed in Boot 4
}
```

## Good Example
```java
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.test.context.bean.override.mockito.MockitoBean;

@WebMvcTest(OrderController.class)
class OrderControllerTest {
    @Autowired MockMvcTester mvc;
    @MockitoBean OrderService service;
}

import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest;
import org.springframework.boot.jdbc.test.autoconfigure.AutoConfigureTestDatabase;
import org.springframework.boot.testcontainers.service.connection.ServiceConnection;
import org.testcontainers.postgresql.PostgreSQLContainer;

@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@Import(ContainersConfig.class)
class OrderRepositoryTest {}

@TestConfiguration(proxyBeanMethods = false)
class ContainersConfig {
    @Bean @ServiceConnection
    PostgreSQLContainer postgres() { return new PostgreSQLContainer("postgres:17-alpine"); }
}
```

## Notes
- Add the `spring-boot-testcontainers` test dependency (and `testcontainers-junit-jupiter` plus the database module) for `@ServiceConnection`.
- Boot 4 uses Testcontainers 2: the module is `org.testcontainers:testcontainers-postgresql` and `PostgreSQLContainer` is the non-generic `org.testcontainers.postgresql` type (Testcontainers 1 used `org.testcontainers.containers.PostgreSQLContainer<?>`).
- In Boot 4, `@SpringBootTest` no longer provides `MockMvc`, `TestRestTemplate` or `WebClient` by itself: add `@AutoConfigureMockMvc`, `@AutoConfigureTestRestTemplate` or `@AutoConfigureRestTestClient`.
- Package names above are from the Boot 4.1 reference. Imports from `org.springframework.boot.test.autoconfigure.*` are the Boot 3 locations.
- Kotlin: confirm that `springmockk` supports your Boot version before using `@MockkBean`; otherwise use `@MockitoBean` or a fake.
- Do not use H2 in place of the production database; behavior and SQL dialects differ.

## References
- [Testing Spring Boot applications](https://docs.spring.io/spring-boot/reference/testing/spring-boot-applications.html)
- [Spring Boot 4.0 Migration Guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide)
- [Testcontainers support](https://docs.spring.io/spring-boot/reference/testing/testcontainers.html)
