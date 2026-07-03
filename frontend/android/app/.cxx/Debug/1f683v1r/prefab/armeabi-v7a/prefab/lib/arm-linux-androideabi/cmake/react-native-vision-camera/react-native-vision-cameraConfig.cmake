if(NOT TARGET react-native-vision-camera::VisionCamera)
add_library(react-native-vision-camera::VisionCamera SHARED IMPORTED)
set_target_properties(react-native-vision-camera::VisionCamera PROPERTIES
    IMPORTED_LOCATION "/home/tanluc/workspace/physical-ai/frontend/node_modules/react-native-vision-camera/android/build/intermediates/cxx/Debug/4w4p2e54/obj/armeabi-v7a/libVisionCamera.so"
    INTERFACE_INCLUDE_DIRECTORIES "/home/tanluc/workspace/physical-ai/frontend/node_modules/react-native-vision-camera/android/build/headers/visioncamera"
    INTERFACE_LINK_LIBRARIES ""
)
endif()

