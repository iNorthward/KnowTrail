import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location(
    "param_guard",
    Path(__file__).resolve().parents[1] / "scripts/java/lint-java-param.py",
)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class JavaParamTests(unittest.TestCase):
    def test_interface_deletion(self):
        old = "interface A {\n/** @param id account */\nvoid remove(Long id);\n}"
        self.assertEqual(m.violations(old, "interface A {}"), [])

    def test_parameter_rename(self):
        old = "interface A {\n/** @param id account */\nvoid update(Long id);\n}"
        new = old.replace("id", "accountId")
        self.assertEqual(m.violations(old, new), [])
        self.assertTrue(
            m.violations(old, new.replace("@param accountId", "@param wrong"))
        )

    def test_retained_method_stripped(self):
        old = "class A {\n/** @param id account */\npublic void keep(Long id) {}\n}"
        self.assertTrue(m.violations(old, old.replace("/** @param id account */", "")))

    def test_mixed_hunk_no_blanket_exemption(self):
        old = "class A {\n/** @param x x */\nvoid gone(int x) {}\n/** @param y y */\nvoid stay(int y) {}\n}"
        self.assertTrue(m.violations(old, "class A { void stay(int y) {} }"))

    def test_overloads_separate(self):
        old = "interface A {\n/** @param x x */\nvoid f(int x);\n/** @param y y */\nvoid f(String y);\n}"
        self.assertTrue(m.violations(old, old.replace("/** @param y y */", "")))
        self.assertEqual(
            m.violations(old, old.replace("/** @param x x */\nvoid f(int x);", "")), []
        )

    def test_nested_class_separate(self):
        old = "class A {\n/** @param x x */\nvoid f(int x) {}\nclass B {\n/** @param x x */\nvoid f(int x) {}\n}\n}"
        self.assertTrue(m.violations(old, old.replace("/** @param x x */", "", 1)))

    def test_annotation_generics_and_multiline(self):
        old = 'interface A {\n/** @param values input */\n@Api(value={"x", "y"})\npublic void f(\n final java.util.Map<String, Long> values\n);\n}'
        self.assertEqual(m.violations(old, old.replace("values", "items")), [])
        self.assertTrue(
            m.violations(old, old.replace("/** @param values input */", ""))
        )
        self.assertTrue(m.violations(old, old.replace("@param values", "@param wrong")))
        self.assertEqual(len(m.methods(old)[0]), 1)

    def test_type_change_does_not_hide_doc_removal(self):
        old = "interface A {\n/** @param x x */\nvoid f(int x);\n}"
        self.assertTrue(m.violations(old, "interface A { void f(long x); }"))

    def test_parameter_removed_not_false_positive(self):
        old = "interface A {\n/** @param x x */\nvoid f(int x);\n}"
        self.assertEqual(m.violations(old, "interface A { void f(); }"), [])


if __name__ == "__main__":
    unittest.main()
