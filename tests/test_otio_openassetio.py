# Copyright The Foundry Visionmongers Ltd
# SPDX-License-Identifier: Apache-2.0
import os
from unittest import mock

import pytest

import opentimelineio as otio
from openassetio import errors
from openassetio.hostApi import ManagerFactory, Manager


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
    with pytest.raises(errors.OpenAssetIOException):
        otio.adapters.read_from_string(
            raw,
            media_linker_name="openassetio_media_linker",
            media_linker_argument_map=bal_linker_args_missing_asset,
        )


def test_when_manager_cant_be_found_exception_thrown(bal_linker_args_malformed_manager):
    with pytest.raises(errors.InputValidationException):
        otio.adapters.read_from_string(
            raw,
            media_linker_name="openassetio_media_linker",
            media_linker_argument_map=bal_linker_args_malformed_manager,
        )


def test_when_manager_cant_resolve_then_exception_thrown(bal_linker_args, monkeypatch):
    hasCapability = mock.Mock(spec=Manager.hasCapability)
    monkeypatch.setattr(Manager, "hasCapability", hasCapability)
    hasCapability.return_value = False

    with pytest.raises(
        errors.ConfigurationException,
        match="Basic Asset Library 📖 is not capable of resolving entity references",
    ):
        otio.adapters.read_from_string(
            raw,
            media_linker_name="openassetio_media_linker",
            media_linker_argument_map=bal_linker_args,
        )

    hasCapability.assert_called_once_with(Manager.Capability.kResolution)


def test_when_no_locatable_content_trait_exception_thrown(
    bal_linker_args_no_locatable_content,
):
    with pytest.raises(errors.OpenAssetIOException) as err:
        otio.adapters.read_from_string(
            raw,
            media_linker_name="openassetio_media_linker",
            media_linker_argument_map=bal_linker_args_no_locatable_content,
        )

    assert isinstance(err.value.__cause__, ValueError)
    assert str(err.value.__cause__) == "Entity 'bal:///asset1' has no location"


def test_when_no_manager_setting_then_default_config_used(
    linker_args_no_settings, monkeypatch
):
    # A bit nasty, but we don't have a portable way to populate a toml
    # file with a library path that isn't sensitive to cwd, so assume
    # that if we managed to specify BAL, without a library, then it is
    # our test toml that was loaded by the default mechanism.
    a_config = os.path.join(
        os.path.dirname(__file__), "resources", "default_config.toml"
    )
    monkeypatch.setenv(ManagerFactory.kDefaultManagerConfigEnvVarName, a_config)

    # Ensure any existing env doesn't affect the tests
    monkeypatch.delenv("BAL_LIBRARY_PATH", raising=False)

    with pytest.raises(
        errors.ConfigurationException,
        match="'library_path'/BAL_LIBRARY_PATH not set or is empty",
    ):
        otio.adapters.read_from_string(
            raw,
            media_linker_name="openassetio_media_linker",
            media_linker_argument_map=linker_args_no_settings,
        )


def test_when_no_manager_setting_and_no_default_config_then_error_raised(
    linker_args_no_settings, monkeypatch
):
    monkeypatch.delenv(ManagerFactory.kDefaultManagerConfigEnvVarName, raising=False)
    with pytest.raises(
        errors.ConfigurationException, match="No default OpenAssetIO manager configured"
    ):
        otio.adapters.read_from_string(
            raw,
            media_linker_name="openassetio_media_linker",
            media_linker_argument_map=linker_args_no_settings,
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


@pytest.fixture()
def linker_args_no_settings():
    """
    Provides an arguments dict for the media linker plugin that
    doesn't include any OpenAssetIO manager settings.
    """
    return {}
