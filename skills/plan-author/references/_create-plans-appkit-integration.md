# AppKit Integration

> When building macOS apps in SwiftUI, often you need to drop down to AppKit for capabilities SwiftUI doesn't expose. Loaded when domain=macos-apps.

## When to drop to AppKit

SwiftUI on macOS is missing or under-developed for:

- Custom window chrome / non-standard window shapes
- Toolbar customization (the user-customizable kind)
- Sophisticated text editing (anything beyond `TextField` / `TextEditor`)
- NSDocument / document-based architecture
- Custom drag-and-drop with NSDragOperation flags
- Sophisticated menu bar manipulation
- Spotlight integration / Quick Look / Services menu
- AppleScript / Automation
- Status bar items (`NSStatusItem`)

For these, you bridge AppKit into SwiftUI.

## Bridging mechanisms

### NSViewRepresentable (for an NSView)

```swift
import SwiftUI
import AppKit

struct CustomTextView: NSViewRepresentable {
    @Binding var text: String

    func makeNSView(context: Context) -> NSScrollView {
        let scrollView = NSTextView.scrollableTextView()
        let textView = scrollView.documentView as! NSTextView
        textView.delegate = context.coordinator
        textView.string = text
        return scrollView
    }

    func updateNSView(_ nsView: NSScrollView, context: Context) {
        let textView = nsView.documentView as! NSTextView
        if textView.string != text {
            textView.string = text
        }
    }

    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }

    class Coordinator: NSObject, NSTextViewDelegate {
        var parent: CustomTextView
        init(_ parent: CustomTextView) { self.parent = parent }

        func textDidChange(_ notification: Notification) {
            guard let textView = notification.object as? NSTextView else { return }
            parent.text = textView.string
        }
    }
}
```

The Coordinator class bridges AppKit delegate callbacks back into SwiftUI bindings.

### NSViewControllerRepresentable (for an NSViewController)

Same pattern but for an entire view controller — useful when the AppKit code is already organized as VC + view.

### NSHostingView (the reverse direction — embed SwiftUI in AppKit)

```swift
import AppKit
import SwiftUI

class MyWindow: NSWindow {
    init() {
        super.init(contentRect: NSRect(x: 0, y: 0, width: 400, height: 300),
                   styleMask: [.titled, .closable, .resizable],
                   backing: .buffered, defer: false)
        contentView = NSHostingView(rootView: MySwiftUIView())
    }
}
```

Useful for legacy AppKit apps adopting SwiftUI piecemeal.

## NSDocument integration

For document-based apps (file open/save, undo, autosave):

```swift
import AppKit

class TextDocument: NSDocument {
    var content: String = ""

    override class var autosavesInPlace: Bool { return true }

    override func makeWindowControllers() {
        let host = NSHostingController(rootView: EditorView(content: $content))
        let window = NSWindow(contentViewController: host)
        addWindowController(NSWindowController(window: window))
    }

    override func data(ofType typeName: String) throws -> Data {
        return content.data(using: .utf8) ?? Data()
    }

    override func read(from data: Data, ofType typeName: String) throws {
        content = String(data: data, encoding: .utf8) ?? ""
    }
}
```

NSDocument gets you free: file menu items, undo, autosave, version browser, document-icon-in-titlebar.

## Status bar item

```swift
import AppKit
import SwiftUI

class StatusBarController {
    var statusItem: NSStatusItem
    var popover: NSPopover

    init() {
        statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
        statusItem.button?.title = "🐠"
        statusItem.button?.action = #selector(togglePopover(_:))
        statusItem.button?.target = self

        popover = NSPopover()
        popover.contentSize = NSSize(width: 300, height: 400)
        popover.behavior = .transient
        popover.contentViewController = NSHostingController(rootView: PopoverView())
    }

    @objc func togglePopover(_ sender: AnyObject) {
        if popover.isShown {
            popover.performClose(sender)
        } else if let button = statusItem.button {
            popover.show(relativeTo: button.bounds, of: button, preferredEdge: .minY)
        }
    }
}
```

Status bar items are core to many menubar-utility apps.

## Menu bar customization

```swift
import AppKit

@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup { ContentView() }
            .commands {
                CommandGroup(replacing: .newItem) {
                    Button("New Session") { ... }
                        .keyboardShortcut("n", modifiers: .command)
                }
            }
    }
}
```

`.commands` is the SwiftUI surface. For deeper customization (dynamic items, accelerators), drop to NSMenu via app delegate.

## Pasteboard / drag-drop

```swift
import AppKit

// Read from pasteboard
if let string = NSPasteboard.general.string(forType: .string) {
    print("Clipboard: \(string)")
}

// Write to pasteboard
NSPasteboard.general.clearContents()
NSPasteboard.general.setString("Hello", forType: .string)
```

For SwiftUI drag-drop: `.onDrag` and `.onDrop` modifiers. Drop to AppKit when you need NSDraggingInfo flags or custom DragOperation logic.

## File panels

```swift
import AppKit

let panel = NSOpenPanel()
panel.allowedContentTypes = [.text, .plainText]
panel.allowsMultipleSelection = false
panel.canChooseDirectories = false
if panel.runModal() == .OK, let url = panel.url {
    // user picked url
}
```

For save:

```swift
let savePanel = NSSavePanel()
savePanel.allowedContentTypes = [.plainText]
savePanel.nameFieldStringValue = "Untitled.txt"
if savePanel.runModal() == .OK, let url = savePanel.url {
    try? "content".write(to: url, atomically: true, encoding: .utf8)
}
```

## Toolbar (advanced)

SwiftUI's `.toolbar` is fine for simple cases. For user-customizable toolbars (Add / Remove / Reorder via right-click), use NSToolbar with NSToolbarDelegate.

## Anti-patterns

| Anti-pattern | Why | Do instead |
|---|---|---|
| Dropping to AppKit when SwiftUI suffices | Adds complexity for nothing | Check SwiftUI first |
| Bridging without Coordinator for delegates | Memory leaks; events never fire back | Always use Coordinator pattern |
| Using AppKit-only types in SwiftUI views directly | Won't compile / crashes at runtime | Use representable wrapper |
| Mixing main-thread AppKit with background SwiftUI | Crashes | Both on main; use Tasks for async work |

## Cross-references

- _Historical: this content was absorbed from the legacy `create-plans` skill into its absorbing parent. The original `create-plans` skill no longer exists in v1._
- `references/swift-conventions.md` — sibling reference
- `references/swiftui-layout.md` — when SwiftUI is enough
- `references/swift-concurrency.md` — async AppKit operations
- Apple's "Adopting SwiftUI in your existing app" — externally authoritative source
