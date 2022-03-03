# Copyright The Foundry Visionmongers Ltd
#
# SPDX-License-Identifier: Apache-2.0
#
"""
A media linker that resolves media reference URLs via OpenAssetIO if
their target_url is set to a valid entity reference.
"""

from collections import namedtuple

from openassetio import log
from openassetio.hostAPI import HostInterface, Session
from openassetio.specifications import LocaleSpecification
from openassetio.pluginSystem import PluginSystemManagerFactory

import opentimelineio as otio


#
# Media Linker
#


def link_media_reference(in_clip, media_linker_argument_map):

    # Once https://github.com/TheFoundryVisionmongers/OpenAssetIO/issues/247
    # is implemented, we can more concisely handle ImageSequenceReference,
    # but we will need to convert file:///a/path/sequence.%04d.ext to the
    # component fields required by OTIO. For now, we only handle simple
    # ExternalReference schemas.
    # We can then also set all other relevant properties of the
    # Clip/MediaReference based on trait properties.
    # For now, keep it simple and just resolve the URL

    mr = in_clip.media_reference

    if not isinstance(mr, otio.schema.ExternalReference):
        return

    session_state = _sessionState(media_linker_argument_map)
    manager = session_state.session.currentManager()

    if not extract_one(manager.isEntityReference([mr.target_url])):
        return

    context = session_state.context
    context.locale.clipName = in_clip.name

    mr.target_url = extract_one(
        manager.resolveEntityReference([mr.target_url], context)
    )


#
# OpenAssetIO classes
#

# Due to the way OTIO imports plugins, we can't factor these out into
# their own module. It thinks this code is part of the the
# opentimelineio.adapters module:
#
#   from .shared import OTIOHostInterface
#   > ModuleNotFoundError: No module named 'opentimelineio.adapters.shared'
#
# Its not really a problem right now as this is the only place we need
# them.


class OTIOHostInterface(HostInterface):
    """
    An OpenAssetIO HostInterface implementation for the OTIO media linker
    """

    def identifier(self):
        return "com.foundry.otio-openassetio.medialinker"

    def displayName(self):
        return "OpenTimelineIO OpenAssetIO Media Linker plugin"


class OTIOClipLocale(LocaleSpecification):
    """
    An OpenAssetIO Locale that represents API calls for a track clip
    """

    _type = "timeline.track.clip.otio"

    clipName = LocaleSpecification.TypedProperty(
        str,
        doc="The name of the clip in the timeline for which the reference is being resolved.",
    )


#
# Helpers
#

# Until we have singular conveniences in hostAPI.Manager (see
# https://github.com/TheFoundryVisionmongers/OpenAssetIO/issues/107),
# then we need to unpack the batch result and raise any exceptions
# returned for our singular reference.


def extract_one(results):
    """
    A convenience to extract the first result from a batch OpenAssetIO
    result, raising if it is an exception.
    """
    result = results[0]
    if isinstance(result, Exception):
        raise result
    return result


#
# Session Management
#

# Ideally we would tie a session into the lifetime of a media linker, but
# as they're free functions, rather than instanitated classes, we don't
# know when they are needed. This simple/naive approach effectively
# persists a session/context for as long as the args to the linker are
# the same. This is not ideal. The context lifetime should really be
# tied to each specific Timeline. That is an exercise for another day.

SessionState = namedtuple("SessionState", ("session", "context"))

_last_args = None
_session_state = None


def _sessionState(args: dict) -> Session:
    """
    Returns a SessionState configured for the supplied settings. If the
    settings are the same as the last invocation, the previously
    constructed state will be reused.
    """

    global _last_args
    global _session_state

    if args != _last_args:
        _session_state = None

    if _session_state is None:
        _last_args = args
        _session_state = _createSessionState(args)

    return _session_state


def _createSessionState(args: dict) -> SessionState:
    """
    Configures a new SessionState with the manager + settings from the
    supplied args. A new Context is created and configured for read NB
    with the correct locale.
    """

    host = OTIOHostInterface()
    logger = log.SeverityFilter(log.ConsoleLogger())
    factory = PluginSystemManagerFactory(logger)

    session = Session(host, logger, factory)
    session.useManager(args["identifier"], args.get("settings", {}))

    # The lifetime of the context would ideally be tied to each specific
    # call to read_from_string or similar. Maybe we could introspect
    # each clip and see which Timeline it belongs to. This will do for
    # now though and is better than making a context per clip.
    context = session.createContext()
    context.access = context.kRead
    context.locale = OTIOClipLocale()

    return SessionState(session=session, context=context)
