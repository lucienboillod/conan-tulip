#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools, AutoToolsBuildEnvironment
import os
import sys

class TulipConan(ConanFile):

    name = "Tulip"
    version = "master"
    description = "Conan.io package for Qt - build of %s" % (version)
    url = "https://github.com/lucienboillod/conan-tulip"
    homepage = "http://tulip.labri.fr"
    license = "Tulip is free software under the terms of GNU Lesser General Public License."
    author = "Lucien Boillod <lucienboillod@gmail.com>"
    settings = "os", "compiler", "build_type", "arch"
    export_sources = ["CmakeLists.txt"]
    generators = "cmake"
    options = {
        "ccache": [True, False],
        "core_only": [True, False],
        "doc": [True, False],
        "fixup_bundle": [True, False],
        "multithreading": [True, False],
        "python_components": [True, False],
        "python_site": [True, False],
        "python_wheels": [True, False],
        "qhull": [True, False],
        "qt5": [True, False],
        "tests": [True, False]
    }
    default_options = "shared=False", "libpng:shared=False", "freetype:with_png=False",\
                       "zlib:shared=False", "freetype:shared=False", "freetype:with_zlib=False", \
                       "glew:shared=True", "Qt:opengl=desktop"
    source_dir = "tulip"
    short_paths = True
    build_policy = "missing"
    keep_imports = True

    def requirements(self):
        self.requires("zlib/1.2.11@conan/stable")
        self.requires("libjpeg/9b@bincrafters/stable")
        self.requires("libpng/1.6.34@bincrafters/stable")
        self.requires("gtest/1.8.0@bincrafters/stable")
        self.requires("freetype/2.9.0@bincrafters/stable")
        self.requires("glew/2.1.0@bincrafters/stable")
        self.requires("Qt/5.11.0@bincrafters/stable")

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

    def imports(self):
        self.copy(pattern="*.dll", dst="bin")
        self.copy(pattern="*.dylib", dst="lib")
        self.copy(pattern="*.so*", dst="lib")

    def build(self):
        env_build = AutoToolsBuildEnvironment(self)
        env_vars = env_build.vars.copy()
        with tools.chdir(os.path.join(self.source_folder, self.source_dir)):
            with tools.environment_append(env_vars):
                cmake = CMake(self)
                cmake.verbose = True
                if self.options.ccache:
                    cmake.definitions["TULIP_USE_CCACHE"] = "ON"
                if self.options.core_only:
                    cmake.definitions["TULIP_BUILD_CORE_ONLY"] = "ON"
                if self.options.doc:
                    cmake.definitions["TULIP_BUILD_DOC"] = "ON"
                if not self.options.fixup_bundle:
                    cmake.definitions["TULIP_FIXUP_BUNDLE"] = "OFF"
                if self.options.multithreading:
                    cmake.definitions["TULIP_ENABLE_MULTI_THREADING"] = "ON"
                if self.options.python_components:
                    cmake.definitions["TULIP_BUILD_PYTHON_COMPONENTS"] = "ON"
                if self.options.python_site:
                    cmake.definitions["TULIP_PYTHON_SITE_INSTALL"] = "ON"
                if self.options.python_wheels:
                    cmake.defintiions["TULIP_ACTIVATE_PYTHON_WHEELS_TARGETS"] = "ON"
                if self.options.qhull:
                    cmake.definitions["TULIP_USE_THIRDPARTY_QHULL"] = "ON"
                if self.options.qt5:
                    cmake.definitions["TULIP_USE_QT5"] = "ON"
                if self.options.tests:
                    cmake.definitions["TULIP_BUILD_TESTS"] = "OFF"
                cmake.configure(source_dir=os.path.join(self.source_folder, self.source_dir))
                cmake.build()
                cmake.install()

    def package(self):
        self.copy(pattern="*.dll", dst="bin", src="bin", keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", src="lib", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", src="lib", keep_path=False)

    def package_info(self):
        self.env_info.LD_LIBRARY_PATH.append(os.path.join(self.package_folder, "lib"))
        self.env_info.DYLD_LIBRARY_PATH.append(os.path.join(self.package_folder, "lib"))
        self.cpp_info.libs = tools.collect_libs(self)
