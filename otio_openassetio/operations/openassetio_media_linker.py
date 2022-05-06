# Copyright The Foundry Visionmongers Ltd
# SPDX-License-Identifier: Apache-2.0
"""
A media linker that resolves media reference URLs via OpenAssetIO if
their target_url is set to a valid entity reference.
"""

from collections import namedtuple

from openassetio import log, Specification
from openassetio.hostAPI import HostInterface, Session
from openassetio.pluginSystem import PluginSystemManagerFactory


import openassetio_mediacreation
from openassetio_mediacreation.trait import ClipTrait
from openassetio_mediacreation.trait.entity import LocatableContentTrait

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

    # The OpenAssetIO session is stateful to allow stable resolution
    # over time, however this function isn't, so we track a shared
    # session based on the arguments to the media linker.
    session_state = _sessionState(media_linker_argument_map)
    manager = session_state.session.currentManager()

    if not extract_one(manager.isEntityReference([mr.target_url])):
        return

    # Update the locale with more information about this call
    # This is perhaps more illustrative than useful at this point.
    context = session_state.context
    ClipTrait(context.locale).setName(in_clip.name)

    # In this simple implementation, we only need the URL to the media,
    # so we use the LocatableContentTrait directly. As we don't know the
    # specifics of what the external reference may point to, using any
    # particular Specification's traits may end up being wrong. By
    # requesting just the specific trait we require, it avoids the
    # manager fetching any data we are not going to use.
    entity_data = extract_one(
        manager.resolve(
            [mr.target_url], {LocatableContentTrait.kId}, context
        )
    )

    # We then use the concrete accessors of the trait as a view on
    # the resolved data to ensure we access the correct keys/values.
    mr.target_url = LocatableContentTrait(entity_data).getLocation()


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


class OTIOClipLocale(Specification):
    """
    An OpenAssetIO Locale that represents API calls for a track clip
    """

    kTraitIds = {
        # Describe where we are in the OTIO structure a little
        openassetio_mediacreation.trait.TimelineTrait.kId,
        openassetio_mediacreation.trait.TrackTrait.kId,
        openassetio_mediacreation.trait.ClipTrait.kId,
        "otio",
    }

    def __init__(self):
        super().__init__(self.kTraitIds)


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
