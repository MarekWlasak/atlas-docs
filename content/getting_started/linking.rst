
Linking Atlas into your project
###############################

:breadcrumb: {filename}/getting_started.rst Getting started

.. role:: green
    :class: m-text m-success

.. role:: warn
    :class: m-text m-warning

.. contents::
  :class: m-block m-default

Guide on how to find and link Atlas into your project

Using CMake
===========

As Atlas is itself built with the CMake build system, it is very convenient to include Atlas
in your own CMake project.

Finding Atlas
-------------

There are two approaches available, with tradeoffs for each.

- Using a pre-installed Atlas
- Bundling Atlas as a subproject

Using a pre-installed Atlas
`````````````````````````````
This is the recommended option if Atlas is not part of your developments,
and rather used as a stable third-party library. You then don't need to
add the overhead of Atlas compilation to each new build of your project.
On the other hand, it is less convenient to try out different build types,
compilers or other build options.

To aid `CMake` in finding Atlas, you can export ``atlas_ROOT`` in the environment

.. code :: bash

  export atlas_ROOT=<path-to-atlas-install-prefix>

Within your own CMake project, then simply add

.. code:: cmake

    find_package( atlas REQUIRED )

The ``REQUIRED`` keyword is optional and causes CMake to exit with error if `atlas` was not found.

When atlas is found, the available atlas CMake :green:`targets` will be defined:

- ``atlas``  -- The core C++ library
- ``atlas_f`` -- The Fortran interface library :warn:`(only available if the atlas FORTRAN feature was enabled)`

Additionally also following CMake :green:`variables` will be defined:

- ``atlas_FOUND`` -- `True` if atlas was found correctly
- ``atlas_HAVE_FORTRAN`` -- `True` if the atlas FORTRAN feature was enabled
- ``atlas_HAVE_MPI`` -- `True` if atlas is capable to run in a MPI parallel context
- ``atlas_HAVE_TESSELATION`` -- `True` if the atlas TESSELATION feature was enabled
- ``atlas_HAVE_TRANS`` -- `True` if the atlas TRANS feature was enabled

.. block-info:: Tip

    To ensure that atlas was compiled with the FORTRAN feature enabled during the ``find_package()`` call, instead it is possible to call

    .. code:: cmake
    
        find_package( atlas REQUIRED COMPONENTS FORTRAN )

Bundling Atlas as a subproject
``````````````````````````````

A self-contained alternative to a shared instance of the libraries,
is to add atlas and its required depenencies directly into your project (as Git submodules,
bundling downloaded archives etc.), and then to use CMake's ``add_subdirectory()``
command to compile them on demand.
With this approach, :green:`you don't need to
care about manually installing atlas`, fckit, eckit, and ecbuild;
however the usual tradeoffs when bundling code apply — slower full rebuilds,
IDEs having more to parse etc. 
Conveniently, in this case, build-time options can be set
before calling add_subdirectory(). Note that it's necessary to use
the ``CACHE ... FORCE`` arguments in order to have the options set properly.

.. code:: cmake

    # Set features required for Atlas
    set( ENABLE_MPI         ON CACHE BOOL "" FORCE )
    set( ENABLE_TESSELATION ON CACHE BOOL "" FORCE )

    # Add Atlas and its dependencies as subprojects
    add_subdirectory( ecbuild )
    add_subdirectory( eckit )
    add_subdirectory( fckit )
    add_subdirectory( atlas )

    find_package( atlas REQUIRED )

.. note-warning::

    Projects that are built like this with subprojects should be treated as standalone
    bundles. In other words, if they are deployed, only its executables should be used,
    whereas its libraries should not be linked to, unless you are absolutely sure what you're
    doing.

Linking your CMake library or executable with Atlas
---------------------------------------------------

To use the C++ API of Atlas all you need to do to link
the ``atlas`` target to your target is using the ``target_link_libraries()``:

.. code:: cmake

    add_library( library_using_atlas
        source_using_atlas_1.cc
        source_using_atlas_2.cc )
    
    target_link_libraries( library_using_atlas PUBLIC atlas )

Atlas include directories, compile definitions, and required C++ language
flags (e.g. ``-std=c++11``) are automatically added to your target.

Complete CMake example
----------------------

We now show a full example of a mixed C++ / Fortran project, describing the
two approaches in finding Atlas. The project contains two executables that simply
print "Hello from atlas" implemented respectively in C++ and Fortran.

In the case of pre-installed Atlas the project's directory structure should be::

    project/
      ├── CMakeLists.txt
      └── src/
            ├── hello_atlas.cc
            └── hello_atlas_f.F90

In the case of bundling Atlas dependencies as subprojects, the project's directory structure should instead be::

    project/
      ├── CMakeLists.txt
      ├── src/
      │     ├── hello_atlas.cc
      │     └── hello_atlas_f.F90
      ├── ecbuild/
      ├── eckit/
      ├── fckit/
      └── atlas/

The bundled dependencies can be e.g. added as git submodules, symbolic links,
or downloaded/added manually/automatically.

The content of the ``CMakeLists.txt`` at the project root contains

.. include:: project_bundle_atlas/CMakeLists.txt
  :code: cmake

Inspection of this ``CMakeLists.txt`` file shows that for this project we created
a ``BUNDLE`` option to toggle the behaviour of either bundling the dependencies or not.
To enable the bundling, the argument ``-DBUNDLE=ON`` needs to be passed
on the cmake configuration command line.

- The content of ``hello_atlas.cc`` is:

.. include:: project_bundle_atlas/src/hello-atlas.cc
  :code: c++

- The content of ``hello_atlas_f.cc`` is:

.. include:: project_bundle_atlas/src/hello-atlas_f.F90
  :code: fortran
  
Creating a new project with ecbuild
-----------------------------------

When creating a new project from scratch, please consider to use ``ecbuild``, which is
also used by atlas. It extends CMake with macros that make the experience easier.
An example project ``CMakeLists.txt`` file would then be:

.. include:: ecbuild_project_atlas/CMakeLists.txt
  :code: cmake

The strange entry ``PUBLIC_INCLUDES $<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/src>`` means that
the directory ``src`` within the project's source dir of ``mylib`` is used as include directory during
compilation, but also propagated automatically (because ``PUBLIC``) when compiling other
targets (such as ``myexe`` further) that link with mylib which is not yet installed.
The ``INSTALL_INTERFACE`` is used when ``myproject`` is installed, and downstream packages
need to link with ``mylib``. The original source directory may have modified, or not be available any more.


Using pkgconfig
===============

The ecbuild CMake scripts provide the Atlas installation with :green:`pkgconfig` files
that contain the instructions for the required include directories, link directories
and link libraries.

Given that the variable ``atlas_ROOT`` is present, we can compile the same
``hello_atlas.cc`` file above, using

.. code:: shell

  export PKG_CONFIG_PATH=$atlas_ROOT/lib64/pkgconfig:$PKG_CONFIG_PATH
  ATLAS_INCLUDES=$(pkg-config atlas --cflags)
  ATLAS_LIBS=$(pkg-config atlas --libs)

  $CXX hello-atlas.cc -o hello-atlas $ATLAS_INCLUDES $ATLAS_LIBS

.. note-danger ::

  Due to the complex nature of how atlas dependencies are defined, and linked, 
  the pkg-config files may not always be generated correctly.
  We don't officially support this method.
