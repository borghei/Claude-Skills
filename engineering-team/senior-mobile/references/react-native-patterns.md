# React Native Patterns & Best Practices

Comprehensive reference for production React Native development covering navigation, state management, performance, testing, native modules, and OTA updates.

---

## Navigation Patterns

### Stack Navigation (Expo Router)

```typescript
// app/_layout.tsx
import { Stack } from 'expo-router';

export default function RootLayout() {
  return (
    <Stack
      screenOptions={{
        headerStyle: { backgroundColor: '#f5f5f5' },
        headerTintColor: '#333',
        animation: 'slide_from_right',
      }}
    >
      <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
      <Stack.Screen name="auth" options={{ headerShown: false }} />
      <Stack.Screen name="[id]" options={{ title: 'Details' }} />
      <Stack.Screen
        name="modal"
        options={{ presentation: 'modal', headerShown: true }}
      />
    </Stack>
  );
}
```

### Tab Navigation

```typescript
// app/(tabs)/_layout.tsx
import { Tabs } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Platform } from 'react-native';

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: '#007AFF',
        tabBarInactiveTintColor: '#8E8E93',
        tabBarStyle: {
          height: Platform.OS === 'ios' ? 88 : 60,
          paddingBottom: Platform.OS === 'ios' ? 28 : 8,
        },
        headerShown: true,
      }}
    >
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
        name="search"
        options={{
          title: 'Search',
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="search" size={size} color={color} />
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

### Drawer Navigation

```typescript
// Using @react-navigation/drawer
import { createDrawerNavigator } from '@react-navigation/drawer';

const Drawer = createDrawerNavigator();

function DrawerNavigator() {
  return (
    <Drawer.Navigator
      screenOptions={{
        drawerPosition: 'left',
        drawerType: 'front',
        headerShown: true,
        drawerStyle: { width: 280 },
      }}
    >
      <Drawer.Screen name="Home" component={HomeScreen} />
      <Drawer.Screen name="Settings" component={SettingsScreen} />
      <Drawer.Screen name="About" component={AboutScreen} />
    </Drawer.Navigator>
  );
}
```

### Deep Linking Configuration

```typescript
// app.json or app.config.ts
{
  "expo": {
    "scheme": "myapp",
    "plugins": ["expo-router"],
    "experiments": {
      "typedRoutes": true
    }
  }
}

// Handling deep links in Expo Router:
// myapp://profile/123 -> app/profile/[id].tsx
// https://myapp.com/profile/123 -> requires universal links config
```

### Navigation Guards / Auth Protection

```typescript
// app/_layout.tsx with auth guard
import { useEffect } from 'react';
import { useRouter, useSegments } from 'expo-router';
import { useAuthStore } from '@/stores/authStore';

function useProtectedRoute() {
  const segments = useSegments();
  const router = useRouter();
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  useEffect(() => {
    const inAuthGroup = segments[0] === 'auth';

    if (!isAuthenticated && !inAuthGroup) {
      router.replace('/auth/login');
    } else if (isAuthenticated && inAuthGroup) {
      router.replace('/');
    }
  }, [isAuthenticated, segments]);
}
```

---

## State Management Comparison

### Zustand (Recommended for most projects)

| Aspect | Details |
|--------|---------|
| Bundle size | ~1 KB |
| Learning curve | Minimal - familiar hooks API |
| Boilerplate | Very low |
| DevTools | Zustand/devtools middleware |
| Best for | Small-medium apps, rapid prototyping |

```typescript
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface CartStore {
  items: CartItem[];
  addItem: (item: CartItem) => void;
  removeItem: (id: string) => void;
  clearCart: () => void;
  total: () => number;
}

export const useCartStore = create<CartStore>()(
  persist(
    (set, get) => ({
      items: [],
      addItem: (item) => set((state) => ({
        items: [...state.items, item],
      })),
      removeItem: (id) => set((state) => ({
        items: state.items.filter((i) => i.id !== id),
      })),
      clearCart: () => set({ items: [] }),
      total: () => get().items.reduce((sum, i) => sum + i.price, 0),
    }),
    {
      name: 'cart-storage',
      storage: createJSONStorage(() => AsyncStorage),
    }
  )
);
```

### Redux Toolkit

| Aspect | Details |
|--------|---------|
| Bundle size | ~11 KB (+ React-Redux) |
| Learning curve | Moderate - actions, reducers, thunks |
| Boilerplate | Medium (much less than classic Redux) |
| DevTools | Excellent (Redux DevTools, Flipper) |
| Best for | Large apps, complex data flows, teams |

```typescript
import { createSlice, createAsyncThunk, configureStore } from '@reduxjs/toolkit';

export const fetchProducts = createAsyncThunk(
  'products/fetch',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/products');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const productsSlice = createSlice({
  name: 'products',
  initialState: { items: [], loading: false, error: null },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchProducts.pending, (state) => { state.loading = true; })
      .addCase(fetchProducts.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchProducts.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});
```

### Jotai (Atomic approach)

| Aspect | Details |
|--------|---------|
| Bundle size | ~3 KB |
| Learning curve | Low - atom-based thinking |
| Boilerplate | Very low |
| DevTools | Jotai DevTools |
| Best for | Derived state, fine-grained reactivity |

```typescript
import { atom, useAtom, useAtomValue, useSetAtom } from 'jotai';
import { atomWithStorage, createJSONStorage } from 'jotai/utils';
import AsyncStorage from '@react-native-async-storage/async-storage';

const storage = createJSONStorage(() => AsyncStorage);

// Base atoms
const userAtom = atomWithStorage('user', null, storage);
const themeAtom = atomWithStorage('theme', 'light', storage);

// Derived atom
const isDarkAtom = atom((get) => get(themeAtom) === 'dark');

// Async atom
const productsAtom = atom(async () => {
  const response = await fetch('https://api.example.com/products');
  return response.json();
});
```

### MobX

| Aspect | Details |
|--------|---------|
| Bundle size | ~16 KB |
| Learning curve | Moderate - observable/observer patterns |
| Boilerplate | Low with decorators |
| DevTools | MobX DevTools |
| Best for | OOP-style state, complex domains |

### State Management Decision Matrix

| Factor | Zustand | Redux | Jotai | MobX |
|--------|---------|-------|-------|------|
| App complexity | S-M | M-L | S-M | M-L |
| Team size | 1-5 | 5+ | 1-5 | 3-10 |
| TS support | Good | Excellent | Good | Good |
| Persistence | Easy | Moderate | Easy | Moderate |
| Server state | TanStack Query | RTK Query | TanStack Query | Built-in |

---

## Performance Optimization Checklist

### Rendering Performance

- [ ] Use `React.memo()` for components that receive stable props
- [ ] Use `useCallback()` for event handlers passed as props
- [ ] Use `useMemo()` for expensive computations
- [ ] Use `FlatList` or `FlashList` instead of `ScrollView` + `.map()` for lists
- [ ] Set `keyExtractor` on all FlatList components
- [ ] Provide `getItemLayout` when item heights are fixed
- [ ] Use `windowSize`, `initialNumToRender`, `maxToRenderPerBatch` on FlatList
- [ ] Avoid inline style objects (use `StyleSheet.create`)
- [ ] Avoid inline arrow functions in render (move to component body with useCallback)
- [ ] Use `removeClippedSubviews={true}` for long lists

### Image Optimization

- [ ] Use WebP format over PNG/JPEG where possible
- [ ] Implement progressive loading with placeholder images
- [ ] Use `expo-image` or `react-native-fast-image` for caching
- [ ] Set explicit `width` and `height` on images
- [ ] Use `resizeMode="cover"` or `"contain"` appropriately
- [ ] Lazy-load off-screen images

### Animation Performance

- [ ] Use `react-native-reanimated` for JS-driven animations (runs on UI thread)
- [ ] Use `LayoutAnimation` for simple layout transitions
- [ ] Avoid animating `width`/`height` - use `transform` instead
- [ ] Set `useNativeDriver: true` when using Animated API
- [ ] Batch state updates that trigger animations

### Memory Management

- [ ] Clean up event listeners in useEffect cleanup
- [ ] Cancel subscriptions, timers, and intervals on unmount
- [ ] Avoid memory leaks from uncancelled async operations
- [ ] Use AbortController for fetch requests
- [ ] Dispose of large data structures when screens unmount

### Bundle Size

- [ ] Use `import x from 'lodash/x'` instead of `import { x } from 'lodash'`
- [ ] Remove unused dependencies
- [ ] Replace `moment.js` with `date-fns` or `dayjs`
- [ ] Use tree-shakeable libraries
- [ ] Analyze bundle with `npx react-native-bundle-visualizer`

### Startup Performance

- [ ] Use Hermes engine (enabled by default in Expo SDK 50+)
- [ ] Lazy-load screens with `React.lazy()` + `Suspense`
- [ ] Defer non-critical initialization
- [ ] Use `SplashScreen.preventAutoHideAsync()` to control splash timing

---

## Testing Strategy

### Unit Testing (Jest)

```typescript
// __tests__/stores/cartStore.test.ts
import { useCartStore } from '@/stores/cartStore';
import { act, renderHook } from '@testing-library/react-hooks';

describe('CartStore', () => {
  beforeEach(() => {
    useCartStore.setState({ items: [] });
  });

  it('adds item to cart', () => {
    const { result } = renderHook(() => useCartStore());

    act(() => {
      result.current.addItem({ id: '1', name: 'Widget', price: 9.99 });
    });

    expect(result.current.items).toHaveLength(1);
    expect(result.current.items[0].name).toBe('Widget');
  });
});
```

### Component Testing (React Native Testing Library)

```typescript
// __tests__/components/Button.test.tsx
import { render, fireEvent, screen } from '@testing-library/react-native';
import { Button } from '@/components/ui/Button';

describe('Button', () => {
  it('renders title correctly', () => {
    render(<Button title="Submit" onPress={() => {}} />);
    expect(screen.getByText('Submit')).toBeTruthy();
  });

  it('calls onPress when pressed', () => {
    const onPress = jest.fn();
    render(<Button title="Submit" onPress={onPress} />);
    fireEvent.press(screen.getByText('Submit'));
    expect(onPress).toHaveBeenCalledTimes(1);
  });

  it('does not call onPress when disabled', () => {
    const onPress = jest.fn();
    render(<Button title="Submit" onPress={onPress} disabled />);
    fireEvent.press(screen.getByText('Submit'));
    expect(onPress).not.toHaveBeenCalled();
  });
});
```

### E2E Testing (Detox)

```typescript
// e2e/login.test.ts
describe('Login Flow', () => {
  beforeAll(async () => {
    await device.launchApp();
  });

  it('should show login screen', async () => {
    await expect(element(by.text('Login'))).toBeVisible();
  });

  it('should login with valid credentials', async () => {
    await element(by.id('email-input')).typeText('user@example.com');
    await element(by.id('password-input')).typeText('password123');
    await element(by.id('login-button')).tap();
    await expect(element(by.text('Welcome Home'))).toBeVisible();
  });
});
```

### Testing Coverage Targets

| Layer | Target | Tool |
|-------|--------|------|
| Unit (utils, hooks, stores) | 80%+ | Jest |
| Component | 70%+ | React Native Testing Library |
| Integration | Critical paths | Jest + RNTL |
| E2E | Happy paths | Detox or Maestro |
| Visual regression | Key screens | Storybook + Chromatic |

---

## Native Module Integration

### Expo Modules (Recommended)

```typescript
// modules/my-native-module/index.ts
import { requireNativeModule } from 'expo-modules-core';

const MyModule = requireNativeModule('MyNativeModule');

export function doNativeWork(input: string): Promise<string> {
  return MyModule.doWork(input);
}
```

### Turbo Modules (React Native 0.68+)

```typescript
// NativeMyModule.ts
import type { TurboModule } from 'react-native';
import { TurboModuleRegistry } from 'react-native';

export interface Spec extends TurboModule {
  multiply(a: number, b: number): Promise<number>;
}

export default TurboModuleRegistry.getEnforcing<Spec>('MyModule');
```

### Common Native Integrations

| Feature | Package | Notes |
|---------|---------|-------|
| Camera | expo-camera | Permissions required |
| File System | expo-file-system | Read/write local files |
| Notifications | expo-notifications | Push + local |
| Location | expo-location | Foreground + background |
| Biometrics | expo-local-authentication | Face ID / Fingerprint |
| Haptics | expo-haptics | Tactile feedback |
| In-App Purchases | react-native-iap | Both stores |
| Maps | react-native-maps | Google Maps + Apple Maps |

---

## CodePush / OTA Updates

### EAS Update (Expo)

```bash
# Install EAS CLI
npm install -g eas-cli

# Configure
eas update:configure

# Create update
eas update --branch production --message "Bug fix for login"

# Check update status
eas update:list
```

### Update Strategy

| Channel | Branch | Auto-update | Use case |
|---------|--------|-------------|----------|
| production | main | On app launch | Stable releases |
| staging | develop | Immediate | QA testing |
| preview | feature/* | Manual | Feature review |

### CodePush (Microsoft) - Alternative

```typescript
import codePush from 'react-native-code-push';

const codePushOptions = {
  checkFrequency: codePush.CheckFrequency.ON_APP_RESUME,
  installMode: codePush.InstallMode.ON_NEXT_RESUME,
  minimumBackgroundDuration: 60 * 5, // 5 minutes
};

function App() {
  return <MainNavigator />;
}

export default codePush(codePushOptions)(App);
```

### OTA Update Best Practices

1. **Never OTA native code changes** - only JS bundle + assets
2. **Use staged rollouts** - 10% -> 50% -> 100%
3. **Include rollback mechanism** - revert to previous bundle on crash
4. **Monitor crash rates** after each update
5. **Keep updates small** - diff-based updates are faster
6. **Test on real devices** before pushing to production
7. **Set minimum app version** - ensure native compatibility
8. **Use update channels** for staging vs production

---

## Project Configuration Best Practices

### ESLint Configuration

```json
{
  "extends": [
    "expo",
    "@react-native",
    "plugin:@typescript-eslint/recommended"
  ],
  "rules": {
    "react-native/no-inline-styles": "warn",
    "react-native/no-unused-styles": "error",
    "react-hooks/exhaustive-deps": "warn",
    "no-console": "warn"
  }
}
```

### Environment Variables

```typescript
// app.config.ts
export default {
  expo: {
    extra: {
      apiUrl: process.env.API_URL ?? 'https://api.example.com',
      environment: process.env.APP_ENV ?? 'development',
    },
  },
};

// Usage
import Constants from 'expo-constants';
const { apiUrl } = Constants.expoConfig.extra;
```

### Error Boundaries

```typescript
import { ErrorBoundary } from 'react-error-boundary';

function ErrorFallback({ error, resetErrorBoundary }) {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Something went wrong</Text>
      <Text style={styles.message}>{error.message}</Text>
      <Button title="Try Again" onPress={resetErrorBoundary} />
    </View>
  );
}

// Wrap your app
<ErrorBoundary FallbackComponent={ErrorFallback}>
  <App />
</ErrorBoundary>
```

---

## API Layer Pattern

### Typed API Client

```typescript
// services/api.ts
import { useAuthStore } from '@/stores/authStore';

const BASE_URL = 'https://api.example.com';

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';

async function request<T>(
  endpoint: string,
  method: HttpMethod = 'GET',
  body?: unknown,
  signal?: AbortSignal,
): Promise<T> {
  const token = useAuthStore.getState().token;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
    signal,
  });

  if (response.status === 401) {
    useAuthStore.getState().logout();
    throw new Error('Session expired');
  }

  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }

  return response.json();
}

export const api = {
  get: <T>(endpoint: string, signal?: AbortSignal) =>
    request<T>(endpoint, 'GET', undefined, signal),
  post: <T>(endpoint: string, body: unknown) =>
    request<T>(endpoint, 'POST', body),
  put: <T>(endpoint: string, body: unknown) =>
    request<T>(endpoint, 'PUT', body),
  delete: <T>(endpoint: string) =>
    request<T>(endpoint, 'DELETE'),
};
```

### React Query / TanStack Query Integration

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/services/api';

export function useProducts() {
  return useQuery({
    queryKey: ['products'],
    queryFn: ({ signal }) => api.get<Product[]>('/products', signal),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useCreateProduct() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (product: CreateProductDTO) =>
      api.post<Product>('/products', product),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
    },
  });
}
```
