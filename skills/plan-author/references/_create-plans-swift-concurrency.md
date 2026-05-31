# Swift Concurrency

> Async/await, actors, structured concurrency. The Swift 5.5+ concurrency model. Loaded when domain=macos-apps or iphone-apps.

## async/await basics

Replace completion handlers with async functions:

```swift
// Old:
func fetchUser(completion: @escaping (User?, Error?) -> Void) { ... }

// New:
func fetchUser() async throws -> User { ... }
```

Call sites:

```swift
// In an async context:
let user = try await fetchUser()

// To launch into async from sync:
Task {
    let user = try await fetchUser()
}
```

`async throws` is more common than `async` alone — most network/IO operations can fail.

## Task

Spawn unstructured concurrency:

```swift
Task {
    let result = try await someAsyncWork()
    print(result)
}

// Task that runs on main:
Task { @MainActor in
    label.text = "Updated"
}

// Detached task (no inheritance from caller):
Task.detached {
    // No actor inheritance, no priority inheritance
    await heavyBackgroundWork()
}
```

`Task` returns a handle you can cancel:

```swift
let handle = Task { ... }
handle.cancel()
```

## TaskGroup (structured concurrency)

For multiple parallel operations:

```swift
let results = await withTaskGroup(of: Result.self) { group in
    for url in urls {
        group.addTask {
            return await fetch(url)
        }
    }
    var collected: [Result] = []
    for await result in group {
        collected.append(result)
    }
    return collected
}
```

Structured concurrency: all child tasks complete (or are cancelled) before the parent returns. Errors propagate cleanly.

## Actors

Reference types that are isolated by default:

```swift
actor SessionStore {
    private var sessions: [Session] = []
    
    func add(_ session: Session) {
        sessions.append(session)
    }
    
    func all() -> [Session] {
        return sessions
    }
}

// Usage:
let store = SessionStore()
await store.add(newSession)
let all = await store.all()
```

Inside an actor: synchronous access to actor state.
Outside an actor: every interaction is `async` (await required).

This eliminates a whole class of threading bugs without manual locks.

## @MainActor

For code that must run on the main thread (UI updates):

```swift
@MainActor
class ViewModel {
    @Published var items: [Item] = []
    
    func reload() async {
        let fetched = try? await network.fetch()
        items = fetched ?? []  // automatically on main
    }
}

// Or per-method:
@MainActor
func updateUI() {
    label.text = "..."
}
```

`@MainActor` annotations cascade — actor-isolated calls into MainActor code must await.

## Sendable

Types that can safely cross actor boundaries:

```swift
struct Session: Sendable {
    let id: String
    let createdAt: Date
}
```

Most value types are implicitly Sendable. Reference types are not (unless explicitly marked + immutable, or they're actors).

Compiler enforces: you can't pass a non-Sendable type across an actor boundary.

## Cancellation

```swift
Task {
    for url in urls {
        try Task.checkCancellation()  // throws CancellationError if cancelled
        let data = try await fetch(url)
        ...
    }
}
```

Check cancellation in loops; respect it. URLSession's async APIs check automatically.

## Continuation (bridge legacy callbacks)

```swift
func legacyFetch() async throws -> Data {
    return try await withCheckedThrowingContinuation { continuation in
        legacy.fetch { data, error in
            if let data = data {
                continuation.resume(returning: data)
            } else {
                continuation.resume(throwing: error ?? UnknownError())
            }
        }
    }
}
```

`withCheckedThrowingContinuation` is the bridge — wrap any completion-based API into async.

Use `withCheckedContinuation` (no throws) for non-failing legacy APIs.

## Common patterns

### Pattern: Cache-then-fetch

```swift
func loadProfile() async throws -> Profile {
    if let cached = await cache.get(.profile) {
        return cached
    }
    let fetched = try await network.fetchProfile()
    await cache.set(.profile, value: fetched)
    return fetched
}
```

### Pattern: Debounce

```swift
private var debounceTask: Task<Void, Never>?

func textChanged(_ text: String) {
    debounceTask?.cancel()
    debounceTask = Task {
        try? await Task.sleep(for: .milliseconds(300))
        guard !Task.isCancelled else { return }
        await search(text)
    }
}
```

### Pattern: Parallel fetches

```swift
async let user = fetchUser()
async let posts = fetchPosts()
async let comments = fetchComments()

let result = (try await user, try await posts, try await comments)
```

`async let` runs the fetches in parallel; `await` waits for all.

## Anti-patterns

| Anti-pattern | Why | Do instead |
|---|---|---|
| `DispatchQueue.main.async` in async code | Mixing concurrency models | `@MainActor` or `MainActor.run` |
| Force-unwrap from async result | `try await foo()!` style | `try?` + handle nil |
| Unstructured `Task { }` without cancellation | Tasks leak; race conditions | Save handle; cancel when done |
| Heavy work in `@MainActor` | Blocks UI | Move to actor or background |
| Mutating shared state without actor | Data race | Wrap in `actor` |

## Cross-references

- _Historical: this content was absorbed from the legacy `create-plans` skill into its absorbing parent. The original `create-plans` skill no longer exists in v1._
- `references/swift-conventions.md` — sibling reference
- `references/swiftui-layout.md` — view + async data
- `references/core-data.md` — async persistence patterns
- Apple's "Concurrency" documentation — externally authoritative source
