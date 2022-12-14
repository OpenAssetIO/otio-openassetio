# Copyright The Foundry Visionmongers Ltd
# SPDX-License-Identifier: Apache-2.0
import os

import pytest

import opentimelineio as otio
from openassetio import exceptions

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


def test_when_linker_used_then_references_are_resolved(bal_linker_args):
    timeline = otio.adapters.read_from_string(
        raw,
        media_linker_name="openassetio_media_linker",
        media_linker_argument_map=bal_linker_args,
    )

    expected = ("file:///asset/1", "file:///asset/2", "file:///not/an/asset")

    for clip, expected in zip(timeline.tracks[0], expected):
        assert clip.media_reference.target_url == expected


def test_when_linker_used_with_incorrect_data_exception_thrown(
    bal_linker_args_missing_asset,
):
    with pytest.raises(exceptions.EntityResolutionError):
        otio.adapters.read_from_string(
            raw,
            media_linker_name="openassetio_media_linker",
            media_linker_argument_map=bal_linker_args_missing_asset,
        )


def test_when_manager_cant_be_found_exception_thrown(
    bal_linker_args_malformed_manager
):
    with pytest.raises(exceptions.PluginError):
        otio.adapters.read_from_string(
            raw,
            media_linker_name="openassetio_media_linker",
            media_linker_argument_map=bal_linker_args_malformed_manager,
        )


def test_when_no_locatable_content_trait_exception_thrown(
    bal_linker_args_no_locatable_content
):
    with pytest.raises(exceptions.EntityResolutionError):
        otio.adapters.read_from_string(
            raw,
            media_linker_name="openassetio_media_linker",
            media_linker_argument_map=bal_linker_args_no_locatable_content,
        )


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


@pytest.fixture()
def bal_linker_args_malformed_manager():
    """
    Provides an arguments dict for the media linker plugin that
    configures it to use the BAL manager, and test resources library.
    """
    return {
        "identifier": "org.notreal.nomanager",
        "settings": {
            "library_path": os.path.join(
                os.path.dirname(__file__), "resources", "test_entity_library.json"
            )
        },
    }


@pytest.fixture()
def bal_linker_args_missing_asset():
    """
    Provides an arguments dict for the media linker plugin that
    configures it to use the BAL manager, with data that is missing an
    expected asset, causing an exception.
    """
    return {
        "identifier": "org.openassetio.examples.manager.bal",
        "settings": {
            "library_path": os.path.join(
                os.path.dirname(__file__),
                "resources",
                "test_entity_library_missing_asset.json",
            )
        },
    }


@pytest.fixture()
def bal_linker_args_no_locatable_content():
    """
    Provides an arguments dict for the media linker plugin that
    configures it to use the BAL manager, with data that does not
    contain the locatable content trait, causing an exception.
    """
    return {
        "identifier": "org.openassetio.examples.manager.bal",
        "settings": {
            "library_path": os.path.join(
                os.path.dirname(__file__),
                "resources",
                "test_entity_library_no_locatable_content.json",
            )
        },
    }
