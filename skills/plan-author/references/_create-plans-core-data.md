# Core Data

> Persistence patterns for iOS/macOS apps using Core Data. Loaded when domain=macos-apps or iphone-apps.

## When Core Data is the right choice

Use Core Data when:
- You need a local object graph with relationships
- You want change tracking (undo/redo, dirty detection)
- You need NSFetchedResultsController-style live queries
- The data fits a relational model

Consider alternatives when:
- The data is fundamentally documents (use `FileManager` + Codable)
- It's truly key-value (use `UserDefaults` for small, file-based KV stores for large)
- You need cloud sync without CKShare (use SwiftData with CloudKit, or external services)
- It's full-text-search-heavy (use SQLite directly with FTS5)

For new iOS 17+ projects, SwiftData is often a better starting point — Swift-native Core Data successor with cleaner API.

## Stack setup

Modern Core Data stack with NSPersistentContainer:

```swift
import CoreData

final class PersistenceController {
    static let shared = PersistenceController()

    let container: NSPersistentContainer

    init(inMemory: Bool = false) {
        container = NSPersistentContainer(name: "AppModel")
        
        if inMemory {
            container.persistentStoreDescriptions.first!.url = URL(fileURLWithPath: "/dev/null")
        }
        
        container.loadPersistentStores { description, error in
            if let error = error {
                fatalError("Failed to load Core Data: \(error)")
            }
        }
        
        container.viewContext.automaticallyMergesChangesFromParent = true
    }
}
```

## Contexts

- **`viewContext`**: main-thread context for UI; backed by `NSPersistentContainer.viewContext`
- **Background contexts**: created via `newBackgroundContext()`; for write-heavy or import work
- **Child contexts**: short-lived for atomic operations; created via `init(concurrencyType: .privateQueueConcurrencyType)`

Rules:
- UI fetches → viewContext (main thread)
- Heavy writes → background context, then merge to viewContext
- Multi-step atomic operations → child context off viewContext

## Fetch

```swift
let request = NSFetchRequest<Session>(entityName: "Session")
request.predicate = NSPredicate(format: "status == %@", "active")
request.sortDescriptors = [NSSortDescriptor(key: "createdAt", ascending: false)]
request.fetchLimit = 50

do {
    let sessions = try viewContext.fetch(request)
    // sessions is [Session]
} catch {
    print("Fetch failed: \(error)")
}
```

For SwiftUI views, prefer `@FetchRequest` property wrapper:

```swift
@FetchRequest(
    entity: Session.entity(),
    sortDescriptors: [NSSortDescriptor(key: "createdAt", ascending: false)],
    predicate: NSPredicate(format: "status == %@", "active")
) var sessions: FetchedResults<Session>
```

`@FetchRequest` automatically updates the view when the underlying data changes.

## Save

```swift
let session = Session(context: viewContext)
session.id = UUID().uuidString
session.name = "Test"
session.createdAt = Date()
session.status = "active"

do {
    try viewContext.save()
} catch {
    print("Save failed: \(error)")
}
```

`save()` is synchronous on the context's thread. Wrap in `viewContext.perform { }` if you're calling from off-thread (which you generally shouldn't for viewContext).

## Background work

```swift
container.performBackgroundTask { context in
    // Heavy import / batch update
    for item in largeArray {
        let entity = Imported(context: context)
        entity.populate(from: item)
    }
    do {
        try context.save()
    } catch {
        print("Background save failed: \(error)")
    }
}
```

The viewContext picks up changes automatically (because `automaticallyMergesChangesFromParent = true`).

## Delete

```swift
viewContext.delete(session)
try viewContext.save()
```

For batch deletes (faster, doesn't materialize objects):

```swift
let request = NSBatchDeleteRequest(
    fetchRequest: NSFetchRequest(entityName: "Session")
)
request.resultType = .resultTypeObjectIDs
let result = try viewContext.execute(request) as? NSBatchDeleteResult
let deletedIDs = result?.result as? [NSManagedObjectID] ?? []
// Manually merge into viewContext if needed
```

## Migrations

For schema changes:
1. Create a new Model Version (.xcdatamodel file)
2. Add the changes
3. Mark new version as current
4. For non-trivial changes: Mapping Model defines transformations

Lightweight migrations (just add/remove non-required fields) happen automatically. Heavy migrations need a Mapping Model.

Test migrations BEFORE shipping — a failed migration on a user's device often means data loss.

## Async patterns (Core Data + async/await)

```swift
extension NSManagedObjectContext {
    func perform<T>(_ block: @escaping () throws -> T) async throws -> T {
        try await withCheckedThrowingContinuation { continuation in
            self.perform {
                do {
                    let result = try block()
                    continuation.resume(returning: result)
                } catch {
                    continuation.resume(throwing: error)
                }
            }
        }
    }
}

// Usage:
let sessions = try await viewContext.perform {
    let request = NSFetchRequest<Session>(entityName: "Session")
    return try self.viewContext.fetch(request)
}
```

iOS 15+ has built-in `perform { ... } async`. The wrapper above is for older targets.

## Common patterns

### Pattern: Repository

Wrap Core Data behind a protocol:

```swift
protocol SessionRepository {
    func all() async throws -> [Session]
    func add(_ session: Session) async throws
    func delete(_ id: String) async throws
}

class CoreDataSessionRepository: SessionRepository { ... }
```

Lets you swap Core Data for SwiftData or a mock without rewriting consumers.

### Pattern: NSFetchedResultsController for live UI

For non-SwiftUI list views:

```swift
let frc = NSFetchedResultsController(
    fetchRequest: request,
    managedObjectContext: viewContext,
    sectionNameKeyPath: nil,
    cacheName: nil
)
frc.delegate = self
try frc.performFetch()
// Implement NSFetchedResultsControllerDelegate to update table view
```

For SwiftUI: `@FetchRequest` handles this for you.

## Anti-patterns

| Anti-pattern | Why | Do instead |
|---|---|---|
| Using viewContext from background | Crashes / corruption | Use `performBackgroundTask` |
| No error handling on save | Silently loses data | Always `do/catch` on save |
| Force-unwrapping fetch results | Crashes on empty | Check count or use `first` |
| In-memory store without justification | Data lost on quit | Use in-memory only for tests |
| Heavy queries on main thread | Janky UI | Move to background context |

## Cross-references

- _Historical: this content was absorbed from the legacy `create-plans` skill into its absorbing parent. The original `create-plans` skill no longer exists in v1._
- `references/swift-conventions.md` — sibling reference
- `references/swift-concurrency.md` — async Core Data
- `references/swiftui-layout.md` — @FetchRequest in views
- Apple's Core Data documentation — externally authoritative source
