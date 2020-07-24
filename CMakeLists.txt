cmake_minimum_required( VERSION 3.5 )
project( icfpc2020 )
if (APPLE)
    set(CMAKE_C_COMPILER /usr/local/bin/gcc-9)
    set(CMAKE_CXX_COMPILER /usr/local/bin/g++-9)
endif (APPLE)
string( TOLOWER ${CMAKE_BUILD_TYPE} BUILD_TYPE_LOWERCASE )
set( CMAKE_CXX_STANDARD 14 )
set( CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_HOME_DIRECTORY}/${BUILD_TYPE_LOWERCASE}/build" )
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Werror -Wall -Wextra")
include_directories( PRIVATE "${PROJECT_SOURCE_DIR}/src" )
find_package( Threads )

SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-sign-compare -Wno-unused-but-set-variable")

add_library(stb STATIC ${PROJECT_SOURCE_DIR}/src/stb/wrapper.cpp)

file( GLOB_RECURSE APP_SOURCES RELATIVE "${PROJECT_SOURCE_DIR}" "${PROJECT_SOURCE_DIR}/src/app/*.cpp" )
add_executable( app ${APP_SOURCES} )
target_link_libraries( app ${CMAKE_THREAD_LIBS_INIT} stb )

find_package(OpenSSL REQUIRED)
file( GLOB_RECURSE APP2_SOURCES RELATIVE "${PROJECT_SOURCE_DIR}" "${PROJECT_SOURCE_DIR}/src/app2/*.cpp" )
add_executable( app2 ${APP2_SOURCES} )
target_link_libraries( app2 ${CMAKE_THREAD_LIBS_INIT} stb OpenSSL::SSL )

file( GLOB_RECURSE APP_SOURCES RELATIVE "${PROJECT_SOURCE_DIR}" "${PROJECT_SOURCE_DIR}/src/stb/sample/*.cpp" )
add_executable( stb_sample ${APP_SOURCES} )
target_link_libraries( stb_sample ${CMAKE_THREAD_LIBS_INIT} stb )

file( GLOB_RECURSE MFS_SOURCES RELATIVE "${PROJECT_SOURCE_DIR}" "${PROJECT_SOURCE_DIR}/src/mfs/*.cpp" )
add_executable( mfs ${MFS_SOURCES} )
target_link_libraries( mfs ${CMAKE_THREAD_LIBS_INIT} stb )

file( GLOB_RECURSE SOLVER_SOURCES RELATIVE "${PROJECT_SOURCE_DIR}" "${PROJECT_SOURCE_DIR}/src/solver/*.cpp" )
add_executable( solver ${SOLVER_SOURCES} )
target_link_libraries( solver ${CMAKE_THREAD_LIBS_INIT} stb )
