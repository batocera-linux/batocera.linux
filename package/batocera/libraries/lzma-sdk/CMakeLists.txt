cmake_minimum_required(VERSION 3.16)
project(lzmasdk C)

# The 7-Zip LZMA SDK ships as raw C with no build system. Build the subset
# needed to open and decode .7z archives into a static library, and export a
# find_package(lzmasdk) config providing lzmasdk::lzmasdk.

add_library(lzmasdk STATIC
    C/7zAlloc.c
    C/7zArcIn.c
    C/7zBuf.c
    C/7zCrc.c
    C/7zCrcOpt.c
    C/7zDec.c
    C/7zFile.c
    C/7zStream.c
    C/Bcj2.c
    C/CpuArch.c
    C/Lzma2Dec.c
    C/LzmaDec.c
)
add_library(lzmasdk::lzmasdk ALIAS lzmasdk)

# No Delta/BCJ/branch-conversion filters: .7z ROM sets do not use them, and
# leaving them out drops the corresponding code from 7zDec.c.
target_compile_definitions(lzmasdk PUBLIC Z7_NO_METHODS_FILTERS)
set_target_properties(lzmasdk PROPERTIES C_STANDARD 11 POSITION_INDEPENDENT_CODE ON)

target_include_directories(lzmasdk PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/C>
    $<INSTALL_INTERFACE:include/lzmasdk>
)

install(TARGETS lzmasdk EXPORT lzmasdk-targets ARCHIVE DESTINATION lib)

# Install every SDK header: the reader's translation units include many of
# them transitively, so shipping the full set avoids chasing dependencies.
file(GLOB LZMASDK_HEADERS "${CMAKE_CURRENT_SOURCE_DIR}/C/*.h")
install(FILES ${LZMASDK_HEADERS} DESTINATION include/lzmasdk)

include(CMakePackageConfigHelpers)
configure_package_config_file(
    lzmasdk-config.cmake.in
    "${CMAKE_CURRENT_BINARY_DIR}/lzmasdk-config.cmake"
    INSTALL_DESTINATION lib/cmake/lzmasdk)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/lzmasdk-config.cmake"
    DESTINATION lib/cmake/lzmasdk)
install(EXPORT lzmasdk-targets
    NAMESPACE lzmasdk::
    FILE lzmasdk-targets.cmake
    DESTINATION lib/cmake/lzmasdk)
