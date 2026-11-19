# Section Definitions

## Coroutines (coroutines)
**Impact:** CRITICAL

**Rules:**
- `coroutines-no-blocking-in-handlers` - Never block the event loop in route handlers

## Configuration (config)
**Impact:** HIGH

**Rules:**
- `config-typed-application-config` - Read configuration once into a typed object from ApplicationConfig

## Errors (errors)
**Impact:** HIGH

**Rules:**
- `errors-status-pages-and-validation` - Map errors centrally with StatusPages and validate bodies with RequestValidation

## Serialization (serialization)
**Impact:** HIGH

**Rules:**
- `serialization-content-negotiation-explicit-json` - Install ContentNegotiation with an explicitly configured kotlinx Json

## Observability (observability)
**Impact:** HIGH

**Rules:**
- `observability-call-id-and-structured-logging` - Add CallId, CallLogging with MDC and JSON output

## Testing (testing)
**Impact:** HIGH

**Rules:**
- `testing-test-application` - Test routes with testApplication and the real module

## Structure (structure)
**Impact:** MEDIUM

**Rules:**
- `structure-module-extension-functions` - Structure a Ktor app as Application.module extensions per feature

## Dependency Injection (di)
**Impact:** MEDIUM

**Rules:**
- `di-constructor-injection-with-koin-modules` - Inject dependencies through constructors; confine Koin to the composition root
