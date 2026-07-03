# Robot Controller — Frontend

An engineering **monitoring dashboard** (not a consumer app) to observe and control a
Physical AI robot. Dark, industrial, minimal. Runs on **mock data by default** so every
screen is fully populated without a backend; point it at the real server in Settings.

Talks to the [`../backend`](../backend) FastAPI "Robot Brain".

---

## Stack

React Native CLI · TypeScript · React Navigation (bottom tabs) · React Native Paper ·
React Query · Zustand · Axios · Vision Camera · MMKV · Reanimated · SVG.

Feature-first, layered, fully reusable components.

---

## Getting started

Prerequisites: **Node ≥ 18**, **JDK 17**, **Android Studio** (SDK + an emulator or a USB
device with USB debugging). The native `android/` and `ios/` projects are included and
pre-configured (Vision Camera permissions + minSdk 26, vector-icon fonts, new architecture).

```bash
npm install                   # JS deps

# Terminal 1 — start the bundler
npm run start

# Terminal 2 — build + install + launch on the running emulator / connected device
npm run android
```

`npm run android` builds the debug APK, installs it, and launches it. First build downloads
Gradle + Android deps (a few minutes); later builds are fast.

Other scripts: `npm run ios` (macOS; run `npm run pods` first), `npm run typecheck`,
`npm run lint`.

The app opens in **Demo Mode** (mock telemetry). To use the backend: Settings → turn off
Demo Mode and set **Server URL** (Android emulator → `http://10.0.2.2:8000`).

---

## Architecture

```
src/
├── components/     Reusable UI: StatusCard · MetricCard · ConnectionBadge · LogItem ·
│                   ActionButton · SectionHeader · InfoRow · RobotStatusIndicator ·
│                   Card · Screen · ScreenHeader · Grid
├── screens/        Feature-first screens
│   ├── dashboard/  DashboardScreen · MissionCard
│   ├── camera/     CameraScreen · CameraOverlay (SVG boxes)
│   ├── logs/       LogsScreen · LogFilterBar
│   └── settings/   SettingsScreen
├── navigation/     BottomTabs (Dashboard · Camera · Logs · Settings)
├── hooks/          useTelemetryEngine · useHealth · useRobotControl · useFilteredLogs ·
│                   useInterval
├── services/       API layer (screens NEVER call axios directly)
│   ├── api/        client (axios) · RobotService · HealthService
│   └── SettingsService (MMKV persistence)
├── store/          Zustand: robotStore · connectionStore · settingsStore · logStore
│                   + MMKV storage
├── types/          Backend contracts + dashboard/camera/log/settings models
├── theme/          colors · spacing · typography · Paper (MD3) dark theme
└── utils/          formatters · constants · mock-data generators
```

**Data flow.** A single headless `useTelemetryEngine()` (mounted once in `App.tsx`) keeps
the Zustand stores live — in Demo Mode it drives an interval that evolves telemetry, streams
logs and sets connection statuses; in Live Mode it polls `GET /health` and `GET /robot/{id}`
via React Query and maps the results in. Screens are thin: they read stores and render
reusable components. All network access goes through the service layer.

**Design rules honored.** No business logic or axios in screens · reusable components
everywhere · large spacing + rounded cards · one purposeful animation only (the "live" status
pulse) · MMKV for instant, synchronous settings rehydration.

---

## Theme

| Token | Value |
|-------|-------|
| Background | `#121212` |
| Cards | `#1E1E1E` |
| Primary (blue) | `#3B82F6` |
| Success (green) | `#22C55E` |
| Warning (orange) | `#F59E0B` |
| Error (red) | `#EF4444` |

All colors live in `src/theme/colors.ts`; spacing/radius in `spacing.ts`. Change them once,
everywhere updates.

---

## Screens

- **Dashboard** — top bar (robot name + live status), subsystem connection cards
  (Server / ESP32 / Camera / Microphone), metrics (Behavior, State, Battery, Latency, FPS),
  current mission with progress, control buttons (Start / Stop / Reconnect / Emergency Stop),
  and the last velocity command.
- **Camera** — large Vision Camera preview with a HUD overlay (FPS, resolution, upload status,
  detection count) and SVG bounding boxes (mock now; wire the detector's boxes later). Degrades
  gracefully without a camera/permission.
- **Logs** — scrollable, level-filterable event stream (All / Info / Success / Warning / Error),
  color-coded, newest first, with clear.
- **Settings** — Server URL, Robot name/ID, Bluetooth device, Camera FPS, Image quality,
  Auto connect / Auto start / Demo mode, Theme, and Save (persisted to MMKV).

---

## Native setup notes

Standard React Native CLI (new architecture, RN 0.76.5). Native config already applied:

- **Android** (`android/`): camera + microphone permissions, `minSdkVersion = 26` (Vision
  Camera), vector-icon fonts bundled via `fonts.gradle`, `newArchEnabled=true` (required by
  MMKV v3). Debug builds allow cleartext HTTP so `http://10.0.2.2:8000` works out of the box.
- **iOS** (`ios/`): run `npm run pods` to install CocoaPods. Add `NSCameraUsageDescription`
  and `NSMicrophoneUsageDescription` to `Info.plist` before using the camera.
- **Reanimated**: Babel plugin is configured last in `babel.config.js`.
- The `@/` import alias is wired in both `babel.config.js` (module-resolver) and `tsconfig.json`.

### Troubleshooting

- **Icons show as boxes** → rebuild (`npm run android`) so `fonts.gradle` copies the fonts;
  a Metro-only reload won't add native assets.
- **`SDK location not found`** → create `android/local.properties` with
  `sdk.dir=/path/to/Android/sdk` (or set `ANDROID_HOME`).
- **Metro stale cache** → `npm run start -- --reset-cache`.
- **Release builds** to a plain-HTTP backend need a network-security-config (debug already
  permits cleartext).

> Native projects were generated from the official RN 0.76.5 template and committed here.
> `android/build/`, `ios/Pods/` and `node_modules/` are gitignored.
