This tells Linux how to stitch all your .cc and .hh files together into the ./shielding app.

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

# Enforce Modern C++ Standard
set_target_properties(shielding PROPERTIES CXX_STANDARD 17)

# Copy the visualization macros to the build folder automatically
file(COPY init_vis.mac vis.mac DESTINATION ${PROJECT_BINARY_DIR})
