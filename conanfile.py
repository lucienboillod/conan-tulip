#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os
import sys

class TulipConan(ConanFile):
    name = "Tulip"
    version = "94f76ffee6c"
    description = "build of %s-%s" % (name, version)
    license = "Tulip is free software under the terms of GNU Lesser General Public License."
    url = "https://github.com/lucienboillod/conan-tulip"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False", "freetype:shared=False"
    repo = "https://github.com/Tulip-Dev/tulip.git"
    source_dir = "tulip"
    export_sources = ["CmakeLists.txt"]
    generators = "cmake"
    short_paths = True

    def requirements(self):
        self.requires("zlib/1.2.11@conan/stable")
        self.requires("libjpeg/9b@bincrafters/stable")
        self.requires("libpng/1.6.34@bincrafters/stable")
        self.requires("gtest/1.8.0@bincrafters/stable")
        self.requires("freetype/2.9.0@lboillod/testing")
        self.requires("glew/2.1.0@dimi309/stable")
        self.requires("Qt/5.9.0@lboillod/testing")

    def source(self):
        cloned_sources = os.path.join(self.source_folder, self.source_dir)
        self.run("git clone {repo} {dir}".format(repo=self.repo, dir=cloned_sources))
        with tools.chdir(cloned_sources):
            self.run("git checkout {commit}".format(commit=self.version))
        os.rename(cloned_sources, "tulip")
        tools.replace_in_file("tulip/CMakeLists.txt", "PROJECT(tulip)", """PROJECT(tulip)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()""")


    def configure(self):
        pass

    def build(self):
        with tools.chdir(os.path.join(self.source_folder, self.source_dir)):
            cmake = CMake(self)
            cmake.verbose = True
            cmake.definitions["TULIP_USE_THIRDPARTY_QHULL"] = "OFF"
            cmake.definitions["TULIP_ENABLE_OPENMP"] = "OFF"
            cmake.definitions["TULIP_BUILD_PYTHON_COMPONENTS"] = "OFF"
            cmake.definitions["TULIP_BUILD_DOC"] = "OFF"
            cmake.definitions["TULIP_USE_QT5"] = "ON"
            cmake.definitions["TULIP_FIXUP_BUNDLE"] = "ON"
            cmake.configure(source_dir=os.path.join(self.source_folder, self.source_dir))
            cmake.build()
            cmake.install()

    def package(self):
        pass

    def package_info(self):
        self.cpp_info.libs = ["tulip"]
