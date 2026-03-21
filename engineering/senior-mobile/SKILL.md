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

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| App crashes on launch after adding a new dependency | Incompatible native module version or missing pod install / gradle sync | Run `npx pod-install` (iOS) or `cd android && ./gradlew clean` (Android). Verify dependency version compatibility in the changelog. |
| FlatList renders blank or flickers | Missing `keyExtractor`, unstable keys, or inline `renderItem` causing full re-renders | Add a stable `keyExtractor`, wrap `renderItem` in `useCallback`, and supply `getItemLayout` for fixed-height rows. |
| iOS build fails with "signing" error | Provisioning profile mismatch or expired certificate | Open Xcode > Signing & Capabilities, select the correct team and profile. Run `security find-identity -v -p codesigning` to verify certificates. |
| Android build OOM during dexing | Insufficient JVM heap for large projects | Add `org.gradle.jvmargs=-Xmx4096m` to `gradle.properties`. Enable `dexOptions { javaMaxHeapSize "4g" }` in `build.gradle`. |
| App Store rejection for missing privacy manifest | Apple requires PrivacyInfo.xcprivacy for apps using required reason APIs (UserDefaults, file timestamp, etc.) | Add a `PrivacyInfo.xcprivacy` file declaring each required reason API. Run `store_metadata_generator.py` to review privacy label guidance. |
| Slow cold start time (>3 seconds) | Too many synchronous operations on the main thread at launch, large bundle size, or unoptimized images | Defer non-critical initialization, lazy-load modules, compress images, and use `app_performance_analyzer.py` to identify bottlenecks. |
| Hot reload / fast refresh stops working | Syntax error in a module boundary, anonymous default export, or class component state | Check terminal for error messages, ensure named exports, and restart the Metro bundler or Flutter daemon with a cache clear. |

---

## Success Criteria

- **App startup time under 2 seconds** on cold launch (measured on mid-range devices, both iOS and Android).
- **Crash-free rate above 99.5%** across all supported OS versions, tracked via Crashlytics or Sentry.
- **Frame rendering at 60 fps** (16ms per frame) for scrolling lists and animations, with zero jank frames during typical user flows.
- **Bundle size under 50 MB** for the initial download (excluding on-demand resources), verified before each release.
- **Performance analyzer score of 75+** (Grade B or above) when running `app_performance_analyzer.py` against the project.
- **Zero critical issues** and fewer than 5 warnings reported by the performance analyzer before submitting to app stores.
- **App Store / Play Store approval on first submission** with complete metadata, correct privacy labels, and proper age rating, validated using `store_metadata_generator.py`.

---

## Scope & Limitations

**This skill covers:**
- Scaffolding production-ready mobile projects for React Native (Expo Router), Flutter, iOS native (SwiftUI), and Android native (Jetpack Compose).
- Static performance analysis including image asset sizing, re-render detection, memory leak patterns, and bundle size estimation.
- App Store and Play Store metadata generation including titles, keywords, privacy labels, age ratings, and submission checklists.
- Platform-specific architecture patterns (MVVM, state management, navigation).

**This skill does NOT cover:**
- Backend API development or server-side logic (see `senior-backend` and `senior-fullstack` skills).
- CI/CD pipeline configuration for mobile builds and automated distribution (see `senior-devops` and `release-orchestrator` skills).
- UI/UX design systems, accessibility auditing, or design token management (see `senior-frontend` and `design-auditor` skills).
- Runtime profiling with native tools (Xcode Instruments, Android Studio Profiler) -- the analyzer performs static code analysis only, not live device profiling.

---

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `senior-frontend` | Shared component patterns, styling conventions, and responsive design principles for React Native web targets | Frontend design tokens and component APIs feed into mobile UI components |
| `senior-backend` | API contract definitions, authentication flows, and data models consumed by mobile clients | Backend OpenAPI specs define mobile service layer interfaces |
| `senior-devops` | Build pipelines, code signing automation, and deployment workflows for mobile releases | Mobile build artifacts flow into CI/CD pipelines for TestFlight / Play Console distribution |
| `senior-qa` | Test strategy alignment, device matrix coverage, and E2E testing patterns for mobile screens | QA test plans drive device coverage; mobile scaffold includes test directory structure |
| `senior-security` | Secure storage patterns (Keychain/Keystore), certificate pinning, and data encryption for mobile apps | Security requirements inform Keychain helper implementation and network client configuration |
| `release-orchestrator` | Version bumping, changelog generation, and coordinated release across iOS and Android | Release metadata and version info flow from orchestrator into store submission workflow |

---

## Tool Reference

### `mobile_scaffold.py`

**Purpose:** Scaffold a production-ready mobile project with proper directory structure, navigation setup, state management, and base configuration files.

**Usage:**
```bash
python scripts/mobile_scaffold.py <name> --platform <platform> [options]
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | positional | Yes | -- | Project name, used as the directory name |
| `--platform`, `-p` | choice | Yes | -- | Target platform: `android-native`, `flutter`, `ios-native`, `react-native` |
| `--typescript`, `-t` | flag | No | `False` (auto-enabled for react-native) | Use TypeScript (React Native only) |
| `--state`, `-s` | string | No | `none` | State management library. React Native: `zustand`, `redux`, `jotai`, `none`. Flutter: `riverpod`, `bloc`, `provider`, `none`. Not applicable for native platforms. |
| `--output-dir`, `-o` | path | No | `.` (current directory) | Parent directory for the generated project |
| `--json` | flag | No | `False` | Output result as JSON instead of human-readable summary |

**Example:**
```bash
# Scaffold a React Native app with Zustand state management
python scripts/mobile_scaffold.py MyApp --platform react-native --state zustand

# Scaffold a Flutter app with Riverpod, output as JSON
python scripts/mobile_scaffold.py my-flutter-app --platform flutter --state riverpod --json

# Scaffold an iOS native app in a specific directory
python scripts/mobile_scaffold.py HealthTracker --platform ios-native --output-dir ~/Projects
```

**Output Formats:**
- **Human-readable (default):** Prints the project name, platform, state management choice, created directory path, and a list of all generated files.
- **JSON (`--json`):** Returns a JSON object with `project_name`, `platform`, `typescript`, `state_management`, `output_directory`, `files_created`, and `generated_at` fields.

---

### `store_metadata_generator.py`

**Purpose:** Generate structured metadata for App Store (iOS) and Google Play Store (Android) submissions, including title variants, keywords, category recommendations, privacy labels, age rating guidance, and submission checklists.

**Usage:**
```bash
python scripts/store_metadata_generator.py --app-name <name> --category <category> --features <features> [options]
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `--app-name` | string | Yes | -- | The app name for store listings |
| `--category` | choice | Yes | -- | Primary app category. Choices: `business`, `education`, `entertainment`, `finance`, `food`, `games`, `health`, `lifestyle`, `music`, `navigation`, `news`, `photo`, `productivity`, `shopping`, `social`, `sports`, `travel`, `utilities`, `weather` |
| `--features` | string | Yes | -- | Comma-separated list of features (e.g., `"offline,sync,biometric"`). Recognized features expand into keywords and trigger privacy/age-rating guidance. |
| `--description` | string | No | `""` | Short app description used in generated store copy |
| `--json` | flag | No | `False` | Output results as JSON |

**Example:**
```bash
# Generate metadata for a health app
python scripts/store_metadata_generator.py --app-name "FitTrack" --category health --features "workout,tracking,social" --description "Track your workouts"

# JSON output for CI integration
python scripts/store_metadata_generator.py --app-name "BudgetPal" --category finance --features "payment,offline,biometric,push" --json
```

**Output Formats:**
- **Human-readable (default):** Formatted report with sections for Title Variants, Keywords (with iOS 100-char field), Store Categories, Privacy Labels / Data Safety, Age Rating Guidance, and Submission Checklist.
- **JSON (`--json`):** Full metadata object including `titles`, `keywords`, `categories`, `descriptions`, `privacy_labels`, `age_rating`, `screenshot_specs`, and `submission_checklist`.

---

### `app_performance_analyzer.py`

**Purpose:** Analyze a mobile project directory for common performance issues including oversized image assets, re-render patterns, memory leak patterns, bundle size estimation, and platform-specific anti-patterns.

**Usage:**
```bash
python scripts/app_performance_analyzer.py <project_dir> [options]
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `project_dir` | positional | Yes | -- | Path to the mobile project directory to analyze |
| `--platform`, `-p` | choice | No | Auto-detected | Target platform: `react-native`, `flutter`, `ios-native`, `android-native`. Auto-detected from project files if omitted. |
| `--json` | flag | No | `False` | Output results as JSON |

**Example:**
```bash
# Analyze with auto-detected platform
python scripts/app_performance_analyzer.py ./my-app

# Analyze a React Native project explicitly
python scripts/app_performance_analyzer.py ./my-app --platform react-native

# JSON output for CI pipeline integration
python scripts/app_performance_analyzer.py ./my-app --platform flutter --json
```

**Output Formats:**
- **Human-readable (default):** Performance score (0-100 with letter grade), issue summary (critical/warning/info counts), bundle size estimate, detailed issues grouped by category, and platform-specific recommendations.
- **JSON (`--json`):** Full report object including `performance_score`, `summary`, `bundle_estimate` (source code size, asset size, file counts), `issues_by_category`, and the flat `issues` array with `category`, `severity`, `file`, `line`, and `message` per issue.
