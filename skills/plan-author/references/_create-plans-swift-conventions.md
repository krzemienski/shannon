# Swift Conventions

> Loaded when create-plans is operating in the macOS / iOS expertise domain. Swift-specific naming, code-style, and idiom conventions that should inform Swift / SwiftUI phase plans.

## Loading discipline

This reference is conditionally loaded by the create-plans skill ONLY when the project domain is detected as `macos-apps` or `iphone-apps` (or `swift-midi-apps`, `unity-games` partial). For non-Swift projects, this file should NOT be in context.

The conditional load preserves the context budget for other projects.

## Naming conventions

### Types

- `UpperCamelCase` for types: `class SessionManager`, `struct UserProfile`, `enum AuthState`
- Acronyms in types: keep canonical case — `URLSession`, `HTTPClient`, `JSONDecoder`
- Generic type parameters: single uppercase letter for simple cases (`T`, `U`), descriptive name otherwise (`Element`, `Wrapped`)

### Variables, properties, methods

- `lowerCamelCase`: `let sessionToken`, `var isLoading`, `func refresh()`
- Boolean properties: `is`, `has`, `should`, `can`, `will` prefixes — `isExpired`, `hasUnsavedChanges`
- Method names read like sentences: `func sortDescriptors(for type: Type)` — call site reads as "sort descriptors for type"

### Constants

- `lowerCamelCase` for instance constants
- `lowerCamelCase` for static constants (NOT `kFoo` Objective-C style anymore)
- File-private with `private let MAX_RETRIES = 3` is acceptable for SCREAMING_CASE if it represents a true constant

### Files

- `<TypeName>.swift` — one type per file when reasonable
- `<TypeName>+<Extension>.swift` — extensions on existing types
- `<Feature>ViewModel.swift`, `<Feature>View.swift` for SwiftUI

## Code style

### Optionals

Prefer:
```swift
if let value = optional { ... }
guard let value = optional else { return }
let result = optional ?? defaultValue
```

Avoid:
```swift
optional!                  // force unwrap — only when truly impossible to be nil
optional.unsafelyUnwrapped  // rarely justified
```

### Trailing closures

```swift
// Good:
sessions.map { $0.id }
list.filter { $0.isActive }

// Less good when the closure is more than a few characters:
sessions.map { session in
    let processed = process(session)
    return processed.id
}
```

### `if let` vs `guard let`

`guard let` for early-return; `if let` for branching:

```swift
// guard for preconditions
guard let user = currentUser else {
    presentLoginScreen()
    return
}

// if-let for branching
if let user = currentUser {
    showProfile(user)
} else {
    showAnonymousState()
}
```

### `as?` vs `as!`

```swift
let cell = tableView.dequeueReusableCell(...) as? CustomCell
// vs.
let cell = tableView.dequeueReusableCell(...) as! CustomCell
```

`as?` returns optional, lets you handle nil; `as!` crashes on mismatch. Prefer `as?` unless the cast is structurally guaranteed.

## Idioms

### Computed properties for derivation

```swift
struct User {
    let firstName: String
    let lastName: String
    var fullName: String { "\(firstName) \(lastName)" }
}
```

If derivable, compute on access instead of storing.

### Lazy stored properties

```swift
class ExpensiveResource {
    lazy var heavyComputation: Data = {
        // computed once, on first access
        return performHeavy()
    }()
}
```

For values that are expensive to compute and not always needed.

### Default protocol implementations

```swift
protocol Identifiable {
    var id: String { get }
}

extension Identifiable {
    var hashKey: String { "\(type(of: self)):\(id)" }
}
```

Default implementations in extensions, conformances in declarations. Lets consumers override per-type if needed.

## SwiftUI-specific

(More detail in `swiftui-layout.md` — this is the high-level summary)

- `@State` for view-local mutable state
- `@Binding` for parent-passed mutable state
- `@StateObject` for view-owned reference type
- `@ObservedObject` for parent-passed reference type
- `@EnvironmentObject` for tree-wide shared state
- `@Environment` for system-provided values

Body protocol return: `some View` (opaque type, compiler-determined).

## Concurrency (more detail in `swift-concurrency.md`)

- Modern Swift: `async`/`await` over completion handlers
- `Task { }` to spawn unstructured concurrency
- `actor` for thread-safe reference types
- `@MainActor` for UI updates

## Error handling

```swift
enum AppError: Error {
    case networkUnavailable
    case decodingFailed(reason: String)
    case unauthorized
}

func fetchSessions() async throws -> [Session] {
    do {
        let data = try await network.get("/sessions")
        return try decoder.decode([Session].self, from: data)
    } catch is URLError {
        throw AppError.networkUnavailable
    } catch let DecodingError.dataCorrupted(ctx) {
        throw AppError.decodingFailed(reason: ctx.debugDescription)
    }
}
```

Typed errors over untyped `Error` when callers must react differently to error categories.

## Anti-patterns

| Anti-pattern | Why | Do instead |
|---|---|---|
| Force-unwrap optionals (`!`) without justification | Crashes on nil; loses safety | `if let` / `guard let` / `??` |
| Returning `Any` from public API | Loses type safety | Specific type or generic |
| Implicit-unwrap (`String!` property) | Crash risk | Optional + handling |
| Using `as!` for runtime casts | Crash on mismatch | `as?` + handle nil |
| `class` when `struct` would suffice | Reference semantics where value is clearer | Prefer `struct` |
| Global mutable state | Threading issues; testability problems | Inject via parameters |

## Cross-references

- _Historical: this content was absorbed from the legacy `create-plans` skill into its absorbing parent. The original `create-plans` skill no longer exists in v1._ (this loads for macOS/iOS domain only)
- `references/swiftui-layout.md` — SwiftUI layout patterns
- `references/swift-concurrency.md` — async/await + actors
- `references/core-data.md` — persistence patterns
- `references/appkit-integration.md` — bridging AppKit into SwiftUI
