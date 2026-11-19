---
title: Prefer Fakes Over MockK; Avoid Relaxed Mocks
impact: MEDIUM
impactDescription: tests assert behavior, not call choreography, and survive refactors
tags: [mockk, fakes, test-doubles]
---

# Prefer Fakes Over MockK; Avoid Relaxed Mocks [MEDIUM]

## Description
For a stateful collaborator, write a small in-memory fake. Use MockK only at real boundaries, with `coEvery`/`coVerify` for suspend functions. A `relaxed = true` mock returns defaults for everything, so a missing stub no longer fails the test. Never mock a type you own that has simple behavior, or a Kotlin `value class`/`data class`.

## Bad Example
```kotlin
val repo = mockk<UserRepository>(relaxed = true)
service.rename(id, "Ada")
verify { repo.save(any()) } // proves a call happened, not that the name changed
```

## Good Example
```kotlin
import kotlinx.coroutines.test.runTest
import kotlin.test.Test
import kotlin.test.assertEquals

@JvmInline value class UserId(val value: String)
data class User(val id: UserId, val name: String)

interface UserRepository {
    suspend fun find(id: UserId): User?
    suspend fun save(user: User)
}

class UserService(private val repo: UserRepository) {
    suspend fun rename(id: UserId, name: String) {
        repo.find(id)?.let { repo.save(it.copy(name = name)) }
    }
}

class FakeUserRepository : UserRepository {
    val users = mutableMapOf<UserId, User>()
    override suspend fun find(id: UserId) = users[id]
    override suspend fun save(user: User) { users[user.id] = user }
}

class UserServiceTest {
    @Test
    fun `rename stores the new name`() = runTest {
        val id = UserId("u-1")
        val repo = FakeUserRepository().apply { users[id] = User(id, "Grace") }
        val service = UserService(repo)
        service.rename(id, "Ada")
        assertEquals("Ada", repo.users.getValue(id).name)
    }
}
```

## Notes
- Use `coVerify(exactly = 1)` only for outward effects (email sent, event published).
- MockK cannot mock inline functions; test them through their callers or a fake.
- `object` mocks need `mockkObject`; call `unmockkAll` in `@AfterEach`.

## References
- [MockK](https://mockk.io)
