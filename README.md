# OpenAssetIO support for OpenTimelineIO

This project adds basic asset resolution capabilities to OpenTimelineIO
via the OpenAssetIO API.

This allows `.otio` media references to point to OpenAssetIO entity
references instead of file URLs. These will be transparently resolved if
the plugin's media linker is enabled.

> Note: This project is currently in it's early alpha stages, more
> information and features coming soon!

## Testing

Initial setup

```shell
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

```python
pytest
```

## Licensing

This project is licensed under the
[Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0.txt).
