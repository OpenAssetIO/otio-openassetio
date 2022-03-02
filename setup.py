# Copyright Contributors to the OpenTimelineIO project
# Copyright The Foundry Visionmongers Ltd
#
# SPDX-License-Identifier: Apache-2.0
#

import io
import setuptools

with io.open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()


setuptools.setup(
    name="otio-openassetio",
    author="The Foundry Visionmongers Ltd",
    author_email="tom@foundry.com",
    version="0.0.0",
    description="Adds asset resolution to OpenTimelineIO via the OpenAssetIO API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # Replace url with your repo
    url="https://github.com/TheFoundryVisionmnogers/otio-openassetio",
    packages=setuptools.find_packages(),
    entry_points={"opentimelineio.plugins": "otio_openassetio = otio_openassetio"},
    package_data={
        "otio_openassetio": [
            "plugin_manifest.json",
        ],
    },
    install_requires=["OpenTimelineIO >= 0.12.0"],
    extras_require={"dev": ["black", "pytest", "twine"]},
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Video",
        "Topic :: Multimedia :: Video :: Display",
        "Topic :: Multimedia :: Video :: Non-Linear Editor",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Operating System :: POSIX :: Linux ",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
    ],
)
