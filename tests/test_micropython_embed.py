import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


REPOSITORY = Path(__file__).resolve().parents[1]
GENERATOR_PATH = REPOSITORY / "scripts" / "generate_micropython_embed.py"
SPEC = importlib.util.spec_from_file_location("generate_micropython_embed", GENERATOR_PATH)
assert SPEC is not None and SPEC.loader is not None
generate_micropython_embed = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = generate_micropython_embed
SPEC.loader.exec_module(generate_micropython_embed)


class MicroPythonEmbedTest(unittest.TestCase):
    def test_extra_profile_modules_are_registered(self):
        moduledefs = (
            generate_micropython_embed.PACKAGE / "genhdr" / "moduledefs.h"
        ).read_text(encoding="utf-8")
        for module in (
            "ARRAY",
            "CMATH",
            "COLLECTIONS",
            "ERRNO",
            "GC",
            "MATH",
            "MICROPYTHON",
            "STRUCT",
            "SYS",
        ):
            self.assertIn(f"MODULE_DEF_{module}", moduledefs)

    def test_extra_profile_keeps_unintegrated_port_features_disabled(self):
        config = (
            generate_micropython_embed.COMPONENT / "mpconfigport.h"
        ).read_text(encoding="utf-8")
        self.assertIn("MICROPY_CONFIG_ROM_LEVEL_EXTRA_FEATURES", config)
        for feature in (
            "MICROPY_ENABLE_EXTERNAL_IMPORT",
            "MICROPY_PY_BUILTINS_EXECFILE",
            "MICROPY_PY_BUILTINS_INPUT",
            "MICROPY_PY_IO",
            "MICROPY_PY_SYS_STDFILES",
            "MICROPY_PY_ASYNCIO",
            "MICROPY_PY_JSON",
            "MICROPY_PY_OS",
            "MICROPY_PY_LWIP",
            "MICROPY_PY_SSL",
            "MICROPY_PY_WEBSOCKET",
        ):
            self.assertRegex(config, rf"#define {feature}\s+\(0\)")

    def test_solaros_port_overrides_match_vendored_output(self):
        for override in generate_micropython_embed.PORT_OVERRIDES.iterdir():
            if override.is_file():
                self.assertEqual(
                    override.read_bytes(),
                    (
                        generate_micropython_embed.PACKAGE
                        / "port"
                        / override.name
                    ).read_bytes(),
                )

    def test_tree_difference_reports_missing_unexpected_and_changed_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            expected = root / "expected"
            actual = root / "actual"
            expected.mkdir()
            actual.mkdir()
            (expected / "missing").write_text("expected", encoding="utf-8")
            (expected / "changed").write_text("expected", encoding="utf-8")
            (actual / "changed").write_text("actual", encoding="utf-8")
            (actual / "unexpected").write_text("actual", encoding="utf-8")
            self.assertEqual(
                generate_micropython_embed.differences(expected, actual),
                ["missing missing", "unexpected unexpected", "changed changed"],
            )


if __name__ == "__main__":
    unittest.main()
