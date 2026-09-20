cmake_minimum_required(VERSION 3.16)

project(ZenohExample C)

set(ZENOH_C_ROOT "/usr/local" CACHE PATH "zenoh-c installation prefix")
option(HAKO_ZENOH_TOPOLOGY_AGENT "Attach the optional Hakoniwa topology observer" OFF)
set(HAKO_ZENOH_TOPOLOGY_AGENT_ROOT "/usr/local" CACHE PATH "Topology agent installation prefix")

find_library(ZENOH_C_LIBRARY NAMES zenohc NO_DEFAULT_PATH HINTS ${ZENOH_C_ROOT}/lib)
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
    PRIVATE ${ZENOH_C_ROOT}/include
    PRIVATE ../../zenoh-c-install/include/
)

add_executable(sub sub.c)
target_link_libraries(sub PRIVATE ${ZENOH_C_LIBRARY})
target_include_directories(
    sub 
    PRIVATE /usr/local/include
    PRIVATE ${ZENOH_C_ROOT}/include
    PRIVATE ../../zenoh-c-install/include/
)

if(HAKO_ZENOH_TOPOLOGY_AGENT)
  find_path(HAKO_ZENOH_TOPOLOGY_AGENT_INCLUDE_DIR
    NAMES hako_zenoh_topology_agent.h
    REQUIRED
    NO_DEFAULT_PATH
    HINTS ${HAKO_ZENOH_TOPOLOGY_AGENT_ROOT}/include)
  find_library(HAKO_ZENOH_TOPOLOGY_AGENT_LIBRARY
    NAMES hako_zenoh_topology_agent
    REQUIRED
    NO_DEFAULT_PATH
    HINTS ${HAKO_ZENOH_TOPOLOGY_AGENT_ROOT}/lib)
  foreach(target pub sub)
    target_compile_definitions(${target} PRIVATE HAKO_ZENOH_TOPOLOGY_AGENT)
    target_include_directories(${target} PRIVATE ${HAKO_ZENOH_TOPOLOGY_AGENT_INCLUDE_DIR})
    target_link_libraries(${target} PRIVATE ${HAKO_ZENOH_TOPOLOGY_AGENT_LIBRARY})
  endforeach()
endif()
