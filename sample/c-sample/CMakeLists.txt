cmake_minimum_required(VERSION 3.16)

project(ZenohExample C)

set(CMAKE_FIND_ROOT_PATH /usr/local/lib)

find_library(ZENOH_C_LIBRARY NAMES zenohc NO_DEFAULT_PATH HINTS ${CMAKE_FIND_ROOT_PATH})
if(NOT ZENOH_C_LIBRARY)
  message(FATAL_ERROR "ZENOH_C_LIBRARY_PATH environment variable is not set.")
endif()
message(STATUS "ZENOH_C_LIBRARY_PATH: " ${ZENOH_C_LIBRARY})

add_executable(pub pub.c)
target_link_libraries(
    pub 
    PRIVATE ${ZENOH_C_LIBRARY}
)
target_include_directories(
    pub 
    PRIVATE /usr/local/include
    PRIVATE ../../zenoh-c-install/include/
)

add_executable(sub sub.c)
target_link_libraries(sub ${ZENOH_C_LIBRARY})
target_include_directories(
    sub 
    PRIVATE /usr/local/include
    PRIVATE ../../zenoh-c-install/include/
)
