---
name: senior-mobile
description: >
  Mobile development across SwiftUI, Jetpack Compose, React Native (Expo) and Flutter:
  scaffolding, feature architecture, static performance checks and store listings. Use when
  building, optimizing or shipping a mobile app.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: mobile-development
  updated: 2026-11-08
  tags: [mobile, ios, android, react-native, flutter, swift, kotlin]
---
# Senior Mobile Developer

Expert mobile application development across iOS, Android, React Native, and Flutter — scaffolding production projects, building MVVM features (SwiftUI, Jetpack Compose, Expo Router), static performance analysis, and App Store / Play Store submission.

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

Before scaffolding, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Platform:** react-native / flutter / ios-native / android-native (`--platform`; an entirely different scaffold).
- **State management:** e.g. zustand (`--state`; changes the generated architecture).
- **Task:** new project scaffold vs store-listing metadata vs performance analysis (selects `mobile_scaffold` / `store_metadata_generator` / `app_performance_analyzer`).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Tools Overview

| Tool | Purpose | Example (runs as written) |
|------|---------|---------|
| `mobile_scaffold.py` | Scaffold react-native (Expo Router), flutter, ios-native (SwiftUI) or android-native (Compose) into `<output-dir>/<name>` (`--platform`, `--state`, `--typescript`, `-o`, `--json`) | `python scripts/mobile_scaffold.py MyApp --platform react-native --state zustand -o /tmp/apps` |
| `store_metadata_generator.py` | App Store / Play Store listing drafts: titles, keywords, privacy labels, age rating, checklist | `python scripts/store_metadata_generator.py --app-name FitTrack --category health --features "workout,tracking"` |
| `app_performance_analyzer.py` | Static scan: image sizes, inline styles, re-render and leak patterns, console logs, bundle estimate | `python scripts/app_performance_analyzer.py /tmp/apps/MyApp --platform react-native` |

Always pass `-o` to the scaffolder: it defaults to the current directory. It refuses to
overwrite an existing project folder.

Exit codes: `0` ok; `2` bad input (missing directory, existing or unwritable target folder, empty
`--app-name` or `--features`, unknown state library). The analyzer reports findings with
exit 0; read its score and issue list rather than gating on the code.

Version currency: the React Native template pins Expo SDK 58 (React Native 0.88, React 19.3)
and installs the native companion packages with `npm run setup` (`npx expo install`, so they
match the SDK). The Android template targets API 36 (Android 16), which Google Play has
required for new apps and updates since 2026-08-31, with the Kotlin 2 Compose compiler plugin
and KSP. After any upgrade, run `npx expo install --fix` to align native packages with the installed SDK;
check the current Google Play target-API requirement and Xcode/iOS SDK minimum before
release, since both move every year.

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

## Anti-Patterns

### Shipping With Mismatched Native Versions
**Mistake:** Bumping `expo` or `react-native` in package.json by hand and leaving the other native packages where they were.
**Why it happens:** It looks like a one-line upgrade.
**Instead:** Upgrade the SDK with `npx expo install expo@latest --fix` so every native module moves to the version that SDK was tested with, then rebuild the dev client.

### Trusting a Static Score as Performance
**Mistake:** Reporting "performance A" from `app_performance_analyzer.py` without profiling.
**Why it happens:** The score is the most visible number in the output.
**Instead:** The analyzer finds code smells. Measure startup time, frame drops and memory on a low-end device with Xcode Instruments, Android Studio Profiler or the React Native performance monitor before claiming an improvement.

### Missing the Annual Store Deadlines
**Mistake:** Discovering at submission time that the build targets an Android API level or iOS SDK the stores no longer accept.
**Why it happens:** The requirements change once a year and the old build still runs.
**Instead:** Check the current Google Play target-API and App Store SDK minimums at the start of each release cycle and bump them in the template.

## Files

| File | Purpose |
|------|---------|
| `scripts/mobile_scaffold.py` | Project scaffolder for four platforms |
| `scripts/store_metadata_generator.py` | Store listing metadata and submission checklist |
| `scripts/app_performance_analyzer.py` | Static performance scan |
| `REFERENCE.md` | Extended worked code for the workflows |
| `references/*.md` | Workflows, tool reference, troubleshooting, RN and native patterns, mobile security |
