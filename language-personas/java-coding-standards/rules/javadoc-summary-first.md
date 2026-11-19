---
title: Start Every Doc Comment With a Summary Sentence
impact: MEDIUM
impactDescription: the summary is the only text shown in indexes and member tables; tag-only blocks render empty there
tags: [javadoc, documentation, style]
---

# Start Every Doc Comment With a Summary Sentence [MEDIUM]

## Description
The first sentence of a doc comment is what Javadoc puts in class and method indexes. A block that holds only tags has no summary, so the index entry is blank. Google Java Style requires each block to begin with a summary fragment, a noun or verb phrase capitalized and punctuated like a sentence. The summary must still add information (see `javadoc-no-signature-narration`): state the behavior, side effect or constraint, not the method name in prose.

## Bad Example
```java
/**
 * @param timeout the overall call may take up to {@code timeout * (retries + 1)}
 */
public void setTimeout(Duration timeout) { ... }

/** Sets the timeout. */
public void setTimeout(Duration timeout) { ... }
```

## Good Example
```java
/**
 * Bounds each attempt individually, not the call as a whole.
 *
 * @param timeout the overall call may take up to {@code timeout * (retries + 1)}
 */
public void setTimeout(Duration timeout) { ... }
```

## Notes
- Inline `{@return the cached count, or 0 before the first load}` generates both the summary and the `@return` text from one sentence; use it for short methods.
- Error Prone's `MissingSummary` check flags tag-only blocks; Checkstyle's `SummaryJavadoc` checks the first sentence.
- Omit the comment entirely when no honest summary adds information.

## References
- [Google Java Style: Javadoc](https://google.github.io/styleguide/javaguide.html#s7-javadoc)
- [Checkstyle SummaryJavadoc](https://checkstyle.org/checks/javadoc/summaryjavadoc.html)
