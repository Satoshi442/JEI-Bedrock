cmake_minimum_required(VERSION 3.22)

project(jeibedrock LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(NOT ANDROID)
    message(FATAL_ERROR
            "JEIBedrock is an Android native mod. Build it with an Android "
            "NDK toolchain (-DCMAKE_TOOLCHAIN_FILE=<ndk>/build/cmake/android.toolchain.cmake).")
endif()

# CONFIRMED: this FetchContent + PRELOADER_ANDROID_ROOT pattern matches
# LeviLaunchroid's own examples/full-cpp-mod/CMakeLists.txt exactly.
# PRELOADER_ANDROID_ROOT must point at a preloader-android checkout
# (the one confirmed against: LiteLDev/preloader-android, tag 0.2.3).
set(PRELOADER_ANDROID_ROOT
    "${CMAKE_CURRENT_LIST_DIR}/third_party/preloader-android"
    CACHE PATH "Path to a LiteLDev/preloader-android checkout")

if(NOT EXISTS "${PRELOADER_ANDROID_ROOT}/include/pl/Mod.hpp")
    message(FATAL_ERROR
            "PRELOADER_ANDROID_ROOT must point to a preloader-android checkout. "
            "Missing: ${PRELOADER_ANDROID_ROOT}/include/pl/Mod.hpp\n"
            "Either clone https://github.com/LiteLDev/preloader-android into "
            "${PRELOADER_ANDROID_ROOT}, or pass -DPRELOADER_ANDROID_ROOT=<path> "
            "to point at an existing checkout.")
endif()

include(FetchContent)

# Same dependency set preloader-android itself declares. Guarded with
# NOT TARGET so this is safe whether or not the preloader subdirectory
# below has already pulled them in.
if(NOT TARGET nlohmann_json::nlohmann_json)
    FetchContent_Declare(
        nlohmann_json
        GIT_REPOSITORY https://github.com/nlohmann/json.git
        GIT_TAG v3.11.3)
    FetchContent_MakeAvailable(nlohmann_json)
endif()

if(NOT TARGET Boost::pfr)
    FetchContent_Declare(
        boost_pfr
        GIT_REPOSITORY https://github.com/boostorg/pfr.git
        GIT_TAG boost-1.88.0)
    FetchContent_MakeAvailable(boost_pfr)
endif()

if(NOT TARGET magic_enum::magic_enum)
    FetchContent_Declare(
        magic_enum
        GIT_REPOSITORY https://github.com/Neargye/magic_enum.git
        GIT_TAG v0.9.7)
    FetchContent_MakeAvailable(magic_enum)
endif()

if(NOT TARGET fmt::fmt)
    FetchContent_Declare(
        fmt
        GIT_REPOSITORY https://github.com/fmtlib/fmt.git
        GIT_TAG 11.2.0)
    set(FMT_DOC OFF CACHE BOOL "Disable fmt docs" FORCE)
    set(FMT_TEST OFF CACHE BOOL "Disable fmt tests" FORCE)
    set(FMT_INSTALL OFF CACHE BOOL "Disable fmt install rules" FORCE)
    FetchContent_MakeAvailable(fmt)
endif()

# Builds the actual preloader shared library + GlossHook static lib link,
# giving us the `preloader` CMake target to link against.
if(NOT TARGET preloader)
    add_subdirectory("${PRELOADER_ANDROID_ROOT}" "${CMAKE_BINARY_DIR}/_preloader_android")
endif()

if(ANDROID_ABI)
    set(JEIBEDROCK_OUTPUT_ABI "${ANDROID_ABI}")
else()
    set(JEIBEDROCK_OUTPUT_ABI "android")
endif()
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/out/${JEIBEDROCK_OUTPUT_ABI}")

find_library(JEIBEDROCK_LOG_LIB log)

add_library(JEIBedrock SHARED
    src/JEIBedrockMod.cpp)
set_target_properties(JEIBedrock PROPERTIES OUTPUT_NAME "jeibedrock")

target_include_directories(JEIBedrock PRIVATE
    "${CMAKE_CURRENT_LIST_DIR}/include")

target_link_libraries(JEIBedrock PRIVATE
    preloader
    nlohmann_json::nlohmann_json
    Boost::pfr
    magic_enum::magic_enum
    fmt::fmt)

if(JEIBEDROCK_LOG_LIB)
    target_link_libraries(JEIBedrock PRIVATE "${JEIBEDROCK_LOG_LIB}")
endif()

target_compile_options(JEIBedrock PRIVATE
    $<$<COMPILE_LANG_AND_ID:CXX,Clang,GNU>:-fvisibility=hidden -fvisibility-inlines-hidden>)

# Packages manifest.json + the .so (+ icon, if present) into a .levipack
# zip, matching the format confirmed from GlobalVoiceChat's build and
# LeviLaunchroid's own manifest.json documentation.
find_package(Python3 COMPONENTS Interpreter)
if(Python3_FOUND)
    add_custom_command(TARGET JEIBedrock POST_BUILD
        COMMAND "${Python3_EXECUTABLE}"
                "${CMAKE_CURRENT_LIST_DIR}/scripts/package_levipack.py"
                --library "$<TARGET_FILE:JEIBedrock>"
                --manifest "${CMAKE_CURRENT_LIST_DIR}/manifest.json"
                --output "$<TARGET_FILE_DIR:JEIBedrock>/JEIBedrock.levipack"
        COMMENT "Packaging JEIBedrock.levipack")
else()
    message(WARNING "Python3 not found - .levipack packaging step will be skipped. "
                     "Run scripts/package_levipack.py manually after building.")
endif()
