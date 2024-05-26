IF(MSVC)
   cmake_minimum_required(VERSION 3.14)
else()
   cmake_minimum_required(VERSION 3.10)
endif()

project(Sugarbox)

# Find includes in the build directories
set(CMAKE_INCLUDE_CURRENT_DIR ON)

set(CMAKE_CXX_STANDARD 17)

# Turn on automatic invocation of the MOC
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

set (SUGARBOX_VERSION "2.0.1" CACHE STRING "Version to build" FORCE)

MESSAGE (STATUS "Version :" ${SUGARBOX_VERSION})

set(CompilerFlags
        CMAKE_CXX_FLAGS
        CMAKE_CXX_FLAGS_DEBUG
        CMAKE_CXX_FLAGS_RELEASE
        CMAKE_C_FLAGS
        CMAKE_C_FLAGS_DEBUG
        CMAKE_C_FLAGS_RELEASE
        CMAKE_CXX_FLAGS_RELWITHDEBINFO
		  _SILENCE_TR1_NAMESPACE_DEPRECATION_WARNING 
        
        )

find_package(Qt6 COMPONENTS Widgets WebSockets OpenGLWidgets REQUIRED)
qt6_add_resources(QRCS resources.qrc)

if(Qt6_FOUND AND WIN32 AND TARGET Qt6::qmake AND NOT TARGET Qt6::windeployqt)
    get_target_property(_qt6_qmake_location Qt6::qmake IMPORTED_LOCATION)

    execute_process(
        COMMAND "${_qt6_qmake_location}" -query QT_INSTALL_PREFIX
        RESULT_VARIABLE return_code
        OUTPUT_VARIABLE qt6_install_prefix
        OUTPUT_STRIP_TRAILING_WHITESPACE
    )

    set(imported_location "${qt6_install_prefix}/bin/windeployqt.exe")

    if(EXISTS ${imported_location})
        add_executable(Qt6::windeployqt IMPORTED)

        set_target_properties(Qt6::windeployqt PROPERTIES
            IMPORTED_LOCATION ${imported_location}
        )
    endif()
endif()

get_target_property(_qmake_executable Qt6::qmake IMPORTED_LOCATION)
get_filename_component(_qt_bin_dir "${_qmake_executable}" DIRECTORY)
find_program(WINDEPLOYQT_EXECUTABLE windeployqt HINTS "${_qt_bin_dir}")

function(windeployqt target)

    # POST_BUILD step
    # - after build, we have a bin/lib for analyzing qt dependencies
    # - we run windeployqt on target and deploy Qt libs

    add_custom_command(TARGET ${target} POST_BUILD
        COMMAND "${_qt_bin_dir}/windeployqt.exe"         
                \"$<TARGET_FILE:${target}>\"
        COMMENT "Deploying Qt libraries using windeployqt for compilation target '${target}' ..."
    )

endfunction()

file(GLOB HEADERS
    *.h
)

file(GLOB SRCS
    *.cpp
)

file(GLOB RES
   ${CMAKE_CURRENT_SOURCE_DIR}/Resources/*.*
)
          
set (HEADERS 
   ${HEADERS}
)
set (SRCS 
      ${SRCS}
   )

set ( UIS
 SugarboxApp.ui
 DebugDialog.ui
)


source_group("Resources" FILES ${RES} )

if(UNIX)
    if (APPLE)
        add_definitions(-DAPPLE)
    else()
        add_definitions(-DLINUX)
    endif()
    add_definitions(-DUNIX)
elseif(WIN32)
    add_definitions(-DWIN32)
    add_definitions(-DMINGW32)
endif()

IF(MSVC)
   set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} /SUBSYSTEM:WINDOWS")
   if (USE_SHARED_CRT)
   else()
      foreach(CompilerFlag ${CompilerFlags})
        string(REPLACE "/MD" "/MT" ${CompilerFlag} "${${CompilerFlag}}")
      endforeach()
   endif()
ENDIF(MSVC)
if(CMAKE_COMPILER_IS_GNUCC)
   set ( LIB_EXT pthread stdc++fs)
endif()

if(CMAKE_CXX_COMPILER_ID MATCHES "Clang")
   set ( LIBZA libz.a pthread stdc++fs)
endif()

IF(WIN32)
   set (OPENGL_LINK opengl32)
endif()


add_executable(Sugarbox ${SRCS} ${HEADERS} ${QRCS} ${UIS} ${RES}  )

target_compile_definitions(Sugarbox PRIVATE SUGARBOX_VERSION=${SUGARBOX_VERSION} )
set_property(TARGET Sugarbox PROPERTY CXX_STANDARD 17)

set ( CMAKE_RUNTIME_OUTPUT_DIRECTORY_DEBUG ${CMAKE_INSTALL_BINDIR})
set ( SUGARBOX_OUTPUT_DEBUG ${CMAKE_RUNTIME_OUTPUT_DIRECTORY_DEBUG})

# Link test executable against gtest & gtest_main
target_link_libraries(Sugarbox CPCCoreEmu zlibstatic OpenAL Qt6::Core Qt6::Widgets Qt6::WebSockets Qt6::OpenGLWidgets ${LIB_EXT})
set_property(TARGET Sugarbox PROPERTY VS_DEBUGGER_WORKING_DIRECTORY "${CMAKE_INSTALL_BINDIR}")

if (APPLE)
  target_link_libraries(Sugarbox "-framework OpenGL")
endif()

# Ready-to-use configuration
install ( TARGETS Sugarbox RUNTIME DESTINATION .)
install ( FILES "${PROJECT_SOURCE_DIR}/Sugarbox.ini" DESTINATION .) 
install ( DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/ROM" DESTINATION .) 
install ( DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/CART" DESTINATION .) 
install ( DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/CONF" DESTINATION .) 
install ( DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/Resources" DESTINATION .) 


# MSVC CPACK Qt dlls
IF(MSVC)
   install (CODE "
      set (_outpath ${CMAKE_INSTALL_PREFIX})
      set (_file ${CMAKE_CURRENT_BINARY_DIR}/$<$<CONFIG:debug>:Debug>$<$<CONFIG:release>:Release>$<$<CONFIG:RelWithDebInfo>:RelWithDebInfo>$<$<CONFIG:MinSizeRel>:MinSizeRel>/Sugarbox.exe)
      set ( rel_or_debug  $<$<CONFIG:debug>:--debug>$<$<CONFIG:release>:--release>$<$<CONFIG:RelWithDebInfo>:--release>$<$<CONFIG:MinSizeRel>:--release> )
      execute_process(
              COMMAND \"${CMAKE_COMMAND}\" -E
                  env PATH=\"${_qt_bin_dir}\" \"${WINDEPLOYQT_EXECUTABLE}\"
                      --dry-run
                      --no-compiler-runtime
                      --list mapping
                      \${rel_or_debug}
                      \${_file}
               OUTPUT_VARIABLE _output
               OUTPUT_STRIP_TRAILING_WHITESPACE
          )
      separate_arguments(_files WINDOWS_COMMAND \${_output})
      while(_files)
         list(GET _files 0 _src)
         list(GET _files 1 _dest)
         execute_process(
            COMMAND \"${CMAKE_COMMAND}\" -E
            copy   \${_src} \${CMAKE_INSTALL_PREFIX}/\${_dest}\
         )
         list(REMOVE_AT _files 0 1)
      endwhile()
   "  )
endif()

# CPACK
set(CPACK_GENERATOR "TGZ;ZIP")
set(CPACK_PACKAGE_NAME "Sugarbox")
set(CPACK_PACKAGE_VENDOR "Thomas GUILLEMIN")
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "Sugarbox - An Amstrad CPC/CPC+/GX4000 Emulator")
set(CPACK_PACKAGE_VERSION ${SUGARBOX_VERSION} )
set(CPACK_PACKAGE_INSTALL_DIRECTORY "Sugarbox")

INCLUDE(CPack)
