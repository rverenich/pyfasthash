#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import math
import codecs
import platform
from glob import glob

from setuptools import setup, Extension

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md')) as f:
    long_description = f.read()

is_x64 = platform.machine() in ['x86_64']
is_arm = platform.machine() in ['aarch64', 'aarch64_be', 'armv8b', 'armv8l']
is_ppc = platform.machine() in ['ppc', 'ppc64', 'ppc64le', 'ppc64le']

macros = []
include_dirs = [
    "src/pybind11/include",
    "src/highwayhash",
]
library_dirs = []
libraries = []
extra_macros = []
extra_compile_args = []
extra_link_args = []

if os.name != "nt":
    macros += [
        ('SUPPORT_INT128', 1),
    ]

if os.name == "nt":
    import platform
    is_64bit = platform.architecture()[0] == "64bit"

    macros += [
        ("WIN32", None),
    ]

    python_home = os.environ.get('PYTHON_HOME')

    if python_home:
        include_dirs += [
            os.path.join(python_home, 'include'),
        ]
        library_dirs += [
            os.path.join(python_home, 'libs'),
        ]

    extra_macros += [("WIN32", 1)]
    extra_compile_args += ["/O2", "/GL", "/MT", "/EHsc", "/Gy", "/Zi"]
    extra_link_args += ["/DLL", "/OPT:REF", "/OPT:ICF",
                        "/MACHINE:X64" if is_64bit else "/MACHINE:X86"]
elif os.name == "posix" and sys.platform == "darwin":
    is_64bit = math.trunc(math.ceil(math.log(sys.maxsize, 2)) + 1) == 64
    include_dirs += [
        '/opt/local/include',
        '/usr/local/include'
    ]

    if is_x64:
        extra_compile_args += ["-msse4.2", "-maes",
                               "-mavx", "-mavx2", "-Wdeprecated-register"]
elif os.name == "posix":
    import platform

    libraries += ["rt", "gcc"]

    if is_x64:
        extra_compile_args += ["-msse4.2", "-maes", "-mavx", "-mavx2"]

highwayhash_sources = [
    "src/highwayhash/highwayhash/arch_specific.cc",
    "src/highwayhash/highwayhash/instruction_sets.cc",
    "src/highwayhash/highwayhash/nanobenchmark.cc",
    "src/highwayhash/highwayhash/os_specific.cc",
    "src/highwayhash/highwayhash/hh_portable.cc",
]

if is_arm:
    extra_compile_args += [
        '-mfloat-abi=hard',
        '-march=armv7-a',
        '-mfpu=neon',
    ]

if is_x64:
    highwayhash_sources += [
        "src/highwayhash/highwayhash/hh_avx2.cc",
        "src/highwayhash/highwayhash/hh_sse41.cc",
    ]
elif is_arm:
    highwayhash_sources.append("src/highwayhash/highwayhash/hh_neon.cc")
elif is_ppc:
    highwayhash_sources.append("src/highwayhash/highwayhash/hh_vsx.cc")

c_libraries = [(
    'fnv', {
        "sources": [
            'src/fnv/hash_32.c',
            'src/fnv/hash_32a.c',
            'src/fnv/hash_64.c',
            'src/fnv/hash_64a.c'
        ],
        "macros": extra_macros,
    }
), (
    'smhasher', {
        "sources": [
            'src/smhasher/MurmurHash1.cpp',
            'src/smhasher/MurmurHash2.cpp',
            'src/smhasher/MurmurHash3.cpp',
            'src/smhasher/City.cpp',
            'src/smhasher/Spooky.cpp',
            'src/smhasher/metrohash64.cpp',
            'src/smhasher/metrohash64crc.cpp',
            'src/smhasher/metrohash128.cpp',
            'src/smhasher/metrohash128crc.cpp',
        ],
        "cflags": extra_compile_args,
    }
), (
    't1ha', {
        "sources": [
            'src/t1ha/src/t1ha0.c',
            'src/t1ha/src/t1ha0_ia32aes_avx.c',
            'src/t1ha/src/t1ha0_ia32aes_avx2.c',
            'src/t1ha/src/t1ha0_ia32aes_noavx.c',
            'src/t1ha/src/t1ha1.c',
            'src/t1ha/src/t1ha2.c',
        ],
        "macros": [
            ("T1HA0_AESNI_AVAILABLE", 1),
            ("T1HA0_RUNTIME_SELECT", 1),
        ],
        "cflags": extra_compile_args,
    }
), (
    'farm', {
        "sources": ['src/smhasher/farmhash-c.c'],
        "macros": extra_macros,
    }
), (
    'lookup3', {
        "sources": ['src/lookup3/lookup3.c'],
        "macros": extra_macros,
    }
), (
    'SuperFastHash', {
        "sources": ['src/SuperFastHash/SuperFastHash.c'],
        "macros": extra_macros,
    }
), (
    "highwayhash", {
        "sources": highwayhash_sources,
        "cflags": extra_compile_args + [
            "-Isrc/highwayhash",
            "-std=c++11"
        ],
    }
), (
    "xxhash", {
        "sources": ["src/xxHash/xxhash.c"],
    }
)]

libraries += [libname for (libname, _) in c_libraries]

pyhash = Extension(name="_pyhash",
                   sources=['src/Hash.cpp'],
                   depends=glob('src/*.h'),
                   define_macros=macros,
                   include_dirs=include_dirs,
                   library_dirs=library_dirs,
                   libraries=libraries,
                   extra_compile_args=extra_compile_args + ["-std=c++11"],
                   extra_link_args=extra_link_args,
                   )

setup(name='pyhash',
      version='0.9.4',
      description='Python Non-cryptographic Hash Library',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/flier/pyfasthash',
      download_url='https://github.com/flier/pyfasthash/releases',
      platforms=["x86", "x64"],
      author='Flier Lu',
      author_email='flier.lu@gmail.com',
      license="Apache Software License",
      packages=['pyhash'],
      libraries=c_libraries,
      ext_modules=[pyhash],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: Apache Software License',
          'Natural Language :: English',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: C++',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: Implementation :: PyPy',
          'Topic :: Internet',
          'Topic :: Software Development',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Utilities'
      ],
      keywords='hash hashing fasthash',
      setup_requires=['pytest-runner', 'pytest-benchmark'],
      tests_require=['pytest'],
      use_2to3=True)
