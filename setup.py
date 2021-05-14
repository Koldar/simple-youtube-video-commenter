import os
from typing import Iterable

import setuptools
import simple_youtube_video_commenter as commenter

PACKAGE_NAME = "simple-youtube-video-commenter"
PACKAGE_VERSION = commenter.version.VERSION
PACKAGE_DESCRIPTION = "CLI utility for adding comments "
PACKAGE_URL = "https://github.com/Koldar/simple-youtube-video-commenter"
PACKAGE_PYTHON_COMPLIANCE = ">=3.6"
PACKAGE_EXE = PACKAGE_NAME
PACKAGE_MAIN_MODULE = "simple_youtube_video_commenter.main"
PACKAGE_CLASSIFIERS = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]
AUTHOR_NAME = "Massimo Bono"
AUTHOR_EMAIL = "massimobono1@gmail.com"

#########################################################
# INTERNALS
#########################################################

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


def get_dependencies(domain: str = None) -> Iterable[str]:
    if domain is None:
        filename = "requirements.txt"
    else:
        filename = f"requirements-{domain}.txt"
    if os.path.exists(filename):
        print(f"DEPENDENCIES OF TYPE {domain} ARE:")
        with open(filename, "r", encoding="utf-8") as fh:
            for dep in fh.readlines():
                dep_name = dep.split("==")[0]
                print(dep_name + ">=" + dep.split("==")[1].strip())
                yield dep_name + ">=" + dep.split("==")[1].strip()


setuptools.setup(
    name=PACKAGE_NAME,  # Replace with your own username
    version=PACKAGE_VERSION,
    author=AUTHOR_NAME,
    author_email=AUTHOR_EMAIL,
    description=PACKAGE_DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    license_files="LICEN[SC]E*",
    url=PACKAGE_URL,
    packages=setuptools.find_packages(),
    classifiers=PACKAGE_CLASSIFIERS,
    requires=[
        "setuptools",
        "wheel"
    ],
    install_requires=list(get_dependencies()),
    extras_require={
        "test": list(get_dependencies("test")),
        "doc": list(get_dependencies("doc")),
    },
    include_package_data=True,
    package_data={
        "": ["package_data/*.*"],
    },
    python_requires=PACKAGE_PYTHON_COMPLIANCE,
    entry_points={"console_scripts": [f"{PACKAGE_EXE}={PACKAGE_MAIN_MODULE}:main"]},
)
