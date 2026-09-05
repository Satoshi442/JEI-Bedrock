# JEI-Bedrock — Phase 0

Native LeviLaunchroid mod foundation for Minecraft Bedrock on Android.
**Phase 0 only** — no item registry, no recipes, no UI, no Mod Menu, no
hooks, no gameplay code. This exists purely to prove the mod loads and
initializes cleanly through the Preloader.

This build uses **CMake + FetchContent**, matching LeviLaunchroid's own
documented quick-start (`docs/guide/developer.md`) and its reference
implementation (`examples/full-cpp-mod`) exactly — not XMake. An earlier
version of this project used XMake to match a different working project's
toolchain; that was a reasonable alternative but not what LeviLaunchroid
itself documents, so this version switches to the officially documented path.

## Project structure

```
JEIBedrock/
├── CMakeLists.txt
├── manifest.json
├── README.md
├── include/
│   └── jeibedrock/
│       └── Version.hpp
├── src/
│   └── JEIBedrockMod.cpp
├── scripts/
│   └── package_levipack.py
├── assets/
│   └── icon.png        (optional — see Assets below)
└── third_party/
    └── preloader-android/   (you provide this — see Setup)
```

## Setup: getting the preloader SDK

CMake needs a checkout of `LiteLDev/preloader-android` to build against.
Either:

```bash
git clone --branch 0.2.3 https://github.com/LiteLDev/preloader-android.git \
    JEIBedrock/third_party/preloader-android
```

or point `PRELOADER_ANDROID_ROOT` at any existing checkout you already have
(e.g. the one you extracted from `preloader-android-0_2_3.zip`) instead of
cloning a second copy — see Build instructions below.

## Build instructions (Termux / Linux-like environment)

Configure, pointing at your Android NDK and (if not using the default
`third_party/preloader-android` path) your preloader checkout:

```bash
cd JEIBedrock
cmake -B build -G Ninja \
    -DCMAKE_TOOLCHAIN_FILE=$ANDROID_NDK_HOME/build/cmake/android.toolchain.cmake \
    -DANDROID_ABI=arm64-v8a \
    -DANDROID_PLATFORM=android-24 \
    -DCMAKE_BUILD_TYPE=Release \
    -DPRELOADER_ANDROID_ROOT=/path/to/preloader-android-0.2.3
```

Build:

```bash
cmake --build build
```

Locate the `.so` and the packaged `.levipack` (built automatically by the
post-build step, next to the `.so`):

```
build/out/arm64-v8a/libjeibedrock.so
build/out/arm64-v8a/JEIBedrock.levipack
```

### Assets

`assets/icon.png` is optional in this build — `manifest.json` has no `icon`
field, and the packaging script only bundles an icon if you pass `--icon`
explicitly. Add one later once you have real artwork; it isn't required for
Phase 0 to load.

## Installation / testing

Confirmed from LeviLaunchroid's own source (`LauncherStorage.java`,
`GameVersion.java`): mods live in a per-profile `mods` folder under the
launcher's app-scoped external media directory:

```
Android/media/org.levimc.launcher/minecraft/<profileId>/mods/
```

(Falls back to the app's internal `getFilesDir()` if external media storage
is unavailable.) Either:

- Import the `.levipack` through Levi Launcher's own mod-import UI, or
- Copy the unpacked mod directory (containing `manifest.json` and
  `libjeibedrock.so`) directly into that `mods/` folder.

## Verification checklist

- [ ] CMake configures without error
- [ ] `cmake --build build` compiles without error
- [ ] `libjeibedrock.so` (ARM64) is generated
- [ ] `JEIBedrock.levipack` is generated
- [ ] Levi Launcher recognizes the mod
- [ ] Mod loads (`load()` is called)
- [ ] Logcat shows the Phase 0 startup sequence (see below)
- [ ] No crash on load/enable
- [ ] Mod Menu entry — **not applicable in Phase 0**, intentionally excluded

## Expected logcat output

```
[JEI-Bedrock] Phase 0 initializing
[JEI-Bedrock] load() called - version 0.1.0 (phase 0)
[JEI-Bedrock] modRoot=<path>
[JEI-Bedrock] configDir=<path>
[JEI-Bedrock] resourceDir=<path>
[JEI-Bedrock] Native library loaded
[JEI-Bedrock] enable() called - mod is now active
[JEI-Bedrock] Phase 0 initialization complete
```

Filter with:

```bash
adb logcat -s JEI-Bedrock
```

(The tag is derived from the mod's display name by `pl::log::Logger`, so it
will show as `JEI-Bedrock` regardless of the C++ class name.)

## API Verification

| API | Purpose | Status | Source |
|---|---|---|---|
| `pl::mod::ModContext` / `ll::mod::NativeMod` | Lifecycle context and persistent mod handle | CONFIRMED | `preloader-android-0.2.3/include/pl/Mod.hpp` |
| `ll::mod::NativeMod::current()` | Officially recommended way to obtain a persistent self-reference in the constructor | CONFIRMED | `LeviLaunchroid-1.5.16/docs/guide/developer.md`, `examples/full-cpp-mod/src/FullCppMod.cpp` |
| `PL_REGISTER_MOD(Class, instance)` | Registers the mod class with Preloader | CONFIRMED | `preloader-android-0.2.3/include/pl/Mod.hpp` |
| `load / enable / disable / unload` lifecycle (no-arg form) | Mod lifecycle callbacks | CONFIRMED | `preloader-android-0.2.3/include/pl/Mod.hpp` (concepts support both `load()` and `load(context)`); `full-cpp-mod` uses the no-arg form |
| `self.getLogger()` / `pl::log::Logger` | fmt-style logging, tagged by mod display name | CONFIRMED | `preloader-android-0.2.3/include/pl/Logger.hpp`, `pl/Mod.hpp` |
| `self.getModDir() / getConfigDir() / getResourceDir()` | Path accessors on `NativeMod` | CONFIRMED | `preloader-android-0.2.3/include/pl/Mod.hpp` |
| CMake + FetchContent build, linking the `preloader` target | Build system | CONFIRMED | `LeviLaunchroid-1.5.16/examples/full-cpp-mod/CMakeLists.txt` |
| `.levipack` zip format (`manifest.json` + `.so`, `type: preload-native`) | Package format Levi Launcher consumes | CONFIRMED | `LeviLaunchroid-1.5.16/docs/guide/developer.md`, `examples/full-cpp-mod/manifest.json` |
| Mod install path: `Android/media/org.levimc.launcher/minecraft/<profileId>/mods/` | Where Levi Launcher expects mods | CONFIRMED | `LeviLaunchroid-1.5.16/.../util/LauncherStorage.java`, `core/versions/GameVersion.java` |
| Mod Menu registration (`pl::modmenu`) | Adding a Mod Menu entry | **Not used** — out of scope for Phase 0 by design, not a placeholder | N/A |
| XMake build (used in an earlier version of this project) | Build system | **Not used here** — this version follows LeviLaunchroid's documented CMake path instead | See note at top of this README |
