# Build file for the Phase 1 narrow-beam application.

cmake_minimum_required(VERSION 3.16...3.27)
project(ShieldingTwin)

# Find Geant4 package, activating UI and Visualization drivers
find_package(Geant4 REQUIRED ui_all vis_all)
include(${Geant4_USE_FILE})

# Locate all source and header files
file(GLOB sources ${PROJECT_SOURCE_DIR}/src/*.cc)
file(GLOB headers ${PROJECT_SOURCE_DIR}/include/*.hh)

# Create the executable
add_executable(shielding shielding.cc ${sources} ${headers})
target_link_libraries(shielding ${Geant4_LIBRARIES})
target_include_directories(shielding PRIVATE ${PROJECT_SOURCE_DIR}/include)

# Enforce Modern C++ Standard
set_target_properties(shielding PROPERTIES CXX_STANDARD 17)

# Copy the visualisation macros and the run driver next to the executable,
# since the driver invokes ./shielding and the macros are loaded by name.
foreach(_script macros/init_vis.mac macros/vis.mac run_phase1.py)
    get_filename_component(_name ${_script} NAME)
    configure_file(
        ${PROJECT_SOURCE_DIR}/${_script}
        ${PROJECT_BINARY_DIR}/${_name}
        COPYONLY
    )
endforeach()
