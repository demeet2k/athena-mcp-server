cmake_minimum_required(VERSION 3.18 FATAL_ERROR)
project(polestargemm_cpp CXX)

find_package(Torch REQUIRED)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Torch sets important compiler flags (including ABI) via TORCH_CXX_FLAGS.
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${TORCH_CXX_FLAGS}")

add_executable(polestargemm_infer src/polestargemm_infer.cpp)
target_link_libraries(polestargemm_infer "${TORCH_LIBRARIES}")

add_executable(polestargemm_stress src/polestargemm_stress.cpp)
target_link_libraries(polestargemm_stress "${TORCH_LIBRARIES}")

# Recommended by PyTorch for Windows to copy DLLs post-build.
if (MSVC)
  file(GLOB TORCH_DLLS "${TORCH_INSTALL_PREFIX}/lib/*.dll")
  add_custom_command(TARGET polestargemm_infer
                     POST_BUILD
                     COMMAND ${CMAKE_COMMAND} -E copy_if_different
                     ${TORCH_DLLS}
                     $<TARGET_FILE_DIR:polestargemm_infer>)
  add_custom_command(TARGET polestargemm_stress
                     POST_BUILD
                     COMMAND ${CMAKE_COMMAND} -E copy_if_different
                     ${TORCH_DLLS}
                     $<TARGET_FILE_DIR:polestargemm_stress>)
endif()
