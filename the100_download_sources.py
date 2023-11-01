##########################################################################
#
# This script will download all the C/C++ package tar sources to a local
# folder -> extract, build and install the tar sources -> extract the .bc
# files from the installed archives using wllvm
#
# invoke this script with sudo, so that packages can be installed
#
# Make sure that clang and llvm-link are set to the same llvm version before
# invoking this script.
#
##########################################################################
from pkg_manager import PackageManager
from ctypes.util import find_library
import os
import subprocess

# import sys
# import re

# make sure paths are set correctly
# path the the mirror file
source_file_to_read_packages_from = (
    "/workdisk/shank/misc/the100/apt-scraper-utils/Sources-JammyMain"
)

# mirror url
mirror_url = "http://mirror.math.ucdavis.edu/ubuntu/"

# sources will be downloaded here
local_download_folder_for_sources = (
    "/workdisk/shank/misc/the100/apt-scraper-utils/apt_scraper_sources"
)

# script will extract and build it here
extracted_tar_sources = (
    "/workdisk/shank/misc/the100/apt-scraper-utils/extracted_tar_sources"
)

# bitcodes will here extracted here
afl_fuzzing_sources = (
    "/workdisk/shank/misc/the100/apt-scraper-utils/afl_sources"
)

# results file(s)
compilation_results_file = (
    "/home/shank/code/research/the100/apt-scraper-utils/results_compilation.txt"
)

if not os.path.isdir(local_download_folder_for_sources):
    cmd = "(" + "mkdir " + local_download_folder_for_sources + ")"
    print(f"executing>> {cmd}")
    subprocess.call(cmd, shell=True)

if not os.path.isdir(afl_fuzzing_sources):
    cmd = "(" + "mkdir " + afl_fuzzing_sources + ")"
    print(f"executing>> {cmd}")
    subprocess.call(cmd, shell=True)

if not os.path.isdir(extracted_tar_sources):
    cmd = "(" + "mkdir " + extracted_tar_sources + ")"
    print(f"executing>> {cmd}")
    subprocess.call(cmd, shell=True)


# p = PackageManager(source_file_to_read_packages_from, mirror_url)
# p.build_pkg_entries()
#
# p.dump_to_pickled_json("dump_jammy_main.picked.json")
p = PackageManager.from_picked_json("dump_jammy_main.picked.json")


# packages_available = p.all_pkg_entries
packages_available = list(p.all_pkg_entries.keys())

# for making package installation noninterative
cmd = "(" + "export DEBIAN_FRONTEND=noninteractive" + ")"
print(f"executing>> {cmd}")
subprocess.call(cmd, shell=True)


# total download count
dl_cnt = 0

# checked deps
checked_available = set()

start_idx = 300

# for pkgs in packages_available[start_idx:]:
#     reverse_dependencies = []
#     dependency_list = p.dependency_map[pkgs]
#     for dependencies in dependency_list:
#         if dependencies not in checked_available:
#             subprocess.call(["sudo apt -yq install", str(dependencies)], shell=True)
#             checked_available.add(dependencies)
#         else:
#             print(f">> dep:{dependencies} already checked")
#
#         # install all reverse dependencies might be too slow (not necessary), uncomment if needed
#         # for reverse_deps in p.reverse_dependency_map[dependencies]:
#         #    subprocess.call(['sudo apt -yq install', str(reverse_deps)], shell=True)
#         reverse_dependencies.extend(p.reverse_dependency_map[dependencies])
#
#     print()
#     print("...")
#     print("DOWNLOADING " + str(pkgs) + "from the mirror...")
#     print("...")
#     p.download_package_source(pkgs, local_download_folder_for_sources)
#     dl_cnt += 1
#     print(f">> dl_cnt={dl_cnt}")
#
#     # for lib in reverse_dependencies:
#     #     if find_library(lib) != None:
#     #         print()
#     #         print("...")
#     #         print("DOWNLOADING " + str(pkgs) + "from the mirror...")
#     #         print("...")
#     #         p.download_package_source(pkgs, local_download_folder_for_sources)
#     #         dl_cnt += 1
#     #         print(f">> dl_cnt={dl_cnt}")
#     #         break
#
#     # all_dep_libs_available = True
#     # print(f">> len(reverse_dependencies)={len(reverse_dependencies)}")
#     # for lib in reverse_dependencies:
#     #     print(f">> checking for lib:{lib}")
#     #     if find_library(lib) is None:
#     #         all_dep_libs_available = False
#     #         break
#     #
#     # if all_dep_libs_available:
#     #     print()
#     #     print("...")
#     #     print("DOWNLOADING " + str(pkgs) + "from the mirror...")
#     #     print("...")
#     #     p.download_package_source(pkgs, local_download_folder_for_sources)
#     #     dl_cnt += 1
#     #     print(f">> dl_cnt={dl_cnt}")
#
#     if dl_cnt == 300:
#         print(f">> downloaded {dl_cnt} packages")
#         break
# start_idx = 0
start_idx = 1400

for (i, pkgs) in enumerate(packages_available[start_idx:]):
    print(f">> processing i:{i}")

    reverse_dependencies = []
    dependency_list = p.dependency_map[pkgs]
    for dependencies in dependency_list:
        if dependencies not in checked_available:
            cmd = f"sudo apt -yq install {dependencies}"
            print(f">> executing>> {cmd}")
            # subprocess.call(["sudo apt -yq install", str(dependencies)], shell=True)
            subprocess.call(cmd, shell=True)
            checked_available.add(dependencies)
        else:
            print(f">> dep:{dependencies} already checked")

        # install all reverse dependencies might be too slow (not necessary), uncomment if needed
        # for reverse_deps in p.reverse_dependency_map[dependencies]:
        #    subprocess.call(['sudo apt -yq install', str(reverse_deps)], shell=True)
        reverse_dependencies.extend(p.reverse_dependency_map[dependencies])

    print()
    print("...")
    print("DOWNLOADING " + str(pkgs) + "from the mirror...")
    print("...")
    p.download_package_source(pkgs, local_download_folder_for_sources)
    dl_cnt += 1
    print(f">> dl_cnt={dl_cnt}")

    if dl_cnt == 500:
        print(f">> downloaded {dl_cnt} packages")
        break


success_cnt = 0
target_success_cnt = 100
# target_success_cnt = 2
# Extract the tar sources, build them and install and put them in another folder
with open(compilation_results_file, "a+") as outf:
    # get list of already processed packages
    outf.seek(0)
    prev_processed = set()
    for line in outf.readlines():
        line = line.strip()
        parts = line.split(",")
        pkg, res = parts[0], parts[1]
        print(f">> adding to prev_processed: {pkg}")
        prev_processed.add(pkg)
        if res == "success":
            success_cnt += 1

    # process all downloaded packages
    for subdir, dirs, files in os.walk(local_download_folder_for_sources):
        for File in files:
            if ".orig." in str(File):

                archive_parts = File.split(".orig")
                underscore_split = archive_parts[0].split("_")

                directory_name = ""
                try:
                    directory_name = (
                        str(underscore_split[0]) + "-" + str(underscore_split[1])
                    )
                except:
                    continue

                print(f">> directory_name: {directory_name}")

                if directory_name in prev_processed:
                    print(f">> skipping {directory_name} (reason: prev_processed)")
                    continue

                # extract the archive
                cmd = (
                    "("
                    + f"cd {local_download_folder_for_sources}"
                    + " && "
                    + f"tar -xf {str(File)}"
                    + ")"
                )
                print(f"executing>> {cmd}")
                subprocess.call(cmd, shell=True)

                configure_path = (
                    local_download_folder_for_sources
                    + "/"
                    + directory_name
                    + "/"
                    + "configure"
                )

                # check if a configure script exists in the directory
                if os.path.exists(configure_path) == True:
                    # print(File)
                    # now cd into the archive
                    # cmd = (
                    #     "("
                    #     + f"cd {local_download_folder_for_sources}/{directory_name}"
                    #     + " && "
                    #     + "export LLVM_COMPILER=clang"
                    #     + " && "
                    #     + "export WLLVM_OUTPUT_LEVEL=Debug"
                    #     + " && "
                    #     + f"export WLLVM_OUTPUT_FILE=/tmp/{str(File)}_wllvm.log"
                    #     + " && "
                    #     + " make clean"
                    #     + " && "
                    #     + "CC=wllvm CXX=wllvm++ CFLAGS='-g -O0' CXXFLAGS='-g -O0' yes '' | ./configure"
                    #     + " && "
                    #     + "make CC=wllvm CXX=wllvm++ -j12"
                    #     + " && "
                    #     + f"make CC=wllvm CXX=wllvm++ install DESTDIR={extracted_tar_sources}/{directory_name}"
                    #     + ")"
                    # )
                    cmd = (
                        "("
                        + f"cd {local_download_folder_for_sources}/{directory_name}"
                        + " && "
                        + "CC=clang CXX=clang++ CFLAGS='-g -O0' CXXFLAGS='-g -O0' yes '' | ./configure"
                        + " && "
                        + "make clean"
                        + " && "
                        + "bear -- make CC=clang CXX=clang++ -j$(nproc)"
                        + " && "
                        + f"rm -rf {extracted_tar_sources}/{directory_name}"
                        + " && "
                        + f"make CC=clang CXX=clang++ install DESTDIR={extracted_tar_sources}/{directory_name}"
                        + ")"
                    )
                    print(f"executing>> {cmd}")
                    res = subprocess.call(cmd, shell=True)
                    if res == 0:
                        success_cnt += 1
                        print(f">> success[{success_cnt}]")
                        outf.write(f"{directory_name},success\n")
                    else:
                        print(f">> failed")
                        outf.write(f"{directory_name},failed\n")

                    if success_cnt == target_success_cnt:
                        print(f">> success_cnt={str(success_cnt)}")
                        break

# # run extract-bc to get the bit-code files form the binaries
# for subdir, dirs, files in os.walk(extracted_tar_sources):
#
#     if subdir.endswith("/bin"):
#
#         for File in files:
#             cmd = (
#                 "("
#                 + f"cd {subdir}"
#                 + " && "
#                 + f"extract-bc {File}"
#                 + " && "
#                 + f"mv {File}.bc {afl_fuzzing_sources}"
#                 + ")"
#             )
#             print(f"executing>> {cmd}")
#             subprocess.call(cmd, shell=True)
#
# # run extract-bc to get bitcodes from library files if any
# for subdir, dirs, files in os.walk(extracted_tar_sources):
#
#     if subdir.endswith("/lib"):
#
#         for File in files:
#             if (".a") in File:
#                 cmd = (
#                     "("
#                     + f"cd {subdir}"
#                     + " && "
#                     + f"extract-bc -b {File}"
#                     + " && "
#                     + f"mv {File}.bc {afl_fuzzing_sources}"
#                     + ")"
#                 )
#                 print(f"executing>> {cmd}")
#                 subprocess.call(cmd, shell=True)
