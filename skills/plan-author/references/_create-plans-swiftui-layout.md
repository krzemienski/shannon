# SwiftUI Layout

> Layout patterns for SwiftUI views. Loaded conditionally when domain=macos-apps or iphone-apps.

## The SwiftUI layout primitives

| Primitive | Purpose |
|-----------|---------|
| `VStack` | Vertical stack |
| `HStack` | Horizontal stack |
| `ZStack` | Layered (z-axis) stack |
| `Grid` (iOS 16+) | 2D grid layout |
| `LazyVGrid` / `LazyHGrid` | Performance-optimized grids |
| `List` | Scrollable list (iOS-styled) |
| `ScrollView` | Generic scrollable container |
| `GeometryReader` | Access to parent size |

## Spacing + alignment

Stack constructors take alignment + spacing:

```swift
VStack(alignment: .leading, spacing: 16) {
    Text("Title")
    Text("Subtitle")
}
```

Default spacing is system-determined; explicit values for tighter control.

For non-uniform spacing inside a stack:

```swift
VStack(spacing: 0) {
    Text("Header")
        .padding(.bottom, 24)
    Text("Body")
        .padding(.bottom, 8)
    Text("Footer")
}
```

## Frame modifiers

```swift
Text("Hello")
    .frame(width: 200)                       // fixed width
    .frame(maxWidth: .infinity)              // fill horizontally
    .frame(minWidth: 100, maxWidth: 400)     // bounded
    .frame(width: 200, height: 50, alignment: .topLeading)
```

`.frame(maxWidth: .infinity)` is the most-used variant — it makes the view fill its container.

## Padding

```swift
Text("Content")
    .padding()                  // system-default on all sides
    .padding(16)                // 16 on all sides
    .padding(.horizontal)       // system-default horizontal only
    .padding(.bottom, 24)       // 24 only on bottom
```

Modifier order matters: `.padding().background(.red)` makes red INCLUDE the padding; `.background(.red).padding()` makes red EXCLUDE the padding.

## Background + foreground

```swift
Text("Hello")
    .foregroundColor(.white)
    .padding()
    .background(Color.blue)
    .cornerRadius(8)
```

Note: `.cornerRadius(8)` after `.background()` rounds the background.

## Spacers

```swift
HStack {
    Text("Left")
    Spacer()                    // pushes Left and Right apart
    Text("Right")
}

VStack {
    Spacer()                    // top space
    Text("Centered")
    Spacer()                    // bottom space
}
```

Spacer expands to fill available space along its axis.

## GeometryReader (use sparingly)

```swift
GeometryReader { geometry in
    Text("Width: \(geometry.size.width)")
        .frame(width: geometry.size.width * 0.8)
}
```

Powerful but introduces layout complexity. Prefer frame modifiers when possible.

## Adaptive layouts

```swift
if horizontalSizeClass == .compact {
    VStack { content }
} else {
    HStack { content }
}
```

Where:
```swift
@Environment(\.horizontalSizeClass) var horizontalSizeClass
```

Adapts between phone-narrow and iPad-wide layouts.

## Dark mode handling

Mostly automatic via system colors:

```swift
Text("Hello")
    .foregroundColor(.primary)         // adapts to dark/light
    .background(Color(.systemBackground))
```

Custom colors in `Assets.xcassets` can have light + dark variants — defined once, picked automatically.

For explicit:
```swift
@Environment(\.colorScheme) var colorScheme

Text("Hello")
    .foregroundColor(colorScheme == .dark ? .white : .black)
```

## Animation

```swift
@State var isExpanded = false

VStack {
    Button("Toggle") {
        withAnimation(.easeInOut(duration: 0.3)) {
            isExpanded.toggle()
        }
    }
    if isExpanded {
        ExpandedContent()
            .transition(.scale.combined(with: .opacity))
    }
}
```

`withAnimation { }` wraps state changes that should animate. `.transition()` defines the in/out animation for added/removed views.

## Performance: List vs ScrollView+VStack

```swift
// Good for large datasets (lazy rendering):
List(items) { item in
    Row(item: item)
}

// OK for small static content:
ScrollView {
    VStack { ForEach(items) { Row(item: $0) } }
}

// Better for many items but not List-styled:
ScrollView {
    LazyVStack { ForEach(items) { Row(item: $0) } }
}
```

`List` and `LazyVStack` only render visible cells; `VStack` renders everything.

## Common layout patterns

### Hero section + body

```swift
VStack(spacing: 0) {
    HeroImage()
        .frame(height: 300)
    ContentBody()
        .padding()
}
```

### Card list

```swift
ScrollView {
    LazyVStack(spacing: 16) {
        ForEach(items) { item in
            CardView(item: item)
                .padding(.horizontal)
        }
    }
}
```

### Sidebar + detail (iPad / Mac)

```swift
NavigationSplitView {
    Sidebar()
} detail: {
    DetailView()
}
```

### Form

```swift
Form {
    Section("Account") {
        TextField("Email", text: $email)
        SecureField("Password", text: $password)
    }
    Section("Preferences") {
        Toggle("Notifications", isOn: $notificationsOn)
    }
}
```

## Anti-patterns

| Anti-pattern | Why | Do instead |
|---|---|---|
| Hardcoded sizes everywhere | Doesn't adapt to dynamic type | Use `.frame(maxWidth: .infinity)` + dynamic type |
| `GeometryReader` for trivial layouts | Adds complexity | `.frame()` modifiers usually suffice |
| `VStack` with many children for scrollable content | Doesn't lazy-render | `LazyVStack` inside `ScrollView`, or `List` |
| Custom colors in code | Doesn't adapt to dark mode | Use `Color(.systemX)` or Asset Catalog |
| Force-unwrapping size class | Crashes on Mac/visionOS | Optional binding |

## Cross-references

- _Historical: this content was absorbed from the legacy `create-plans` skill into its absorbing parent. The original `create-plans` skill no longer exists in v1._
- `references/swift-conventions.md` — sibling reference
- `references/swift-concurrency.md` — async data fetching for views
- Apple HIG documentation — externally authoritative source
