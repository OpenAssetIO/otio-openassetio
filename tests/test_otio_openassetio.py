# Copyright The Foundry Visionmongers Ltd
#
# SPDX-License-Identifier: Apache-2.0
#

import os

import pytest

import opentimelineio as otio


def test_when_linker_used_then_references_are_resolved(bal_linker_args):
    raw = """{
        "OTIO_SCHEMA": "Timeline.1",
        "name": "Linker Test",
        "tracks": {
            "OTIO_SCHEMA": "Stack.1",
            "children": [
                {
                    "OTIO_SCHEMA": "Track.1",
                    "kind": "Video",
                    "children": [
                        {
                            "OTIO_SCHEMA": "Clip.1",
                            "media_reference": {
                                "OTIO_SCHEMA": "ExternalReference.1",
                                "target_url": "bal:///asset1"
                            },
                            "name": "Asset1",
                            "source_range": {
                                "OTIO_SCHEMA": "TimeRange.1",
                                "duration": {
                                    "OTIO_SCHEMA": "RationalTime.1",
                                    "rate": 24,
                                    "value": 50
                                },
                                "start_time": {
                                    "OTIO_SCHEMA": "RationalTime.1",
                                    "rate": 24,
                                    "value": 0.0
                                }
                            }
                        },
                        {
                            "OTIO_SCHEMA": "Clip.1",
                            "media_reference": {
                                "OTIO_SCHEMA": "ExternalReference.1",
                                "target_url": "bal:///asset2"
                            },
                            "name": "Asset2",
                            "source_range": {
                                "OTIO_SCHEMA": "TimeRange.1",
                                "duration": {
                                    "OTIO_SCHEMA": "RationalTime.1",
                                    "rate": 24,
                                    "value": 50
                                },
                                "start_time": {
                                    "OTIO_SCHEMA": "RationalTime.1",
                                    "rate": 24,
                                    "value": 0.0
                                }
                            }
                        },
                        {
                            "OTIO_SCHEMA": "Clip.1",
                            "media_reference": {
                                "OTIO_SCHEMA": "ExternalReference.1",
                                "target_url": "file:///not/an/asset"
                            },
                            "name": "NotAnAsset",
                            "source_range": {
                                "OTIO_SCHEMA": "TimeRange.1",
                                "duration": {
                                    "OTIO_SCHEMA": "RationalTime.1",
                                    "rate": 24,
                                    "value": 50
                                },
                                "start_time": {
                                    "OTIO_SCHEMA": "RationalTime.1",
                                    "rate": 24,
                                    "value": 0.0
                                }
                            }
                        }
                    ]
                }
            ]
        }
    }"""

    timeline = otio.adapters.read_from_string(
        raw,
        media_linker_name="openassetio_media_linker",
        media_linker_argument_map=bal_linker_args,
    )

    expected = ("file:///asset/1", "file:///asset/2", "file:///not/an/asset")

    for clip, expected in zip(timeline.tracks[0], expected):
        assert clip.media_reference.target_url == expected


@pytest.fixture()
def bal_linker_args():
    """
    Provides an arguments dict for the media linker plugin that
    configures it to use the BAL manager, and test resources library.
    """
    return {
        "identifier": "org.openassetio.examples.manager.bal",
        "settings": {
            "library_path": os.path.join(
                os.path.dirname(__file__), "resources", "test_entity_library.json"
            )
        },
    }


@pytest.fixture(autouse=True)
def bal_plugin_env(base_dir, monkeypatch):
    """
    Provides a modified environment with the BasicAssetLibrary
    plugin on the OpenAssetIO search path based on the expected
    dependencies install location
    """
    plugin_dir = os.path.join(
        base_dir,
        "dependencies",
        "OpenAssetIO",
        "resources",
        "examples",
        "manager",
        "BasicAssetLibrary",
        "plugin",
    )
    monkeypatch.setenv("OPENASSETIO_PLUGIN_PATH", plugin_dir)


@pytest.fixture()
def base_dir():
    """
    Provides the path to the base directory of this codebase.
    """
    return os.path.dirname(os.path.dirname(__file__))
