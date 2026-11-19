---
title: Log Constant Messages With Structured Fields, Not String Concatenation
impact: MEDIUM
impactDescription: avoids building strings for disabled levels and keeps messages groupable
tags: [logging, performance, observability]
---

# Log Constant Messages With Structured Fields, Not String Concatenation [MEDIUM]

## Description
Concatenating values into the message builds the string even when the level is disabled and makes every message unique, which defeats grouping. Use SLF4J placeholders or the fluent `addKeyValue` API. Guard only expensive argument computation, with a `Supplier` or `isDebugEnabled()`.

## Bad Example
```java
log.debug("loaded " + items.size() + " items for " + tenant + ": " + render(items));
```

## Good Example
```java
log.atDebug()
   .addKeyValue("count", items.size())
   .addKeyValue("tenant", tenant)
   .addKeyValue("items", () -> render(items)) // evaluated only when DEBUG is on
   .log("items loaded");
```

## Notes
- Keep rendered values out of the message text: JSON encoders write the formatted message, so a `{}` placeholder filled with a changing value makes every line unique and breaks grouping (see `logging-structured-json`).
- In Kotlin use kotlin-logging lambdas: `logger.debug { "items loaded" }`.
- Pass the exception as the last argument or `.setCause(e)`; never `e.getMessage()` alone.

## References
- [SLF4J FAQ: parameterized logging](https://www.slf4j.org/faq.html#logging_performance)
