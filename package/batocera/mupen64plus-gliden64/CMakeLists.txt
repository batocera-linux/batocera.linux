cmake_minimum_required(VERSION 2.6)

project( GLideNHQ )

set(GLideNHQ_SOURCES
  TextureFilters.cpp
  TextureFilters_2xsai.cpp
  TextureFilters_hq2x.cpp
  TextureFilters_hq4x.cpp
  TextureFilters_xbrz.cpp
  TxCache.cpp
  TxDbg.cpp
  TxFilter.cpp
  TxFilterExport.cpp
  TxHiResCache.cpp
  TxImage.cpp
  TxQuantize.cpp
  TxReSample.cpp
  TxTexCache.cpp
  TxUtil.cpp
)

if(PANDORA OR BCMHOST)
  include_directories( ${CMAKE_CURRENT_SOURCE_DIR}/../osal )
else(PANDORA OR BCMHOST)
  include_directories( inc ${CMAKE_CURRENT_SOURCE_DIR}/../osal )
endif(PANDORA OR BCMHOST)
LINK_DIRECTORIES( ${CMAKE_CURRENT_SOURCE_DIR}/lib )

if(UNIX)
  add_definitions(
    -DNDEBUG
    -DOS_LINUX
  )
endif(UNIX)

if(WIN32)
  LINK_DIRECTORIES( ${CMAKE_CURRENT_SOURCE_DIR}/lib )
  add_definitions(
	-DWIN32
	-DOS_WINDOWS
	-D_CRT_SECURE_NO_WARNINGS
  )
endif(WIN32)

# Build type

if( NOT CMAKE_BUILD_TYPE)
	set( CMAKE_BUILD_TYPE Release)
endif( NOT CMAKE_BUILD_TYPE)

if( CMAKE_BUILD_TYPE STREQUAL "Debug")
	set( CMAKE_BUILD_TYPE Debug)
	set( DEBUG_BUILD TRUE)
	add_definitions(
		-DDEBUG
	)
endif( CMAKE_BUILD_TYPE STREQUAL "Debug")

find_package(OpenGL REQUIRED)
include_directories(${OpenGL_INCLUDE_DIRS})
link_directories(${OpenGL_LIBRARY_DIRS})
add_definitions(${OpenGL_DEFINITIONS})
if(NOT OPENGL_FOUND)
	message(ERROR " OPENGL not found!")
endif(NOT OPENGL_FOUND)

if("${CMAKE_CXX_COMPILER_ID}" STREQUAL "MSVC")
	add_definitions( -D__MSC__)
endif()

if("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU")
    SET(GCC_CPP11_COMPILE_FLAGS "-std=c++0x")
    if( NOT GHQCHK )
      SET( CMAKE_CXX_FLAGS  "${CMAKE_CXX_FLAGS} ${GCC_CPP11_COMPILE_FLAGS} -static -fPIC " )
      SET( CMAKE_C_FLAGS  "${CMAKE_C_FLAGS} -static -fPIC " )
    else( NOT GHQCHK )
      SET( CMAKE_CXX_FLAGS  "${CMAKE_CXX_FLAGS} ${GCC_CPP11_COMPILE_FLAGS}" )
    endif( NOT GHQCHK )
#SET( CMAKE_CXX_FLAGS  "${CMAKE_CXX_FLAGS} ${GCC_CPP11_COMPILE_FLAGS} " )
endif()

if( NOT GHQCHK )

    add_definitions( -DTXFILTER_LIB)

    if( CMAKE_BUILD_TYPE STREQUAL "Debug")
      add_library( GLideNHQd STATIC ${GLideNHQ_SOURCES})

      set_target_properties(GLideNHQd PROPERTIES LINK_SEARCH_START_STATIC 1)
      set_target_properties(GLideNHQd PROPERTIES LINK_SEARCH_END_STATIC 1)

      if(BCMHOST)
        FIND_PACKAGE( ZLIB REQUIRED )
        FIND_PACKAGE( PNG REQUIRED )
        target_link_libraries(GLideNHQd
          ${PNG_LIBRARIES}
          ${ZLIB_LIBRARIES}
          osald
        )
      else(BCMHOST)
        target_link_libraries(GLideNHQd PRIVATE
          ${CMAKE_CURRENT_SOURCE_DIR}/lib/libpng.a
          ${CMAKE_CURRENT_SOURCE_DIR}/lib/libz.a
          dl
          osald
        )
      endif(BCMHOST)
    endif( CMAKE_BUILD_TYPE STREQUAL "Debug")

    if( CMAKE_BUILD_TYPE STREQUAL "Release")
      add_library( GLideNHQ STATIC ${GLideNHQ_SOURCES})

#      set_target_properties(GLideNHQ PROPERTIES LINK_SEARCH_START_STATIC 1)
#      set_target_properties(GLideNHQ PROPERTIES LINK_SEARCH_END_STATIC 1)
#      set(CMAKE_FIND_LIBRARY_SUFFIXES ".a")
#      find_library(PNGLIB libpng.a)

      if(PANDORA)
        target_link_libraries(GLideNHQ PRIVATE
          /mnt/utmp/codeblocks/usr/lib/libpng.a
          /mnt/utmp/codeblocks/usr/lib/libz.a
          osal
        )
      elseif(BCMHOST)
        FIND_PACKAGE( ZLIB REQUIRED )
        FIND_PACKAGE( PNG REQUIRED )
        target_link_libraries(GLideNHQ
          ${PNG_LIBRARIES}
          ${ZLIB_LIBRARIES}
          osal
        )
      else(PANDORA)
        target_link_libraries(GLideNHQ PRIVATE
          ${CMAKE_CURRENT_SOURCE_DIR}/lib/libpng.a
          ${CMAKE_CURRENT_SOURCE_DIR}/lib/libz.a
          dl
          osal
        )
      endif(PANDORA)
    endif( CMAKE_BUILD_TYPE STREQUAL "Release")
else( NOT GHQCHK )
    add_definitions(-DGHQCHK)

    add_library( ghqchk SHARED ${GLideNHQ_SOURCES})

    SET_TARGET_PROPERTIES(
      ghqchk
      PROPERTIES
      LINKER_LANGUAGE CXX # Or else we get an error message, because cmake can't figure out from the ".o"-suffix that it is a C-linker we need.
      PREFIX ""
      LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/plugin
      )

    if( CMAKE_BUILD_TYPE STREQUAL "Debug")
    target_link_libraries(ghqchk ${OPENGL_LIBRARIES} png z )
    endif( CMAKE_BUILD_TYPE STREQUAL "Debug")

    if( CMAKE_BUILD_TYPE STREQUAL "Release")
    target_link_libraries(ghqchk ${OPENGL_LIBRARIES} png z )
    endif( CMAKE_BUILD_TYPE STREQUAL "Release")
endif( NOT GHQCHK )

