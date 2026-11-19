---
title: Never Narrate the Signature in a Doc Comment
impact: MEDIUM
impactDescription: removes comments that add zero information beyond the method signature
tags: [javadoc, documentation, comments]
---

# Never Narrate the Signature in a Doc Comment [MEDIUM]

## Description
A doc comment that restates the method name and parameter list in prose ("Sets the name. @param name the name") transfers no information the signature didn't already give the reader — it exists to satisfy a linter demanding every public method have *a* Javadoc, not to help anyone. Worse than useless, it's a maintenance liability: when the method's actual behavior changes but the narration still parses as plausible prose, nothing forces it to be updated, and a reader trusts a stale doc comment more than they'd trust no comment at all. A doc comment earns its place only by saying something the signature can't: a precondition, a side effect, a unit, an edge case, a reason.

The test for any doc comment before it's written: if it were deleted, would the caller lose real information, or only a sentence that repeats the identifier? If nothing is lost, either delete it or replace it with the one fact — a range, a default, a failure mode — that the signature doesn't carry.

## Bad Example
```java
/**
 * Sets the timeout.
 *
 * @param timeout the timeout
 */
public void setTimeout(Duration timeout) {
    this.timeout = timeout;
}

/**
 * Gets the retry count.
 *
 * @return the retry count
 */
public int getRetryCount() {
    return retryCount;
}
```

## Good Example
```java
/**
 * Bounds each attempt individually, not the call as a whole.
 *
 * @param timeout the overall call may take up to {@code timeout * (getRetryCount() + 1)}
 */
public void setTimeout(Duration timeout) {
    this.timeout = timeout;
}

public int getRetryCount() {
    return retryCount;
}
```

## Notes
- A trivial accessor with no non-obvious behavior is better left with no Javadoc at all than with a narrated one — see `javadoc-param-return-tags-only-when-non-obvious`.
- This is the Javadoc analogue of the general comment rule: comment the consequence, not the visible arguments — a non-doc `//` comment that restates the line above it has the same problem.
- A lint rule requiring 100% Javadoc coverage on public methods produces exactly this anti-pattern at scale; requiring Javadoc only where the contract is non-obvious avoids the incentive to narrate.

## References
- [How to Write Doc Comments for the Javadoc Tool (Oracle)](https://www.oracle.com/technical-resources/articles/java/javadoc-tool.html)
- [Effective Java, 3rd Edition — Item 56: Write doc comments for all exposed API elements](https://www.oreilly.com/library/view/effective-java-3rd/9780134686097/)
