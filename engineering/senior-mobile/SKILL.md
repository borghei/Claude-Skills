---
name: senior-mobile
description: 
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: mobile-development
  updated: 2026-06-17
  tags: [mobile, ios, android, react-native, flutter, swift, kotlin]
---
# Senior Mobile Developer

Expert mobile application development across iOS, Android, React Native, and Flutter — scaffolding production projects, building MVVM features (SwiftUI, Jetpack Compose, Expo Router), static performance analysis, and App Store / Play Store submission.

## Keywords

mobile, ios, android, react-native, flutter, swift, kotlin, swiftui,
jetpack-compose, expo-router, zustand, app-store, performance, offline-first

## Core Capabilities

- **Project scaffolding** — production-ready structure, navigation, and state management for React Native (Expo Router), Flutter, iOS native (SwiftUI), and Android native (Jetpack Compose).
- **Platform selection** — decision matrix across native iOS/Android, React Native, and Flutter by language, performance, and code-sharing.
- **Feature architecture** — MVVM patterns: SwiftUI `@MainActor` ViewModels, Compose sealed `UiState` + `StateFlow`, Zustand stores.
- **Performance optimization** — static analysis of image assets, re-renders, memory leaks, bundle size, plus FlatList/RecyclerView/collection-view tuning.
- **Store submission** — metadata, keywords, privacy labels, age ratings, and submission checklists for both stores.

## When to Use

- Starting a new mobile app and choosing a platform.
- Building a SwiftUI, Jetpack Compose, or React Native feature with clean architecture.
- Diagnosing and fixing mobile performance issues.
- Preparing an App Store / Play Store submission.

## Clarify First

Before scaffolding, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Platform** — react-native / flutter / ios-native / android-native (`--platform`; an entirely different scaffold)
- [ ] **State management** — e.g. zustand (`--state`; changes the generated architecture)
- [ ] **Task** — new project scaffold vs store-listing metadata vs performance analysis (selects `mobile_scaffold` / `store_metadata_generator` / `app_performance_analyzer`)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `mobile_scaffold.py` | Scaffold a project for react-native, flutter, ios-native, or android-native | `python scripts/mobile_scaffold.py MyApp --platform react-native --state zustand` |
| `store_metadata_generator.py` | Generate App Store / Play Store listing metadata | `python scripts/store_metadata_generator.py --app-name FitTrack --category health --features "workout,tracking"` |
| `app_performance_analyzer.py` | Static performance analysis (score, issues, bundle estimate) | `python scripts/app_performance_analyzer.py ./my-app --platform react-native` |

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/workflows.md](references/workflows.md)** — the platform decision matrix and all five end-to-end workflows (React Native scaffold, SwiftUI feature, Jetpack Compose feature, performance optimization, store submission) with SwiftUI/Compose code examples. Read when executing any workflow.
- **[references/tool-reference.md](references/tool-reference.md)** — full parameter tables, examples, and output formats for the three scripts. Read when running the scripts.
- **[references/troubleshooting-and-success.md](references/troubleshooting-and-success.md)** — the build/render/submission troubleshooting table and the success-criteria bar. Read when debugging or validating quality.
- **[references/react-native-patterns.md](references/react-native-patterns.md)** — production React Native: navigation, state management, performance, testing, native modules, OTA updates. Read for deep RN work.
- **[references/ios-android-patterns.md](references/ios-android-patterns.md)** — native iOS/Android architecture, UI frameworks, concurrency, platform UX guidelines, and CI/CD. Read for deep native work.
- **[references/mobile-security-guide.md](references/mobile-security-guide.md)** — secure storage, network security, authentication, code protection, and OWASP Mobile Top 10 compliance. Read when hardening an app.
- **[REFERENCE.md](REFERENCE.md)** — extended code examples for the workflows above. Read when you need fuller worked code.

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

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `senior-frontend` | Shared component patterns, styling conventions, and responsive design principles for React Native web targets | Frontend design tokens and component APIs feed into mobile UI components |
| `senior-backend` | API contract definitions, authentication flows, and data models consumed by mobile clients | Backend OpenAPI specs define mobile service layer interfaces |
| `senior-devops` | Build pipelines, code signing automation, and deployment workflows for mobile releases | Mobile build artifacts flow into CI/CD pipelines for TestFlight / Play Console distribution |
| `senior-qa` | Test strategy alignment, device matrix coverage, and E2E testing patterns for mobile screens | QA test plans drive device coverage; mobile scaffold includes test directory structure |
| `senior-security` | Secure storage patterns (Keychain/Keystore), certificate pinning, and data encryption for mobile apps | Security requirements inform Keychain helper implementation and network client configuration |
| `release-orchestrator` | Version bumping, changelog generation, and coordinated release across iOS and Android | Release metadata and version info flow from orchestrator into store submission workflow |
