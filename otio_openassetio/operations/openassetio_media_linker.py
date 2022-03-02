# Copyright The Foundry Visionmongers Ltd
#
# SPDX-License-Identifier: Apache-2.0
#
"""
A media linker that resolves media reference URLs via OpenAssetIO if they
contain a valid entity reference.
"""


import re
import opentimelineio as otio


def link_media_reference(in_clip, media_linker_argument_map):

    mr = in_clip.media_reference

    if not mr:
        return

    if isinstance(mr, otio.schema.ExternalReference):
        mr.target_url = "<resolved>"
