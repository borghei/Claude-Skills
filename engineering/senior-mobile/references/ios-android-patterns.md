# iOS & Android Native Development Patterns

Comprehensive reference for native mobile development covering architecture, UI frameworks, concurrency, platform UX guidelines, and CI/CD.

---

## iOS: SwiftUI vs UIKit Decision

### When to Use SwiftUI

- **Green-field projects** targeting iOS 16+
- Teams with Swift experience wanting **declarative UI**
- Apps with **dynamic layouts** that adapt to content
- Rapid prototyping and design iteration
- Apps leveraging **Combine/async-await** for reactive data flow

### When to Use UIKit

- Apps requiring **iOS 13-15** support
- **Complex custom animations** and gesture handling
- Integration with **legacy Objective-C** codebases
- Fine-grained control over **view lifecycle** and layout
- Features not yet available in SwiftUI (some UIKit-only APIs)

### Hybrid Approach (Recommended for most projects)

```swift
// Use SwiftUI for new screens, wrap UIKit when needed

// SwiftUI hosting UIKit
struct MapView: UIViewRepresentable {
    func makeUIView(context: Context) -> MKMapView {
        return MKMapView()
    }

    func updateUIView(_ uiView: MKMapView, context: Context) {
        // Update map region
    }
}

// UIKit hosting SwiftUI
let swiftUIView = UIHostingController(rootView: ProfileView())
navigationController?.pushViewController(swiftUIView, animated: true)
```

### SwiftUI vs UIKit Comparison

| Aspect | SwiftUI | UIKit |
|--------|---------|-------|
| Paradigm | Declarative | Imperative |
| Min iOS | 13 (practical: 16+) | All versions |
| Learning curve | Lower | Higher |
| Customization | Growing | Complete |
| Performance | Good (improving) | Excellent |
| Previews | Live previews | Storyboard/XIB |
| Accessibility | Built-in | Manual setup |
| Testing | Snapshot + unit | XCTest + UI tests |

---

## iOS: MVVM-C Architecture

### Overview

MVVM-C (Model-View-ViewModel-Coordinator) separates navigation from presentation logic.

```
┌──────────────┐
│  Coordinator  │  - Navigation flow
│               │  - Dependency injection
└──────┬───────┘
       │ creates
┌──────▼───────┐
│     View      │  - SwiftUI View or UIViewController
│               │  - Displays data from ViewModel
└──────┬───────┘
       │ observes
┌──────▼───────┐
│  ViewModel    │  - Business logic
│               │  - Data transformation
└──────┬───────┘
       │ uses
┌──────▼───────┐
│    Model      │  - Data structures
│  + Services   │  - Network, persistence
└──────────────┘
```

### Coordinator Pattern

```swift
protocol Coordinator: AnyObject {
    var childCoordinators: [Coordinator] { get set }
    func start()
}

class AppCoordinator: Coordinator {
    var childCoordinators: [Coordinator] = []
    private let window: UIWindow

    init(window: UIWindow) {
        self.window = window
    }

    func start() {
        let authCoordinator = AuthCoordinator()
        authCoordinator.onLoginSuccess = { [weak self] in
            self?.showMainFlow()
        }
        childCoordinators.append(authCoordinator)
        window.rootViewController = authCoordinator.start()
        window.makeKeyAndVisible()
    }

    private func showMainFlow() {
        let mainCoordinator = MainTabCoordinator()
        childCoordinators = [mainCoordinator]
        window.rootViewController = mainCoordinator.start()
    }
}
```

### ViewModel with async/await

```swift
@MainActor
class ProductListViewModel: ObservableObject {
    @Published private(set) var products: [Product] = []
    @Published private(set) var state: ViewState = .idle

    private let productService: ProductServiceProtocol
    private var loadTask: Task<Void, Never>?

    enum ViewState: Equatable {
        case idle, loading, loaded, error(String)
    }

    init(productService: ProductServiceProtocol = ProductService()) {
        self.productService = productService
    }

    func loadProducts() {
        loadTask?.cancel()
        loadTask = Task {
            state = .loading
            do {
                products = try await productService.fetchProducts()
                state = .loaded
            } catch is CancellationError {
                // Ignore cancellation
            } catch {
                state = .error(error.localizedDescription)
            }
        }
    }

    func refresh() async {
        do {
            products = try await productService.fetchProducts()
        } catch {
            state = .error(error.localizedDescription)
        }
    }

    deinit {
        loadTask?.cancel()
    }
}
```

---

## iOS: Combine and async/await

### Combine Publishers

```swift
import Combine

class SearchViewModel: ObservableObject {
    @Published var searchText = ""
    @Published private(set) var results: [SearchResult] = []

    private var cancellables = Set<AnyCancellable>()
    private let searchService: SearchServiceProtocol

    init(searchService: SearchServiceProtocol) {
        self.searchService = searchService

        $searchText
            .debounce(for: .milliseconds(300), scheduler: RunLoop.main)
            .removeDuplicates()
            .filter { $0.count >= 2 }
            .sink { [weak self] query in
                self?.performSearch(query)
            }
            .store(in: &cancellables)
    }

    private func performSearch(_ query: String) {
        Task {
            do {
                results = try await searchService.search(query: query)
            } catch {
                results = []
            }
        }
    }
}
```

### Structured Concurrency

```swift
// TaskGroup for parallel requests
func loadDashboard() async throws -> Dashboard {
    async let profile = userService.getProfile()
    async let notifications = notificationService.getRecent()
    async let stats = analyticsService.getDailyStats()

    return try await Dashboard(
        profile: profile,
        notifications: notifications,
        stats: stats
    )
}

// Task cancellation
class DownloadManager {
    private var downloadTask: Task<Data, Error>?

    func startDownload(url: URL) {
        downloadTask = Task {
            let (data, _) = try await URLSession.shared.data(from: url)
            try Task.checkCancellation()
            return data
        }
    }

    func cancelDownload() {
        downloadTask?.cancel()
    }
}
```

---

## Android: Compose vs XML Decision

### When to Use Jetpack Compose

- **New projects** targeting API 21+
- Teams ready for **declarative UI** paradigm
- Apps with **dynamic, state-driven** interfaces
- Faster iteration with **live previews**
- Material Design 3 compliance

### When to Use XML Layouts

- **Existing large codebases** with XML infrastructure
- Apps needing **RecyclerView** with complex item types
- Teams not yet trained on Compose
- Libraries that expose XML-only custom views

### Compose vs XML Comparison

| Aspect | Compose | XML |
|--------|---------|-----|
| Paradigm | Declarative | Imperative |
| Min API | 21 | All |
| Tooling | Preview, Layout Inspector | Layout Editor |
| Performance | Good (improving) | Mature |
| Theming | Material3 built-in | Manual theme setup |
| Testing | ComposeTestRule | Espresso |
| Interop | Can embed XML views | Can embed Compose |
| Code sharing | Easy with KMP | Limited |

---

## Android: MVVM with Hilt

### Project Structure

```
app/
├── di/                        # Hilt modules
│   ├── AppModule.kt
│   ├── NetworkModule.kt
│   └── DatabaseModule.kt
├── data/
│   ├── local/                 # Room database
│   │   ├── AppDatabase.kt
│   │   ├── dao/
│   │   └── entity/
│   ├── remote/                # Retrofit API
│   │   ├── ApiService.kt
│   │   └── dto/
│   └── repository/            # Repository implementations
│       └── ProductRepositoryImpl.kt
├── domain/
│   ├── model/                 # Domain models
│   ├── repository/            # Repository interfaces
│   └── usecase/               # Business logic
├── presentation/
│   ├── navigation/
│   │   └── AppNavigation.kt
│   ├── theme/
│   │   └── AppTheme.kt
│   └── features/
│       ├── home/
│       │   ├── HomeScreen.kt
│       │   └── HomeViewModel.kt
│       └── detail/
│           ├── DetailScreen.kt
│           └── DetailViewModel.kt
└── App.kt                     # @HiltAndroidApp
```

### Hilt Dependency Injection

```kotlin
// di/NetworkModule.kt
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideOkHttpClient(): OkHttpClient =
        OkHttpClient.Builder()
            .addInterceptor(HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            })
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .build()

    @Provides
    @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit =
        Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()

    @Provides
    @Singleton
    fun provideApiService(retrofit: Retrofit): ApiService =
        retrofit.create(ApiService::class.java)
}

// di/DatabaseModule.kt
@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {

    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): AppDatabase =
        Room.databaseBuilder(context, AppDatabase::class.java, "app_db")
            .fallbackToDestructiveMigration()
            .build()

    @Provides
    fun provideProductDao(db: AppDatabase): ProductDao = db.productDao()
}
```

### ViewModel with StateFlow

```kotlin
@HiltViewModel
class ProductListViewModel @Inject constructor(
    private val getProductsUseCase: GetProductsUseCase,
    private val savedStateHandle: SavedStateHandle,
) : ViewModel() {

    private val _uiState = MutableStateFlow(ProductListUiState())
    val uiState: StateFlow<ProductListUiState> = _uiState.asStateFlow()

    private val _events = Channel<ProductListEvent>()
    val events: Flow<ProductListEvent> = _events.receiveAsFlow()

    init {
        loadProducts()
    }

    fun loadProducts() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }

            getProductsUseCase()
                .catch { error ->
                    _uiState.update {
                        it.copy(isLoading = false, error = error.message)
                    }
                }
                .collect { products ->
                    _uiState.update {
                        it.copy(isLoading = false, products = products, error = null)
                    }
                }
        }
    }

    fun onProductClick(productId: String) {
        viewModelScope.launch {
            _events.send(ProductListEvent.NavigateToDetail(productId))
        }
    }
}

data class ProductListUiState(
    val products: List<Product> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null,
)

sealed interface ProductListEvent {
    data class NavigateToDetail(val productId: String) : ProductListEvent
}
```

---

## Android: Coroutines and Flow

### Structured Concurrency

```kotlin
// Repository with Flow
class ProductRepositoryImpl @Inject constructor(
    private val apiService: ApiService,
    private val productDao: ProductDao,
) : ProductRepository {

    override fun getProducts(): Flow<List<Product>> = flow {
        // Emit cached data first
        val cached = productDao.getAll().map { it.toDomain() }
        if (cached.isNotEmpty()) emit(cached)

        // Fetch from network
        try {
            val remote = apiService.getProducts().map { it.toDomain() }
            productDao.insertAll(remote.map { it.toEntity() })
            emit(remote)
        } catch (e: Exception) {
            if (cached.isEmpty()) throw e
        }
    }.flowOn(Dispatchers.IO)

    override suspend fun getProduct(id: String): Product =
        withContext(Dispatchers.IO) {
            apiService.getProduct(id).toDomain()
        }
}
```

### Parallel Execution

```kotlin
// Parallel network calls
suspend fun loadDashboard(): Dashboard = coroutineScope {
    val profileDeferred = async { userRepository.getProfile() }
    val statsDeferred = async { analyticsRepository.getStats() }
    val notificationsDeferred = async { notificationRepository.getRecent() }

    Dashboard(
        profile = profileDeferred.await(),
        stats = statsDeferred.await(),
        notifications = notificationsDeferred.await(),
    )
}
```

### Flow Operators

```kotlin
// Search with debounce
class SearchViewModel @Inject constructor(
    private val searchRepository: SearchRepository,
) : ViewModel() {

    private val _query = MutableStateFlow("")
    val query: StateFlow<String> = _query.asStateFlow()

    val results: StateFlow<List<SearchResult>> = _query
        .debounce(300)
        .distinctUntilChanged()
        .filter { it.length >= 2 }
        .flatMapLatest { query ->
            searchRepository.search(query)
                .catch { emit(emptyList()) }
        }
        .stateIn(viewModelScope, SharingStarted.Lazily, emptyList())

    fun onQueryChange(query: String) {
        _query.value = query
    }
}
```

---

## Platform-Specific UX Guidelines

### iOS (Human Interface Guidelines)

| Principle | Implementation |
|-----------|----------------|
| **Navigation** | Tab bar for 3-5 top-level destinations; NavigationStack for hierarchical |
| **Gestures** | Swipe back, pull to refresh, long press for context menus |
| **Typography** | SF Pro, Dynamic Type support required for accessibility |
| **Colors** | Support Light/Dark mode; use system colors for adaptability |
| **Haptics** | Use for confirmations, selections, errors (UIFeedbackGenerator) |
| **Spacing** | 16pt margins, 8pt grid system |
| **Safe areas** | Always respect safe area insets (notch, home indicator) |
| **Sheets** | Use .sheet() for non-blocking content, .fullScreenCover() for blocking |

### Android (Material Design 3)

| Principle | Implementation |
|-----------|----------------|
| **Navigation** | Bottom nav for 3-5 destinations; NavDrawer for 5+ |
| **Gestures** | Swipe to dismiss, pull to refresh, FAB for primary action |
| **Typography** | Roboto / Google Sans; Material type scale |
| **Colors** | Dynamic color (Material You) on Android 12+; fallback palette |
| **Motion** | Shared element transitions, container transforms |
| **Spacing** | 16dp margins, 4dp grid system |
| **Edge-to-edge** | Enable edge-to-edge display with WindowInsets handling |
| **Predictive back** | Support predictive back gesture on Android 14+ |

### Cross-Platform Consistency Tips

- Use platform-native navigation patterns (do NOT use iOS-style tabs on Android)
- Respect platform back button behavior (hardware back on Android)
- Match platform date/time pickers
- Use platform-specific sharing intents
- Match platform notification behavior and permissions flow

---

## CI/CD for Native Apps

### Fastlane Configuration

```ruby
# ios/fastlane/Fastfile
default_platform(:ios)

platform :ios do
  desc "Run tests"
  lane :test do
    run_tests(
      scheme: "MyApp",
      devices: ["iPhone 15 Pro"],
      clean: true,
    )
  end

  desc "Build and upload to TestFlight"
  lane :beta do
    increment_build_number(xcodeproj: "MyApp.xcodeproj")
    build_app(
      scheme: "MyApp",
      export_method: "app-store",
    )
    upload_to_testflight(skip_waiting_for_build_processing: true)
    slack(message: "New iOS beta uploaded to TestFlight!")
  end

  desc "Deploy to App Store"
  lane :release do
    build_app(scheme: "MyApp", export_method: "app-store")
    upload_to_app_store(
      force: true,
      skip_screenshots: true,
      submit_for_review: true,
    )
  end
end

# android/fastlane/Fastfile
platform :android do
  desc "Run tests"
  lane :test do
    gradle(task: "test")
  end

  desc "Build and upload to Play Store internal track"
  lane :beta do
    gradle(task: "bundleRelease")
    upload_to_play_store(
      track: "internal",
      aab: "app/build/outputs/bundle/release/app-release.aab",
    )
  end

  desc "Promote to production"
  lane :release do
    upload_to_play_store(
      track: "production",
      track_promote_to: "production",
    )
  end
end
```

### Xcode Cloud

```yaml
# ci_scripts/ci_post_clone.sh
#!/bin/sh
# Install dependencies after Xcode Cloud clones the repo
brew install swiftlint
```

Xcode Cloud workflow configuration is done via Xcode GUI:
- **Start condition:** Push to `main` branch or PR
- **Actions:** Build, Test, Archive
- **Post-actions:** Distribute to TestFlight

### Firebase App Distribution

```yaml
# .github/workflows/android-ci.yml
name: Android CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Build with Gradle
        run: ./gradlew assembleRelease

      - name: Run tests
        run: ./gradlew testReleaseUnitTest

      - name: Upload to Firebase App Distribution
        uses: wzieba/Firebase-Distribution-Github-Action@v1
        with:
          appId: ${{ secrets.FIREBASE_APP_ID }}
          serviceCredentialsFileContent: ${{ secrets.FIREBASE_CREDENTIALS }}
          groups: testers
          file: app/build/outputs/apk/release/app-release.apk
```

### GitHub Actions for iOS

```yaml
# .github/workflows/ios-ci.yml
name: iOS CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: macos-14
    steps:
      - uses: actions/checkout@v4

      - name: Select Xcode
        run: sudo xcode-select -s /Applications/Xcode_15.2.app

      - name: Install dependencies
        run: |
          gem install fastlane
          bundle install

      - name: Run tests
        run: fastlane ios test

      - name: Build for TestFlight
        if: github.ref == 'refs/heads/main'
        run: fastlane ios beta
        env:
          MATCH_PASSWORD: ${{ secrets.MATCH_PASSWORD }}
          APP_STORE_CONNECT_API_KEY: ${{ secrets.ASC_KEY }}
```

### CI/CD Pipeline Summary

| Stage | iOS | Android |
|-------|-----|---------|
| Lint | SwiftLint | ktlint / detekt |
| Unit tests | XCTest | JUnit + Mockk |
| UI tests | XCUITest | Espresso / Compose UI Test |
| Build | xcodebuild / Fastlane | Gradle (AAB) |
| Sign | Match / manual certs | Keystore |
| Distribute beta | TestFlight | Firebase App Distribution |
| Distribute prod | App Store Connect | Google Play Console |
| Monitor | Xcode Organizer / Sentry | Crashlytics / Sentry |
