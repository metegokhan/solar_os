MicroPython Embed Component
===========================

This component vendors the MicroPython `ports/embed` package as a self-contained
ESP-IDF component for SolarOS. It is generated from the exact upstream commit
pinned in `scripts/generate_micropython_embed.py` using `mpconfigport.h` and
`qstrdefs.h` as generator inputs.

Run the generator from the repository root:

```sh
python3 scripts/generate_micropython_embed.py
```

By default, the generator fetches the pinned commit from the official
MicroPython repository. For an offline or already-fetched checkout, use:

```sh
python3 scripts/generate_micropython_embed.py \
    --micropython-repo /path/to/micropython
```

Use `--check` with either form to regenerate into a temporary directory and
fail if the checked-in package differs. The generator fixes the source date and
version metadata, so repeated runs produce the same tracked files.

The generated package lives in `micropython_embed/`. SolarOS-specific port
files in `overrides/port/` are applied automatically. They provide cooperative
VM cancellation/yielding, route stdout through SolarOS, provide the interrupt
hook used by `micropython.kbd_intr()`, and keep `__assert_func()` weak for
ESP-IDF newlib.
