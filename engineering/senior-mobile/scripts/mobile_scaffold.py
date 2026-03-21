#!/usr/bin/env python3
"""
Mobile Project Scaffolder
=========================

CLI tool that scaffolds a production-ready mobile project with proper
directory structure, base configuration files, and navigation setup.

Supported platforms:
  - react-native (Expo with Expo Router)
  - flutter
  - ios-native (Swift / SwiftUI)
  - android-native (Kotlin / Jetpack Compose)

Usage:
  python mobile_scaffold.py my-app --platform react-native
  python mobile_scaffold.py my-app --platform flutter --state riverpod
  python mobile_scaffold.py my-app --platform react-native --typescript --state zustand --json

Dependencies: Python 3.8+ standard library only.
"""

import argparse
import json
import os
import sys
import textwrap
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Template content generators
# ---------------------------------------------------------------------------

# ---- React Native (Expo) -------------------------------------------------

def _rn_app_layout(ts: bool) -> str:
    ext = "tsx" if ts else "jsx"
    return textwrap.dedent(f"""\
        // app/_layout.{ext}
        import {{ Stack }} from 'expo-router';
        import {{ StatusBar }} from 'expo-status-bar';

        export default function RootLayout() {{
          return (
            <>
              <StatusBar style="auto" />
              <Stack screenOptions={{{{ headerShown: false }}}}>
                <Stack.Screen name="(tabs)" />
                <Stack.Screen name="auth" />
                <Stack.Screen name="modal" options={{{{ presentation: 'modal' }}}} />
              </Stack>
            </>
          );
        }}
    """)


def _rn_tab_layout(ts: bool) -> str:
    ext = "tsx" if ts else "jsx"
    return textwrap.dedent(f"""\
        // app/(tabs)/_layout.{ext}
        import {{ Tabs }} from 'expo-router';
        import {{ Ionicons }} from '@expo/vector-icons';

        export default function TabLayout() {{
          return (
            <Tabs
              screenOptions={{{{
                tabBarActiveTintColor: '#007AFF',
                headerShown: true,
              }}}}
            >
              <Tabs.Screen
                name="index"
                options={{{{
                  title: 'Home',
                  tabBarIcon: ({{{{ color, size }}}}) => (
                    <Ionicons name="home" size={{size}} color={{color}} />
                  ),
                }}}}
              />
              <Tabs.Screen
                name="profile"
                options={{{{
                  title: 'Profile',
                  tabBarIcon: ({{{{ color, size }}}}) => (
                    <Ionicons name="person" size={{size}} color={{color}} />
                  ),
                }}}}
              />
              <Tabs.Screen
                name="settings"
                options={{{{
                  title: 'Settings',
                  tabBarIcon: ({{{{ color, size }}}}) => (
                    <Ionicons name="settings" size={{size}} color={{color}} />
                  ),
                }}}}
              />
            </Tabs>
          );
        }}
    """)


def _rn_home_screen(ts: bool) -> str:
    ext = "tsx" if ts else "jsx"
    return textwrap.dedent(f"""\
        // app/(tabs)/index.{ext}
        import {{ View, Text, StyleSheet }} from 'react-native';

        export default function HomeScreen() {{
          return (
            <View style={{styles.container}}>
              <Text style={{styles.title}}>Welcome Home</Text>
            </View>
          );
        }}

        const styles = StyleSheet.create({{
          container: {{ flex: 1, alignItems: 'center', justifyContent: 'center' }},
          title: {{ fontSize: 24, fontWeight: '700' }},
        }});
    """)


def _rn_store_zustand(ts: bool) -> str:
    ext = "ts" if ts else "js"
    type_annotation = ": string | null" if ts else ""
    interface_block = textwrap.dedent("""\
        interface AuthState {
          token: string | null;
          isAuthenticated: boolean;
          login: (token: string) => void;
          logout: () => void;
        }

    """) if ts else ""
    generic = "<AuthState>" if ts else ""
    return textwrap.dedent(f"""\
        // stores/authStore.{ext}
        import {{ create }} from 'zustand';
        import {{ persist, createJSONStorage }} from 'zustand/middleware';
        import AsyncStorage from '@react-native-async-storage/async-storage';

        {interface_block}export const useAuthStore = create{generic}()(
          persist(
            (set) => ({{
              token: null,
              isAuthenticated: false,
              login: (token{type_annotation}) => set({{ token, isAuthenticated: true }}),
              logout: () => set({{ token: null, isAuthenticated: false }}),
            }}),
            {{
              name: 'auth-storage',
              storage: createJSONStorage(() => AsyncStorage),
            }}
          )
        );
    """)


def _rn_store_redux(ts: bool) -> str:
    ext = "ts" if ts else "js"
    return textwrap.dedent(f"""\
        // stores/authSlice.{ext}
        import {{ createSlice }} from '@reduxjs/toolkit';

        const authSlice = createSlice({{
          name: 'auth',
          initialState: {{ token: null, isAuthenticated: false }},
          reducers: {{
            login(state, action) {{
              state.token = action.payload;
              state.isAuthenticated = true;
            }},
            logout(state) {{
              state.token = null;
              state.isAuthenticated = false;
            }},
          }},
        }});

        export const {{ login, logout }} = authSlice.actions;
        export default authSlice.reducer;
    """)


def _rn_package_json(name: str, state: str) -> str:
    deps = {
        "expo": "~50.0.0",
        "expo-router": "~3.4.0",
        "react": "18.2.0",
        "react-native": "0.73.0",
        "@expo/vector-icons": "^14.0.0",
        "react-native-reanimated": "~3.6.0",
        "react-native-safe-area-context": "4.8.0",
        "react-native-screens": "~3.29.0",
    }
    if state == "zustand":
        deps["zustand"] = "^4.5.0"
        deps["@react-native-async-storage/async-storage"] = "1.21.0"
    elif state == "redux":
        deps["@reduxjs/toolkit"] = "^2.0.0"
        deps["react-redux"] = "^9.0.0"
    elif state == "jotai":
        deps["jotai"] = "^2.6.0"

    pkg = {
        "name": name,
        "version": "1.0.0",
        "main": "expo-router/entry",
        "scripts": {
            "start": "expo start",
            "android": "expo start --android",
            "ios": "expo start --ios",
            "web": "expo start --web",
            "lint": "eslint . --ext .ts,.tsx",
            "test": "jest",
        },
        "dependencies": deps,
        "devDependencies": {
            "typescript": "^5.3.0",
            "@types/react": "~18.2.0",
            "jest": "^29.7.0",
            "eslint": "^8.56.0",
        },
    }
    return json.dumps(pkg, indent=2) + "\n"


def _rn_tsconfig() -> str:
    cfg = {
        "extends": "expo/tsconfig.base",
        "compilerOptions": {
            "strict": True,
            "paths": {"@/*": ["./src/*"]},
        },
        "include": ["**/*.ts", "**/*.tsx", ".expo/types/**/*.ts", "expo-env.d.ts"],
    }
    return json.dumps(cfg, indent=2) + "\n"


def _rn_app_json(name: str) -> str:
    cfg = {
        "expo": {
            "name": name,
            "slug": name.lower().replace(" ", "-"),
            "version": "1.0.0",
            "orientation": "portrait",
            "scheme": name.lower().replace(" ", "").replace("-", ""),
            "userInterfaceStyle": "automatic",
            "ios": {"supportsTablet": True, "bundleIdentifier": f"com.example.{name.lower().replace('-', '')}"},
            "android": {"adaptiveIcon": {"backgroundColor": "#ffffff"}, "package": f"com.example.{name.lower().replace('-', '')}"},
            "plugins": ["expo-router"],
        }
    }
    return json.dumps(cfg, indent=2) + "\n"


def scaffold_react_native(root: Path, name: str, ts: bool, state: str) -> list:
    """Scaffold a React Native (Expo Router) project."""
    ext_c = "tsx" if ts else "jsx"
    ext_m = "ts" if ts else "js"
    files = {}

    # Config files
    files["package.json"] = _rn_package_json(name, state)
    files["app.json"] = _rn_app_json(name)
    if ts:
        files["tsconfig.json"] = _rn_tsconfig()
    files[".gitignore"] = "node_modules/\n.expo/\ndist/\n*.jks\n*.p8\n*.p12\n*.key\n*.mobileprovision\n*.orig.*\nweb-build/\n"
    files["babel.config.js"] = "module.exports = function (api) {\n  api.cache(true);\n  return { presets: ['babel-preset-expo'] };\n};\n"

    # Navigation / screens
    files[f"app/_layout.{ext_c}"] = _rn_app_layout(ts)
    files[f"app/(tabs)/_layout.{ext_c}"] = _rn_tab_layout(ts)
    files[f"app/(tabs)/index.{ext_c}"] = _rn_home_screen(ts)
    files[f"app/(tabs)/profile.{ext_c}"] = f"// app/(tabs)/profile.{ext_c}\nimport {{ View, Text }} from 'react-native';\n\nexport default function ProfileScreen() {{\n  return <View style={{{{ flex: 1, alignItems: 'center', justifyContent: 'center' }}}}><Text>Profile</Text></View>;\n}}\n"
    files[f"app/(tabs)/settings.{ext_c}"] = f"// app/(tabs)/settings.{ext_c}\nimport {{ View, Text }} from 'react-native';\n\nexport default function SettingsScreen() {{\n  return <View style={{{{ flex: 1, alignItems: 'center', justifyContent: 'center' }}}}><Text>Settings</Text></View>;\n}}\n"
    files[f"app/auth/login.{ext_c}"] = f"// app/auth/login.{ext_c}\nimport {{ View, Text }} from 'react-native';\n\nexport default function LoginScreen() {{\n  return <View style={{{{ flex: 1, alignItems: 'center', justifyContent: 'center' }}}}><Text>Login</Text></View>;\n}}\n"

    # Src layout
    files[f"src/components/ui/.gitkeep"] = ""
    files[f"src/components/features/.gitkeep"] = ""
    files[f"src/hooks/.gitkeep"] = ""
    files[f"src/services/api.{ext_m}"] = f"// src/services/api.{ext_m}\n// Configure your API client here\n\nconst API_BASE_URL = 'https://api.example.com';\n\nexport {{ API_BASE_URL }};\n"
    files[f"src/utils/helpers.{ext_m}"] = f"// src/utils/helpers.{ext_m}\n\nexport function formatDate(date{': Date' if ts else ''}) {{\n  return new Intl.DateTimeFormat('en-US').format(date);\n}}\n"

    # State management
    if state == "zustand":
        files[f"src/stores/authStore.{ext_m}"] = _rn_store_zustand(ts)
    elif state == "redux":
        files[f"src/stores/authSlice.{ext_m}"] = _rn_store_redux(ts)

    # Tests
    files["__tests__/.gitkeep"] = ""

    created = []
    for rel_path, content in files.items():
        full = root / rel_path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content)
        created.append(str(rel_path))

    return sorted(created)


# ---- Flutter --------------------------------------------------------------

def _flutter_pubspec(name: str, state: str) -> str:
    state_dep = ""
    if state == "riverpod":
        state_dep = "  flutter_riverpod: ^2.4.0\n  riverpod_annotation: ^2.3.0\n"
    elif state == "bloc":
        state_dep = "  flutter_bloc: ^8.1.0\n  bloc: ^8.1.0\n"
    elif state == "provider":
        state_dep = "  provider: ^6.1.0\n"

    return textwrap.dedent(f"""\
        name: {name.replace('-', '_')}
        description: A new Flutter project.
        version: 1.0.0+1
        publish_to: 'none'

        environment:
          sdk: '>=3.2.0 <4.0.0'

        dependencies:
          flutter:
            sdk: flutter
          go_router: ^13.0.0
          dio: ^5.4.0
          flutter_secure_storage: ^9.0.0
        {state_dep}
        dev_dependencies:
          flutter_test:
            sdk: flutter
          flutter_lints: ^3.0.0
          mockito: ^5.4.0
          build_runner: ^2.4.0

        flutter:
          uses-material-design: true
    """)


def _flutter_main() -> str:
    return textwrap.dedent("""\
        import 'package:flutter/material.dart';
        import 'router.dart';

        void main() {
          runApp(const MyApp());
        }

        class MyApp extends StatelessWidget {
          const MyApp({super.key});

          @override
          Widget build(BuildContext context) {
            return MaterialApp.router(
              title: 'My App',
              theme: ThemeData(
                colorSchemeSeed: Colors.blue,
                useMaterial3: true,
              ),
              darkTheme: ThemeData(
                colorSchemeSeed: Colors.blue,
                useMaterial3: true,
                brightness: Brightness.dark,
              ),
              routerConfig: router,
            );
          }
        }
    """)


def _flutter_router() -> str:
    return textwrap.dedent("""\
        import 'package:go_router/go_router.dart';
        import 'features/home/home_screen.dart';
        import 'features/profile/profile_screen.dart';
        import 'features/settings/settings_screen.dart';
        import 'shell_screen.dart';

        final router = GoRouter(
          initialLocation: '/',
          routes: [
            ShellRoute(
              builder: (context, state, child) => ShellScreen(child: child),
              routes: [
                GoRoute(path: '/', builder: (context, state) => const HomeScreen()),
                GoRoute(path: '/profile', builder: (context, state) => const ProfileScreen()),
                GoRoute(path: '/settings', builder: (context, state) => const SettingsScreen()),
              ],
            ),
          ],
        );
    """)


def _flutter_shell_screen() -> str:
    return textwrap.dedent("""\
        import 'package:flutter/material.dart';
        import 'package:go_router/go_router.dart';

        class ShellScreen extends StatelessWidget {
          final Widget child;
          const ShellScreen({super.key, required this.child});

          @override
          Widget build(BuildContext context) {
            return Scaffold(
              body: child,
              bottomNavigationBar: NavigationBar(
                selectedIndex: _calculateSelectedIndex(context),
                onDestinationSelected: (index) => _onItemTapped(index, context),
                destinations: const [
                  NavigationDestination(icon: Icon(Icons.home), label: 'Home'),
                  NavigationDestination(icon: Icon(Icons.person), label: 'Profile'),
                  NavigationDestination(icon: Icon(Icons.settings), label: 'Settings'),
                ],
              ),
            );
          }

          int _calculateSelectedIndex(BuildContext context) {
            final location = GoRouterState.of(context).uri.toString();
            if (location.startsWith('/profile')) return 1;
            if (location.startsWith('/settings')) return 2;
            return 0;
          }

          void _onItemTapped(int index, BuildContext context) {
            switch (index) {
              case 0: context.go('/');
              case 1: context.go('/profile');
              case 2: context.go('/settings');
            }
          }
        }
    """)


def _flutter_feature_screen(name: str, label: str) -> str:
    class_name = name.title().replace("_", "") + "Screen"
    return textwrap.dedent(f"""\
        import 'package:flutter/material.dart';

        class {class_name} extends StatelessWidget {{
          const {class_name}({{super.key}});

          @override
          Widget build(BuildContext context) {{
            return Center(child: Text('{label}', style: Theme.of(context).textTheme.headlineMedium));
          }}
        }}
    """)


def scaffold_flutter(root: Path, name: str, state: str) -> list:
    """Scaffold a Flutter project."""
    pkg = name.replace("-", "_")
    files = {}

    files["pubspec.yaml"] = _flutter_pubspec(name, state)
    files["analysis_options.yaml"] = "include: package:flutter_lints/flutter.yaml\n\nlinter:\n  rules:\n    prefer_const_constructors: true\n    prefer_const_declarations: true\n    avoid_print: true\n"
    files[".gitignore"] = ".dart_tool/\n.packages\nbuild/\n*.iml\n.idea/\n.DS_Store\n"

    files[f"lib/main.dart"] = _flutter_main()
    files[f"lib/router.dart"] = _flutter_router()
    files[f"lib/shell_screen.dart"] = _flutter_shell_screen()

    for feat, label in [("home", "Home"), ("profile", "Profile"), ("settings", "Settings")]:
        files[f"lib/features/{feat}/{feat}_screen.dart"] = _flutter_feature_screen(feat, label)

    files["lib/core/constants.dart"] = "class AppConstants {\n  static const String apiBaseUrl = 'https://api.example.com';\n  static const Duration timeout = Duration(seconds: 30);\n}\n"
    files["lib/core/theme.dart"] = "import 'package:flutter/material.dart';\n\nclass AppTheme {\n  static ThemeData get light => ThemeData(\n    colorSchemeSeed: Colors.blue,\n    useMaterial3: true,\n  );\n\n  static ThemeData get dark => ThemeData(\n    colorSchemeSeed: Colors.blue,\n    useMaterial3: true,\n    brightness: Brightness.dark,\n  );\n}\n"
    files["lib/services/.gitkeep"] = ""
    files["lib/models/.gitkeep"] = ""
    files["test/widget_test.dart"] = "// Widget tests go here\n"
    files["test/unit/.gitkeep"] = ""

    created = []
    for rel_path, content in files.items():
        full = root / rel_path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content)
        created.append(str(rel_path))

    return sorted(created)


# ---- iOS Native -----------------------------------------------------------

def _ios_app_swift(name: str) -> str:
    struct_name = name.replace("-", "").replace("_", "").title() + "App"
    return textwrap.dedent(f"""\
        import SwiftUI

        @main
        struct {struct_name}: App {{
            @StateObject private var appState = AppState()

            var body: some Scene {{
                WindowGroup {{
                    ContentView()
                        .environmentObject(appState)
                }}
            }}
        }}
    """)


def _ios_content_view() -> str:
    return textwrap.dedent("""\
        import SwiftUI

        struct ContentView: View {
            @EnvironmentObject var appState: AppState

            var body: some View {
                TabView {
                    HomeView()
                        .tabItem {
                            Label("Home", systemImage: "house")
                        }

                    ProfileView()
                        .tabItem {
                            Label("Profile", systemImage: "person")
                        }

                    SettingsView()
                        .tabItem {
                            Label("Settings", systemImage: "gear")
                        }
                }
            }
        }

        #Preview {
            ContentView()
                .environmentObject(AppState())
        }
    """)


def _ios_simple_view(name: str) -> str:
    return textwrap.dedent(f"""\
        import SwiftUI

        struct {name}View: View {{
            var body: some View {{
                NavigationStack {{
                    VStack {{
                        Text("{name}")
                            .font(.largeTitle)
                            .fontWeight(.bold)
                    }}
                    .navigationTitle("{name}")
                }}
            }}
        }}

        #Preview {{
            {name}View()
        }}
    """)


def _ios_app_state() -> str:
    return textwrap.dedent("""\
        import Foundation

        @MainActor
        class AppState: ObservableObject {
            @Published var isAuthenticated = false
            @Published var isLoading = false

            func login(email: String, password: String) async throws {
                isLoading = true
                defer { isLoading = false }

                // TODO: Implement authentication logic
                try await Task.sleep(nanoseconds: 1_000_000_000)
                isAuthenticated = true
            }

            func logout() {
                isAuthenticated = false
            }
        }
    """)


def scaffold_ios_native(root: Path, name: str) -> list:
    """Scaffold a native iOS (SwiftUI) project."""
    safe_name = name.replace("-", "_")
    files = {}

    files[f"{safe_name}/App/{safe_name}App.swift"] = _ios_app_swift(name)
    files[f"{safe_name}/App/ContentView.swift"] = _ios_content_view()
    files[f"{safe_name}/App/AppState.swift"] = _ios_app_state()

    for view in ["Home", "Profile", "Settings"]:
        files[f"{safe_name}/Features/{view}/{view}View.swift"] = _ios_simple_view(view)

    files[f"{safe_name}/Core/Network/APIClient.swift"] = textwrap.dedent("""\
        import Foundation

        actor APIClient {
            static let shared = APIClient()
            private let session: URLSession
            private let baseURL = URL(string: "https://api.example.com")!

            private init() {
                let config = URLSessionConfiguration.default
                config.timeoutIntervalForRequest = 30
                config.waitsForConnectivity = true
                self.session = URLSession(configuration: config)
            }

            func request<T: Decodable>(_ endpoint: String, method: String = "GET") async throws -> T {
                let url = baseURL.appendingPathComponent(endpoint)
                var request = URLRequest(url: url)
                request.httpMethod = method
                request.setValue("application/json", forHTTPHeaderField: "Content-Type")

                let (data, response) = try await session.data(for: request)

                guard let httpResponse = response as? HTTPURLResponse,
                      (200...299).contains(httpResponse.statusCode) else {
                    throw URLError(.badServerResponse)
                }

                return try JSONDecoder().decode(T.self, from: data)
            }
        }
    """)

    files[f"{safe_name}/Core/Storage/KeychainHelper.swift"] = textwrap.dedent("""\
        import Foundation
        import Security

        enum KeychainHelper {
            static func save(_ data: Data, forKey key: String) -> Bool {
                let query: [String: Any] = [
                    kSecClass as String: kSecClassGenericPassword,
                    kSecAttrAccount as String: key,
                    kSecValueData as String: data,
                ]

                SecItemDelete(query as CFDictionary)
                return SecItemAdd(query as CFDictionary, nil) == errSecSuccess
            }

            static func read(forKey key: String) -> Data? {
                let query: [String: Any] = [
                    kSecClass as String: kSecClassGenericPassword,
                    kSecAttrAccount as String: key,
                    kSecReturnData as String: true,
                    kSecMatchLimit as String: kSecMatchLimitOne,
                ]

                var result: AnyObject?
                SecItemCopyMatching(query as CFDictionary, &result)
                return result as? Data
            }

            static func delete(forKey key: String) {
                let query: [String: Any] = [
                    kSecClass as String: kSecClassGenericPassword,
                    kSecAttrAccount as String: key,
                ]
                SecItemDelete(query as CFDictionary)
            }
        }
    """)

    files[f"{safe_name}/Models/.gitkeep"] = ""
    files[f"{safe_name}/Resources/Assets.xcassets/.gitkeep"] = ""
    files[f"{safe_name}Tests/.gitkeep"] = ""
    files[f"{safe_name}UITests/.gitkeep"] = ""
    files[".gitignore"] = "build/\n*.xcuserdata\n*.xcworkspace\nPods/\nDerivedData/\n.DS_Store\n"

    created = []
    for rel_path, content in files.items():
        full = root / rel_path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content)
        created.append(str(rel_path))

    return sorted(created)


# ---- Android Native -------------------------------------------------------

def _android_manifest(name: str) -> str:
    pkg = f"com.example.{name.replace('-', '').lower()}"
    return textwrap.dedent(f"""\
        <?xml version="1.0" encoding="utf-8"?>
        <manifest xmlns:android="http://schemas.android.com/apk/res/android"
            package="{pkg}">

            <uses-permission android:name="android.permission.INTERNET" />

            <application
                android:allowBackup="true"
                android:label="{name}"
                android:supportsRtl="true"
                android:theme="@style/Theme.Material3.DayNight">

                <activity
                    android:name=".MainActivity"
                    android:exported="true"
                    android:theme="@style/Theme.Material3.DayNight">
                    <intent-filter>
                        <action android:name="android.intent.action.MAIN" />
                        <category android:name="android.intent.category.LAUNCHER" />
                    </intent-filter>
                </activity>
            </application>
        </manifest>
    """)


def _android_main_activity(name: str) -> str:
    pkg = f"com.example.{name.replace('-', '').lower()}"
    return textwrap.dedent(f"""\
        package {pkg}

        import android.os.Bundle
        import androidx.activity.ComponentActivity
        import androidx.activity.compose.setContent
        import androidx.compose.foundation.layout.fillMaxSize
        import androidx.compose.material3.MaterialTheme
        import androidx.compose.material3.Surface
        import androidx.compose.ui.Modifier
        import {pkg}.navigation.AppNavigation
        import {pkg}.ui.theme.AppTheme
        import dagger.hilt.android.AndroidEntryPoint

        @AndroidEntryPoint
        class MainActivity : ComponentActivity() {{
            override fun onCreate(savedInstanceState: Bundle?) {{
                super.onCreate(savedInstanceState)
                setContent {{
                    AppTheme {{
                        Surface(
                            modifier = Modifier.fillMaxSize(),
                            color = MaterialTheme.colorScheme.background
                        ) {{
                            AppNavigation()
                        }}
                    }}
                }}
            }}
        }}
    """)


def _android_navigation(name: str) -> str:
    pkg = f"com.example.{name.replace('-', '').lower()}"
    return textwrap.dedent(f"""\
        package {pkg}.navigation

        import androidx.compose.foundation.layout.padding
        import androidx.compose.material.icons.Icons
        import androidx.compose.material.icons.filled.Home
        import androidx.compose.material.icons.filled.Person
        import androidx.compose.material.icons.filled.Settings
        import androidx.compose.material3.*
        import androidx.compose.runtime.*
        import androidx.compose.ui.Modifier
        import androidx.navigation.compose.*
        import {pkg}.features.home.HomeScreen
        import {pkg}.features.profile.ProfileScreen
        import {pkg}.features.settings.SettingsScreen

        @Composable
        fun AppNavigation() {{
            val navController = rememberNavController()

            Scaffold(
                bottomBar = {{
                    NavigationBar {{
                        val currentRoute = navController
                            .currentBackStackEntryAsState().value?.destination?.route

                        NavigationBarItem(
                            selected = currentRoute == "home",
                            onClick = {{ navController.navigate("home") {{ launchSingleTop = true }} }},
                            icon = {{ Icon(Icons.Default.Home, contentDescription = "Home") }},
                            label = {{ Text("Home") }}
                        )
                        NavigationBarItem(
                            selected = currentRoute == "profile",
                            onClick = {{ navController.navigate("profile") {{ launchSingleTop = true }} }},
                            icon = {{ Icon(Icons.Default.Person, contentDescription = "Profile") }},
                            label = {{ Text("Profile") }}
                        )
                        NavigationBarItem(
                            selected = currentRoute == "settings",
                            onClick = {{ navController.navigate("settings") {{ launchSingleTop = true }} }},
                            icon = {{ Icon(Icons.Default.Settings, contentDescription = "Settings") }},
                            label = {{ Text("Settings") }}
                        )
                    }}
                }}
            ) {{ padding ->
                NavHost(navController, startDestination = "home", Modifier.padding(padding)) {{
                    composable("home") {{ HomeScreen() }}
                    composable("profile") {{ ProfileScreen() }}
                    composable("settings") {{ SettingsScreen() }}
                }}
            }}
        }}
    """)


def _android_feature_screen(name: str, pkg_base: str) -> str:
    lower = name.lower()
    return textwrap.dedent(f"""\
        package {pkg_base}.features.{lower}

        import androidx.compose.foundation.layout.*
        import androidx.compose.material3.*
        import androidx.compose.runtime.Composable
        import androidx.compose.ui.Alignment
        import androidx.compose.ui.Modifier
        import androidx.compose.ui.unit.dp

        @Composable
        fun {name}Screen() {{
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {{
                Text(
                    text = "{name}",
                    style = MaterialTheme.typography.headlineMedium
                )
            }}
        }}
    """)


def _android_build_gradle(name: str) -> str:
    return textwrap.dedent(f"""\
        plugins {{
            id 'com.android.application'
            id 'org.jetbrains.kotlin.android'
            id 'com.google.dagger.hilt.android'
            id 'kotlin-kapt'
        }}

        android {{
            namespace 'com.example.{name.replace("-", "").lower()}'
            compileSdk 34

            defaultConfig {{
                applicationId "com.example.{name.replace("-", "").lower()}"
                minSdk 26
                targetSdk 34
                versionCode 1
                versionName "1.0"
            }}

            buildFeatures {{
                compose true
            }}

            composeOptions {{
                kotlinCompilerExtensionVersion '1.5.0'
            }}

            kotlinOptions {{
                jvmTarget = '17'
            }}
        }}

        dependencies {{
            // Compose
            implementation platform('androidx.compose:compose-bom:2024.01.00')
            implementation 'androidx.compose.ui:ui'
            implementation 'androidx.compose.material3:material3'
            implementation 'androidx.compose.ui:ui-tooling-preview'
            implementation 'androidx.activity:activity-compose:1.8.0'
            implementation 'androidx.navigation:navigation-compose:2.7.0'
            implementation 'androidx.lifecycle:lifecycle-runtime-compose:2.7.0'

            // Hilt
            implementation 'com.google.dagger:hilt-android:2.50'
            kapt 'com.google.dagger:hilt-compiler:2.50'
            implementation 'androidx.hilt:hilt-navigation-compose:1.1.0'

            // Networking
            implementation 'com.squareup.retrofit2:retrofit:2.9.0'
            implementation 'com.squareup.retrofit2:converter-gson:2.9.0'
            implementation 'com.squareup.okhttp3:logging-interceptor:4.12.0'

            // Testing
            testImplementation 'junit:junit:4.13.2'
            androidTestImplementation 'androidx.test.ext:junit:1.1.5'
            androidTestImplementation 'androidx.compose.ui:ui-test-junit4'
        }}
    """)


def scaffold_android_native(root: Path, name: str) -> list:
    """Scaffold a native Android (Kotlin/Compose) project."""
    pkg = f"com.example.{name.replace('-', '').lower()}"
    pkg_path = pkg.replace(".", "/")
    files = {}

    files["app/build.gradle"] = _android_build_gradle(name)
    files["app/src/main/AndroidManifest.xml"] = _android_manifest(name)
    files[f"app/src/main/java/{pkg_path}/MainActivity.kt"] = _android_main_activity(name)
    files[f"app/src/main/java/{pkg_path}/navigation/AppNavigation.kt"] = _android_navigation(name)

    for feat in ["Home", "Profile", "Settings"]:
        files[f"app/src/main/java/{pkg_path}/features/{feat.lower()}/{feat}Screen.kt"] = _android_feature_screen(feat, pkg)

    files[f"app/src/main/java/{pkg_path}/ui/theme/AppTheme.kt"] = textwrap.dedent(f"""\
        package {pkg}.ui.theme

        import androidx.compose.material3.MaterialTheme
        import androidx.compose.material3.dynamicLightColorScheme
        import androidx.compose.runtime.Composable
        import androidx.compose.ui.platform.LocalContext

        @Composable
        fun AppTheme(content: @Composable () -> Unit) {{
            MaterialTheme(
                colorScheme = dynamicLightColorScheme(LocalContext.current),
                content = content,
            )
        }}
    """)

    files[f"app/src/main/java/{pkg_path}/data/network/ApiService.kt"] = textwrap.dedent(f"""\
        package {pkg}.data.network

        import retrofit2.http.GET

        interface ApiService {{
            @GET("items")
            suspend fun getItems(): List<Any>
        }}
    """)

    files[f"app/src/main/java/{pkg_path}/di/AppModule.kt"] = textwrap.dedent(f"""\
        package {pkg}.di

        import dagger.Module
        import dagger.Provides
        import dagger.hilt.InstallIn
        import dagger.hilt.components.SingletonComponent
        import {pkg}.data.network.ApiService
        import retrofit2.Retrofit
        import retrofit2.converter.gson.GsonConverterFactory
        import javax.inject.Singleton

        @Module
        @InstallIn(SingletonComponent::class)
        object AppModule {{

            @Provides
            @Singleton
            fun provideRetrofit(): Retrofit = Retrofit.Builder()
                .baseUrl("https://api.example.com/")
                .addConverterFactory(GsonConverterFactory.create())
                .build()

            @Provides
            @Singleton
            fun provideApiService(retrofit: Retrofit): ApiService =
                retrofit.create(ApiService::class.java)
        }}
    """)

    files["app/src/test/.gitkeep"] = ""
    files["app/src/androidTest/.gitkeep"] = ""
    files[".gitignore"] = "*.iml\n.gradle/\n/local.properties\n/.idea/\n/build/\n/captures\n.externalNativeBuild\n.cxx\n*.apk\n*.aab\n"

    created = []
    for rel_path, content in files.items():
        full = root / rel_path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content)
        created.append(str(rel_path))

    return sorted(created)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

PLATFORMS = {
    "react-native": scaffold_react_native,
    "flutter": scaffold_flutter,
    "ios-native": scaffold_ios_native,
    "android-native": scaffold_android_native,
}

STATE_OPTIONS = {
    "react-native": ["zustand", "redux", "jotai", "none"],
    "flutter": ["riverpod", "bloc", "provider", "none"],
    "ios-native": [],
    "android-native": [],
}


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="mobile_scaffold",
        description="Scaffold a production-ready mobile project.",
        epilog="Example: python mobile_scaffold.py my-app --platform react-native --typescript --state zustand",
    )
    parser.add_argument("name", help="Project name (used as directory name)")
    parser.add_argument(
        "--platform", "-p",
        required=True,
        choices=sorted(PLATFORMS.keys()),
        help="Target mobile platform",
    )
    parser.add_argument(
        "--typescript", "-t",
        action="store_true",
        default=False,
        help="Use TypeScript (React Native only, default: True when applicable)",
    )
    parser.add_argument(
        "--state", "-s",
        default="none",
        help="State management library (platform-dependent, e.g. zustand, redux, riverpod, bloc)",
    )
    parser.add_argument(
        "--output-dir", "-o",
        default=".",
        help="Parent directory for the generated project (default: current directory)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output result as JSON",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    platform = args.platform
    name = args.name
    state = args.state.lower()
    ts = args.typescript or (platform == "react-native")  # default TS for RN
    output_dir = Path(args.output_dir).resolve()
    root = output_dir / name

    # Validate state choice
    valid_states = STATE_OPTIONS.get(platform, [])
    if valid_states and state != "none" and state not in valid_states:
        sys.stderr.write(
            f"Error: --state '{state}' is not supported for {platform}. "
            f"Valid options: {', '.join(valid_states)}\n"
        )
        sys.exit(1)

    if root.exists():
        sys.stderr.write(f"Error: Directory '{root}' already exists.\n")
        sys.exit(1)

    root.mkdir(parents=True, exist_ok=True)

    # Dispatch to platform scaffolder
    if platform == "react-native":
        created = scaffold_react_native(root, name, ts, state)
    elif platform == "flutter":
        created = scaffold_flutter(root, name, state)
    elif platform == "ios-native":
        created = scaffold_ios_native(root, name)
    elif platform == "android-native":
        created = scaffold_android_native(root, name)
    else:
        sys.stderr.write(f"Error: Unknown platform '{platform}'.\n")
        sys.exit(1)

    result = {
        "project_name": name,
        "platform": platform,
        "typescript": ts if platform == "react-native" else None,
        "state_management": state if state != "none" else None,
        "output_directory": str(root),
        "files_created": len(created),
        "files": created,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Mobile project scaffolded successfully!")
        print(f"  Project:    {name}")
        print(f"  Platform:   {platform}")
        if platform == "react-native":
            print(f"  TypeScript: {'Yes' if ts else 'No'}")
        if state != "none":
            print(f"  State Mgmt: {state}")
        print(f"  Location:   {root}")
        print(f"  Files:      {len(created)} created")
        print()
        print("Files created:")
        for f in created:
            print(f"  {f}")
        print()

        # Platform-specific next steps
        if platform == "react-native":
            print("Next steps:")
            print(f"  cd {name}")
            print("  npm install")
            print("  npx expo start")
        elif platform == "flutter":
            print("Next steps:")
            print(f"  cd {name}")
            print("  flutter pub get")
            print("  flutter run")
        elif platform == "ios-native":
            print("Next steps:")
            print(f"  cd {name}")
            print("  open *.xcodeproj  # or create via Xcode > New Project")
            print("  # Copy generated Swift files into Xcode project")
        elif platform == "android-native":
            print("Next steps:")
            print(f"  cd {name}")
            print("  # Open in Android Studio")
            print("  ./gradlew assembleDebug")


if __name__ == "__main__":
    main()
