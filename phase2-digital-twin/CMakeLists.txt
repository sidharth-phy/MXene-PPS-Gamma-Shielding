cmake_minimum_required(VERSION 3.16)
project(ShieldingExactTwin)

find_package(Geant4 REQUIRED ui_all vis_all)
include(${Geant4_USE_FILE})

file(GLOB sources ${PROJECT_SOURCE_DIR}/src/*.cc)
add_executable(shielding shielding.cc ${sources})
target_link_libraries(shielding ${Geant4_LIBRARIES})
target_include_directories(shielding PRIVATE ${PROJECT_SOURCE_DIR}/include)
set_target_properties(shielding PROPERTIES CXX_STANDARD 17)

# ── Copy runtime files to build directory ──────────────────────────────────
# These files must be in the SAME directory as the shielding executable
# because:
#   - run_phase2.py / quick_check_phase2.py call ./shielding (current dir)
#   - Output CSV files are written relative to CWD (the build directory)
#   - Macro files (run.mac, vis.mac) are loaded relative to CWD
foreach(_script
        macros/run.mac
        macros/vis.mac
        macros/init_vis.mac
        run_phase2.py
        quick_check_phase2.py
        )
    get_filename_component(_name ${_script} NAME)
    configure_file(
        ${PROJECT_SOURCE_DIR}/${_script}
        ${PROJECT_BINARY_DIR}/${_name}
        COPYONLY
    )
endforeach()
