# Copyright The Foundry Visionmongers Ltd
#
# SPDX-License-Identifier: Apache-2.0
#
import opentimelineio as otio


def test_when_media_linker_enabled_then_references_are_resolved():
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
                                "target_url": "bal:///assetClipA"
                            },
                            "name": "A",
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
        raw, media_linker_name="openassetio_media_linker"
    )

    for clip in timeline.tracks[0]:
        assert clip.media_reference.target_url == "<resolved>"
