---
title: Model Expected Failures as Values, Not Exceptions
impact: HIGH
impactDescription: callers are forced by the compiler to handle each failure case
tags: [errors, sealed, result]
---

# Model Expected Failures as Values, Not Exceptions [HIGH]

## Description
Kotlin has no checked exceptions, so a thrown exception is invisible in the signature. Return a sealed result for domain failures a caller can act on, and keep exceptions for bugs and infrastructure faults. Use `kotlin.Result` only for wrapping a throwing call at a boundary; it cannot carry a typed error. Arrow's `Either<E, A>` is the typed alternative where the team uses it.

## Bad Example
```kotlin
fun withdraw(account: Account, amount: Money): Account {
    if (amount > account.balance) throw InsufficientFunds() // invisible in the signature
    return account.copy(balance = account.balance - amount)
}
```

## Good Example
```kotlin
sealed interface WithdrawResult {
    data class Ok(val account: Account) : WithdrawResult
    data class InsufficientFunds(val shortBy: Money) : WithdrawResult
}

fun withdraw(account: Account, amount: Money): WithdrawResult =
    if (amount > account.balance) WithdrawResult.InsufficientFunds(amount - account.balance)
    else WithdrawResult.Ok(account.copy(balance = account.balance - amount))
```

## Notes
- Never catch `Throwable` or `Exception` blindly in suspend code; see `coroutines-rethrow-cancellation`.
- Translate to HTTP status or exit codes only at the outermost layer.

## References
- [Kotlin sealed classes](https://kotlinlang.org/docs/sealed-classes.html)
