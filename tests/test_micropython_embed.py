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
    def test_array_module_is_registered(self):
        moduledefs = (
            generate_micropython_embed.PACKAGE / "genhdr" / "moduledefs.h"
        ).read_text(encoding="utf-8")
        self.assertIn("MODULE_DEF_ARRAY", moduledefs)
        self.assertIn("MP_QSTR_array", moduledefs)

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
