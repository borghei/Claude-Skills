---
name: senior-mobile
description: Expert mobile development covering iOS, Android, React Native, and Flutter for native and cross-platform applications.
version: 1.0.0
author: Claude Skills
category: engineering
tags: [mobile, ios, android, react-native, flutter, swift, kotlin]
---

# Senior Mobile Developer

Expert-level mobile application development.

## Core Competencies

- iOS development (Swift, SwiftUI)
- Android development (Kotlin, Jetpack Compose)
- Cross-platform (React Native, Flutter)
- Mobile architecture patterns
- Performance optimization
- App Store deployment
- Push notifications
- Offline-first design

## Platform Comparison

| Aspect | Native iOS | Native Android | React Native | Flutter |
|--------|-----------|----------------|--------------|---------|
| Language | Swift | Kotlin | TypeScript | Dart |
| UI Framework | SwiftUI/UIKit | Compose/XML | React | Widgets |
| Performance | Best | Best | Good | Very Good |
| Code Sharing | None | None | ~80% | ~95% |
| Team Skills | iOS devs | Android devs | Web devs | New skills |

## React Native

### Project Structure

```
src/
├── app/
│   ├── (tabs)/
│   │   ├── index.tsx
│   │   ├── profile.tsx
│   │   └── settings.tsx
│   ├── auth/
│   │   ├── login.tsx
│   │   └── register.tsx
│   └── _layout.tsx
├── components/
│   ├── ui/
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   └── Card.tsx
│   └── features/
│       ├── ProductCard.tsx
│       └── UserAvatar.tsx
├── hooks/
│   ├── useAuth.ts
│   └── useApi.ts
├── services/
│   ├── api.ts
│   └── storage.ts
├── stores/
│   └── authStore.ts
└── utils/
    └── helpers.ts
```

### Components

```typescript
import { View, Text, Pressable, StyleSheet } from 'react-native';
import Animated, {
  useAnimatedStyle,
  withSpring,
  useSharedValue,
} from 'react-native-reanimated';

interface ButtonProps {
  title: string;
  variant?: 'primary' | 'secondary';
  loading?: boolean;
  disabled?: boolean;
  onPress: () => void;
}

export function Button({
  title,
  variant = 'primary',
  loading,
  disabled,
  onPress,
}: ButtonProps) {
  const scale = useSharedValue(1);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  const handlePressIn = () => {
    scale.value = withSpring(0.95);
  };

  const handlePressOut = () => {
    scale.value = withSpring(1);
  };

  return (
    <Pressable
      onPress={onPress}
      onPressIn={handlePressIn}
      onPressOut={handlePressOut}
      disabled={disabled || loading}
    >
      <Animated.View
        style={[
          styles.button,
          styles[variant],
          disabled && styles.disabled,
          animatedStyle,
        ]}
      >
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={[styles.text, styles[`${variant}Text`]]}>{title}</Text>
        )}
      </Animated.View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  button: {
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  primary: {
    backgroundColor: '#007AFF',
  },
  secondary: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: '#007AFF',
  },
  disabled: {
    opacity: 0.5,
  },
  text: {
    fontSize: 16,
    fontWeight: '600',
  },
  primaryText: {
    color: '#fff',
  },
  secondaryText: {
    color: '#007AFF',
  },
});
```

### Navigation (Expo Router)

```typescript
// app/_layout.tsx
import { Stack } from 'expo-router';
import { AuthProvider } from '@/contexts/AuthContext';

export default function RootLayout() {
  return (
    <AuthProvider>
      <Stack screenOptions={{ headerShown: false }}>
        <Stack.Screen name="(tabs)" />
        <Stack.Screen name="auth" />
        <Stack.Screen
          name="modal"
          options={{ presentation: 'modal' }}
        />
      </Stack>
    </AuthProvider>
  );
}

// app/(tabs)/_layout.tsx
import { Tabs } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

export default function TabLayout() {
  return (
    <Tabs>
      <Tabs.Screen
        name="index"
        options={{
          title: 'Home',
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="home" size={size} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: 'Profile',
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="person" size={size} color={color} />
          ),
        }}
      />
    </Tabs>
  );
}
```

### State Management (Zustand)

```typescript
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface User {
  id: string;
  email: string;
  name: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isLoading: false,

      login: async (email, password) => {
        set({ isLoading: true });
        try {
          const response = await api.post('/auth/login', { email, password });
          set({
            user: response.data.user,
            token: response.data.token,
            isLoading: false,
          });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      logout: () => {
        set({ user: null, token: null });
      },

      refreshToken: async () => {
        const { token } = get();
        if (!token) return;

        const response = await api.post('/auth/refresh', { token });
        set({ token: response.data.token });
      },
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => AsyncStorage),
      partialize: (state) => ({ user: state.user, token: state.token }),
    }
  )
);
```

## iOS (Swift/SwiftUI)

### SwiftUI Views

```swift
import SwiftUI

struct ProductListView: View {
    @StateObject private var viewModel = ProductListViewModel()
    @State private var searchText = ""

    var body: some View {
        NavigationStack {
            Group {
                if viewModel.isLoading {
                    ProgressView()
                } else if let error = viewModel.error {
                    ErrorView(error: error, onRetry: viewModel.loadProducts)
                } else {
                    productList
                }
            }
            .navigationTitle("Products")
            .searchable(text: $searchText)
            .refreshable {
                await viewModel.loadProducts()
            }
        }
        .task {
            await viewModel.loadProducts()
        }
    }

    private var productList: some View {
        List(viewModel.filteredProducts(searchText)) { product in
            NavigationLink(value: product) {
                ProductRow(product: product)
            }
        }
        .navigationDestination(for: Product.self) { product in
            ProductDetailView(product: product)
        }
    }
}

struct ProductRow: View {
    let product: Product

    var body: some View {
        HStack(spacing: 12) {
            AsyncImage(url: product.imageURL) { image in
                image
                    .resizable()
                    .aspectRatio(contentMode: .fill)
            } placeholder: {
                Color.gray.opacity(0.3)
            }
            .frame(width: 60, height: 60)
            .clipShape(RoundedRectangle(cornerRadius: 8))

            VStack(alignment: .leading, spacing: 4) {
                Text(product.name)
                    .font(.headline)
                Text(product.formattedPrice)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }

            Spacer()
        }
        .padding(.vertical, 4)
    }
}
```

### ViewModel

```swift
import Foundation
import Combine

@MainActor
class ProductListViewModel: ObservableObject {
    @Published private(set) var products: [Product] = []
    @Published private(set) var isLoading = false
    @Published private(set) var error: Error?

    private let productService: ProductServiceProtocol
    private var cancellables = Set<AnyCancellable>()

    init(productService: ProductServiceProtocol = ProductService()) {
        self.productService = productService
    }

    func loadProducts() async {
        isLoading = true
        error = nil

        do {
            products = try await productService.fetchProducts()
        } catch {
            self.error = error
        }

        isLoading = false
    }

    func filteredProducts(_ searchText: String) -> [Product] {
        guard !searchText.isEmpty else { return products }
        return products.filter {
            $0.name.localizedCaseInsensitiveContains(searchText)
        }
    }
}
```

## Android (Kotlin/Compose)

### Compose UI

```kotlin
@Composable
fun ProductListScreen(
    viewModel: ProductListViewModel = hiltViewModel(),
    onProductClick: (Product) -> Unit
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    Scaffold(
        topBar = {
            TopAppBar(title = { Text("Products") })
        }
    ) { padding ->
        when (val state = uiState) {
            is UiState.Loading -> {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator()
                }
            }
            is UiState.Error -> {
                ErrorContent(
                    message = state.message,
                    onRetry = { viewModel.loadProducts() }
                )
            }
            is UiState.Success -> {
                ProductList(
                    products = state.products,
                    onProductClick = onProductClick,
                    modifier = Modifier.padding(padding)
                )
            }
        }
    }
}

@Composable
fun ProductList(
    products: List<Product>,
    onProductClick: (Product) -> Unit,
    modifier: Modifier = Modifier
) {
    LazyColumn(
        modifier = modifier,
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        items(products, key = { it.id }) { product ->
            ProductCard(
                product = product,
                onClick = { onProductClick(product) }
            )
        }
    }
}

@Composable
fun ProductCard(
    product: Product,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        onClick = onClick
    ) {
        Row(
            modifier = Modifier.padding(12.dp),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            AsyncImage(
                model = product.imageUrl,
                contentDescription = null,
                modifier = Modifier
                    .size(60.dp)
                    .clip(RoundedCornerShape(8.dp)),
                contentScale = ContentScale.Crop
            )

            Column {
                Text(
                    text = product.name,
                    style = MaterialTheme.typography.titleMedium
                )
                Text(
                    text = product.formattedPrice,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}
```

### ViewModel

```kotlin
@HiltViewModel
class ProductListViewModel @Inject constructor(
    private val productRepository: ProductRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState<List<Product>>>(UiState.Loading)
    val uiState: StateFlow<UiState<List<Product>>> = _uiState.asStateFlow()

    init {
        loadProducts()
    }

    fun loadProducts() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading

            productRepository.getProducts()
                .catch { e ->
                    _uiState.value = UiState.Error(e.message ?: "Unknown error")
                }
                .collect { products ->
                    _uiState.value = UiState.Success(products)
                }
        }
    }
}

sealed interface UiState<out T> {
    data object Loading : UiState<Nothing>
    data class Success<T>(val data: T) : UiState<T>
    data class Error(val message: String) : UiState<Nothing>
}
```

## Performance Optimization

### React Native Performance

```typescript
// Use FlatList for long lists
<FlatList
  data={items}
  renderItem={renderItem}
  keyExtractor={(item) => item.id}
  initialNumToRender={10}
  maxToRenderPerBatch={10}
  windowSize={5}
  removeClippedSubviews={true}
  getItemLayout={(data, index) => ({
    length: ITEM_HEIGHT,
    offset: ITEM_HEIGHT * index,
    index,
  })}
/>

// Memoize components
const MemoizedItem = React.memo(ItemComponent);

// Use useCallback for handlers
const handlePress = useCallback((id: string) => {
  navigation.navigate('Detail', { id });
}, [navigation]);

// Image optimization
<Image
  source={{ uri: imageUrl }}
  style={styles.image}
  resizeMode="cover"
  fadeDuration={0}
/>
```

### Native Performance

```swift
// iOS - Prefetching
func collectionView(
    _ collectionView: UICollectionView,
    prefetchItemsAt indexPaths: [IndexPath]
) {
    for indexPath in indexPaths {
        let product = products[indexPath.row]
        imageLoader.prefetch(url: product.imageURL)
    }
}

// Android - RecyclerView optimization
recyclerView.apply {
    setHasFixedSize(true)
    setItemViewCacheSize(20)
    recycledViewPool.setMaxRecycledViews(0, 20)
}
```

## Reference Materials

- `references/react_native_guide.md` - React Native best practices
- `references/ios_patterns.md` - iOS architecture patterns
- `references/android_patterns.md` - Android architecture patterns
- `references/app_store_guide.md` - App Store submission guide

## Scripts

```bash
# Project scaffolder
python scripts/mobile_scaffold.py --platform react-native --name MyApp

# Build automation
python scripts/build.py --platform ios --env production

# App Store metadata generator
python scripts/store_metadata.py --screenshots ./screenshots

# Performance profiler
python scripts/profile.py --platform android --output report.html
```
