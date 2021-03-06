# OpenAssetIO support for OpenTimelineIO

This project adds basic asset resolution capabilities to OpenTimelineIO
via the OpenAssetIO API.

This allows `.otio` media references to point to OpenAssetIO entity
references instead of file URLs. These will be transparently resolved if
the plugin's media linker is enabled.

> Note: This project is currently in it's early alpha stages, more
> information and features coming soon!

## Configuration

The media linker currently takes the following arguments, `settings` is
optional, and should be any required settings for the chosen manager:

```
{
    "identifier": "<required manager identifier>"
    "settings": { ...  }
}
```

Eg:

```python
linker_args = {
    "identifier": "org.openassetio.examples.manager.bal",
    "settings": {
        "library_path": "my_library.json"
    }
}

timeline = otio.adapters.read_from_string(
    otio_str,
    media_linker_name="openassetio_media_linker",
    media_linker_argument_map=linker_args
)
```

## Setup and testing

At this stage, due to the alpha nature of this project, and OpenAssetIO
itself, setup is somewhat manual.

First, clone this repository:

```shell
git clone https://github.com/TheFoundryVisionmongers/otio-openassetio
cd otio-openassetio
```

We recommend a local venv, but feel feel to adapt this to your needs:

```shell
python -m venv .venv
. .venv/bin/activate
```

### Dependencies

To use the linker in OpenTimelineIO `openassetio` and
`openassetio_mediacreation` need to be installed.

At present, for OpenAssetIO, we require installation from source of the
`v0.0.0-alpha.1` tag.

```shell
mkdir dependencies
git clone -b v1.0.0-alpha.1 git@github.com:OpenAssetIO/OpenAssetIO.git dependencies/OpenAssetIO
cmake -S dependencies/OpenAssetIO -B build
cmake --build build --target openassetio-python-py-install
. dist/bin activate
```

The Media Creation library is more straightforward.

```shell
git clone -b v1.0.0-alpha.1 git@github.com:OpenAssetIO/OpenAssetIO-MediaCreation
pip install dependencies/OpenAssetIO-MediaCreation
```

You will now be in a Python virtual environment with `openassetio` and `openassetio_mediacreation` available.

### OpenTimelineIO plugin

The dev extras will also install the required testing dependencies.

```shell
pip install -e '.[dev]'
```

### Testing

The tests make us of the `BasicAssetLibrary` example manager plugin from
the OpenAssetIO repository. They include a `pytest` fixture that extends
the process environment to set the OpenAssetIO plugin search paths to
the dependencies directory as installed above.

Running the tests is then as follows:

```shell
pytest tests
```

## Licensing

This project is licensed under the
[Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0.txt).
