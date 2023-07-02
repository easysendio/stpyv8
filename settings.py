import sys
import os
import platform

STPYV8_HOME = os.path.dirname(os.path.realpath(__file__))
DEPOT_HOME  = os.environ.get('DEPOT_HOME', os.path.join(STPYV8_HOME, 'depot_tools'))
V8_HOME     = os.environ.get('V8_HOME', os.path.join(STPYV8_HOME, 'v8'))

V8_GIT_URL        = "https://chromium.googlesource.com/v8/v8.git"
V8_GIT_TAG_STABLE = "11.4.183.19"
V8_GIT_TAG_MASTER = "master"
V8_GIT_TAG        = V8_GIT_TAG_STABLE
DEPOT_GIT_URL     = "https://chromium.googlesource.com/chromium/tools/depot_tools.git"

STPYV8_VERSION = V8_GIT_TAG_STABLE

v8_deps_linux = os.environ.get('V8_DEPS_LINUX', '1') in ('1', )

ICU_DATA_FOLDER_UNIX = "/usr/share/stpyv8"
ICU_DATA_FOLDER_OSX  = "/Library/Application Support/STPyV8/"
ICU_DATA_FOLDER_WINDOWS = "/usr/share/stpyv8"

if os.name in ("posix", ):
    icu_data_folder = ICU_DATA_FOLDER_OSX if sys.platform in ("darwin", ) else ICU_DATA_FOLDER_UNIX
elif os.name in ("nt", ):
    icu_data_folder = ICU_DATA_FOLDER_WINDOWS
else:
    icu_data_folder = None

os.environ['PATH'] = f"{os.environ['PATH']}:{DEPOT_HOME}"

gn_args = {
  "dcheck_always_on"                   : "false",
  "target_os"                          : "win",
  "is_component_build"                 : "true",
  "is_debug"                           : "true",
  "target_cpu"                         : "x64",
  "treat_warnings_as_errors"           : "false",
  "use_custom_libcxx"                  : "false",
  "v8_deprecation_warnings"            : "true",
  "v8_enable_disassembler"             : "false",
  "v8_enable_i18n_support"             : "true",
  "v8_enable_pointer_compression"      : "false",
  "v8_enable_31bit_smis_on_64bit_arch" : "false",
  "v8_imminent_deprecation_warnings"   : "true",
  "v8_monolithic"                      : "true",
  "v8_use_external_startup_data"       : "false"
}

GN_ARGS = ' '.join(f"{key}={value}" for key, value in gn_args.items())

source_files = ["Exception.cpp",
                "Platform.cpp",
                "Isolate.cpp",
                "Context.cpp",
                "Engine.cpp",
                "Wrapper.cpp",
                "Locker.cpp",
                "Utils.cpp",
                "STPyV8.cpp"]


macros             = [("BOOST_PYTHON_STATIC_LIB", None)]
include_dirs       = []
library_dirs       = []
libraries          = []
extra_compile_args = []
extra_link_args    = []

include_dirs.append(os.path.join(V8_HOME, 'include'))
library_dirs.append(os.path.join(V8_HOME, 'out.gn/x64.release.sample/obj/'))

BOOST_PYTHON_LIB_SHORT = f"boost_python{sys.version_info.major}"
BOOST_PYTHON_LIB_LONG  = f"boost_python{sys.version_info.major}{sys.version_info.minor}"

BOOST_PYTHON_UBUNTU_MATRIX = {
    'default' : BOOST_PYTHON_LIB_LONG,
    '18.04'   : BOOST_PYTHON_LIB_SHORT,
    '20.04'   : f"{BOOST_PYTHON_LIB_SHORT}8",
    '22.04'   : f"{BOOST_PYTHON_LIB_SHORT}10"
}

def get_libboost_python_name():
    if not os.path.exists("/etc/lsb-release"):
        return BOOST_PYTHON_UBUNTU_MATRIX['default']

    platform_info = {}

    with open('/etc/lsb-release', encoding = 'utf-8', mode = 'r') as fd:
        for line in fd.readlines():
            s = line.strip()
            p = s.split("=")

            if len(p) < 2:
                continue

            platform_info[p[0]] = p[1]

    if 'DISTRIB_ID' not in platform_info:
        return BOOST_PYTHON_UBUNTU_MATRIX['default']

    if platform_info['DISTRIB_ID'].lower() not in ('ubuntu', ):
        return BOOST_PYTHON_UBUNTU_MATRIX['default']

    release = platform_info['DISTRIB_RELEASE']

    if release not in BOOST_PYTHON_UBUNTU_MATRIX:
        return BOOST_PYTHON_UBUNTU_MATRIX['default']

    return BOOST_PYTHON_UBUNTU_MATRIX[release]

STPYV8_BOOST_PYTHON = os.getenv('STPYV8_BOOST_PYTHON', default = get_libboost_python_name())

if os.name in ("nt", ):
    include_dirs       += [os.environ["BOOST_INCLUDE_DIR"]]
    library_dirs       += [os.environ["BOOST_LIBRARY_DIR"]]
    include_dirs       += [x for x in os.environ.get("INCLUDE", "").split(';') if x]
    library_dirs       += [x for x in os.environ.get("LIB", "").split(';') if x]
    # libraries          += ["winmm", "ws2_32"]
    extra_compile_args += ["/std:c++20", "/O2", "/MT", "/EHsc", "/Gy", "/Zi"]
    extra_link_args    += ["/DLL", "/OPT:REF", "/OPT:ICF", "/MACHINE:X86"]
elif os.name in ("posix", ):
    libraries = ["boost_system", "boost_iostreams", "v8_monolith", STPYV8_BOOST_PYTHON]
    extra_compile_args.append('-std=c++17')

    if platform.system() in ('Linux', ):
        libraries.append("rt")
