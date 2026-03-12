---
name: senior-mobile
description: >-
  Use when the user asks to "build a mobile app", "scaffold React Native project",
  "create SwiftUI views", "set up Jetpack Compose", "optimize mobile performance",
  "configure Expo Router navigation", "implement offline-first storage",
  "submit to App Store", or "profile mobile rendering".
  Expert mobile development covering iOS (Swift/SwiftUI), Android (Kotlin/Compose),
  React Native, and Flutter for native and cross-platform applications.
version: 1.0.0
author: borghei
category: engineering
tags: [mobile, ios, android, react-native, flutter, swift, kotlin]
---

# Senior Mobile Developer

Expert mobile application development across iOS, Android, React Native, and Flutter.

## Keywords

mobile, ios, android, react-native, flutter, swift, kotlin, swiftui,
jetpack-compose, expo-router, zustand, app-store, performance, offline-first

---

## Quick Start

```bash
# Scaffold a React Native project
python scripts/mobile_scaffold.py --platform react-native --name MyApp

# Build for production
python scripts/build.py --platform ios --env production

# Generate App Store metadata
python scripts/store_metadata.py --screenshots ./screenshots

# Profile rendering performance
python scripts/profile.py --platform android --output report.html
```

---

## Tools

| Script | Purpose |
|--------|---------|
| `scripts/mobile_scaffold.py` | Scaffold project for react-native, ios, android, or flutter |
| `scripts/build.py` | Build automation with environment and platform flags |
| `scripts/store_metadata.py` | Generate App Store / Play Store listing metadata |
| `scripts/profile.py` | Profile rendering, memory, and startup performance |

---

## Platform Decision Matrix

| Aspect | Native iOS | Native Android | React Native | Flutter |
|--------|-----------|----------------|--------------|---------|
| Language | Swift | Kotlin | TypeScript | Dart |
| UI Framework | SwiftUI/UIKit | Compose/XML | React | Widgets |
| Performance | Best | Best | Good | Very Good |
| Code Sharing | None | None | ~80% | ~95% |
| Best For | iOS-only, hardware-heavy | Android-only, hardware-heavy | Web team, shared logic | Maximum code sharing |

---

## Workflow 1: Scaffold a React Native App (Expo Router)

1. **Generate project** -- `python scripts/mobile_scaffold.py --platform react-native --name MyApp`
2. **Verify directory structure** matches this layout:
   ```
   src/
   ├── app/              # Expo Router file-based routes
   │   ├── (tabs)/       # Tab navigation group
   │   ├── auth/         # Auth screens
   │   └── _layout.tsx   # Root layout
   ├── components/
   │   ├── ui/           # Reusable primitives (Button, Input, Card)
   │   └── features/     # Domain components (ProductCard, UserAvatar)
   ├── hooks/            # Custom hooks (useAuth, useApi)
   ├── services/         # API clients and storage
   ├── stores/           # Zustand state stores
   └── utils/            # Helpers
   ```
3. **Configure navigation** in `app/_layout.tsx` with Stack and Tabs.
4. **Set up state management** with Zustand + AsyncStorage persistence.
5. **Validate** -- Run the app on both iOS simulator and Android emulator. Confirm navigation and state persistence work.

## Workflow 2: Build a SwiftUI Feature (iOS)

1. **Create the View** using `NavigationStack`, `@StateObject` for ViewModel binding, and `.task` for async data loading.
2. **Create the ViewModel** as `@MainActor class` with `@Published` properties. Inject services via protocol for testability.
3. **Wire data flow**: View observes ViewModel -> ViewModel calls Service -> Service returns data -> ViewModel updates `@Published` -> View re-renders.
4. **Add search/refresh**: `.searchable(text:)` for filtering, `.refreshable` for pull-to-refresh.
5. **Validate** -- Run in Xcode previews first, then simulator. Confirm async loading, error states, and empty states all render correctly.

### Example: SwiftUI ViewModel Pattern

```swift
@MainActor
class ProductListViewModel: ObservableObject {
    @Published private(set) var products: [Product] = []
    @Published private(set) var isLoading = false
    @Published private(set) var error: Error?

    private let service: ProductServiceProtocol

    init(service: ProductServiceProtocol = ProductService()) {
        self.service = service
    }

    func loadProducts() async {
        isLoading = true
        error = nil
        do {
            products = try await service.fetchProducts()
        } catch {
            self.error = error
        }
        isLoading = false
    }
}
```

## Workflow 3: Build a Jetpack Compose Feature (Android)

1. **Create the Composable screen** with `Scaffold`, `TopAppBar`, and state collection via `collectAsStateWithLifecycle()`.
2. **Handle UI states** with a sealed interface: `Loading`, `Success<T>`, `Error`.
3. **Create the ViewModel** with `@HiltViewModel`, `MutableStateFlow`, and repository injection.
4. **Build list UI** using `LazyColumn` with `key` parameter for stable identity and `Arrangement.spacedBy()` for spacing.
5. **Validate** -- Run on emulator. Confirm state transitions (loading -> success, loading -> error -> retry) work correctly.

### Example: Compose UiState Pattern

```kotlin
sealed interface UiState<out T> {
    data object Loading : UiState<Nothing>
    data class Success<T>(val data: T) : UiState<T>
    data class Error(val message: String) : UiState<Nothing>
}

@HiltViewModel
class ProductListViewModel @Inject constructor(
    private val repository: ProductRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow<UiState<List<Product>>>(UiState.Loading)
    val uiState: StateFlow<UiState<List<Product>>> = _uiState.asStateFlow()

    fun loadProducts() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            repository.getProducts()
                .catch { e -> _uiState.value = UiState.Error(e.message ?: "Unknown error") }
                .collect { products -> _uiState.value = UiState.Success(products) }
        }
    }
}
```

## Workflow 4: Optimize Mobile Performance

1. **Profile** -- `python scripts/profile.py --platform <ios|android> --output report.html`
2. **Apply React Native optimizations:**
   - Use `FlatList` with `keyExtractor`, `initialNumToRender=10`, `windowSize=5`, `removeClippedSubviews=true`
   - Memoize components with `React.memo` and handlers with `useCallback`
   - Supply `getItemLayout` for fixed-height rows to skip measurement
3. **Apply native iOS optimizations:**
   - Implement `prefetchItemsAt` for image pre-loading in collection views
4. **Apply native Android optimizations:**
   - Set `setHasFixedSize(true)` and `setItemViewCacheSize(20)` on RecyclerViews
5. **Validate** -- Re-run profiler and confirm frame drops reduced and startup time improved.

## Workflow 5: Submit to App Store / Play Store

1. **Generate metadata** -- `python scripts/store_metadata.py --screenshots ./screenshots`
2. **Build release** -- `python scripts/build.py --platform ios --env production`
3. **Review** the generated listing (title, description, keywords, screenshots).
4. **Upload** via Xcode (iOS) or Play Console (Android).
5. **Validate** -- Monitor review status and address any rejection feedback.

---

## Reference Materials

| Document | Path |
|----------|------|
| React Native Guide | [references/react_native_guide.md](references/react_native_guide.md) |
| iOS Patterns | [references/ios_patterns.md](references/ios_patterns.md) |
| Android Patterns | [references/android_patterns.md](references/android_patterns.md) |
| App Store Guide | [references/app_store_guide.md](references/app_store_guide.md) |
| Full Code Examples | [REFERENCE.md](REFERENCE.md) |
